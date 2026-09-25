from pathlib import Path

from experiments.provider_generation_history.activation_coordinator import ActivationCoordinatorMixin
from experiments.provider_generation_history.activation_transition import ActivationTransitionMixin
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def test_supported_ledger_composes_both_activation_authority_slices():
    assert issubclass(SupportedHistoricalSharedAnchorLedger, ActivationTransitionMixin)
    assert issubclass(SupportedHistoricalSharedAnchorLedger, ActivationCoordinatorMixin)


def test_supported_rotation_uses_only_fenced_transition_then_durable_ack():
    source = Path("experiments/provider_generation_history/supported.py").read_text()
    start = source.index("    def rotate_provider(")
    end = source.index("\n    def _stored_receipt", start)
    rotation = source[start:end]

    assert "FencedActivationProvider" in rotation
    assert "self._preack_activation_transition(provider, new, proof)" in rotation
    assert "self._commit_or_reconcile_activation(provider, ticket)" in rotation
    assert "self._history().current()" in rotation
    assert "self.provider_history" not in rotation
    assert "_rotate_locked" not in rotation
    assert "authenticated_read" not in rotation

    preack = rotation.index("self._preack_activation_transition(provider, new, proof)")
    acknowledge = rotation.index("self._commit_or_reconcile_activation(provider, ticket)", preack)
    install_runtime = rotation.index("self.attested = new_attested", acknowledge)
    assert preack < acknowledge < install_runtime


def test_retry_reconciles_only_durable_current_generation():
    source = Path("experiments/provider_generation_history/supported.py").read_text()
    start = source.index("    def rotate_provider(")
    end = source.index("\n    def _stored_receipt", start)
    rotation = source[start:end]

    existing = rotation.index("existing = self._activation_row(generation_id=new.generation_id)")
    durable = rotation.index("durable = self._history().current()", existing)
    reject = rotation.index("activation retry is not durable current generation", durable)
    sql_reconcile = rotation.index('existing[6] == "SQL_COMMITTED"', reject)
    committed_release = rotation.index('existing[6] == "COMMITTED"', sql_reconcile)
    assert existing < durable < reject < sql_reconcile < committed_release
