import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.shared_anchor_intent_ledger.protocol import (
    Intent,
    IntentConflict,
    IntentGap,
    IntentSubstitution,
    PendingIntent,
    ProviderMismatch,
    SharedAnchorLedger,
    UnexplainedAdvance,
    UnsafeMonotonicOnly,
)


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ledger.db"
        self.provider = SignedAnchorProvider(value=0)
        self.attested = self._attested(self.provider)
        self.ledger = SharedAnchorLedger(self.path, self.attested)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _attested(provider):
        verifier = AttestationVerifier(
            {(provider.provider_id, provider.generation): provider.key},
            ProviderIdentity(provider.provider_id, provider.generation),
        )
        return AttestedCatchup(provider, verifier)

    @staticmethod
    def intent(i, component="A", kind="migration", value=1):
        return Intent(i, component, kind, {"value": value})

    def test_two_components_share_provider_and_explain_ahead_positions(self):
        self.ledger.execute(self.intent("i1", "A"))
        self.assertEqual(self.ledger.verify_component("A"), 1)
        self.ledger.execute(self.intent("i2", "B", "root_rotation", 2))
        self.assertEqual(self.provider.value, 2)
        self.assertEqual(self.ledger.verify_component("A"), 2)
        self.assertEqual(self.ledger.verify_component("B"), 2)

    def test_timeout_after_commit_reconciles_without_duplicate_increment(self):
        entry = self.ledger.execute(self.intent("i1"), timeout_after_commit=True)
        self.assertEqual(entry.status, "CONFIRMED")
        self.assertEqual((self.provider.value, self.provider.increment_calls), (1, 1))
        again = self.ledger.execute(self.intent("i1"))
        self.assertEqual(again.receipt_binding, entry.receipt_binding)
        self.assertEqual(self.provider.increment_calls, 1)

    def test_intent_id_content_substitution_rejected(self):
        self.ledger.execute(self.intent("i1", value=1))
        with self.assertRaises(IntentConflict):
            self.ledger.reserve(self.intent("i1", value=2))

    def test_unknown_intent_type_rejected_before_provider(self):
        with self.assertRaises(IntentSubstitution):
            self.ledger.reserve(self.intent("i1", kind="anything"))
        self.assertEqual(self.provider.value, 0)

    def test_gap_in_ledger_is_rejected(self):
        self.ledger.execute(self.intent("i1"))
        self.ledger.execute(self.intent("i2", "B"))
        q = sqlite3.connect(self.path)
        q.execute("DELETE FROM shared_anchor_intents WHERE position=1")
        q.commit(); q.close()
        with self.assertRaises(IntentGap):
            self.ledger.verify_component("C")

    def test_receipt_substitution_rejected(self):
        self.ledger.execute(self.intent("i1"))
        q = sqlite3.connect(self.path)
        q.execute("UPDATE shared_anchor_intents SET receipt_binding=? WHERE position=1", ("0" * 64,))
        q.commit(); q.close()
        with self.assertRaises(IntentSubstitution):
            self.ledger.verify_component("A")

    def test_provider_generation_rotation_fails_closed_for_old_ledger(self):
        self.ledger.execute(self.intent("i1"))
        self.provider.rotate("anchor-A", 2, b"k2")
        restarted = SharedAnchorLedger(self.path, self._attested(self.provider))
        with self.assertRaises((ProviderMismatch, UnexplainedAdvance)):
            restarted.verify_component("A")

    def test_unrelated_external_advance_is_unexplained(self):
        challenge = self.attested.challenge()
        self.provider.increment(
            expected=0, challenge=challenge, request_id="unrelated"
        )
        with self.assertRaises(IntentGap):
            self.ledger.verify_component("A")

    def test_only_one_prepared_intent_at_a_time(self):
        self.ledger.reserve(self.intent("i1"))
        with self.assertRaises(PendingIntent):
            self.ledger.reserve(self.intent("i2", "B"))

    def test_allowed_intent_type_substitution_breaks_request_binding(self):
        self.ledger.execute(self.intent("i1", kind="migration"))
        q = sqlite3.connect(self.path)
        q.execute("UPDATE shared_anchor_intents SET intent_type='root_rotation' WHERE position=1")
        q.commit(); q.close()
        with self.assertRaises(IntentSubstitution):
            self.ledger.entry("i1")

    def test_request_id_tamper_rejected(self):
        self.ledger.reserve(self.intent("i1"))
        q = sqlite3.connect(self.path)
        q.execute("UPDATE shared_anchor_intents SET request_id='evil' WHERE intent_id='i1'")
        q.commit(); q.close()
        with self.assertRaises(IntentSubstitution):
            self.ledger.entry("i1")

    def test_unsafe_monotonic_only_accepts_unrelated_advance(self):
        self.assertTrue(UnsafeMonotonicOnly.accepts(0, 1))


if __name__ == "__main__":
    unittest.main()
