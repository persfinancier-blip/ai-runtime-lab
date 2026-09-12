import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AnchorMismatch,
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    ProviderUnavailable,
)
from experiments.provider_generation_history.activation import (
    ActivationFenced,
    ActivationState,
    FencedActivationProvider,
)
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
    PendingRotationBlocked,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class AttemptAdvanceDuringPrepare(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.advance_result = None

    def prepare_activation(self, **kwargs):
        ticket = super().prepare_activation(**kwargs)
        try:
            self.increment(
                expected=ticket.expected_position,
                challenge="race",
                request_id="external-race",
            )
            self.advance_result = "advanced"
        except Exception as exc:
            self.advance_result = type(exc).__name__
        return ticket


class AttemptAdvanceAfterProviderCommit(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.advance_result = None

    def commit_activation(self, ticket, *, timeout_after_commit=False):
        status = super().commit_activation(
            ticket, timeout_after_commit=timeout_after_commit
        )
        try:
            self.increment(
                expected=ticket.expected_position,
                challenge="post-provider-commit-race",
                request_id="post-provider-commit-race",
            )
            self.advance_result = "advanced"
        except Exception as exc:
            self.advance_result = type(exc).__name__
        return status


class UnknownAfterCommitProvider(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_commit = True

    def commit_activation(self, ticket, *, timeout_after_commit=False):
        if self.first_commit:
            self.first_commit = False
            return super().commit_activation(ticket, timeout_after_commit=True)
        return super().commit_activation(ticket, timeout_after_commit=timeout_after_commit)


class UnavailableOnFirstCommitProvider(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_once = True

    def commit_activation(self, ticket, *, timeout_after_commit=False):
        if self.fail_once:
            self.fail_once = False
            raise ProviderUnavailable("simulated post-SQL provider outage")
        return super().commit_activation(ticket, timeout_after_commit=timeout_after_commit)


class UnavailableOnFirstReleaseProvider(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_release_once = True

    def release_activation(self, ticket):
        if self.fail_release_once:
            self.fail_release_once = False
            raise ProviderUnavailable("simulated outage after durable coordinator acknowledgement")
        return super().release_activation(ticket)


class ActivationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.k1 = b"provider-key-1"
        self.k2 = b"provider-key-2"
        self.g1 = descriptor(1, self.k1)
        self.g2 = descriptor(2, self.k2)

    def ledger(self, path, provider, generation, key):
        return SupportedHistoricalSharedAnchorLedger(
            path, attested(provider, generation, key), self.g1
        )

    def test_prepare_fences_external_advance_before_sql_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            p2 = AttemptAdvanceDuringPrepare("anchor-A", 2, self.k2, value=0)

            ledger.rotate_provider(
                self.g2,
                ledger.provider_history.make_transition(self.g1, self.g2),
                attested(p2, 2, self.k2),
            )

            self.assertEqual(p2.advance_result, ActivationFenced.__name__)
            self.assertEqual(p2.value, 0)
            self.assertEqual(ledger.provider_history.current().generation, 2)
            row = ledger._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")

    def test_provider_commit_remains_fenced_until_durable_sql_ack(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            p2 = AttemptAdvanceAfterProviderCommit("anchor-A", 2, self.k2, value=0)

            ledger.rotate_provider(
                self.g2,
                ledger.provider_history.make_transition(self.g1, self.g2),
                attested(p2, 2, self.k2),
            )

            self.assertEqual(p2.advance_result, ActivationFenced.__name__)
            self.assertEqual(p2.value, 0)
            row = ledger._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")
            ticket = ledger._ticket_from_row(row)
            self.assertEqual(p2.activation_status(ticket), "RELEASED")

    def test_stale_candidate_is_rejected_before_sql_generation_commit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            p2 = FencedActivationProvider("anchor-A", 2, self.k2, value=1)

            with self.assertRaises(AnchorMismatch):
                ledger.rotate_provider(
                    self.g2,
                    ledger.provider_history.make_transition(self.g1, self.g2),
                    attested(p2, 2, self.k2),
                )
            self.assertEqual(ledger.provider_history.current().generation, 1)
            self.assertIsNone(ledger._activation_row(generation_id=self.g2.generation_id))

    def test_sql_failure_aborts_provider_reservation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            ledger.reserve(Intent("pending", "component-A", "migration", {"x": 1}))
            p2 = FencedActivationProvider("anchor-A", 2, self.k2, value=1)

            with self.assertRaises(PendingRotationBlocked):
                ledger.rotate_provider(
                    self.g2,
                    ledger.provider_history.make_transition(self.g1, self.g2),
                    attested(p2, 2, self.k2),
                )

            self.assertIsNone(p2.activation_state.pending)
            self.assertEqual(ledger.provider_history.current().generation, 1)
            self.assertIsNone(ledger._activation_row(generation_id=self.g2.generation_id))

    def test_unknown_after_provider_commit_reconciles_committed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            p2 = UnknownAfterCommitProvider("anchor-A", 2, self.k2, value=0)

            ledger.rotate_provider(
                self.g2,
                ledger.provider_history.make_transition(self.g1, self.g2),
                attested(p2, 2, self.k2),
            )

            row = ledger._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")
            ticket = ledger._ticket_from_row(row)
            self.assertEqual(p2.activation_status(ticket), "RELEASED")

    def test_restart_reconciles_sql_committed_ticket(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            state = ActivationState()
            p2 = UnavailableOnFirstCommitProvider(
                "anchor-A", 2, self.k2, value=0, activation_state=state
            )

            with self.assertRaises(ProviderUnavailable):
                ledger.rotate_provider(
                    self.g2,
                    ledger.provider_history.make_transition(self.g1, self.g2),
                    attested(p2, 2, self.k2),
                )

            q = sqlite3.connect(path)
            try:
                row = q.execute(
                    "SELECT status FROM provider_generation_activations WHERE new_generation_id=?",
                    (self.g2.generation_id,),
                ).fetchone()
            finally:
                q.close()
            self.assertEqual(row, ("SQL_COMMITTED",))
            self.assertEqual(ledger.provider_history.current().generation, 2)
            with self.assertRaises(PendingRotationBlocked):
                ledger.reserve(Intent("blocked", "component-A", "migration", {"x": 2}))

            restarted_provider = FencedActivationProvider(
                "anchor-A", 2, self.k2, value=0, activation_state=state
            )
            restarted = self.ledger(path, restarted_provider, 2, self.k2)
            row = restarted._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")
            ticket = restarted._ticket_from_row(row)
            self.assertEqual(restarted_provider.activation_status(ticket), "RELEASED")
            self.assertEqual(restarted.provider_history.current().generation, 2)

    def test_failed_release_stale_runtime_cannot_poison_next_intent(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            state = ActivationState()
            p2 = UnavailableOnFirstReleaseProvider(
                "anchor-A", 2, self.k2, value=0, activation_state=state
            )

            with self.assertRaises(ProviderUnavailable):
                ledger.rotate_provider(
                    self.g2,
                    ledger.provider_history.make_transition(self.g1, self.g2),
                    attested(p2, 2, self.k2),
                )

            self.assertEqual(ledger.provider_history.current().generation, 2)
            self.assertIs(ledger.attested.provider, p1)
            row = ledger._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")

            with self.assertRaises(CurrentGenerationRequired):
                ledger.execute(
                    Intent("must-not-persist", "component-A", "migration", {"x": 3})
                )

            q = sqlite3.connect(path)
            try:
                meta = q.execute(
                    "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
                ).fetchone()
                intent = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id='must-not-persist'"
                ).fetchone()
            finally:
                q.close()
            self.assertEqual(meta, (0,))
            self.assertIsNone(intent)

    def test_restart_releases_fence_after_sql_ack_if_release_was_lost(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, p1, 1, self.k1)
            state = ActivationState()
            p2 = UnavailableOnFirstReleaseProvider(
                "anchor-A", 2, self.k2, value=0, activation_state=state
            )

            with self.assertRaises(ProviderUnavailable):
                ledger.rotate_provider(
                    self.g2,
                    ledger.provider_history.make_transition(self.g1, self.g2),
                    attested(p2, 2, self.k2),
                )

            row = ledger._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")
            ticket = ledger._ticket_from_row(row)
            self.assertEqual(p2.activation_status(ticket), "COMMITTED_FENCED")
            with self.assertRaises(ActivationFenced):
                p2.increment(expected=0, challenge="still-fenced", request_id="still-fenced")

            restarted_provider = FencedActivationProvider(
                "anchor-A", 2, self.k2, value=0, activation_state=state
            )
            restarted = self.ledger(path, restarted_provider, 2, self.k2)
            row = restarted._activation_row(generation_id=self.g2.generation_id)
            self.assertEqual(row[6], "COMMITTED")
            ticket = restarted._ticket_from_row(row)
            self.assertEqual(restarted_provider.activation_status(ticket), "RELEASED")
            restarted_provider.increment(
                expected=0, challenge="after-recovery", request_id="after-recovery"
            )
            self.assertEqual(restarted_provider.value, 1)


if __name__ == "__main__":
    unittest.main()
