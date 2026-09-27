import unittest

from experiments.anchor_attestation.protocol import AnchorMismatch, UnknownOutcome
from experiments.provider_generation_history.activation import (
    ActivationFenced,
    ActivationState,
    ActivationTicket,
    ActivationTicketMismatch,
    FencedActivationProvider,
)


class ComposedProviderActivationFenceTests(unittest.TestCase):
    def test_prepare_fences_external_advance_until_exact_release(self):
        provider = FencedActivationProvider(generation=2, value=10)
        ticket = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        with self.assertRaises(ActivationFenced):
            provider.increment(expected=10, challenge="outside", request_id="outside")
        self.assertEqual(provider.commit_activation(ticket), "COMMITTED_FENCED")
        with self.assertRaises(ActivationFenced):
            provider.increment(expected=10, challenge="before-ack", request_id="before-ack")
        self.assertEqual(provider.release_activation(ticket), "RELEASED")
        provider.increment(expected=10, challenge="after-ack", request_id="after-ack")
        self.assertEqual(provider.value, 11)

    def test_stale_candidate_and_wrong_release_ticket_fail_closed(self):
        provider = FencedActivationProvider(generation=2, value=10)
        with self.assertRaises(AnchorMismatch):
            provider.prepare_activation(expected_position=9, activation_id="stale")
        ticket = provider.prepare_activation(expected_position=10, activation_id="rotate-2")
        provider.commit_activation(ticket)
        wrong = ActivationTicket(ticket.provider_id, ticket.generation, ticket.expected_position, ticket.activation_id, ticket.fence + 1)
        with self.assertRaises(ActivationTicketMismatch):
            provider.release_activation(wrong)
        self.assertEqual(provider.activation_status(ticket), "COMMITTED_FENCED")

    def test_unknown_commit_and_restart_preserve_fence(self):
        state = ActivationState()
        first = FencedActivationProvider(generation=2, value=10, activation_state=state)
        ticket = first.prepare_activation(expected_position=10, activation_id="rotate-2")
        with self.assertRaises(UnknownOutcome):
            first.commit_activation(ticket, timeout_after_commit=True)
        restarted = FencedActivationProvider(generation=2, value=10, activation_state=state)
        self.assertEqual(restarted.activation_status(ticket), "COMMITTED_FENCED")
        with self.assertRaises(ActivationFenced):
            restarted.increment(expected=10, challenge="restart", request_id="restart")


if __name__ == "__main__":
    unittest.main()
