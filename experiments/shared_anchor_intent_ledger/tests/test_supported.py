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
from experiments.shared_anchor_intent_ledger.protocol import Intent, IntentSubstitution
from experiments.shared_anchor_intent_ledger.supported import SupportedSharedAnchorLedger


class SupportedTests(unittest.TestCase):
    @staticmethod
    def attested(provider):
        return AttestedCatchup(
            provider,
            AttestationVerifier(
                {(provider.provider_id, provider.generation): provider.key},
                ProviderIdentity(provider.provider_id, provider.generation),
            ),
        )

    def test_restart_rejects_reserved_position_ahead_of_ledger_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.db"
            provider = SignedAnchorProvider(value=0)
            ledger = SupportedSharedAnchorLedger(path, self.attested(provider))
            ledger.execute(Intent("i1", "A", "migration", {"n": 1}))
            q = sqlite3.connect(path)
            q.execute("UPDATE shared_anchor_meta SET reserved_position=9 WHERE singleton=1")
            q.commit(); q.close()
            with self.assertRaises(IntentSubstitution):
                SupportedSharedAnchorLedger(path, self.attested(provider))

    def test_restart_rejects_reserved_position_behind_ledger_tail(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.db"
            provider = SignedAnchorProvider(value=0)
            ledger = SupportedSharedAnchorLedger(path, self.attested(provider))
            ledger.execute(Intent("i1", "A", "migration", {"n": 1}))
            q = sqlite3.connect(path)
            q.execute("UPDATE shared_anchor_meta SET reserved_position=0 WHERE singleton=1")
            q.commit(); q.close()
            with self.assertRaises(IntentSubstitution):
                SupportedSharedAnchorLedger(path, self.attested(provider))

    def test_verified_slice_mutation_before_watermark_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.db"
            provider = SignedAnchorProvider(value=0)
            ledger = SupportedSharedAnchorLedger(path, self.attested(provider))
            ledger.execute(Intent("i1", "A", "migration", {"n": 1}))
            ledger.execute(Intent("i2", "B", "root_rotation", {"n": 2}))

            original = ledger._reauthenticate
            mutated = {"done": False}
            def racing(entry):
                receipt = original(entry)
                if entry.position == 2 and not mutated["done"]:
                    q = sqlite3.connect(path)
                    q.execute(
                        "UPDATE shared_anchor_intents SET receipt_binding=? WHERE position=1",
                        ("0" * 64,),
                    )
                    q.commit(); q.close()
                    mutated["done"] = True
                return receipt
            ledger._reauthenticate = racing
            with self.assertRaises(IntentSubstitution):
                ledger.verify_component("A")
            self.assertEqual(ledger.watermark("A"), 0)

    def test_restart_rejects_provider_generation_rotation_without_historical_verifier(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.db"
            provider = SignedAnchorProvider(value=0)
            ledger = SupportedSharedAnchorLedger(path, self.attested(provider))
            ledger.execute(Intent("i1", "A", "migration", {"n": 1}))
            provider.rotate("anchor-A", 2, b"k2")
            with self.assertRaises(Exception):
                SupportedSharedAnchorLedger(path, self.attested(provider))


if __name__ == "__main__":
    unittest.main()
