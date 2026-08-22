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
    IntentGap,
    SharedAnchorLedger,
)


class RestartRollbackTests(unittest.TestCase):
    @staticmethod
    def _attested(provider):
        return AttestedCatchup(
            provider,
            AttestationVerifier(
                {(provider.provider_id, provider.generation): provider.key},
                ProviderIdentity(provider.provider_id, provider.generation),
            ),
        )

    @staticmethod
    def _backup(source_path, backup_path):
        source = sqlite3.connect(source_path)
        target = sqlite3.connect(backup_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

    @staticmethod
    def _restore(backup_path, target_path):
        source = sqlite3.connect(backup_path)
        target = sqlite3.connect(target_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

    def test_component_restart_accepts_other_components_explained_advance(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.db"
            provider = SignedAnchorProvider(value=0)
            ledger = SharedAnchorLedger(path, self._attested(provider))
            ledger.execute(Intent("a1", "A", "migration", {"n": 1}))
            self.assertEqual(ledger.verify_component("A"), 1)
            ledger.execute(Intent("b1", "B", "root_rotation", {"n": 2}))

            restarted = SharedAnchorLedger(path, self._attested(provider))
            self.assertEqual(restarted.watermark("A"), 1)
            self.assertEqual(restarted.verify_component("A"), 2)

    def test_whole_ledger_snapshot_rollback_is_detected_when_provider_is_ahead(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.db"
            snapshot = Path(td) / "before-second.sqlite"
            provider = SignedAnchorProvider(value=0)
            ledger = SharedAnchorLedger(path, self._attested(provider))
            ledger.execute(Intent("a1", "A", "migration", {"n": 1}))
            self.assertEqual(ledger.verify_component("A"), 1)
            self._backup(path, snapshot)

            ledger.execute(Intent("b1", "B", "root_rotation", {"n": 2}))
            self.assertEqual(provider.value, 2)
            self._restore(snapshot, path)

            restored = SharedAnchorLedger(path, self._attested(provider))
            self.assertEqual(restored.watermark("A"), 1)
            with self.assertRaises(IntentGap):
                restored.verify_component("A")


if __name__ == "__main__":
    unittest.main()
