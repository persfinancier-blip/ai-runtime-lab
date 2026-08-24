import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
    authority,
    signatures,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.protocol import ProviderRotationIntent
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    custody_rotation_payload,
)
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
    public_recovery,
    public_signatures,
)


class UnfencedSupportedSurfaceRegressionTests(unittest.TestCase):
    @staticmethod
    def _root_state(path):
        q = sqlite3.connect(path)
        try:
            return (
                q.execute(
                    "SELECT authority_id,version,generation FROM provider_rotation_authority_head WHERE singleton=1"
                ).fetchone(),
                q.execute("SELECT COUNT(*) FROM provider_rotation_authorities").fetchone()[0],
                q.execute("SELECT COUNT(*) FROM provider_rotation_authority_transitions").fetchone()[0],
            )
        finally:
            q.close()

    @staticmethod
    def _provider_state(path):
        q = sqlite3.connect(path)
        try:
            return (
                q.execute(
                    "SELECT generation_id,generation FROM asymmetric_provider_head WHERE singleton=1"
                ).fetchone(),
                q.execute("SELECT COUNT(*) FROM asymmetric_provider_generations").fetchone()[0],
                q.execute("SELECT COUNT(*) FROM asymmetric_provider_transitions").fetchone()[0],
                q.execute("SELECT COUNT(*) FROM provider_rotation_threshold_proofs").fetchone()[0],
            )
        finally:
            q.close()

    def test_direct_supported_suffix_cannot_rotate_public_recovery_after_cutoff(self):
        """The underlying LAB-086 class must not remain a weaker supported authority."""
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                ledger,
                _,
                _,
                root_raw,
                _,
                _,
                _,
                old_public_signers,
                _,
            ) = helper.make_ledger(path)
            helper.migrate(ledger, old_public_signers)

            q = sqlite3.connect(path)
            before_head = q.execute(
                "SELECT authority_id,version,generation "
                "FROM provider_recovery_public_head WHERE singleton=1"
            ).fetchone()
            before_authorities = q.execute(
                "SELECT COUNT(*) FROM provider_recovery_public_authorities"
            ).fetchone()[0]
            before_transitions = q.execute(
                "SELECT COUNT(*) FROM provider_recovery_public_transitions"
            ).fetchone()[0]
            before_proofs = q.execute(
                "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
            ).fetchone()[0]
            q.close()

            new_public, new_public_signers = public_recovery(2, 2, "direct-surface")
            custody_q = ledger.public_recovery_custody._con()
            try:
                old_public = ledger.public_recovery_custody.current_locked(custody_q)
            finally:
                custody_q.close()
            payload = custody_rotation_payload(
                old_public,
                new_public,
                ledger.rotation_authority.current().authority_id,
            )

            with self.assertRaises(Exception):
                ledger.rotate_public_recovery_authority(
                    new_public,
                    public_signatures(old_public_signers, payload, 3),
                    public_signatures(new_public_signers, payload, 3),
                    signatures(root_raw, payload, 2),
                )

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT authority_id,version,generation "
                        "FROM provider_recovery_public_head WHERE singleton=1"
                    ).fetchone(),
                    before_head,
                )
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM provider_recovery_public_authorities").fetchone()[0],
                    before_authorities,
                )
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM provider_recovery_public_transitions").fetchone()[0],
                    before_transitions,
                )
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs").fetchone()[0],
                    before_proofs,
                )
            finally:
                q.close()

    def test_direct_supported_suffix_cannot_normal_root_rotate_after_cutoff(self):
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, root1_raw, _, _, _, public_signers, _ = helper.make_ledger(path)
            helper.migrate(ledger, public_signers)
            before = self._root_state(path)
            root2, root2_raw = authority(2, 2, "direct-normal-root")
            payload = ledger.rotation_authority.authority_rotation_payload(root1, root2)
            with self.assertRaises(Exception):
                ledger.rotate_rotation_authority(
                    root2,
                    signatures(root1_raw, payload, 2),
                    signatures(root2_raw, payload, 2),
                )
            self.assertEqual(self._root_state(path), before)

    def test_direct_supported_suffix_cannot_provider_rotate_after_cutoff(self):
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer1, root1, root1_raw, _, _, _, public_signers, _ = helper.make_ledger(path)
            helper.migrate(ledger, public_signers)
            before = self._provider_state(path)
            signer2 = GenerationSigner.from_seed("anchor-A", 2, b"B" * 32)
            continuity = ledger.provider_history.make_transition(signer1, signer2)
            _, a2 = attested(2, b"hmac-2", 0)
            intent = ProviderRotationIntent(
                "anchor-A",
                signer1.public.generation_id,
                signer2.public.generation_id,
                root1.authority_id,
                root1.version,
                root1.generation,
            )
            with self.assertRaises(Exception):
                ledger.rotate_provider(
                    signer2,
                    continuity,
                    a2,
                    signatures(root1_raw, intent.payload, 2),
                )
            self.assertEqual(self._provider_state(path), before)


if __name__ == "__main__":
    unittest.main()
