import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.signed_history_compaction.protocol import (
    ArchiveError,
    AuthenticationError,
    HeadMismatch,
    SignedPrunableHistory,
    UnknownOutcome,
    UnsafeDeleteFirst,
)
from experiments.transition_history_integrity.protocol import (
    Authority,
    HistoryStore,
    IntegrityError,
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
                    "recovery", self.recovery.version + 1, self.recovery.generation + 1,
                    f"recovery-{self.index + 1}"
                )
                payload = rotation_payload(self.root, self.recovery, new_recovery)
                proposal = Proposal(
                    f"p-{self.index}", "rotate_recovery", self.root.authority_id,
                    self.recovery.authority_id, new_recovery,
                    sigs(self.recovery_keys, payload), sigs(new_keys, payload), sigs(self.root_keys, payload)
                )
                self.store.commit(proposal)
                self.recovery, self.recovery_keys = new_recovery, new_keys
            else:
                new_root, new_keys = authority(
                    "root", self.root.version + 1, self.root.generation + 1,
                    f"root-{self.index + 1}"
                )
                payload = recovery_payload(self.root, new_root, self.recovery)
                proposal = Proposal(
                    f"p-{self.index}", "recover_root", self.root.authority_id,
                    self.recovery.authority_id, new_root, sigs(self.recovery_keys, payload)
                )
                self.store.commit(proposal)
                self.root, self.root_keys = new_root, new_keys
        return self


