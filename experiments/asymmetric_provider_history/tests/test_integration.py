import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.asymmetric_provider_history.integration import (
    AsymmetricHistoricalSharedAnchorLedger,
    PendingRotationBlocked,
)
from experiments.asymmetric_provider_history.protocol import (
    AsymmetricProviderHistory,
    CurrentGenerationRequired,
    GenerationSigner,
    HistoricalVerificationError,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent, IntentSubstitution


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.s1 = GenerationSigner.from_seed("anchor-A", 1, b"\x11" * 32)
        self.s2 = GenerationSigner.from_seed("anchor-A", 2, b"\x22" * 32)

    @staticmethod
    def attested(generation, key, value):
        provider = SignedAnchorProvider("anchor-A", generation, key, value=value)
        verifier = AttestationVerifier(
            {("anchor-A", generation): key},
            ProviderIdentity("anchor-A", generation),
        )
        return provider, AttestedCatchup(provider, verifier)

    @staticmethod
    def intent(name):
        return Intent(name, "component-A", "migration", {"name": name})

    def test_mixed_generation_receipts_survive_restart_without_old_hmac_key(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1, a1 = self.attested(1, b"hmac-generation-one", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            first = self.intent("first")
            self.assertEqual(ledger.execute(first).status, "CONFIRMED")

            p2, a2 = self.attested(2, b"hmac-generation-two", 1)
            proof = AsymmetricProviderHistory.make_transition(self.s1, self.s2)
            ledger.rotate_provider(self.s2, proof, a2)
            second = self.intent("second")
            self.assertEqual(ledger.execute(second).status, "CONFIRMED")

            restarted = AsymmetricHistoricalSharedAnchorLedger(path, a2, self.s1.public, self.s2)
            self.assertTrue(restarted.verify_durable())
            self.assertEqual(restarted.provider_history.load_receipt(ledger.entry("first").request_id).generation, 1)
            self.assertEqual(restarted.provider_history.load_receipt(ledger.entry("second").request_id).generation, 2)
            # No generation-1 HMAC verification key exists in the restarted verifier.
            self.assertNotIn(("anchor-A", 1), restarted.attested.verifier.keyring)

    def test_confirmed_historical_retry_is_receipt_only_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            intent = self.intent("first")
            confirmed = ledger.execute(intent)
            p2, a2 = self.attested(2, b"h2", 1)
            ledger.rotate_provider(self.s2, AsymmetricProviderHistory.make_transition(self.s1, self.s2), a2)
            p2.available = False
            again = ledger.execute(intent)
            self.assertEqual(again.receipt_binding, confirmed.receipt_binding)
            self.assertEqual(p2.increment_calls, 0)

    def test_prepared_intent_blocks_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            ledger.reserve(self.intent("pending"))
            _, a2 = self.attested(2, b"h2", 0)
            with self.assertRaises(PendingRotationBlocked):
                ledger.rotate_provider(
                    self.s2,
                    AsymmetricProviderHistory.make_transition(self.s1, self.s2),
                    a2,
                )
            self.assertEqual(ledger.provider_history.current().generation, 1)

    def test_old_signer_or_old_attested_runtime_cannot_resume_current_head(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            _, a2 = self.attested(2, b"h2", 0)
            ledger.rotate_provider(self.s2, AsymmetricProviderHistory.make_transition(self.s1, self.s2), a2)
            with self.assertRaises(CurrentGenerationRequired):
                AsymmetricHistoricalSharedAnchorLedger(path, a2, self.s1.public, self.s1)
            with self.assertRaises(CurrentGenerationRequired):
                AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s2)

    def test_private_and_hmac_signing_material_are_not_durable_history(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, a1 = self.attested(1, b"unique-hmac-one", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            ledger.execute(self.intent("one"))
            _, a2 = self.attested(2, b"unique-hmac-two", 1)
            ledger.rotate_provider(self.s2, AsymmetricProviderHistory.make_transition(self.s1, self.s2), a2)
            ledger.execute(self.intent("two"))
            raw = path.read_bytes()
            self.assertNotIn(b"\x11" * 32, raw)
            self.assertNotIn(b"\x22" * 32, raw)
            self.assertNotIn(b"unique-hmac-one", raw)
            self.assertNotIn(b"unique-hmac-two", raw)

    def test_receipt_signature_corruption_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            ledger.execute(self.intent("one"))
            q = sqlite3.connect(path)
            q.execute("UPDATE asymmetric_provider_receipts SET signature=?", ("00" * 64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)

    def test_ledger_to_receipt_rebinding_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            ledger.execute(self.intent("one"))
            q = sqlite3.connect(path)
            q.execute("UPDATE shared_anchor_intents SET provider_generation=2 WHERE intent_id='one'")
            q.commit(); q.close()
            with self.assertRaises(IntentSubstitution):
                AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)

    def test_transition_corruption_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            _, a2 = self.attested(2, b"h2", 0)
            ledger.rotate_provider(self.s2, AsymmetricProviderHistory.make_transition(self.s1, self.s2), a2)
            q = sqlite3.connect(path)
            q.execute("UPDATE asymmetric_provider_transitions SET old_signature=?", ("00" * 64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                AsymmetricHistoricalSharedAnchorLedger(path, a2, self.s1.public, self.s2)

    def test_reservation_rotation_race_has_no_historical_prepared_intent(self):
        for _ in range(10):
            with tempfile.TemporaryDirectory() as td:
                path = Path(td) / "shared.db"
                _, a1 = self.attested(1, b"h1", 0)
                ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
                _, a2 = self.attested(2, b"h2", 0)
                barrier = threading.Barrier(3)
                outcomes = []

                def reserve():
                    barrier.wait()
                    try:
                        outcomes.append(("reserve", ledger.reserve(self.intent("race"))))
                    except Exception as exc:
                        outcomes.append(("reserve-error", exc))

                def rotate():
                    barrier.wait()
                    try:
                        outcomes.append(("rotate", ledger.rotate_provider(
                            self.s2,
                            AsymmetricProviderHistory.make_transition(self.s1, self.s2),
                            a2,
                        )))
                    except Exception as exc:
                        outcomes.append(("rotate-error", exc))

                t1 = threading.Thread(target=reserve)
                t2 = threading.Thread(target=rotate)
                t1.start(); t2.start(); barrier.wait(); t1.join(5); t2.join(5)
                self.assertFalse(t1.is_alive() or t2.is_alive())
                entry = ledger.entry("race")
                head = ledger.provider_history.current()
                if entry.status == "PREPARED" and entry.provider_generation != head.generation:
                    # This state is forbidden: rotation must not strand PREPARED work on history.
                    self.fail("rotation stranded a PREPARED intent on a historical generation")
                rotate_errors = [x[1] for x in outcomes if x[0] == "rotate-error"]
                if rotate_errors:
                    self.assertTrue(any(isinstance(x, PendingRotationBlocked) for x in rotate_errors))

    def test_local_snapshot_rollback_is_not_claimed_as_external_freshness_proof(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            snapshot = Path(td) / "pre-rotation.db"
            _, a1 = self.attested(1, b"h1", 0)
            ledger = AsymmetricHistoricalSharedAnchorLedger(path, a1, self.s1.public, self.s1)
            ledger.execute(self.intent("one"))
            sqlite3.connect(path).backup(sqlite3.connect(snapshot))
            _, a2 = self.attested(2, b"h2", 1)
            ledger.rotate_provider(self.s2, AsymmetricProviderHistory.make_transition(self.s1, self.s2), a2)
            # LAB-082 deliberately does not claim that an internally consistent old DB
            # snapshot is fresh when the external anchor/trust context is also rolled back.
            rolled = Path(td) / "rolled.db"
            rolled.write_bytes(snapshot.read_bytes())
            restarted = AsymmetricHistoricalSharedAnchorLedger(rolled, a1, self.s1.public, self.s1)
            self.assertTrue(restarted.verify_durable())
            self.assertEqual(restarted.provider_history.current().generation, 1)


if __name__ == "__main__":
    unittest.main()
