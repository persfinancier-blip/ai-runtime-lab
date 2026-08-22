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
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
    HistoricalVerificationError,
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


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.k1 = b"provider-key-1"
        self.k2 = b"provider-key-2"
        self.g1 = descriptor(1, self.k1)
        self.g2 = descriptor(2, self.k2)

    def ledger(self, path, attested_value):
        return SupportedHistoricalSharedAnchorLedger(path, attested_value, self.g1)

    def test_mixed_old_new_confirmed_history_survives_rotation_and_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            a1 = attested(p1, 1, self.k1)
            ledger = self.ledger(path, a1)

            i1 = Intent("old", "component-A", "migration", {"v": 1})
            e1 = ledger.execute(i1)
            self.assertEqual((e1.status, e1.provider_generation, p1.value), ("CONFIRMED", 1, 1))

            p2 = SignedAnchorProvider("anchor-A", 2, self.k2, value=1)
            a2 = attested(p2, 2, self.k2)
            ledger.rotate_provider(
                self.g2, ledger.provider_history.make_transition(self.g1, self.g2), a2
            )
            p1.available = False

            i2 = Intent("new", "component-A", "root_rotation", {"v": 2})
            e2 = ledger.execute(i2)
            self.assertEqual((e2.status, e2.provider_generation, p2.value), ("CONFIRMED", 2, 2))

            restarted = self.ledger(path, a2)
            self.assertTrue(restarted.verify_durable())
            self.assertEqual(restarted.provider_history.load_receipt(e1.request_id).generation, 1)
            self.assertEqual(restarted.provider_history.load_receipt(e2.request_id).generation, 2)
            self.assertEqual(restarted.verify_component("component-A"), 2)
            self.assertEqual(restarted.verify_component("component-A"), 2)

    def test_old_generation_is_verification_only_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, attested(p1, 1, self.k1))
            p2 = SignedAnchorProvider("anchor-A", 2, self.k2, value=0)
            ledger.rotate_provider(
                self.g2,
                ledger.provider_history.make_transition(self.g1, self.g2),
                attested(p2, 2, self.k2),
            )
            with self.assertRaises(CurrentGenerationRequired):
                ledger.provider_history.require_current("anchor-A", 1)

    def test_prepared_intent_and_rotation_serialize_in_same_database(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            ledger = self.ledger(path, attested(p1, 1, self.k1))
            entry = ledger.reserve(Intent("pending", "component-A", "migration", {"x": 1}))
            self.assertEqual(entry.status, "PREPARED")

            p2 = SignedAnchorProvider("anchor-A", 2, self.k2, value=1)
            with self.assertRaises(PendingRotationBlocked):
                ledger.rotate_provider(
                    self.g2,
                    ledger.provider_history.make_transition(self.g1, self.g2),
                    attested(p2, 2, self.k2),
                )
            self.assertEqual(ledger.provider_history.current().generation, 1)

    def test_reserve_vs_rotation_has_only_safe_serialized_outcomes(self):
        for _ in range(20):
            with tempfile.TemporaryDirectory() as td:
                path = Path(td) / "shared.db"
                p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
                ledger = self.ledger(path, attested(p1, 1, self.k1))
                p2 = SignedAnchorProvider("anchor-A", 2, self.k2, value=0)
                a2 = attested(p2, 2, self.k2)
                gate = threading.Barrier(3)
                results = []
                lock = threading.Lock()

                def reserve():
                    gate.wait()
                    try:
                        value = ledger.reserve(Intent("r", "component-A", "migration", {"x": 1}))
                        result = ("reserve", "ok", value.provider_generation)
                    except Exception as exc:
                        result = ("reserve", type(exc).__name__, None)
                    with lock:
                        results.append(result)

                def rotate():
                    gate.wait()
                    try:
                        ledger.rotate_provider(
                            self.g2,
                            ledger.provider_history.make_transition(self.g1, self.g2),
                            a2,
                        )
                        result = ("rotate", "ok", 2)
                    except Exception as exc:
                        result = ("rotate", type(exc).__name__, None)
                    with lock:
                        results.append(result)

                t1 = threading.Thread(target=reserve)
                t2 = threading.Thread(target=rotate)
                t1.start(); t2.start(); gate.wait(); t1.join(5); t2.join(5)
                self.assertFalse(t1.is_alive() or t2.is_alive())

                current = ledger.provider_history.current().generation
                entry = ledger.entry("r")
                if current == 2:
                    self.assertEqual(entry.provider_generation, 2)
                    self.assertIn(("rotate", "ok", 2), results)
                else:
                    self.assertEqual(current, 1)
                    self.assertEqual(entry.provider_generation, 1)
                    self.assertTrue(any(r[0] == "rotate" and r[1] == "PendingRotationBlocked" for r in results))

    def test_historical_receipt_corruption_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            a1 = attested(p1, 1, self.k1)
            ledger = self.ledger(path, a1)
            ledger.execute(Intent("old", "component-A", "migration", {"v": 1}))
            q = sqlite3.connect(path)
            q.execute("UPDATE historical_provider_receipts SET signature=?", ("0" * 64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                self.ledger(path, a1)


if __name__ == "__main__":
    unittest.main()
