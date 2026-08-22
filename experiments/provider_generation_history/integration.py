from __future__ import annotations

import hmac

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    DurableProviderHistory,
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
    HistoryRollback,
    InvalidTransition,
    PendingRotationBlocked,
    TransitionProof,
    mac,
)
from experiments.shared_anchor_intent_ledger.protocol import (
    Intent,
    IntentConflict,
    IntentSubstitution,
    LedgerEntry,
    PendingIntent,
    ProviderMismatch,
    UnexplainedAdvance,
)
from experiments.shared_anchor_intent_ledger.supported import SupportedSharedAnchorLedger


class IntegratedProviderHistory(DurableProviderHistory):
    """LAB-081 provider history with transaction-internal verification/rotation helpers."""

    def _current_locked(self, q):
        row = q.execute(
            "SELECT generation_id,generation FROM provider_generation_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing provider generation head")
        generation_id, generation = row
        desc = self._descriptor_locked(q, generation_id)
        if desc.generation != generation:
            raise HistoryRollback("head generation mismatch")
        return desc

    def _verify_durable_locked(self, q):
        rows = q.execute(
            "SELECT generation_id,provider_id,generation,verification_key_hex "
            "FROM provider_generations ORDER BY generation"
        ).fetchall()
        if not rows:
            raise HistoricalVerificationError("missing provider history")
        descriptors = []
        for generation_id, provider_id, generation, key_hex in rows:
            desc = GenerationDescriptor(provider_id, generation, key_hex)
            if desc.generation_id != generation_id:
                raise HistoricalVerificationError("generation identity mismatch")
            descriptors.append(desc)
        if descriptors[0].generation_id != self.bootstrap.generation_id:
            raise HistoryRollback("bootstrap generation changed")
        for old, new in zip(descriptors, descriptors[1:]):
            row = q.execute(
                "SELECT old_generation_id,provider_id,old_mac,new_mac "
                "FROM provider_generation_transitions WHERE new_generation_id=?",
                (new.generation_id,),
            ).fetchone()
            if row is None:
                raise HistoricalVerificationError("missing transition proof")
            proof = TransitionProof(row[1], row[0], new.generation_id, row[2], row[3])
            if proof != self.make_transition(old, new):
                raise HistoricalVerificationError("corrupt transition proof")
        current = self._current_locked(q)
        if current.generation_id != descriptors[-1].generation_id:
            raise HistoryRollback("provider head rollback/substitution")
        return current

    def _verify_receipt_locked(self, q, receipt: HistoricalReceipt):
        row = q.execute(
            "SELECT generation_id FROM provider_generations WHERE provider_id=? AND generation=?",
            (receipt.provider_id, receipt.generation),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("unknown historical generation")
        desc = self._descriptor_locked(q, row[0])
        expected = mac(desc.key, receipt.unsigned)
        if not hmac.compare_digest(expected, receipt.signature):
            raise HistoricalVerificationError("historical receipt signature mismatch")
        return receipt

    def _load_receipt_locked(self, q, request_id):
        row = q.execute(
            "SELECT provider_id,generation,position,request_id,kind,challenge,signature "
            "FROM historical_provider_receipts WHERE request_id=?",
            (request_id,),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing historical receipt")
        return self._verify_receipt_locked(q, HistoricalReceipt(*row))

    def _rotate_locked(self, q, new: GenerationDescriptor, proof: TransitionProof):
        new.validate()
        old = self._current_locked(q)
        expected = self.make_transition(old, new)
        if proof != expected:
            raise InvalidTransition("transition proof mismatch")
        if new.provider_id != old.provider_id or new.generation != old.generation + 1:
            raise InvalidTransition("invalid successor")
        q.execute(
            "INSERT INTO provider_generations VALUES(?,?,?,?)",
            (new.generation_id, new.provider_id, new.generation, new.verification_key_hex),
        )
        q.execute(
            "INSERT INTO provider_generation_transitions VALUES(?,?,?,?,?)",
            (new.generation_id, old.generation_id, new.provider_id, proof.old_mac, proof.new_mac),
        )
        changed = q.execute(
            "UPDATE provider_generation_head SET generation_id=?,generation=? "
            "WHERE singleton=1 AND generation_id=? AND generation=?",
            (new.generation_id, new.generation, old.generation_id, old.generation),
        ).rowcount
        if changed != 1:
            raise HistoryRollback("generation head changed during rotation")
        return new


class HistoricalSharedAnchorLedger(SupportedSharedAnchorLedger):
    """Supported LAB-081 integration over the exact LAB-080 SQLite ledger.

    The shared-anchor DB is the single serialization boundary for reservation and
    provider-generation rotation. Historical provider keys are verification-only;
    all new external effects require the runtime AttestedCatchup identity to equal
    the durable provider-generation head.
    """

    def __init__(self, path, attested: AttestedCatchup, bootstrap: GenerationDescriptor):
        if type(attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        self.provider_history = IntegratedProviderHistory(path, bootstrap)
        super().__init__(path, attested)
        self._require_runtime_matches_durable_head()

    @staticmethod
    def _descriptor_from_attested(attested: AttestedCatchup):
        expected = attested.verifier.expected
        key = attested.verifier.keyring.get((expected.provider_id, expected.generation))
        if key is None:
            raise HistoricalVerificationError("runtime verifier lacks current provider key")
        return GenerationDescriptor(expected.provider_id, expected.generation, key.hex())

    def _require_runtime_matches_durable_head(self):
        runtime = self._descriptor_from_attested(self.attested)
        durable = self.provider_history.current()
        if runtime.generation_id != durable.generation_id:
            raise CurrentGenerationRequired("runtime provider generation is not durable current head")
        return durable

    def reserve(self, intent: Intent):
        """Reserve using provider identity read under the same write lock as rotation."""
        intent.validate()
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                "predecessor_position,position,request_id,status,receipt_binding "
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
                q.commit()
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
                "UPDATE shared_anchor_meta SET reserved_position=? WHERE singleton=1 AND reserved_position=?",
                (position, predecessor),
            ).rowcount
            if changed != 1:
                raise IntentConflict("shared anchor tail changed during reservation")
            q.commit()
            return self.entry(intent.intent_id)
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_provider(self, new: GenerationDescriptor, proof: TransitionProof, new_attested: AttestedCatchup):
        if type(new_attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        runtime_new = self._descriptor_from_attested(new_attested)
        if runtime_new.generation_id != new.generation_id:
            raise InvalidTransition("new runtime verifier does not match generation descriptor")

        challenge = new_attested.challenge()
        observed = new_attested.authenticated_read(
            challenge=challenge, request_id=f"provider-rotation-read:{new.generation}"
        )

        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            pending = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
            ).fetchone()[0]
            if pending:
                raise PendingRotationBlocked("unresolved PREPARED anchor intent")
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            if observed.position != reserved:
                raise InvalidTransition("new provider position does not match durable ledger tail")
            self.provider_history._rotate_locked(q, new, proof)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        self.attested = new_attested
        self._require_runtime_matches_durable_head()
        return new

    def _runtime_matches_entry(self, entry: LedgerEntry):
        durable = self.provider_history.current()
        runtime = self._descriptor_from_attested(self.attested)
        if runtime.generation_id != durable.generation_id:
            raise CurrentGenerationRequired("runtime provider is stale relative to durable history")
        if (entry.provider_id, entry.provider_generation) != (
            durable.provider_id,
            durable.generation,
        ):
            raise CurrentGenerationRequired("historical generation cannot execute a new effect")
        return durable

    @staticmethod
    def _historical_from_observation(obs):
        return HistoricalReceipt(
            obs.provider_id,
            obs.generation,
            obs.position,
            obs.request_id,
            obs.kind,
            obs.challenge,
            obs.mac,
        )

    def _reauthenticate(self, entry: LedgerEntry):
        durable = self.provider_history.current()
        if (entry.provider_id, entry.provider_generation) != (
            durable.provider_id,
            durable.generation,
        ):
            receipt = self.provider_history.load_receipt(entry.request_id)
            if (
                receipt.provider_id != entry.provider_id
                or receipt.generation != entry.provider_generation
                or receipt.position != entry.position
                or receipt.request_id != entry.request_id
            ):
                raise IntentSubstitution("historical receipt does not bind exact ledger entry")
            return receipt.stable_binding

        self._runtime_matches_entry(entry)
        challenge = self.attested.challenge()
        obs = self.attested.provider.reconcile_increment(
            challenge=challenge, request_id=entry.request_id
        )
        if obs is None:
            raise UnexplainedAdvance("provider has no result for ledger request")
        verified = self.attested.verifier.verify(
            obs, expected_challenge=challenge, allowed_kinds={"RECONCILE"}
        )
        if verified.position != entry.position or verified.request_id != entry.request_id:
            raise UnexplainedAdvance("provider result does not bind ledger position/request")
        receipt = self._historical_from_observation(verified)
        binding = self.provider_history.store_receipt(receipt)
        if binding != self._stable_receipt(verified):
            raise IntentSubstitution("historical receipt identity mismatch")
        return binding

    def execute(self, intent: Intent, *, timeout_after_commit=False):
        entry = self.reserve(intent)
        if entry.status == "PREPARED":
            self._runtime_matches_entry(entry)
        return super().execute(intent, timeout_after_commit=timeout_after_commit)

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            head = self.provider_history._verify_durable_locked(q)
            meta = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchall()
            if len(meta) != 1 or type(meta[0][0]) is not int or meta[0][0] < 0:
                raise IntentSubstitution("invalid reserved_position metadata")
            reserved = meta[0][0]
            rows = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                "predecessor_position,position,request_id,status,receipt_binding "
                "FROM shared_anchor_intents ORDER BY position"
            ).fetchall()
            if len(rows) != reserved:
                raise IntentSubstitution("reserved_position does not match ledger tail")

            prepared = 0
            for expected, row in enumerate(rows, 1):
                entry = self._row_entry(row)
                if entry.position != expected or entry.predecessor_position != expected - 1:
                    raise IntentSubstitution("durable ledger is not contiguous")
                if entry.status == "PREPARED":
                    prepared += 1
                    if entry.position != reserved:
                        raise IntentSubstitution("PREPARED intent is not the ledger tail")
                    if (entry.provider_id, entry.provider_generation) != (
                        head.provider_id,
                        head.generation,
                    ):
                        raise ProviderMismatch("PREPARED intent belongs to historical provider generation")
                else:
                    receipt = self.provider_history._load_receipt_locked(q, entry.request_id)
                    if receipt.stable_binding != entry.receipt_binding:
                        raise IntentSubstitution("confirmed ledger receipt/history mismatch")
                    if (
                        receipt.provider_id != entry.provider_id
                        or receipt.generation != entry.provider_generation
                        or receipt.position != entry.position
                    ):
                        raise IntentSubstitution("confirmed historical receipt does not bind ledger row")
            if prepared > 1:
                raise IntentSubstitution("multiple unresolved durable intents")

            for component_id, position in q.execute(
                "SELECT component_id,position FROM component_anchor_watermarks"
            ).fetchall():
                if not isinstance(component_id, str) or not component_id:
                    raise IntentSubstitution("invalid durable component watermark identity")
                if type(position) is not int or position < 0 or position > reserved:
                    raise IntentSubstitution("invalid durable component watermark")
                if position:
                    row = q.execute(
                        "SELECT status FROM shared_anchor_intents WHERE position=?", (position,)
                    ).fetchone()
                    if row is None or row[0] != "CONFIRMED":
                        raise IntentSubstitution("watermark does not end on confirmed history")
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
