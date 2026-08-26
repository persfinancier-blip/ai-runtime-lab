from __future__ import annotations

from experiments.shared_anchor_intent_ledger.protocol import (
    Intent,
    IntentSubstitution,
    PendingIntent,
)

from .operation_permit import one_shot_permit
from .operation_scoped_integration import (
    SupportedOperationScopedAsymmetricSharedAnchorLedger,
)


class SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger(
    SupportedOperationScopedAsymmetricSharedAnchorLedger
):
    """LAB-091 operation-scoped writer with identical-worker confirmation convergence.

    Two workers may legitimately race on the same exact request. If one worker
    already committed PREPARED->CONFIRMED with the same authenticated receipt,
    the loser must converge on that durable winner rather than treating the
    idempotent outcome as a substitution.
    """

    def _commit_confirmation(self, intent_id, entry, receipt):
        q = self._con()
        try:
            with self._write_txn(q):
                raw = q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,"
                    "provider_id,provider_generation,predecessor_position,position,"
                    "request_id,status,receipt_binding "
                    "FROM shared_anchor_intents WHERE intent_id=?",
                    (intent_id,),
                ).fetchone()
                if raw is None:
                    raise IntentSubstitution("ledger entry disappeared before confirmation")
                current = self._row_entry(raw)

                if current.status == "CONFIRMED":
                    if not self._same_request(current, entry):
                        raise IntentSubstitution(
                            "confirmed winner does not match the original request"
                        )
                    if current.receipt_binding != receipt:
                        raise IntentSubstitution(
                            "confirmed winner receipt binding mismatch"
                        )
                    return current

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
                        "UPDATE shared_anchor_intents "
                        "SET status='CONFIRMED',receipt_binding=? "
                        "WHERE intent_id=? AND status='PREPARED' "
                        "AND receipt_binding IS NULL",
                        (receipt, intent_id),
                    ).rowcount
                if changed != 1:
                    raise IntentSubstitution("ledger confirmation lost CAS")
            return self.entry(intent_id)
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

        return self._commit_confirmation(intent.intent_id, entry, receipt)
