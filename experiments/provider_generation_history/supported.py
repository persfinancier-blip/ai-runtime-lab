from __future__ import annotations

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.database_binding import CanonicalDatabaseBinding
from experiments.provider_generation_history.activation import FencedActivationProvider
from experiments.provider_generation_history.activation_coordinator import ActivationCoordinatorMixin
from experiments.provider_generation_history.activation_transition import ActivationTransitionMixin
from experiments.provider_generation_history.integration import (
    HistoricalSharedAnchorLedger,
    IntegratedProviderHistory,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
    InvalidTransition,
    PendingRotationBlocked,
)
from experiments.shared_anchor_intent_ledger.protocol import IntentSubstitution, LedgerEntry, UnexplainedAdvance
from experiments.shared_anchor_intent_ledger.supported import SupportedSharedAnchorLedger


class ProviderHistoryInspectionView:
    """Read-only public inspection surface for a bound provider-history strategy."""

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


class SupportedHistoricalSharedAnchorLedger(
    ActivationTransitionMixin,
    ActivationCoordinatorMixin,
    HistoricalSharedAnchorLedger,
):
    """Audited LAB-081 surface with construction-bound history and LAB-090 fencing."""

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

    def rotate_provider(self, new: GenerationDescriptor, proof, new_attested: AttestedCatchup):
        """Rotate only through provider-owned exact-ticket fencing and durable acknowledgement."""
        if type(new_attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        runtime_new = self._descriptor_from_attested(new_attested)
        if runtime_new.generation_id != new.generation_id:
            raise InvalidTransition("new runtime verifier does not match generation descriptor")
        provider = new_attested.provider
        if not isinstance(provider, FencedActivationProvider):
            raise TypeError("LAB-090 rotation requires FencedActivationProvider")

        existing = self._activation_row(generation_id=new.generation_id)
        if existing is not None:
            durable = self._history().current()
            if new.generation_id != durable.generation_id:
                raise InvalidTransition("activation retry is not durable current generation")
            ticket = self._ticket_from_activation_row(existing)
            if existing[6] == "SQL_COMMITTED":
                self._commit_or_reconcile_activation(provider, ticket)
            elif existing[6] == "COMMITTED":
                self._release_committed_activation(provider, ticket)
            else:
                raise HistoricalVerificationError("invalid durable activation status")
            self.attested = new_attested
            self._require_runtime_matches_durable_head()
            return new

        ticket = self._preack_activation_transition(provider, new, proof)
        self._commit_or_reconcile_activation(provider, ticket)
        self.attested = new_attested
        self._require_runtime_matches_durable_head()
        return new

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

    def _guard_receipt_persistence_locked(self, q):
        return None

    def _store_receipt(self, receipt: HistoricalReceipt):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._guard_receipt_persistence_locked(q)
            self._history()._verify_receipt_locked(q, receipt)
            existing = q.execute(
                "SELECT provider_id,generation,position,kind,challenge,signature,stable_binding "
                "FROM historical_provider_receipts WHERE request_id=?",
                (receipt.request_id,),
            ).fetchone()
            expected = (
                receipt.provider_id,
                receipt.generation,
                receipt.position,
                receipt.kind,
                receipt.challenge,
                receipt.signature,
                receipt.stable_binding,
            )
            if existing is not None and existing != expected:
                raise HistoricalVerificationError("request receipt substitution")
            if existing is None:
                q.execute(
                    "INSERT INTO historical_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
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
            q.commit()
            return receipt.stable_binding
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

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
        binding = self._store_receipt(receipt)
        if binding != self._stable_receipt(verified):
            raise IntentSubstitution("historical receipt identity mismatch")
        return binding
