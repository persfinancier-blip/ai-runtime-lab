from __future__ import annotations

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.provider_generation_history.integration import HistoricalSharedAnchorLedger
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
)
from experiments.shared_anchor_intent_ledger.protocol import IntentSubstitution, LedgerEntry, UnexplainedAdvance


class SupportedHistoricalSharedAnchorLedger(HistoricalSharedAnchorLedger):
    """Audited LAB-081 surface.

    The first exact signed provider observation for a confirmed request is immutable
    historical evidence. Later verification never replaces it with a new challenge;
    current anchor freshness is established separately by LAB-080 authenticated reads.
    """

    def __init__(self, path, attested: AttestedCatchup, bootstrap: GenerationDescriptor):
        if type(attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        super().__init__(path, attested, bootstrap)

    def _stored_receipt(self, entry: LedgerEntry):
        q = self._con()
        try:
            q.execute("BEGIN")
            row = q.execute(
                "SELECT 1 FROM historical_provider_receipts WHERE request_id=?",
                (entry.request_id,),
            ).fetchone()
            if row is None:
                q.commit()
                return None
            receipt = self.provider_history._load_receipt_locked(q, entry.request_id)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        if (
            receipt.provider_id != entry.provider_id
            or receipt.generation != entry.provider_generation
            or receipt.position != entry.position
            or receipt.request_id != entry.request_id
        ):
            raise IntentSubstitution("historical receipt does not bind exact ledger entry")
        return receipt

    def _reauthenticate(self, entry: LedgerEntry):
        stored = self._stored_receipt(entry)
        if stored is not None:
            return stored.stable_binding

        durable = self.provider_history.current()
        if (entry.provider_id, entry.provider_generation) != (
            durable.provider_id,
            durable.generation,
        ):
            raise HistoricalVerificationError("historical ledger entry has no signed receipt evidence")

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
        receipt = HistoricalReceipt(
            verified.provider_id,
            verified.generation,
            verified.position,
            verified.request_id,
            verified.kind,
            verified.challenge,
            verified.mac,
        )
        binding = self.provider_history.store_receipt(receipt)
        if binding != self._stable_receipt(verified):
            raise IntentSubstitution("historical receipt identity mismatch")
        return binding
