import json, sqlite3, tempfile, unittest
from dataclasses import replace
from pathlib import Path

from experiments.transition_history_pruning.protocol import (
    ArchiveError, AuthenticationError, HeadMismatch, IntegrityError, PrunableHistory,
    StaleCheckpoint, UnknownOutcome, UnsafeDeleteFirst, sha
)

def aid(label):
    return sha(label.encode())

class Builder:
    def __init__(self,root):
        self.db=Path(root)/"db.sqlite"; self.archives=Path(root)/"archives"
        self.h=PrunableHistory(self.db,self.archives,checkpoint_key=b"k",external_anchor_id="anchor-A")
        self.root=aid("root-0"); self.rec=aid("rec-0"); self.h.initialize(self.root,self.rec); self.i=0
    def append(self,n=1):
        for _ in range(n):
            self.i+=1
            if self.i%2:
                self.rec=aid(f"rec-{self.i}")
                self.h.append(f"p-{self.i}","rotate_recovery",self.root,self.rec)
            else:
                self.root=aid(f"root-{self.i}")
                self.h.append(f"p-{self.i}","recover_root",self.root,self.rec)
        return self

class Tests(unittest.TestCase):
    def test_compacted_restart_equals_preprune_terminal_state(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(10)
            before=b.h.verify_restart()
            cp=b.h.create_checkpoint(); m=b.h.compact(cp)
            after=b.h.verify_restart()
            self.assertEqual((before["root_id"],before["recovery_id"],before["sequence"]),
                             (after["root_id"],after["recovery_id"],after["sequence"]))
            self.assertEqual(after["base_sequence"],10)
            self.assertEqual(b.h.live_transition_count(),0)
            self.assertEqual(b.h.audit_archive(m.archive_id)["rows_verified"],10)

    def test_live_storage_tracks_suffix_not_total_history(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(25); cp=b.h.create_checkpoint(); b.h.compact(cp)
            b.append(3)
            self.assertEqual(b.h.live_transition_count(),3)
            self.assertEqual(b.h.verify_restart()["sequence"],28)

    def test_new_transitions_and_second_compaction(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(8); m1=b.h.compact(b.h.create_checkpoint())
            b.append(5); cp2=b.h.create_checkpoint(); m2=b.h.compact(cp2)
            self.assertEqual(m2.previous_archive_id,m1.archive_id)
            self.assertEqual(m2.start_sequence,9); self.assertEqual(m2.end_sequence,13)
            self.assertEqual(b.h.live_transition_count(),0)
            b.append(2)
            self.assertEqual(b.h.verify_restart()["sequence"],15)
            self.assertEqual(b.h.live_transition_count(),2)
            self.assertEqual(b.h.audit_archive(m1.archive_id)["rows_verified"],8)
            self.assertEqual(b.h.audit_archive(m2.archive_id)["rows_verified"],5)

    def test_archive_export_then_crash_leaves_preprune_live_state(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(6); cp=b.h.create_checkpoint()
            with self.assertRaises(UnknownOutcome): b.h.compact(cp,fail_after_archive=True)
            self.assertEqual(b.h.verify_restart()["base_sequence"],0)
            self.assertEqual(b.h.live_transition_count(),6)

    def test_crash_inside_prune_transaction_rolls_back(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(6); cp=b.h.create_checkpoint()
            with self.assertRaises(UnknownOutcome): b.h.compact(cp,fail_before_commit=True)
            self.assertEqual(b.h.verify_restart()["base_sequence"],0)
            self.assertEqual(b.h.live_transition_count(),6)
            q=sqlite3.connect(b.db)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM archives").fetchone()[0],0)
            q.close()

    def test_timeout_after_commit_is_valid_postprune_state(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(6); cp=b.h.create_checkpoint()
            with self.assertRaises(UnknownOutcome): b.h.compact(cp,timeout_after_commit=True)
            out=b.h.verify_restart()
            self.assertEqual(out["base_sequence"],6)
            self.assertEqual(b.h.live_transition_count(),0)

    def test_stale_checkpoint_cannot_authorize_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); old=b.h.create_checkpoint()
            b.append(2); b.h.create_checkpoint()
            with self.assertRaises(StaleCheckpoint): b.h.compact(old)
            self.assertEqual(b.h.live_transition_count(),6)

    def test_missing_archive_manifest_rejects_restart(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); m=b.h.compact(b.h.create_checkpoint())
            q=sqlite3.connect(b.db); q.execute("DELETE FROM archives WHERE archive_id=?",(m.archive_id,)); q.commit(); q.close()
            with self.assertRaises(ArchiveError): b.h.verify_restart()

    def test_archive_file_tamper_fails_forensic_audit_but_not_restart(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); m=b.h.compact(b.h.create_checkpoint())
            artifact=b.archives/f"{m.archive_id}.json"
            artifact.write_bytes(artifact.read_bytes()+b"x")
            self.assertEqual(b.h.verify_restart()["sequence"],4)
            with self.assertRaises(ArchiveError): b.h.audit_archive(m.archive_id)

    def test_archive_manifest_substitution_fails_forensic_audit(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); m=b.h.compact(b.h.create_checkpoint())
            p=b.archives/f"{m.archive_id}.manifest.json"
            raw=json.loads(p.read_text()); raw["end_root_id"]=aid("evil"); p.write_text(json.dumps(raw))
            with self.assertRaises(ArchiveError): b.h.audit_archive(m.archive_id)

    def test_retained_suffix_gap_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(6); b.h.compact(b.h.create_checkpoint()); b.append(3)
            q=sqlite3.connect(b.db); q.execute("DELETE FROM transitions WHERE sequence=8"); q.commit(); q.close()
            with self.assertRaises(IntegrityError): b.h.verify_restart()

    def test_head_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(6); b.h.compact(b.h.create_checkpoint()); b.append(2)
            q=sqlite3.connect(b.db); q.execute("UPDATE head SET sequence=99"); q.commit(); q.close()
            with self.assertRaises((IntegrityError,HeadMismatch)): b.h.verify_restart()

    def test_tampered_base_checkpoint_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); b.h.compact(b.h.create_checkpoint())
            q=sqlite3.connect(b.db)
            checkpoint_id=q.execute("SELECT checkpoint_id FROM compaction_base WHERE singleton=1").fetchone()[0]
            raw=json.loads(q.execute("SELECT body_json FROM compact_checkpoints WHERE checkpoint_id=?",(checkpoint_id,)).fetchone()[0])
            raw["signature"]="00"*32
            q.execute("UPDATE compact_checkpoints SET body_json=? WHERE checkpoint_id=?",
                      (json.dumps(raw,sort_keys=True,separators=(",",":")),checkpoint_id))
            q.commit(); q.close()
            with self.assertRaises(AuthenticationError): b.h.verify_restart()

    def test_wrong_history_identity_in_archive_manifest_fails(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); m=b.h.compact(b.h.create_checkpoint())
            q=sqlite3.connect(b.db)
            raw=json.loads(q.execute("SELECT manifest_json FROM archives WHERE archive_id=?",(m.archive_id,)).fetchone()[0])
            raw["history_id"]=aid("other-history")
            q.execute("UPDATE archives SET manifest_json=? WHERE archive_id=?",(json.dumps(raw,sort_keys=True,separators=(",",":")),m.archive_id))
            q.commit(); q.close()
            with self.assertRaises(ArchiveError): b.h.verify_restart()

    def test_checkpoint_substitution_fails_before_prune(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(4); cp=b.h.create_checkpoint()
            bad=replace(cp,root_id=aid("evil"))
            with self.assertRaises(AuthenticationError): b.h.compact(bad)
            self.assertEqual(b.h.live_transition_count(),4)

    def test_unsafe_delete_before_archive_destroys_restartability(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(5)
            UnsafeDeleteFirst().prune(b.db,3)
            with self.assertRaises(IntegrityError): b.h.verify_restart()

if __name__=="__main__": unittest.main()
