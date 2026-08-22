from __future__ import annotations

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.asymmetric_provider_history.protocol import (
    AsymmetricProviderHistory,
    CurrentGenerationRequired,
    GenerationSigner,
    HistoricalVerificationError,
    HistoryRollback,
    InvalidTransition,
    PublicGeneration,
    SignedReceipt,
    TransitionProof,
    verify_signature,
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


class PendingRotationBlocked(HistoricalVerificationError):
    pass


class IntegratedAsymmetricProviderHistory(AsymmetricProviderHistory):
    """LAB-082 history helpers that operate inside LAB-080's SQL transaction."""

    def _current_locked(self, q):
        row = q.execute(
            "SELECT generation_id,generation FROM asymmetric_provider_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing asymmetric provider head")
        generation_id, generation = row
        public = self._public_locked(q, generation_id)
        if public.generation != generation:
            raise HistoryRollback("asymmetric head generation mismatch")
        return public

    def _verify_durable_locked(self, q):
        rows = q.execute(
            "SELECT generation_id,provider_id,generation,public_key_hex "
            "FROM asymmetric_provider_generations ORDER BY generation"
        ).fetchall()
        if not rows:
            raise HistoricalVerificationError("missing asymmetric provider history")

        publics = []
        for generation_id, provider_id, generation, public_key_hex in rows:
            public = PublicGeneration(provider_id, generation, public_key_hex)
            public.validate()
            if public.generation_id != generation_id:
                raise HistoricalVerificationError("public generation identity mismatch")
            publics.append(public)

        if publics[0].generation_id != self.bootstrap.generation_id:
            raise HistoryRollback("asymmetric bootstrap generation changed")

        for old, new in zip(publics, publics[1:]):
            row = q.execute(
                "SELECT old_generation_id,provider_id,old_signature,new_signature "
                "FROM asymmetric_provider_transitions WHERE new_generation_id=?",
                (new.generation_id,),
            ).fetchone()
            if row is None:
                raise HistoricalVerificationError("missing asymmetric transition proof")
            proof = TransitionProof(row[1], row[0], new.generation_id, row[2], row[3])
            try:
                proof.validate()
            except InvalidTransition as exc:
                raise HistoricalVerificationError("invalid persisted asymmetric transition") from exc
            if (
                proof.provider_id != old.provider_id
                or proof.old_generation_id != old.generation_id
                or proof.new_generation_id != new.generation_id
                or new.provider_id != old.provider_id
                or new.generation != old.generation + 1
            ):
                raise HistoricalVerificationError("asymmetric transition continuity mismatch")
            verify_signature(old, proof.unsigned, proof.old_signature)
            verify_signature(new, proof.unsigned, proof.new_signature)

        current = self._current_locked(q)
        if current.generation_id != publics[-1].generation_id:
            raise HistoryRollback("asymmetric head rollback/substitution")

        for row in q.execute(
            "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts"
        ).fetchall():
            receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
            if row[7] != receipt.stable_binding:
                raise HistoricalVerificationError("asymmetric receipt stable binding mismatch")
        return current

    def _load_receipt_locked(self, q, request_id):
        row = q.execute(
            "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts WHERE request_id=?",
            (request_id,),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing asymmetric historical receipt")
        receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
        if row[7] != receipt.stable_binding:
            raise HistoricalVerificationError("asymmetric historical receipt binding mismatch")
        return receipt

    def _maybe_load_receipt_locked(self, q, request_id):
        row = q.execute(
            "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts WHERE request_id=?",
            (request_id,),
        ).fetchone()
        if row is None:
            return None
        receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
        if row[7] != receipt.stable_binding:
            raise HistoricalVerificationError("asymmetric historical receipt binding mismatch")
        return receipt

    def _store_receipt_locked(self, q, receipt: SignedReceipt):
        self._verify_receipt_locked(q, receipt)
        expected = (
            receipt.provider_id,
            receipt.generation,
            receipt.position,
            receipt.kind,
            receipt.challenge,
            receipt.signature,
            receipt.stable_binding,
        )
        existing = q.execute(
            "SELECT provider_id,generation,position,kind,challenge,signature,stable_binding "
            "FROM asymmetric_provider_receipts WHERE request_id=?",
            (receipt.request_id,),
        ).fetchone()
        if existing is not None and existing != expected:
            raise HistoricalVerificationError("asymmetric receipt substitution")
        if existing is None:
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                (
                    receipt.request_id,
                    receipt.provider_id,
                    receipt.generation,
                    receipt.position,
                    receipt.kind,
                    receipt.challenge,
                    receipt.signature,
                    receipt.stable_binding,
                ),
            )
        return receipt.stable_binding

    def _rotate_locked(self, q, new: PublicGeneration, proof: TransitionProof):
        new.validate()
        proof.validate()
        old = self._current_locked(q)
        if (
            proof.provider_id != old.provider_id
            or proof.old_generation_id != old.generation_id
            or proof.new_generation_id != new.generation_id
        ):
            raise InvalidTransition("asymmetric transition identity mismatch")
        if new.provider_id != old.provider_id or new.generation != old.generation + 1:
            raise InvalidTransition("invalid asymmetric provider successor")
        verify_signature(old, proof.unsigned, proof.old_signature)
        verify_signature(new, proof.unsigned, proof.new_signature)
        q.execute(
            "INSERT INTO asymmetric_provider_generations VALUES(?,?,?,?)",
            (new.generation_id, new.provider_id, new.generation, new.public_key_hex),
        )
        q.execute(
            "INSERT INTO asymmetric_provider_transitions VALUES(?,?,?,?,?)",
            (
                new.generation_id,
                old.generation_id,
                old.provider_id,
                proof.old_signature,
                proof.new_signature,
            ),
        )
        changed = q.execute(
            "UPDATE asymmetric_provider_head SET generation_id=?,generation=? "
            "WHERE singleton=1 AND generation_id=? AND generation=?",
            (new.generation_id, new.generation, old.generation_id, old.generation),
        ).rowcount
        if changed != 1:
            raise HistoryRollback("asymmetric provider head changed during rotation")
        return new


class AsymmetricHistoricalSharedAnchorLedger(SupportedSharedAnchorLedger):
    """Supported LAB-082 integration over the LAB-080 serialization boundary.

    LAB-036 HMAC observations are authenticated only at execution time.  Once an
    effect is observed, the current runtime Ed25519 signer signs the exact provider
    receipt fields and only that public-verifiable receipt is kept for historical
    verification.  Old private signing capability is never required after rotation.
    """

    def __init__(
        self,
        path,
        attested: AttestedCatchup,
        bootstrap: PublicGeneration,
        signer: GenerationSigner,
    ):
        if type(attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        if type(signer) is not GenerationSigner:
            raise TypeError("exact LAB-082 GenerationSigner required")
        self.provider_history = IntegratedAsymmetricProviderHistory(path, bootstrap)
        self.signer = signer
        super().__init__(path, attested)
        self._require_runtime_matches_durable_head()

    def _require_runtime_matches_durable_head(self):
        durable = self.provider_history.current()
        expected = self.attested.verifier.expected
        if (expected.provider_id, expected.generation) != (
            durable.provider_id,
            durable.generation,
        ):
            raise CurrentGenerationRequired("runtime LAB-036 provider is not durable current head")
        if self.signer.public.generation_id != durable.generation_id:
            raise CurrentGenerationRequired("runtime Ed25519 signer is not durable current head")
        return durable

    def reserve(self, intent: Intent):
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
                "UPDATE shared_anchor_meta SET reserved_position=? "
                "WHERE singleton=1 AND reserved_position=?",
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

    def rotate_provider(
        self,
        new_signer: GenerationSigner,
        proof: TransitionProof,
        new_attested: AttestedCatchup,
    ):
        if type(new_signer) is not GenerationSigner:
            raise TypeError("exact LAB-082 GenerationSigner required")
        if type(new_attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        new = new_signer.public
        expected = new_attested.verifier.expected
        if (expected.provider_id, expected.generation) != (new.provider_id, new.generation):
            raise InvalidTransition("new LAB-036 provider does not match Ed25519 generation")

        challenge = new_attested.challenge()
        observed = new_attested.authenticated_read(
            challenge=challenge,
            request_id=f"asymmetric-provider-rotation-read:{new.generation}",
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
        self.signer = new_signer
        self._require_runtime_matches_durable_head()
        return new

    def _runtime_matches_entry(self, entry: LedgerEntry):
        durable = self._require_runtime_matches_durable_head()
        if (entry.provider_id, entry.provider_generation) != (
            durable.provider_id,
            durable.generation,
        ):
            raise CurrentGenerationRequired("historical generation cannot execute a new effect")
        return durable

    def _signed_receipt_from_observation(self, observed):
        current = self._require_runtime_matches_durable_head()
        if (observed.provider_id, observed.generation) != (
            current.provider_id,
            current.generation,
        ):
            raise ProviderMismatch("LAB-036 observation does not match current asymmetric generation")
        unsigned = {
            "kind": observed.kind,
            "provider_id": observed.provider_id,
            "generation": observed.generation,
            "position": observed.position,
            "request_id": observed.request_id,
            "challenge": observed.challenge,
        }
        return SignedReceipt(
            observed.provider_id,
            observed.generation,
            observed.position,
            observed.request_id,
            observed.kind,
            observed.challenge,
            self.signer.sign(unsigned),
        )

    @staticmethod
    def _receipt_binds_entry(receipt: SignedReceipt, entry: LedgerEntry):
        if (
            receipt.provider_id != entry.provider_id
            or receipt.generation != entry.provider_generation
            or receipt.position != entry.position
            or receipt.request_id != entry.request_id
        ):
            raise IntentSubstitution("asymmetric receipt does not bind exact ledger entry")
        return receipt.stable_binding

    def _reauthenticate(self, entry: LedgerEntry):
        q = self._con()
        try:
            q.execute("BEGIN")
            receipt = self.provider_history._maybe_load_receipt_locked(q, entry.request_id)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        if receipt is not None:
            return self._receipt_binds_entry(receipt, entry)
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

        receipt = self._signed_receipt_from_observation(verified)
        self._receipt_binds_entry(receipt, entry)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            current = self._row_entry(
                q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                    "predecessor_position,position,request_id,status,receipt_binding "
                    "FROM shared_anchor_intents WHERE intent_id=?",
                    (entry.intent_id,),
                ).fetchone()
            )
            if current != entry:
                raise IntentSubstitution("ledger entry changed before asymmetric receipt persistence")
            binding = self.provider_history._store_receipt_locked(q, receipt)
            q.commit()
            return binding
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

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
            for expected_position, row in enumerate(rows, 1):
                entry = self._row_entry(row)
                if (
                    entry.position != expected_position
                    or entry.predecessor_position != expected_position - 1
                ):
                    raise IntentSubstitution("durable ledger is not contiguous")
                if entry.status == "PREPARED":
                    prepared += 1
                    if entry.position != reserved:
                        raise IntentSubstitution("PREPARED intent is not ledger tail")
                    if (entry.provider_id, entry.provider_generation) != (
                        head.provider_id,
                        head.generation,
                    ):
                        raise ProviderMismatch("PREPARED intent belongs to historical generation")
                    if self.provider_history._maybe_load_receipt_locked(q, entry.request_id) is not None:
                        receipt = self.provider_history._load_receipt_locked(q, entry.request_id)
                        self._receipt_binds_entry(receipt, entry)
                else:
                    receipt = self.provider_history._load_receipt_locked(q, entry.request_id)
                    if receipt.stable_binding != entry.receipt_binding:
                        raise IntentSubstitution("confirmed ledger/asymmetric receipt mismatch")
                    self._receipt_binds_entry(receipt, entry)
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
                        "SELECT status FROM shared_anchor_intents WHERE position=?",
                        (position,),
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