class Tests(unittest.TestCase):
    def layer(self, builder, archive_dir):
        return SignedPrunableHistory(builder.store, archive_dir, checkpoint_key=b"cp-key", external_anchor_id="anchor-A")

    def test_compacted_restart_equals_full_threshold_replay(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            compacted = ChainBuilder(td / "compacted.db").append(8)
            full = ChainBuilder(td / "full.db").append(8)
            layer = self.layer(compacted, td / "archives")
            cp = layer.create_checkpoint(); layer.compact(cp)
            compacted.append(4); full.append(4)
            expected = full.store.verify_history()
            actual = layer.verify_restart()
            self.assertEqual((actual["root_id"], actual["recovery_id"], actual["sequence"]),
                             (expected["root_id"], expected["recovery_id"], expected["sequence"]))
            self.assertEqual(actual["rows_verified"], 4)

    def test_live_rows_are_bounded_by_suffix(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(20); layer = self.layer(b, td / "a")
            layer.compact(layer.create_checkpoint())
            self.assertEqual(layer.live_transition_count(), 0)
            b.append(3)
            self.assertEqual(layer.live_transition_count(), 3)

    def test_retained_suffix_corrupted_threshold_signature_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            layer.compact(layer.create_checkpoint()); b.append(2)
            q = sqlite3.connect(td / "db")
            raw = json.loads(q.execute("SELECT proof_json FROM transitions WHERE sequence=5").fetchone()[0])
            raw["sig1"][0]["signature"] = "00" * 32
            q.execute("UPDATE transitions SET proof_json=? WHERE sequence=5", (json.dumps(raw, sort_keys=True, separators=(",", ":")),))
            q.commit(); q.close()
            with self.assertRaises(ThresholdError): layer.verify_restart()

    def test_archive_corrupted_signature_fails_forensic_audit(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            manifest = layer.compact(layer.create_checkpoint())
            artifact, _ = layer._archive_paths(manifest.archive_id)
            body = json.loads(artifact.read_text())
            proof = json.loads(body["rows"][0]["proof_json"])
            proof["sig1"][0]["signature"] = "11" * 32
            body["rows"][0]["proof_json"] = json.dumps(proof, sort_keys=True, separators=(",", ":"))
            artifact.write_bytes(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
            with self.assertRaises(ArchiveError): layer.audit_archive(manifest.archive_id)

    def test_archive_payload_or_digest_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            manifest = layer.compact(layer.create_checkpoint())
            artifact, _ = layer._archive_paths(manifest.archive_id)
            body = json.loads(artifact.read_text())
            body["rows"][1]["transition_digest"] = "f" * 64
            artifact.write_bytes(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
            with self.assertRaises(ArchiveError): layer.audit_archive(manifest.archive_id)

    def test_compacted_base_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            layer.compact(layer.create_checkpoint())
            q = sqlite3.connect(td / "db")
            q.execute("UPDATE signed_compaction_base SET root_id=?", ("f" * 64,)); q.commit(); q.close()
            with self.assertRaises(AuthenticationError): layer.verify_restart()

    def test_audit_rejects_manifest_start_state_substitution_even_with_rehashed_id(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            manifest = layer.compact(layer.create_checkpoint())
            q = sqlite3.connect(td / "db")
            raw = json.loads(q.execute("SELECT manifest_json FROM signed_archives WHERE archive_id=?", (manifest.archive_id,)).fetchone()[0])
            other_root = q.execute("SELECT authority_id FROM authorities WHERE authority_id<>? LIMIT 1", (raw["start_root_id"],)).fetchone()[0]
            raw["start_root_id"] = other_root
            old_id = raw.pop("archive_id")
            import hashlib
            new_id = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            raw["archive_id"] = new_id
            q.execute("DELETE FROM signed_archives WHERE archive_id=?", (old_id,))
            q.execute("INSERT INTO signed_archives VALUES(?,?,?)", (new_id, raw["end_sequence"], json.dumps(raw, sort_keys=True, separators=(",", ":"))))
            q.execute("UPDATE signed_compaction_base SET archive_id=?", (new_id,))
            q.commit(); q.close()
            with self.assertRaises(ArchiveError): layer.verify_restart()

    def test_archive_history_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            manifest = layer.compact(layer.create_checkpoint())
            q = sqlite3.connect(td / "db")
            raw = json.loads(q.execute("SELECT manifest_json FROM signed_archives WHERE archive_id=?", (manifest.archive_id,)).fetchone()[0])
            raw["history_id"] = "f" * 64
            q.execute("UPDATE signed_archives SET manifest_json=? WHERE archive_id=?", (json.dumps(raw, sort_keys=True, separators=(",", ":")), manifest.archive_id))
            q.commit(); q.close()
            with self.assertRaises(ArchiveError): layer.verify_restart()

    def test_retained_suffix_gap_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            layer.compact(layer.create_checkpoint()); b.append(3)
            q = sqlite3.connect(td / "db"); q.execute("DELETE FROM transitions WHERE sequence=6"); q.commit(); q.close()
            with self.assertRaises(IntegrityError): layer.verify_restart()

    def test_head_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(4); layer = self.layer(b, td / "a")
            layer.compact(layer.create_checkpoint()); b.append(2)
            q = sqlite3.connect(td / "db"); q.execute("UPDATE head SET sequence=99"); q.commit(); q.close()
            with self.assertRaises((HeadMismatch, IntegrityError)): layer.verify_restart()

    def test_failure_after_archive_before_sql_commit_keeps_preprune_state(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(5); layer = self.layer(b, td / "a"); cp = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome): layer.compact(cp, fail_after_archive=True)
            self.assertEqual(layer.live_transition_count(), 5)
            self.assertEqual(b.store.verify_history()["sequence"], 5)

    def test_failure_inside_prune_transaction_rolls_back(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(5); layer = self.layer(b, td / "a"); cp = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome): layer.compact(cp, fail_before_commit=True)
            self.assertEqual(layer.live_transition_count(), 5)
            self.assertEqual(layer.verify_restart()["sequence"], 5)

    def test_timeout_after_commit_reconciles_idempotently(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(5); layer = self.layer(b, td / "a"); cp = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome): layer.compact(cp, timeout_after_commit=True)
            self.assertEqual(layer.live_transition_count(), 0)
            manifest = layer.compact(cp)
            self.assertEqual(manifest.end_sequence, 5)
            self.assertEqual(layer.verify_restart()["sequence"], 5)

    def test_second_compaction_after_new_signed_transitions(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(6); layer = self.layer(b, td / "a")
            first = layer.compact(layer.create_checkpoint()); b.append(4)
            second_cp = layer.create_checkpoint(); second = layer.compact(second_cp)
            self.assertEqual(first.end_sequence, 6); self.assertEqual(second.end_sequence, 10)
            self.assertEqual(second.previous_archive_id, first.archive_id)
            self.assertEqual(layer.live_transition_count(), 0)
            self.assertEqual(layer.audit_archive(first.archive_id)["rows_verified"], 6)
            self.assertEqual(layer.audit_archive(second.archive_id)["rows_verified"], 4)
            self.assertEqual(layer.verify_restart()["sequence"], 10)

    def test_unsafe_delete_first_destroys_restartability(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td); b = ChainBuilder(td / "db").append(5); layer = self.layer(b, td / "a")
            UnsafeDeleteFirst().prune(td / "db", 3)
            with self.assertRaises(IntegrityError): layer.verify_restart()


if __name__ == "__main__":
    unittest.main()
