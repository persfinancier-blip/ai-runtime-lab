from __future__ import annotations

import contextlib
import sqlite3

from experiments.asymmetric_provider_history.protocol import HistoricalVerificationError
from experiments.asymmetric_provider_history.supported import (
    SupportedAsymmetricHistoricalSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import (
    Intent,
    IntentConflict,
    IntentGap,
    IntentSubstitution,
    PendingIntent,
    ProviderMismatch,
    UnexplainedAdvance,
)


class WriterAuthorizationError(RuntimeError):
    pass


class _BrokerConnection(sqlite3.Connection):
    """Connection-local LAB-091 authorization state."""

    pass


class SupportedMutableAsymmetricSharedAnchorLedger(
    SupportedAsymmetricHistoricalSharedAnchorLedger
):
    """LAB-091 integration over the actual LAB-080/LAB-082 supported surface.

    The final supported object never exposes a raw writable connection. Every
    connection created by `_con()` has `lab091_writer_authorized()==0` by default.
    Only narrow audited SQL sections enter `_authorized_txn()`, which sets the
    predicate after `BEGIN IMMEDIATE` and clears it *before* commit/rollback.

    External provider calls therefore happen with no SQL writer authorization.
    This composes with LAB-087: the broker/process/filesystem boundary owns the
    only writable database handle, while LAB-091 constrains DML on that handle.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._install_guards()
        self.verify_durable()

    def _con(self):
        q = sqlite3.connect(
            self.path,
            timeout=5,
            isolation_level=None,
            factory=_BrokerConnection,
        )
        q.execute("PRAGMA busy_timeout=5000")
        q._lab091_authorized = False
        q.create_function(
            "lab091_writer_authorized",
            0,
            lambda q=q: 1 if q._lab091_authorized else 0,
        )
        return q

    @contextlib.contextmanager
    def _authorized_txn(self, q):
        if type(q) is not _BrokerConnection:
            raise TypeError("exact LAB-091 broker connection required")
        if q._lab091_authorized:
            raise WriterAuthorizationError("nested writer authorization")
        q.execute("BEGIN IMMEDIATE")
        q._lab091_authorized = True
        try:
            yield q
            q._lab091_authorized = False
            q.commit()
        except Exception:
            q._lab091_authorized = False
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q._lab091_authorized = False

    def _install_guards(self):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            for name in (
                "lab091_meta_no_insert",
                "lab091_meta_authorized_update",
                "lab091_meta_no_delete",
                "lab091_intent_authorized_insert",
                "lab091_intent_authorized_update",
                "lab091_intent_no_delete",
                "lab091_watermark_authorized_insert",
                "lab091_watermark_authorized_update",
                "lab091_watermark_no_delete",
                "lab091_receipt_authorized_insert",
                "lab091_receipt_no_update",
                "lab091_receipt_no_delete",
            ):
                q.execute(f"DROP TRIGGER IF EXISTS {name}")
            trigger_sql = (
                """CREATE TRIGGER lab091_meta_no_insert
                   BEFORE INSERT ON shared_anchor_meta
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 meta singleton already initialized');
                   END""",
                """CREATE TRIGGER lab091_meta_authorized_update
                   BEFORE UPDATE ON shared_anchor_meta
                   WHEN lab091_writer_authorized()!=1
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 meta update requires broker writer');
                   END""",
                """CREATE TRIGGER lab091_meta_no_delete
                   BEFORE DELETE ON shared_anchor_meta
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 meta cannot be deleted');
                   END""",
                """CREATE TRIGGER lab091_intent_authorized_insert
                   BEFORE INSERT ON shared_anchor_intents
                   WHEN lab091_writer_authorized()!=1
                     OR EXISTS(
                       SELECT 1 FROM shared_anchor_intents
                       WHERE intent_id=NEW.intent_id
                          OR request_id=NEW.request_id
                          OR position=NEW.position
                     )
                   BEGIN
                     SELECT RAISE(
                       ABORT,
                       'LAB-091 intent creation requires a fresh broker-authorized identity'
                     );
                   END""",
                """CREATE TRIGGER lab091_intent_authorized_update
                   BEFORE UPDATE ON shared_anchor_intents
                   WHEN lab091_writer_authorized()!=1
                     OR OLD.status!='PREPARED'
                     OR NEW.status!='CONFIRMED'
                     OR NEW.intent_id IS NOT OLD.intent_id
                     OR NEW.component_id IS NOT OLD.component_id
                     OR NEW.intent_type IS NOT OLD.intent_type
                     OR NEW.payload_digest IS NOT OLD.payload_digest
                     OR NEW.provider_id IS NOT OLD.provider_id
                     OR NEW.provider_generation IS NOT OLD.provider_generation
                     OR NEW.predecessor_position IS NOT OLD.predecessor_position
                     OR NEW.position IS NOT OLD.position
                     OR NEW.request_id IS NOT OLD.request_id
                     OR OLD.receipt_binding IS NOT NULL
                     OR NEW.receipt_binding IS NULL
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 invalid intent transition');
                   END""",
                """CREATE TRIGGER lab091_intent_no_delete
                   BEFORE DELETE ON shared_anchor_intents
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 intent history cannot be deleted');
                   END""",
                """CREATE TRIGGER lab091_watermark_authorized_insert
                   BEFORE INSERT ON component_anchor_watermarks
                   WHEN lab091_writer_authorized()!=1
                     OR EXISTS(
                       SELECT 1 FROM component_anchor_watermarks
                       WHERE component_id=NEW.component_id
                     )
                   BEGIN
                     SELECT RAISE(
                       ABORT,
                       'LAB-091 watermark creation requires a fresh broker-authorized component'
                     );
                   END""",
                """CREATE TRIGGER lab091_watermark_authorized_update
                   BEFORE UPDATE ON component_anchor_watermarks
                   WHEN lab091_writer_authorized()!=1
                     OR NEW.component_id IS NOT OLD.component_id
                     OR NEW.position<OLD.position
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 invalid watermark transition');
                   END""",
                """CREATE TRIGGER lab091_watermark_no_delete
                   BEFORE DELETE ON component_anchor_watermarks
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 watermark cannot be deleted');
                   END""",
                """CREATE TRIGGER lab091_receipt_authorized_insert
                   BEFORE INSERT ON asymmetric_provider_receipts
                   WHEN lab091_writer_authorized()!=1
                     OR EXISTS(
                       SELECT 1 FROM asymmetric_provider_receipts
                       WHERE request_id=NEW.request_id
                     )
                   BEGIN
                     SELECT RAISE(
                       ABORT,
                       'LAB-091 provider receipt creation requires a fresh broker-authorized request'
                     );
                   END""",
                """CREATE TRIGGER lab091_receipt_no_update
                   BEFORE UPDATE ON asymmetric_provider_receipts
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 provider receipt is immutable');
                   END""",
                """CREATE TRIGGER lab091_receipt_no_delete
                   BEFORE DELETE ON asymmetric_provider_receipts
                   BEGIN
                     SELECT RAISE(ABORT,'LAB-091 provider receipt cannot be deleted');
                   END""",
            )
            for statement in trigger_sql:
                q.execute(statement)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def reserve(self, intent: Intent):
        intent.validate()
        q = self._con()
        try:
            with self._authorized_txn(q):
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
                q.execute(
                    "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                    (
                        intent.intent_id,
                        intent.component_id,
                        intent.intent_type,
                        intent.payload_digest,
                        durable.provider_id,
                        durable.generation,
                        predecessor,
                        position,
                        request_id,
                    ),
                )
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
            with self._authorized_txn(q):
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
            with self._authorized_txn(q):
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
            with self._authorized_txn(q):
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
                    q.execute(
                        "INSERT INTO component_anchor_watermarks VALUES(?,?)",
                        (component_id, observed.position),
                    )
                elif prior[0] != local:
                    raise IntentConflict("component watermark changed during verification")
                else:
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
