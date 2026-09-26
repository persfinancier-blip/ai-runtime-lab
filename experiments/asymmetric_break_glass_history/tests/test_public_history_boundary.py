import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.suffix import SupportedAsymmetricBreakGlassLedger
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_recovery_authority_lifecycle.custody_break_glass import custody_enablement_payload
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
    authority,
    public_recovery,
    public_signatures,
    recovery,
    signatures,
)


class PublicHistoryBoundaryTests(unittest.TestCase):
    def make_ledger(self, path):
        signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
        _, a1 = attested(1, b"hmac-1")
        root, root_raw = authority()
        rec, rec_raw = recovery()
        public, public_signers = public_recovery()
        base = ThresholdEnablement(
            signer.public.generation_id, 1, root.authority_id, 1, 1, ()
        )
        enable = ThresholdEnablement(
            base.start_provider_generation_id,
            1,
            root.authority_id,
            1,
            1,
            signatures(root_raw, base.payload, 2),
        )
        enable_payload = custody_enablement_payload(root, rec, public)
        ledger = SupportedAsymmetricBreakGlassLedger(
            path,
            a1,
            signer.public,
            signer,
            root,
            enable,
            rec.recovery,
            public,
            custody_enablement_signatures=public_signatures(
                public_signers, enable_payload, 3
            ),
        )
        return ledger, root_raw, rec, rec_raw, public_signers

    def test_cutoff_payload_rejects_corrupted_public_custody_rotation_history(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, root_raw, rec1, rec1_raw, public1_signers = self.make_ledger(path)
            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            public2, public2_signers = public_recovery(2, 2, "public-new")
            symmetric_payload, public_payload = ledger.recovery_custody_rotation_payloads(
                rec2, public2
            )
            ledger.rotate_recovery_authority_with_custody(
                rec2,
                public2,
                signatures(rec1_raw, symmetric_payload, 3),
                signatures(rec2_raw, symmetric_payload, 3),
                signatures(root_raw, symmetric_payload, 2),
                public_signatures(public1_signers, public_payload, 3),
                public_signatures(public2_signers, public_payload, 3),
            )
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_recovery_public_transitions SET old_signatures_json='[]'"
            )
            q.commit()
            q.close()
            with self.assertRaises(Exception):
                ledger.migration_guard.payload()


if __name__ == "__main__":
    unittest.main()
