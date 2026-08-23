import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path

from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_recovery_authority_lifecycle.final_supported import SupportedRecoveryCustodyLedger
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
    authority,
    public_recovery,
    recovery,
    signatures,
)


class FinalSupportedCustodyTests(unittest.TestCase):
    def make_ledger(self, path):
        signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
        _, a1 = attested(1, b"hmac-1")
        root, root_raw = authority()
        rec, rec_raw = recovery()
        public, public_signers = public_recovery()
        base = ThresholdEnablement(signer.public.generation_id, 1, root.authority_id, 1, 1, ())
        enable = ThresholdEnablement(
            base.start_provider_generation_id,
            1,
            root.authority_id,
            1,
            1,
            signatures(root_raw, base.payload, 2),
        )
        ledger = SupportedRecoveryCustodyLedger(
            path, a1, signer.public, signer, root, enable, rec.recovery, public
        )
        return ledger, signer, root, rec, public, enable

    def test_final_supported_surface_restarts_with_bound_heads(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer, root, rec, public, enable = self.make_ledger(path)
            self.assertTrue(ledger.verify_durable())
            restarted = SupportedRecoveryCustodyLedger(
                path, ledger.attested, signer.public, signer, root, enable, rec.recovery, public
            )
            self.assertTrue(restarted.verify_durable())

    def test_final_verification_holds_write_excluding_barrier(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *_ = self.make_ledger(path)
            entered = threading.Event()
            writer_done = threading.Event()
            observed_writer_during_verify = []
            original = ledger._verify_custody_bindings_locked

            def wrapped(q):
                entered.set()
                time.sleep(0.15)
                observed_writer_during_verify.append(writer_done.is_set())
                return original(q)

            ledger._verify_custody_bindings_locked = wrapped

            def writer():
                entered.wait(2)
                q = sqlite3.connect(path, timeout=5)
                try:
                    q.execute("BEGIN IMMEDIATE")
                    q.execute(
                        "UPDATE provider_recovery_custody_bindings SET generation=generation"
                    )
                    q.commit()
                finally:
                    q.close()
                writer_done.set()

            thread = threading.Thread(target=writer)
            thread.start()
            self.assertTrue(ledger.verify_durable())
            thread.join(5)
            self.assertFalse(any(observed_writer_during_verify))
            self.assertTrue(writer_done.is_set())


if __name__ == "__main__":
    unittest.main()
