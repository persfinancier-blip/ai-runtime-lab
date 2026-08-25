import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.final_supported import (
    SupportedFencedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_break_glass_history.suffix import (
    PublicRecoveryRotationError,
)
from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
    authority,
    public_recovery,
    public_signatures,
    signatures,
)
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    custody_rotation_payload,
    sha as custody_sha,
)


class PublicRotationCrossBindingTests(unittest.TestCase):
    def test_public_transition_and_root_proof_must_bind_same_root(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            helper = AsymmetricSuffixIntegrationTests()
            (
                ledger,
                _,
                root1,
                root1_raw,
                _,
                _,
                public1,
                public1_signers,
                _,
            ) = helper.make_ledger(path)
            helper.migrate(ledger, public1_signers)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(ledger)

            public2, public2_signers = public_recovery(2, 2, "cross-binding-public")
            public_payload = ledger.public_recovery_rotation_payload(public2)
            ledger.rotate_public_recovery_authority(
                public2,
                public_signatures(public1_signers, public_payload, 3),
                public_signatures(public2_signers, public_payload, 3),
                signatures(root1_raw, public_payload, 2),
            )

            # Advance the normal root legitimately so a second, independently
            # valid root quorum exists. The public transition above remains
            # Ed25519-authenticated for root1.
            root2, root2_raw = authority(2, 2, "cross-binding-root")
            root_payload = ledger.rotation_authority.authority_rotation_payload(
                root1, root2
            )
            ledger.rotate_rotation_authority(
                root2,
                signatures(root1_raw, root_payload, 2),
                signatures(root2_raw, root_payload, 2),
            )

            # Rebind only the LAB-086 root-threshold proof to root2, with a
            # completely valid quorum over that different payload. Ordinary DML
            # is fenced, so remove only the proof UPDATE guard to model
            # out-of-band durable corruption and exercise verifier cross-binding.
            rebound = custody_rotation_payload(public1, public2, root2.authority_id)
            rebound_root_signatures = signatures(root2_raw, rebound, 2)
            encoded = ledger.rotation_authority._encode_signatures(
                rebound_root_signatures
            )
            q = sqlite3.connect(path)
            q.execute("DROP TRIGGER lab086_public_root_proof_is_immutable")
            q.execute(
                "UPDATE provider_asymmetric_recovery_public_root_proofs "
                "SET root_authority_id=?,root_version=?,root_generation=?,"
                "intent_digest=?,root_signatures_json=? "
                "WHERE new_public_authority_id=?",
                (
                    root2.authority_id,
                    root2.version,
                    root2.generation,
                    custody_sha(rebound),
                    encoded,
                    public2.authority_id,
                ),
            )
            q.commit()
            q.close()

            with self.assertRaises(PublicRecoveryRotationError):
                ledger.verify_durable()


if __name__ == "__main__":
    unittest.main()
