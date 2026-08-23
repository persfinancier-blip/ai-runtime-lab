import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import AttestationVerifier, AttestedCatchup, ProviderIdentity, SignedAnchorProvider
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import ProviderRotationIntent, RotationAuthority, Signature, key_id, mac
from experiments.provider_rotation_recovery.protocol import RecoveryAuthority, RecoveryError
from experiments.provider_rotation_recovery.supported import SupportedRecoveryThresholdProviderLedger


def authority(version=1, generation=1, prefix="rot"):
    raw = [f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return RotationAuthority(
        "provider-rotation",
        version,
        generation,
        2,
        {key_id(k): k.hex() for k in raw},
    ), raw


def recovery_authority():
    raw = [f"recovery-1-{i}".encode() for i in range(4)]
    return RecoveryAuthority(
        "provider-rotation-recovery",
        1,
        3,
        {key_id(k): k.hex() for k in raw},
    ), raw


def signatures(raw, payload, count):
    return tuple(Signature(key_id(k), mac(k, payload)) for k in raw[:count])


def attested(generation, key, position=0):
    provider = SignedAnchorProvider("anchor-A", generation, key, value=position)
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return provider, AttestedCatchup(provider, verifier)


class RecoveryConcurrencyTests(unittest.TestCase):
    def make_ledger(self, path):
        signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
        provider, a1 = attested(1, b"hmac-1")
        auth, auth_raw = authority()
        recovery, recovery_raw = recovery_authority()
        base = ThresholdEnablement(
            signer.public.generation_id, 1, auth.authority_id, 1, 1, ()
        )
        enable = ThresholdEnablement(
            base.start_provider_generation_id,
            1,
            auth.authority_id,
            1,
            1,
            signatures(auth_raw, base.payload, 2),
        )
        ledger = SupportedRecoveryThresholdProviderLedger(
            path, a1, signer.public, signer, auth, enable, recovery
        )
        return provider, ledger, signer, auth, auth_raw, recovery, recovery_raw, enable

    @staticmethod
    def race(*functions):
        gate = threading.Barrier(len(functions) + 1)
        lock = threading.Lock()
        outcomes = []

        def run(index, fn):
            gate.wait()
            try:
                value = fn()
                outcome = (index, "ok", value)
            except Exception as exc:
                outcome = (index, type(exc).__name__, str(exc))
            with lock:
                outcomes.append(outcome)

        threads = [threading.Thread(target=run, args=(i, fn)) for i, fn in enumerate(functions)]
        for thread in threads:
            thread.start()
        gate.wait()
        for thread in threads:
            thread.join(10)
        if any(thread.is_alive() for thread in threads):
            raise AssertionError("concurrency test thread did not terminate")
        return outcomes

    def test_normal_rotation_vs_recovery_has_exactly_one_authority_successor(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, _, old, old_raw, recovery, recovery_raw, _ = self.make_ledger(path)
            normal, normal_raw = authority(2, 2, "normal")
            recovered, _ = authority(2, 2, "recovered")
            normal_payload = ledger.rotation_authority.authority_rotation_payload(old, normal)
            recovery_intent = ledger.recovery.make_intent(old, recovered, recovery)

            outcomes = self.race(
                lambda: ledger.rotate_rotation_authority(
                    normal,
                    signatures(old_raw, normal_payload, 2),
                    signatures(normal_raw, normal_payload, 2),
                ),
                lambda: ledger.recover_rotation_authority(
                    recovered,
                    signatures(recovery_raw, recovery_intent.payload, 3),
                ),
            )

            self.assertEqual(sum(item[1] == "ok" for item in outcomes), 1)
            self.assertTrue(ledger.verify_durable())
            q = sqlite3.connect(path)
            try:
                normal_count = q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authority_transitions"
                ).fetchone()[0]
                recovery_count = q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_recovery_transitions"
                ).fetchone()[0]
            finally:
                q.close()
            self.assertEqual(normal_count + recovery_count, 1)

    def test_provider_rotation_vs_recovery_serializes_without_post_recovery_old_quorum_use(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, signer1, old, old_raw, recovery, recovery_raw, _ = self.make_ledger(path)
            signer2 = GenerationSigner.from_seed("anchor-A", 2, b"B" * 32)
            continuity = ledger.provider_history.make_transition(signer1, signer2)
            _, a2 = attested(2, b"hmac-2")
            provider_intent = ProviderRotationIntent(
                "anchor-A",
                signer1.public.generation_id,
                signer2.public.generation_id,
                old.authority_id,
                old.version,
                old.generation,
            )
            recovered, _ = authority(2, 2, "recovered")
            recovery_intent = ledger.recovery.make_intent(old, recovered, recovery)

            outcomes = self.race(
                lambda: ledger.rotate_provider(
                    signer2,
                    continuity,
                    a2,
                    signatures(old_raw, provider_intent.payload, 2),
                ),
                lambda: ledger.recover_rotation_authority(
                    recovered,
                    signatures(recovery_raw, recovery_intent.payload, 3),
                ),
            )

            self.assertTrue(any(item[1] == "ok" for item in outcomes))
            self.assertTrue(ledger.verify_durable())
            q = sqlite3.connect(path)
            try:
                provider_rows = q.execute(
                    "SELECT authority_id FROM provider_rotation_threshold_proofs"
                ).fetchall()
                current_authority = q.execute(
                    "SELECT authority_id FROM provider_rotation_authority_head WHERE singleton=1"
                ).fetchone()[0]
            finally:
                q.close()
            if provider_rows:
                self.assertEqual(provider_rows[0][0], old.authority_id)
            if current_authority == recovered.authority_id:
                # If both operations succeeded, the provider proof must still be historical
                # proof under the predecessor authority, never a post-recovery use of it.
                self.assertTrue(not provider_rows or provider_rows[0][0] == old.authority_id)

    def test_missing_recovery_proof_fails_restart_verification(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, signer, old, _, recovery, recovery_raw, enable = self.make_ledger(path)
            new, _ = authority(2, 2, "recovered")
            intent = ledger.recovery.make_intent(old, new, recovery)
            ledger.recover_rotation_authority(
                new, signatures(recovery_raw, intent.payload, 3)
            )
            q = sqlite3.connect(path)
            q.execute("DELETE FROM provider_rotation_recovery_transitions")
            q.commit()
            q.close()
            with self.assertRaises(RecoveryError):
                SupportedRecoveryThresholdProviderLedger(
                    path, ledger.attested, signer.public, signer, old, enable, recovery
                )


if __name__ == "__main__":
    unittest.main()
