from __future__ import annotations

import contextlib
import sqlite3

from experiments.asymmetric_provider_history.protocol import HistoricalVerificationError
from experiments.shared_anchor_intent_ledger.protocol import (
    Intent,
    IntentConflict,
    IntentGap,
    IntentSubstitution,
    PendingIntent,
    ProviderMismatch,
    UnexplainedAdvance,
)

from .full_operation_guards import install_full_operation_guards
from .operation_permit import (
    OperationPermitError,
    PermitConnection,
    install_operation_permit_udf,
    one_shot_permit,
)
from .real_integration import SupportedMutableAsymmetricSharedAnchorLedger
from .row_tokens import (
    install_row_token_udfs,
    intent_row_token,
    receipt_row_token,
)


class SupportedOperationScopedAsymmetricSharedAnchorLedger(
    SupportedMutableAsymmetricSharedAnchorLedger
):
    """Final LAB-091 candidate with exact one-shot authorization per DML.

    SQL transaction scope and write authority are deliberately separate. A
    `BEGIN IMMEDIATE` holds serialization but grants no mutation capability by
    itself. Each consequential DML statement receives one exact connection-local
    permit immediately before execution; the trigger consumes it before the row
    mutation. External provider/network calls therefore run with no SQL permit.
    """

    def _con(self):
        q = sqlite3.connect(
            self.path,
            timeout=5,
            isolation_level=None,
            factory=PermitConnection,
        )
        q.execute("PRAGMA busy_timeout=5000")
        install_operation_permit_udf(q)
        install_row_token_udfs(q)
        return q

    @contextlib.contextmanager
    def _write_txn(self, q):
        if type(q) is not PermitConnection:
            raise TypeError("exact LAB-091 permit connection required")
        if getattr(q, "_lab091_permit", None) is not None:
            raise OperationPermitError("stale permit before transaction")
        q.execute("BEGIN IMMEDIATE")
        try:
            yield q
            if q._lab091_permit is not None:
                raise OperationPermitError("unused operation permit at commit boundary")
            q.commit()
        except Exception:
            q._lab091_permit = None
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q._lab091_permit = None

    def _install_guards(self):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            install_full_operation_guards(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _entry_token(entry, *, status=None, receipt_binding=...):
        if status is None:
            status = entry.status
        if receipt_binding is ...:
            receipt_binding = entry.receipt_binding
        return intent_row_token(
            entry.intent_id,
            entry.component_id,
            entry.intent_type,
            entry.payload_digest,
            entry.provider_id,
            entry.provider_generation,
            entry.predecessor_position,
            entry.position,
            entry.request_id,
            status,
            receipt_binding,
        )

    @staticmethod
    def _receipt_token(receipt):
        return receipt_row_token(
            receipt.request_id,
            receipt.provider_id,
            receipt.generation,
            receipt.position,
            receipt.kind,
            receipt.challenge,
            receipt.signature,
            receipt.stable_binding,
        )

    def reserve(self, intent: Intent):
        intent.validate()
        q = self._con()
        try:
            with self._write_txn(q):
                existing = q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,"
                    "provider_id,provider_generation,predecessor_position,position,"
                    "request_id,status,receipt_binding "
                    "FROM shared_anchor_intents WHERE intent_id=?",
                    (intent.intent_id,),
                ).fetchone()
                if existing is not None:
                    entry = self._row_entry(existing)
                    if (
                        entry.component_id != intent.component_id
                        or entry.intent_type != intent.intent_type
                        or entry.payload_digest != intent.payload_digest
                    ):
                        raise IntentConflict("intent_id reused with different content")
                    return entry

                pending = q.execute(
                    "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
                ).fetchone()[0]
                if pending:
                    raise PendingIntent("another anchor intent is unresolved")

                durable = self.provider_history._current_locked(q)
                predecessor = q.execute(
                    "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
                ).fetchone()[0]
                position = predecessor + 1
                request_id = self._request_id(
                    position,
                    intent.intent_id,
                    intent.component_id,
                    intent.intent_type,
                    intent.payload_digest,
                )
                row = (
                    intent.intent_id,
                    intent.component_id,
                    intent.intent_type,
                    intent.payload_digest,
                    durable.provider_id,
                    durable.generation,
                    predecessor,
                    position,
                    request_id,
                    "PREPARED",
                    None,
                )
                with one_shot_permit(
                    q,
                    kind="intent-insert",
                    identity=intent.intent_id,
                    old_value="",
                    new_value=intent_row_token(*row),
                ):
                    q.execute(
                        "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                        row[:9],
                    )
                with one_shot_permit(
                    q,
                    kind="meta-update",
                    identity="1",
                    old_value=str(predecessor),
                    new_value=str(position),
                ):
                    changed = q.execute(
                        "UPDATE shared_anchor_meta SET reserved_position=? "
                        "WHERE singleton=1 AND reserved_position=?",
                        (position, predecessor),
                    ).rowcount
                if changed != 1:
                    raise IntentConflict("shared anchor tail changed during reservation")
            return self.entry(intent.intent_id)
        finally:
            q.close()

    def _reauthenticate(self, entry):
        q = self._con()
        try:
            q.execute("BEGIN")
            existing = self.provider_history._maybe_load_receipt_locked(q, entry.request_id)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        if existing is not None:
            return self._receipt_binds_entry(existing, entry)
        if entry.status == "CONFIRMED":
            raise HistoricalVerificationError("confirmed ledger row is missing asymmetric receipt")

        self._runtime_matches_entry(entry)
        challenge = self.attested.challenge()
        observed = self.attested.provider.reconcile_increment(
            challenge=challenge,
            request_id=entry.request_id,
        )
        if observed is None:
            raise UnexplainedAdvance("provider has no result for ledger request")
        verified = self.attested.verifier.verify(
            observed,
            expected_challenge=challenge,
            allowed_kinds={"RECONCILE"},
        )
        if verified.position != entry.position or verified.request_id != entry.request_id:
            raise UnexplainedAdvance("provider result does not bind ledger position/request")

        candidate = self._signed_receipt_from_observation(verified)
        self._receipt_binds_entry(candidate, entry)

        q = self._con()
        try:
            with self._write_txn(q):
                current = self._row_entry(
                    q.execute(
                        "SELECT intent_id,component_id,intent_type,payload_digest,"
                        "provider_id,provider_generation,predecessor_position,position,"
                        "request_id,status,receipt_binding "
                        "FROM shared_anchor_intents WHERE intent_id=?",
                        (entry.intent_id,),
                    ).fetchone()
                )
                if not self._same_request(current, entry):
                    raise IntentSubstitution("ledger request changed before asymmetric receipt persistence")

                winner = self.provider_history._maybe_load_receipt_locked(q, entry.request_id)
                if winner is not None:
                    binding = self._receipt_binds_entry(winner, entry)
                else:
                    if current.status == "CONFIRMED":
                        raise HistoricalVerificationError("confirmed ledger row is missing asymmetric receipt")
                    with one_shot_permit(
                        q,
                        kind="receipt-insert",
                        identity=candidate.request_id,
                        old_value="",
                        new_value=self._receipt_token(candidate),
                    ):
                        binding = self.provider_history._store_receipt_locked(q, candidate)

                if current.status == "CONFIRMED":
                    if current.receipt_binding != binding:
                        raise IntentSubstitution("concurrent confirmation receipt binding mismatch")
                    return binding
                if current != entry:
                    raise IntentSubstitution("unexpected PREPARED ledger mutation during reconciliation")
                return binding
        finally:
            q.close()

    def execute(self, intent: Intent, *, timeout_after_commit=False):
        entry = self.reserve(intent)
        if entry.status == "CONFIRMED":
            receipt = self._reauthenticate(entry)
            if receipt != entry.receipt_binding:
                raise IntentSubstitution("confirmed receipt binding changed")
            return entry

        self._runtime_matches_entry(entry)
        try:
            self.attested.catch_up_one(
                db_sequence=entry.position,
                request_id=entry.request_id,
                timeout_after_commit=timeout_after_commit,
            )
            receipt = self._reauthenticate(entry)
        except Exception as exc:
            raise PendingIntent(str(exc)) from exc

        q = self._con()
        try:
            with self._write_txn(q):
                current = self._row_entry(
                    q.execute(
                        "SELECT intent_id,component_id,intent_type,payload_digest,"
                        "provider_id,provider_generation,predecessor_position,position,"
                        "request_id,status,receipt_binding "
                        "FROM shared_anchor_intents WHERE intent_id=?",
                        (intent.intent_id,),
                    ).fetchone()
                )
                if current != entry:
                    raise IntentSubstitution("ledger entry changed before confirmation")
                with one_shot_permit(
                    q,
                    kind="intent-confirm",
                    identity=current.intent_id,
                    old_value=self._entry_token(current),
                    new_value=self._entry_token(
                        current,
                        status="CONFIRMED",
                        receipt_binding=receipt,
                    ),
                ):
                    changed = q.execute(
                        "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? "
                        "WHERE intent_id=? AND status='PREPARED' AND receipt_binding IS NULL",
                        (receipt, intent.intent_id),
                    ).rowcount
                if changed != 1:
                    raise IntentSubstitution("ledger confirmation lost CAS")
            return self.entry(intent.intent_id)
        finally:
            q.close()

    def verify_component(self, component_id):
        if not isinstance(component_id, str) or not component_id:
            raise IntentSubstitution("invalid component")

        challenge = self.attested.challenge()
        observed = self.attested.authenticated_read(
            challenge=challenge,
            request_id=f"shared-ledger-read:{component_id}",
        )
        provider_id, generation = self._provider()
        if (observed.provider_id, observed.generation) != (provider_id, generation):
            raise ProviderMismatch("read provider mismatch")

        local = self.watermark(component_id)
        if observed.position < local:
            raise UnexplainedAdvance("external anchor rolled back below component watermark")
        if observed.position == local:
            return local

        q = self._con()
        try:
            rows = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,"
                "provider_id,provider_generation,predecessor_position,position,"
                "request_id,status,receipt_binding "
                "FROM shared_anchor_intents WHERE position>? AND position<=? ORDER BY position",
                (local, observed.position),
            ).fetchall()
        finally:
            q.close()

        if len(rows) != observed.position - local:
            raise IntentGap("missing ledger position")
        expected = local + 1
        for row in rows:
            entry = self._row_entry(row)
            if entry.position != expected or entry.predecessor_position != expected - 1:
                raise IntentGap("non-contiguous ledger history")
            if entry.status != "CONFIRMED":
                raise UnexplainedAdvance("ahead position is not confirmed")
            receipt = self._reauthenticate(entry)
            if receipt != entry.receipt_binding:
                raise IntentSubstitution("stored receipt differs from authenticated provider result")
            expected += 1

        q = self._con()
        try:
            with self._write_txn(q):
                current_rows = q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,"
                    "provider_id,provider_generation,predecessor_position,position,"
                    "request_id,status,receipt_binding "
                    "FROM shared_anchor_intents WHERE position>? AND position<=? ORDER BY position",
                    (local, observed.position),
                ).fetchall()
                if current_rows != rows:
                    raise IntentSubstitution("ledger changed after external verification")
                prior = q.execute(
                    "SELECT position FROM component_anchor_watermarks WHERE component_id=?",
                    (component_id,),
                ).fetchone()
                if prior is None:
                    with one_shot_permit(
                        q,
                        kind="watermark-insert",
                        identity=component_id,
                        old_value="",
                        new_value=str(observed.position),
                    ):
                        q.execute(
                            "INSERT INTO component_anchor_watermarks VALUES(?,?)",
                            (component_id, observed.position),
                        )
                elif prior[0] != local:
                    raise IntentConflict("component watermark changed during verification")
                else:
                    with one_shot_permit(
                        q,
                        kind="watermark-update",
                        identity=component_id,
                        old_value=str(local),
                        new_value=str(observed.position),
                    ):
                        changed = q.execute(
                            "UPDATE component_anchor_watermarks SET position=? "
                            "WHERE component_id=? AND position=?",
                            (observed.position, component_id, local),
                        ).rowcount
                    if changed != 1:
                        raise IntentConflict("component watermark lost CAS")
            return observed.position
        finally:
            q.close()
