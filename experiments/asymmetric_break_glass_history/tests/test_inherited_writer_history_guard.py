import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.final_supported import (
    SupportedFencedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
    authority,
    public_signatures,
    signatures,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.protocol import ProviderRotationIntent
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
)


class InheritedWriterHistoryGuardTests(unittest.TestCase):
    def _corrupted_ledger(self, path):
        helper = AsymmetricSuffixIntegrationTests()
        (
            ledger,
            signer1,
            _,
            _,
            _,
            _,
            _,
            public1_signers,
            _,
        ) = helper.make_ledger(path)
        helper.migrate(ledger, public1_signers)
        ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(ledger)

        root2, root2_raw = authority(2, 2, "inherited-guard-asym")
        payload = ledger.asymmetric_recovery_payload(root2)
        ledger.recover_rotation_authority_asymmetric(
            root2, public_signatures(public1_signers, payload, 3)
        )
        q = sqlite3.connect(path)
        q.execute(
            "UPDATE provider_asymmetric_break_glass_proofs "
            "SET public_signatures_json='[]' WHERE new_rotation_authority_id=?",
            (root2.authority_id,),
        )
        q.commit()
        q.close()
        return ledger, signer1, root2, root2_raw

    @staticmethod
    def _root_state(path):
        q = sqlite3.connect(path)
        try:
            return {
                "head": q.execute(
                    "SELECT authority_id,version,generation "
                    "FROM provider_rotation_authority_head WHERE singleton=1"
                ).fetchone(),
                "authorities": q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authorities"
                ).fetchone()[0],
                "normal_transitions": q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authority_transitions"
                ).fetchone()[0],
            }
        finally:
            q.close()

    @staticmethod
    def _provider_state(path):
        q = sqlite3.connect(path)
        try:
            return {
                "head": q.execute(
                    "SELECT generation_id,generation FROM asymmetric_provider_head WHERE singleton=1"
                ).fetchone(),
                "generations": q.execute(
                    "SELECT COUNT(*) FROM asymmetric_provider_generations"
                ).fetchone()[0],
                "transitions": q.execute(
                    "SELECT COUNT(*) FROM asymmetric_provider_transitions"
                ).fetchone()[0],
                "threshold_proofs": q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_threshold_proofs"
                ).fetchone()[0],
            }
        finally:
            q.close()

    def test_corrupt_lab086_history_blocks_inherited_normal_root_rotation_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root2, root2_raw = self._corrupted_ledger(path)
            before = self._root_state(path)
            root3, root3_raw = authority(3, 3, "inherited-guard-normal")
            payload = ledger.rotation_authority.authority_rotation_payload(root2, root3)
            with self.assertRaises(Exception):
                ledger.rotate_rotation_authority(
                    root3,
                    signatures(root2_raw, payload, 2),
                    signatures(root3_raw, payload, 2),
                )
            self.assertEqual(self._root_state(path), before)

    def test_corrupt_lab086_history_blocks_inherited_provider_rotation_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer1, root2, root2_raw = self._corrupted_ledger(path)
            before = self._provider_state(path)
            signer2 = GenerationSigner.from_seed("anchor-A", 2, b"B" * 32)
            continuity = ledger.provider_history.make_transition(signer1, signer2)
            _, a2 = attested(2, b"hmac-2", 0)
            intent = ProviderRotationIntent(
                "anchor-A",
                signer1.public.generation_id,
                signer2.public.generation_id,
                root2.authority_id,
                root2.version,
                root2.generation,
            )
            quorum = signatures(root2_raw, intent.payload, 2)
            with self.assertRaises(Exception):
                ledger.rotate_provider(signer2, continuity, a2, quorum)
            self.assertEqual(self._provider_state(path), before)


if __name__ == "__main__":
    unittest.main()
