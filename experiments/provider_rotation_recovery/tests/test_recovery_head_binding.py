import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_threshold_rotation.protocol import (
    DurableRotationAuthority,
    RotationAuthority,
    Signature,
    key_id,
    mac,
)
from experiments.provider_rotation_recovery.protocol import (
    DurableRecoveryController,
    RecoveryAuthority,
    RecoveryAuthorityMismatch,
)


def rotation_authority(version=1, generation=1, prefix="rot"):
    raw = [f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return RotationAuthority(
        "provider-rotation",
        version,
        generation,
        2,
        {key_id(k): k.hex() for k in raw},
    )


def recovery_authority(generation=1):
    raw = [f"recovery-{generation}-{i}".encode() for i in range(4)]
    return (
        RecoveryAuthority(
            "provider-rotation-recovery",
            generation,
            3,
            {key_id(k): k.hex() for k in raw},
        ),
        raw,
    )


def signatures(raw, payload):
    return tuple(Signature(key_id(k), mac(k, payload)) for k in raw[:3])


class RecoveryHeadBindingTests(unittest.TestCase):
    def test_unheaded_recovery_authority_cannot_authorize_persisted_transition(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            old = rotation_authority()
            bootstrap, _ = recovery_authority(1)
            attacker, attacker_raw = recovery_authority(2)
            new = rotation_authority(2, 2, "new")

            store = DurableRotationAuthority(path, old)
            controller = DurableRecoveryController(path, store, bootstrap)
            intent = controller.make_intent(old, new, attacker)
            attacker_signatures = signatures(attacker_raw, intent.payload)

            q = sqlite3.connect(path)
            controller._insert_recovery_locked(q, attacker)
            store._insert_authority_locked(q, new)
            q.execute(
                "INSERT INTO provider_rotation_recovery_transitions VALUES(?,?,?,?,?,?,?,?)",
                (
                    new.authority_id,
                    old.authority_id,
                    old.version,
                    old.generation,
                    attacker.authority_id,
                    attacker.generation,
                    intent.intent_digest,
                    controller._encode_signatures(attacker_signatures),
                ),
            )
            q.execute(
                "UPDATE provider_rotation_authority_head SET authority_id=?,version=?,generation=? WHERE singleton=1",
                (new.authority_id, new.version, new.generation),
            )
            q.commit()
            q.close()

            with self.assertRaises(RecoveryAuthorityMismatch):
                DurableRecoveryController(path, store, bootstrap)


if __name__ == "__main__":
    unittest.main()
