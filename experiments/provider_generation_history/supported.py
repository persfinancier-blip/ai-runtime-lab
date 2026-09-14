from __future__ import annotations

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.database_binding import CanonicalDatabaseBinding
from experiments.provider_generation_history.integration import (
    HistoricalSharedAnchorLedger,
    IntegratedProviderHistory,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
    PendingRotationBlocked,
)
from experiments.shared_anchor_intent_ledger.protocol import IntentSubstitution, LedgerEntry, UnexplainedAdvance
from experiments.shared_anchor_intent_ledger.supported import SupportedSharedAnchorLedger


class ProviderHistoryInspectionView:
    """Read-only public inspection surface for a bound provider-history strategy.

    The live coordinator strategy remains private to the supported ledger. This view
    intentionally omits connection access, receipt storage, rotation, and all locked
    helpers so delegating a ledger does not also delegate coordinator mutation power.
    """

    __slots__ = ("__history",)

    def __init__(self, history: "CoordinatorOnlyProviderHistory"):
        object.__setattr__(self, "_ProviderHistoryInspectionView__history", history)

    def __setattr__(self, name, value):
        raise AttributeError("provider history inspection view is immutable")

    def current(self):
        return self.__history.current()

    def verify_durable(self):
        return self.__history.verify_durable()

    def load_receipt(self, request_id):
        return self.__history.load_receipt(request_id)

    def verify_receipt(self, receipt: HistoricalReceipt):
        return self.__history.verify_receipt(receipt)

    def require_current(self, provider_id, generation):
        return self.__history.require_current(provider_id, generation)

    @staticmethod
    def make_transition(old: GenerationDescriptor, new: GenerationDescriptor):
        return IntegratedProviderHistory.make_transition(old, new)


class CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory):
    """Provider history whose authority-changing API is only the shared-ledger coordinator."""

    def rotate(self, *args, **kwargs):
        raise PendingRotationBlocked(
            "integrated provider rotation must use SupportedHistoricalSharedAnchorLedger.rotate_provider()"
        )


class SupportedHistoricalSharedAnchorLedger(HistoricalSharedAnchorLedger):
    """Audited LAB-081 surface.

    The first exact signed provider observation for a confirmed request is immutable
    historical evidence. Later verification never replaces it with a new challenge;
    current anchor freshness is established separately by LAB-080 authenticated reads.

    Provider-generation mutation is coordinator-only so a caller cannot bypass the
    shared LAB-080 PREPARED check by invoking the standalone history API directly.

    The provider-history strategy is construction-bound private state. Existing callers
    may inspect ``provider_history`` for compatibility, but receive only a read-only
    least-capability view with no connection, locked-helper, receipt-mutation, or
    rotation authority.
    """

    _PROVIDER_HISTORY_SLOT = "_provider_history"

    def __setattr__(self, name, value):
        if name in {"provider_history", self._PROVIDER_HISTORY_SLOT} and hasattr(
            self, self._PROVIDER_HISTORY_SLOT
        ):
            raise AttributeError("provider history strategy is construction-bound")
        super().__setattr__(name, value)

    @property
    def provider_history(self) -> ProviderHistoryInspectionView:
        try:
            history = object.__getattribute__(self, self._PROVIDER_HISTORY_SLOT)
        except AttributeError as exc:
            raise AttributeError("provider history strategy is not initialized") from exc
        return ProviderHistoryInspectionView(history)

    @provider_history.setter
    def provider_history(self, value: CoordinatorOnlyProviderHistory) -> None:
        if hasattr(self, self._PROVIDER_HISTORY_SLOT):
            raise AttributeError("provider history strategy is construction-bound")
        if type(value) is not CoordinatorOnlyProviderHistory:
            raise TypeError("exact CoordinatorOnlyProviderHistory required")
        object.__setattr__(self, self._PROVIDER_HISTORY_SLOT, value)

    def __init__(self, path, attested: AttestedCatchup, bootstrap: GenerationDescriptor):
        if type(attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        self.provider_history = CoordinatorOnlyProviderHistory(path, bootstrap)
        SupportedSharedAnchorLedger.__init__(self, path, attested)
        self._require_runtime_matches_durable_head()

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
            receipt = self._history()._load_receipt_locked(q, entry.request_id)
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

        durable = self._history().current()
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
        binding = self._history().store_receipt(receipt)
        if binding != self._stable_receipt(verified):
            raise IntentSubstitution("historical receipt identity mismatch")
        return binding
