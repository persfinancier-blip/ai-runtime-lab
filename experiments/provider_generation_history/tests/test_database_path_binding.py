from __future__ import annotations

import shutil
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
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import (
    CoordinatorOnlyProviderHistory,
    SupportedHistoricalSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class DatabasePathBindingTests(unittest.TestCase):
    def setUp(self):
        self.k1 = b"provider-key-1"
        self.k2 = b"provider-key-2"
        self.g1 = descriptor(1, self.k1)
        self.g2 = descriptor(2, self.k2)

    def test_supported_ledger_and_history_cannot_rebind_to_corrupt_matching_head_db(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_a = root / "a.sqlite"
            db_b = root / "b.sqlite"

            p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                db_a, attested(p1, 1, self.k1), self.g1
            )
            ledger.execute(Intent("a-1", "component-A", "migration", {"v": 1}))

            p2 = SignedAnchorProvider("anchor-A", 2, self.k2, value=1)
            ledger.rotate_provider(
                self.g2,
                ledger.provider_history.make_transition(self.g1, self.g2),
                attested(p2, 2, self.k2),
            )
            self.assertEqual(ledger.provider_history.current().generation, 2)
            self.assertTrue(ledger.verify_durable())

            shutil.copy2(db_a, db_b)
            q = sqlite3.connect(db_b)
            q.execute(
                "UPDATE provider_generation_transitions SET old_mac=? WHERE new_generation_id=?",
                ("0" * 64, self.g2.generation_id),
            )
            self.assertEqual(
                q.execute(
                    "SELECT generation FROM provider_generation_head WHERE singleton=1"
                ).fetchone(),
                (2,),
            )
            b_tail_before = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            q.commit()
            q.close()

            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                ledger.path = db_b
            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                ledger.provider_history.path = db_b

            self.assertEqual(Path(ledger.path), db_a.resolve())
            self.assertEqual(Path(ledger.provider_history.path), db_a.resolve())
            self.assertTrue(ledger.verify_durable())

            confirmed = ledger.execute(
                Intent("a-2", "component-A", "root_rotation", {"v": 2})
            )
            self.assertEqual((confirmed.status, confirmed.position), ("CONFIRMED", 2))

            q = sqlite3.connect(db_b)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
                    ).fetchone()[0],
                    b_tail_before,
                )
                self.assertIsNone(
                    q.execute(
                        "SELECT 1 FROM shared_anchor_intents WHERE intent_id='a-2'"
                    ).fetchone()
                )
            finally:
                q.close()

    def test_legitimate_db_b_history_object_cannot_replace_construction_bound_strategy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            db_a = root / "a.sqlite"
            db_b = root / "b.sqlite"

            provider = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                db_a, attested(provider, 1, self.k1), self.g1
            )
            original = ledger.provider_history
            replacement = CoordinatorOnlyProviderHistory(db_b, self.g1)

            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                ledger.provider_history = replacement
            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                ledger._provider_history = replacement

            self.assertIs(ledger.provider_history, original)
            self.assertEqual(Path(ledger.provider_history.path), db_a.resolve())
            self.assertEqual(Path(replacement.path), db_b.resolve())

            confirmed = ledger.execute(
                Intent("a-1", "component-A", "migration", {"v": 1})
            )
            self.assertEqual((confirmed.status, confirmed.position), ("CONFIRMED", 1))

            q = sqlite3.connect(db_b)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
                    ).fetchone()[0],
                    0,
                )
                self.assertIsNone(
                    q.execute(
                        "SELECT 1 FROM shared_anchor_intents WHERE intent_id='a-1'"
                    ).fetchone()
                )
            finally:
                q.close()

    def test_private_canonical_path_slot_cannot_be_rebound_after_construction(self):
        with tempfile.TemporaryDirectory() as td:
            db_a = Path(td) / "a.sqlite"
            db_b = Path(td) / "b.sqlite"
            p1 = SignedAnchorProvider("anchor-A", 1, self.k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                db_a, attested(p1, 1, self.k1), self.g1
            )

            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                ledger._canonical_database_path = str(db_b)
            with self.assertRaisesRegex(AttributeError, "construction-bound"):
                ledger.provider_history._canonical_database_path = str(db_b)

            self.assertEqual(Path(ledger.path), db_a.resolve())
            self.assertEqual(Path(ledger.provider_history.path), db_a.resolve())


if __name__ == "__main__":
    unittest.main()
