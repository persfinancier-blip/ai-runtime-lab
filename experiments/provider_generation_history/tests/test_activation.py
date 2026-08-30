import unittest

from experiments.anchor_attestation.protocol import AnchorMismatch, UnknownOutcome
from experiments.provider_generation_history.activation import (
    ActivationFenced,
    ActivationState,
    FencedActivationProvider,
)


class ProviderActivationFenceTests(unittest.TestCase):
    def test_prepare_blocks_external_advance_until_resolution(self):
        provider = FencedActivationProvider(generation=2, value=10)
        ticket = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        self.assertEqual(ticket.fence, 1)
        self.assertEqual(provider.activation_status(ticket), "PREPARED")
        with self.assertRaises(ActivationFenced):
            provider.increment(expected=10, challenge="outside", request_id="outside")

    def test_stale_candidate_is_rejected_at_provider_linearization_point(self):
        provider = FencedActivationProvider(generation=2, value=11)
        with self.assertRaises(AnchorMismatch):
            provider.prepare_activation(expected_position=10, activation_id="rotate-2")

    def test_prepare_is_idempotent_for_same_activation(self):
        provider = FencedActivationProvider(generation=2, value=10)
        first = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        second = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        self.assertEqual(first, second)
        self.assertEqual(second.fence, 1)

    def test_unknown_commit_reconciles_as_committed(self):
        provider = FencedActivationProvider(generation=2, value=10)
        ticket = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        with self.assertRaises(UnknownOutcome):
            provider.commit_activation(ticket, timeout_after_commit=True)
        self.assertEqual(provider.activation_status(ticket), "COMMITTED")
        self.assertEqual(provider.commit_activation(ticket), "COMMITTED")

    def test_provider_owned_state_survives_coordinator_restart(self):
        state = ActivationState()
        first = FencedActivationProvider(generation=2, value=10, activation_state=state)
        ticket = first.prepare_activation(expected_position=10, activation_id="rotate-2")

        restarted = FencedActivationProvider(generation=2, value=10, activation_state=state)
        self.assertEqual(restarted.activation_status(ticket), "PREPARED")
        self.assertEqual(restarted.commit_activation(ticket), "COMMITTED")

    def test_abort_releases_fence_without_advancing_provider(self):
        provider = FencedActivationProvider(generation=2, value=10)
        ticket = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        self.assertEqual(provider.abort_activation(ticket), "ABORTED")
        provider.increment(expected=10, challenge="after-abort", request_id="after-abort")
        self.assertEqual(provider.value, 11)


if __name__ == "__main__":
    unittest.main()
