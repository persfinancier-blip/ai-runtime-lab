import json
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from experiments.transition_history_checkpoints.protocol import (
    CheckpointAuthenticationError,
    CheckpointHeadMismatch,
    CheckpointRollbackError,
    CheckpointSubstitutionError,
    CheckpointedHistory,
    HistoryCheckpoint,
    SuffixIntegrityError,
    UnsafeCheckpointCache,
)
from experiments.transition_history_integrity.protocol import (
    Authority,
    HistoryStore,
    Proposal,
    Sig,
    ThresholdError,
    kid,
    recovery_payload,
    rotation_payload,
    sign,
)


def authority(kind, version, generation, prefix, n=3, threshold=2):
    raw = [f"{prefix}-{i}".encode() for i in range(n)]
    return Authority(kind, version, generation, threshold, {kid(k): k.hex() for k in raw}), raw


def sigs(keys, payload, n=2):
    return tuple(Sig(kid(k), sign(k, payload)) for k in keys[:n])


class ChainBuilder:
    def __init__(self, path: Path, seed="A"):
        self.bootstrap_root, self.root_keys = authority("root", 1, 1, f"{seed}-root-1")
        self.bootstrap_recovery, self.recovery_keys = authority("recovery", 1, 1, f"{seed}-recovery-1")
        self.root = self.bootstrap_root
        self.recovery = self.bootstrap_recovery
        self.store = HistoryStore(path, self.bootstrap_root, self.bootstrap_recovery)
        self.index = 0

    def append(self, count=1):
        for _ in range(count):
            self.index += 1
            if self.index % 2:
                new_recovery, new_keys = authority(
                    "recovery",
                    self.recovery.version + 1,
                    self.recovery.generation + 1,
                    f"recovery-{self.index + 1}",
                )
                payload = rotation_payload(self.root, self.recovery, new_recovery)
                proposal = Proposal(
                    f"p-{self.index}",
                    "rotate_recovery",
                    self.root.authority_id,
                    self.recovery.authority_id,
                    new_recovery,
                    sigs(self.recovery_keys, payload),
                    sigs(new_keys, payload),
                    sigs(self.root_keys, payload),
                )
                self.store.commit(proposal)
                self.recovery, self.recovery_keys = new_recovery, new_keys
            else:
                new_root, new_keys = authority(
                    "root",
                    self.root.version + 1,
                    self.root.generation + 1,
                    f"root-{self.index + 1}",
                )
                payload = recovery_payload(self.root, new_root, self.recovery)
                proposal = Proposal(
                    f"p-{self.index}",
                    "recover_root",
                    self.root.authority_id,
                    self.recovery.authority_id,
                    new_root,
                    sigs(self.recovery_keys, payload),
                )
                self.store.commit(proposal)
                self.root, self.root_keys = new_root, new_keys
        return self

    def checkpointed(self, key=b"checkpoint-key", anchor="anchor-A"):
        return CheckpointedHistory(self.store, checkpoint_key=key, external_anchor_id=anchor)


