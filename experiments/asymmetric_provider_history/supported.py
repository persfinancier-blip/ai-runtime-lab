from __future__ import annotations

from experiments.asymmetric_provider_history.integration import (
    AsymmetricHistoricalSharedAnchorLedger,
)
from experiments.asymmetric_provider_history.protocol import HistoricalVerificationError
from experiments.shared_anchor_intent_ledger.protocol import (
    IntentSubstitution,
    UnexplainedAdvance,
)


class SupportedAsymmetricHistoricalSharedAnchorLedger(
    AsymmetricHistoricalSharedAnchorLedger
):
    """Audited LAB-082 surface.

    The first valid Ed25519 receipt durably stored for a request becomes the
    canonical historical receipt. Concurrent workers that independently obtain
    equivalent provider reconciliation evidence converge on that receipt instead
    of treating a different challenge/signature as content substitution.
    """

    def _reauthenticate(self, entry):
        q = self._con()
        try:
            q.execute("BEGIN")
            existing = self.provider_history._maybe_load_receipt_locked(
                q, entry.request_id
            )
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
            raise HistoricalVerificationError(
                "confirmed ledger row is missing asymmetric receipt"
            )

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
            raise UnexplainedAdvance(
                "provider result does not bind ledger position/request"
            )

        candidate = self._signed_receipt_from_observation(verified)
        self._receipt_binds_entry(candidate, entry)

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
                raise IntentSubstitution(
                    "ledger entry changed before asymmetric receipt persistence"
                )

            # Another worker may have reconciled the same request with a different
            # fresh challenge while we were outside the SQL lock. That is not a
            # request substitution. Re-verify and reuse the first durable receipt.
            winner = self.provider_history._maybe_load_receipt_locked(
                q, entry.request_id
            )
            if winner is not None:
                binding = self._receipt_binds_entry(winner, entry)
            else:
                binding = self.provider_history._store_receipt_locked(q, candidate)
            q.commit()
            return binding
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
