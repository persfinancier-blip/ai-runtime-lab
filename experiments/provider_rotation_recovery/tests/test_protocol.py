import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_threshold_rotation.protocol import (
    DurableRotationAuthority,
    RotationAuthority,
    Signature,
    ThresholdNotMet,
    key_id,
    mac,
)
from experiments.provider_rotation_recovery.protocol import (
    DurableRecoveryController,
    RecoveryAuthority,
    RecoveryProofSubstitution,
    StaleAuthority,
    UnsafeSelfAuthorizedRecovery,
)


def rotation_authority(version=1, generation=1, prefix="rot"):
    raw = [f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return (
        RotationAuthority(
            "provider-rotation",
            version,
            generation,
            2,
            {key_id(k): k.hex() for k in raw},
        ),
        raw,
    )


def recovery_authority(generation=1, revoked=()):
    raw = [f"recovery-{generation}-{i}".encode() for i in range(4)]
    return (
        RecoveryAuthority(
            "provider-rotation-recovery",
            generation,
            3,
            {key_id(k): k.hex() for k in raw},
            tuple(revoked),
        ),
        raw,
    )


def signatures(raw, payload, indexes):
    return tuple(Signature(key_id(raw[i]), mac(raw[i], payload)) for i in indexes)


class RecoveryTests(unittest.TestCase):
    def setup_store(self, td):
        path = Path(td) / "db"
        root, root_raw = rotation_authority()
        recovery, recovery_raw = recovery_authority()
        store = DurableRotationAuthority(path, root)
        controller = DurableRecoveryController(path, store, recovery)
        return path, store, controller, root, root_raw, recovery, recovery_raw

    def test_recovery_requires_separate_recovery_quorum(self):
        with tempfile.TemporaryDirectory() as td:
            _, store, controller, old, old_raw, recovery, recovery_raw = self.setup_store(td)
            new, _ = rotation_authority(2, 2, "new")
            intent = controller.make_intent(old, new, recovery)
            with self.assertRaises(ThresholdNotMet):
                controller.recover(new, ())
            normal = signatures(old_raw, intent.payload, [0, 1])
            with self.assertRaises(ThresholdNotMet):
                controller.recover(new, normal)
            self.assertEqual(store.current().authority_id, old.authority_id)

    def test_recovery_quorum_advances_authority(self):
        with tempfile.TemporaryDirectory() as td:
            _, store, controller, old, _, recovery, recovery_raw = self.setup_store(td)
            new, _ = rotation_authority(2, 2, "new")
            intent = controller.make_intent(old, new, recovery)
            out = controller.recover(new, signatures(recovery_raw, intent.payload, [0, 1, 2]))
            self.assertEqual(store.current().authority_id, new.authority_id)
            self.assertEqual(len(out["recovery_signers"]), 3)

    def test_duplicate_unknown_and_revoked_do_not_inflate_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            old, _ = rotation_authority()
            base, raw = recovery_authority()
            revoked = key_id(raw[0])
            recovery = RecoveryAuthority(
                base.name, base.generation, 3, base.keys, (revoked,)
            )
            store = DurableRotationAuthority(path, old)
            controller = DurableRecoveryController(path, store, recovery)
            new, _ = rotation_authority(2, 2, "new")
            intent = controller.make_intent(old, new, recovery)
            good1 = Signature(key_id(raw[1]), mac(raw[1], intent.payload))
            good2 = Signature(key_id(raw[2]), mac(raw[2], intent.payload))
            revoked_sig = Signature(key_id(raw[0]), mac(raw[0], intent.payload))
            unknown = Signature("unknown", "0" * 64)
            with self.assertRaises(ThresholdNotMet):
                controller.recover(
                    new, (good1, good1, good2, revoked_sig, unknown)
                )

    def test_stale_successor_generation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, controller, _, _, recovery, recovery_raw = self.setup_store(td)
            new, _ = rotation_authority(2, 3, "new")
            old = controller.rotation_store.current()
            intent = controller.make_intent(old, new, recovery)
            with self.assertRaises(StaleAuthority):
                controller.recover(
                    new, signatures(recovery_raw, intent.payload, [0, 1, 2])
                )

    def test_persisted_recovery_proof_reverified(self):
        with tempfile.TemporaryDirectory() as td:
            path, store, controller, old, _, recovery, recovery_raw = self.setup_store(td)
            new, _ = rotation_authority(2, 2, "new")
            intent = controller.make_intent(old, new, recovery)
            controller.recover(new, signatures(recovery_raw, intent.payload, [0, 1, 2]))
            q = sqlite3.connect(path)
            try:
                q.execute("BEGIN")
                self.assertTrue(controller.verify_recovery_transition_locked(q, old, new))
                q.commit()
            finally:
                q.close()

    def test_corrupted_recovery_digest_fails_restart_verification(self):
        with tempfile.TemporaryDirectory() as td:
            path, _, controller, old, _, recovery, recovery_raw = self.setup_store(td)
            new, _ = rotation_authority(2, 2, "new")
            intent = controller.make_intent(old, new, recovery)
            controller.recover(new, signatures(recovery_raw, intent.payload, [0, 1, 2]))
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_rotation_recovery_transitions SET intent_digest=?",
                ("0" * 64,),
            )
            q.commit()
            with self.assertRaises(RecoveryProofSubstitution):
                controller.verify_recovery_transition_locked(q, old, new)
            q.close()

    def test_restart_reverifies_recovery_bootstrap_and_proof(self):
        with tempfile.TemporaryDirectory() as td:
            path, store, controller, old, _, recovery, recovery_raw = self.setup_store(td)
            new, _ = rotation_authority(2, 2, "new")
            intent = controller.make_intent(old, new, recovery)
            controller.recover(new, signatures(recovery_raw, intent.payload, [0, 1, 2]))
            restarted = DurableRecoveryController(path, store, recovery)
            self.assertTrue(restarted.verify_durable())

    def test_recovery_head_substitution_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path, store, controller, _, _, recovery, _ = self.setup_store(td)
            other, _ = recovery_authority(generation=2)
            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_rotation_recovery_authorities VALUES(?,?,?,?,?,?)",
                (
                    other.authority_id,
                    other.name,
                    other.generation,
                    other.threshold,
                    __import__("json").dumps(other.keys, sort_keys=True, separators=(",", ":")),
                    __import__("json").dumps(sorted(other.revoked), separators=(",", ":")),
                ),
            )
            q.execute(
                "UPDATE provider_rotation_recovery_head SET authority_id=?,generation=? WHERE singleton=1",
                (other.authority_id, other.generation),
            )
            q.commit()
            q.close()
            with self.assertRaises(Exception):
                DurableRecoveryController(path, store, recovery)

    def test_unsafe_normal_quorum_self_recovery_baseline(self):
        self.assertTrue(UnsafeSelfAuthorizedRecovery.allows(True))


if __name__ == "__main__":
    unittest.main()