class Tests(unittest.TestCase):
    def test_full_replay_and_checkpoint_suffix_converge(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(8)
            layer = b.checkpointed()
            cp = layer.create_checkpoint()
            b.append(4)
            full = b.store.verify_history()
            resumed = layer.verify_suffix(cp)
            self.assertEqual(
                (full["root_id"], full["recovery_id"], full["sequence"]),
                (resumed["root_id"], resumed["recovery_id"], resumed["sequence"]),
            )
            self.assertEqual(resumed["suffix_transitions_verified"], 4)

    def test_restart_work_is_suffix_length_not_prefix_length(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(30)
            layer = b.checkpointed()
            cp = layer.create_checkpoint()
            b.append(3)
            restarted = b.checkpointed()
            resumed = restarted.verify_suffix(restarted.latest_checkpoint())
            self.assertEqual(cp.sequence, 30)
            self.assertEqual(resumed["sequence"], 33)
            self.assertEqual(resumed["suffix_transitions_verified"], 3)

    def test_checkpoint_created_only_after_full_verified_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(4)
            q = sqlite3.connect(path)
            raw = json.loads(q.execute("SELECT proof_json FROM transitions WHERE sequence=2").fetchone()[0])
            raw["sig1"][0]["signature"] = "00" * 32
            q.execute(
                "UPDATE transitions SET proof_json=? WHERE sequence=2",
                (json.dumps(raw, sort_keys=True, separators=(",", ":")),),
            )
            q.commit(); q.close()
            with self.assertRaises(ThresholdError):
                b.checkpointed().create_checkpoint()

    def test_tampered_checkpoint_signature_fails(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(4)
            layer = b.checkpointed(); cp = layer.create_checkpoint()
            bad = replace(cp, root_id="evil")
            with self.assertRaises(CheckpointAuthenticationError):
                layer.verify_checkpoint(bad)

    def test_checkpoint_from_other_history_fails(self):
        with tempfile.TemporaryDirectory() as td:
            a = ChainBuilder(Path(td) / "a", seed="A").append(4)
            b = ChainBuilder(Path(td) / "b", seed="B").append(4)
            cp = a.checkpointed(key=b"shared", anchor="anchor").create_checkpoint()
            other = b.checkpointed(key=b"shared", anchor="anchor")
            q = b.store._con()
            try:
                q.execute(
                    "INSERT INTO history_checkpoints VALUES(?,?,?)",
                    (cp.checkpoint_id, cp.sequence, json.dumps(cp.__dict__, sort_keys=True, separators=(",", ":"))),
                )
                q.execute("INSERT INTO checkpoint_watermark VALUES(1,?,?)", (cp.sequence, cp.checkpoint_id))
            finally:
                q.close()
            with self.assertRaises(CheckpointSubstitutionError):
                other.verify_checkpoint(cp)

    def test_old_checkpoint_rejected_after_newer_watermark(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(4)
            layer = b.checkpointed(); old = layer.create_checkpoint()
            b.append(4); new = layer.create_checkpoint()
            self.assertGreater(new.sequence, old.sequence)
            with self.assertRaises(CheckpointRollbackError):
                layer.verify_checkpoint(old)

    def test_skipped_suffix_transition_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(6)
            layer = b.checkpointed(); cp = layer.create_checkpoint(); b.append(4)
            q = sqlite3.connect(path); q.execute("DELETE FROM transitions WHERE sequence=8"); q.commit(); q.close()
            with self.assertRaises(SuffixIntegrityError):
                layer.verify_suffix(cp)

    def test_head_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(6)
            layer = b.checkpointed(); cp = layer.create_checkpoint(); b.append(2)
            q = sqlite3.connect(path); q.execute("UPDATE head SET sequence=99"); q.commit(); q.close()
            with self.assertRaises(CheckpointHeadMismatch):
                layer.verify_suffix(cp)

    def test_tampered_checkpoint_row_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(4)
            layer = b.checkpointed(); cp = layer.create_checkpoint()
            q = sqlite3.connect(path)
            raw = json.loads(q.execute("SELECT body_json FROM history_checkpoints WHERE checkpoint_id=?", (cp.checkpoint_id,)).fetchone()[0])
            raw["prefix_commitment"] = "f" * 64
            q.execute(
                "UPDATE history_checkpoints SET body_json=? WHERE checkpoint_id=?",
                (json.dumps(raw, sort_keys=True, separators=(",", ":")), cp.checkpoint_id),
            )
            q.commit(); q.close()
            with self.assertRaises(CheckpointSubstitutionError):
                layer.verify_checkpoint(cp)

    def test_external_anchor_identity_is_bound(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(4)
            layer = b.checkpointed(key=b"k", anchor="anchor-A"); cp = layer.create_checkpoint()
            wrong = b.checkpointed(key=b"k", anchor="anchor-B")
            with self.assertRaises(CheckpointSubstitutionError):
                wrong.verify_checkpoint(cp)

    def test_strict_schema_rejects_bool_sequence(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(2); cp = b.checkpointed().create_checkpoint()
            raw = dict(cp.__dict__); raw["sequence"] = True
            with self.assertRaises(CheckpointAuthenticationError):
                HistoryCheckpoint.from_json(raw)

    def test_archived_prefix_tamper_detected_by_explicit_audit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(6)
            layer = b.checkpointed(); cp = layer.create_checkpoint(); b.append(2)
            q = sqlite3.connect(path)
            raw = json.loads(q.execute("SELECT proof_json FROM transitions WHERE sequence=2").fetchone()[0])
            raw["sig1"][0]["signature"] = "ab" * 32
            q.execute(
                "UPDATE transitions SET proof_json=? WHERE sequence=2",
                (json.dumps(raw, sort_keys=True, separators=(",", ":")),),
            )
            q.commit(); q.close()
            self.assertEqual(layer.verify_suffix(cp)["suffix_transitions_verified"], 2)
            with self.assertRaises(CheckpointSubstitutionError):
                layer.audit_checkpoint_prefix(cp)

    def test_strict_schema_rejects_malformed_digest(self):
        with tempfile.TemporaryDirectory() as td:
            b = ChainBuilder(Path(td) / "db").append(2); cp = b.checkpointed().create_checkpoint()
            raw = dict(cp.__dict__); raw["history_id"] = "not-a-digest"
            with self.assertRaises(CheckpointAuthenticationError):
                HistoryCheckpoint.from_json(raw)

    def test_unsafe_cache_can_hide_broken_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(4)
            q = sqlite3.connect(path)
            row2 = q.execute("SELECT successor_root_id,successor_recovery_id FROM transitions WHERE sequence=2").fetchone()
            raw = json.loads(q.execute("SELECT proof_json FROM transitions WHERE sequence=1").fetchone()[0])
            raw["sig1"][0]["signature"] = "ee" * 32
            q.execute(
                "UPDATE transitions SET proof_json=? WHERE sequence=1",
                (json.dumps(raw, sort_keys=True, separators=(",", ":")),),
            )
            q.commit(); q.close()
            with self.assertRaises(ThresholdError):
                b.store.verify_history()
            unsafe = UnsafeCheckpointCache().resume(
                b.store, {"sequence": 2, "root_id": row2[0], "recovery_id": row2[1]}
            )
            self.assertEqual(unsafe["sequence"], 4)


if __name__ == "__main__":
    unittest.main()
