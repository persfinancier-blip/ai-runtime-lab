import shutil
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.archive_scavenging.protocol import (
    ArchiveScavenger,
    CandidateBecameReachable,
    StaleRetentionGeneration,
)
from experiments.namespace_reacquisition.integration import NamespaceAuthorityUnavailable
from experiments.signed_history_compaction.protocol import (
    SignedPrunableHistory,
    UnknownOutcome,
)
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class SignedCompactionIntegrationTests(unittest.TestCase):
    def layer(self, builder, archive_dir):
        return SignedPrunableHistory(
            builder.store,
            archive_dir,
            checkpoint_key=b"cp-key",
            external_anchor_id="anchor-A",
        )

    def age(self, scavenger, generations=2):
        for _ in range(generations):
            scavenger.advance_generation()

    def test_real_fail_after_archive_orphan_is_reclaimed(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(5)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome):
                layer.compact(checkpoint, fail_after_archive=True)

            scavenger = ArchiveScavenger(layer, grace_generations=2)
            candidates = scavenger.scan()
            self.assertEqual(len(candidates), 1)
            candidate = candidates[0]
            artifact, manifest = layer._archive_paths(candidate.archive_id)
            self.assertTrue(artifact.exists() and manifest.exists())
            self.assertEqual(layer.live_transition_count(), 5)

            self.age(scavenger, 2)
            self.assertEqual(scavenger.delete_candidate(candidate), "DELETED")
            self.assertFalse(artifact.exists() or manifest.exists())
            self.assertEqual(layer.verify_restart()["sequence"], 5)

    def test_real_timeout_after_commit_archive_is_never_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(5)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome):
                layer.compact(checkpoint, timeout_after_commit=True)

            scavenger = ArchiveScavenger(layer, grace_generations=1)
            self.age(scavenger, 3)
            self.assertEqual(scavenger.scan(), ())
            self.assertEqual(layer.live_transition_count(), 0)
            self.assertEqual(layer.verify_restart()["sequence"], 5)

    def test_real_multi_archive_chain_is_fully_reachable(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            layer = self.layer(builder, td / "archives")
            first = layer.compact(layer.create_checkpoint())
            builder.append(4)
            second = layer.compact(layer.create_checkpoint())

            scavenger = ArchiveScavenger(layer, grace_generations=1)
            self.age(scavenger, 4)
            self.assertEqual(scavenger.scan(), ())
            for archive_id in (first.archive_id, second.archive_id):
                self.assertTrue(all(path.exists() for path in layer._archive_paths(archive_id)))
                self.assertGreater(layer.audit_archive(archive_id)["rows_verified"], 0)

    def test_scavenger_refuses_replaced_namespace_even_after_initial_reacquisition(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(5)
            archive = td / "archives"
            layer = self.layer(builder, archive)
            checkpoint = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome):
                layer.compact(checkpoint, fail_after_archive=True)
            scavenger = ArchiveScavenger(layer, grace_generations=1)
            self.assertEqual(len(scavenger.scan()), 1)

            old = td / "old-archives"
            archive.rename(old)
            shutil.copytree(old, archive)
            with self.assertRaises(NamespaceAuthorityUnavailable):
                scavenger.scan()
            self.age(scavenger, 2)
            candidate_rows = []
            q = layer.store._con()
            try:
                candidate_rows = q.execute(
                    "SELECT archive_id,first_seen_generation,last_seen_generation "
                    "FROM archive_orphan_candidates"
                ).fetchall()
            finally:
                q.close()
            self.assertEqual(len(candidate_rows), 1)
            from experiments.archive_scavenging.protocol import Candidate
            candidate = Candidate(candidate_rows[0][0], candidate_rows[0][2], candidate_rows[0][1], True, True)
            with self.assertRaises(NamespaceAuthorityUnavailable):
                scavenger.delete_candidate(candidate)
            self.assertTrue(any(old.iterdir()))

    def test_real_compaction_gc_race_never_commits_missing_archive(self):
        """Either compaction wins and protects the archive, or GC wins and compaction fails closed."""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(6)
            layer = self.layer(builder, td / "archives")
            checkpoint = layer.create_checkpoint()
            with self.assertRaises(UnknownOutcome):
                layer.compact(checkpoint, fail_after_archive=True)

            scavenger = ArchiveScavenger(layer, grace_generations=1)
            candidate = scavenger.scan()[0]
            self.age(scavenger, 1)
            gate = threading.Barrier(3)
            outcomes = {}

            def compact_worker():
                gate.wait()
                try:
                    manifest = layer.compact(checkpoint)
                    outcomes["compact"] = ("ok", manifest.archive_id)
                except Exception as exc:
                    outcomes["compact"] = (type(exc).__name__, str(exc))

            def gc_worker():
                gate.wait()
                try:
                    outcomes["gc"] = ("ok", scavenger.delete_candidate(candidate))
                except (CandidateBecameReachable, StaleRetentionGeneration) as exc:
                    outcomes["gc"] = (type(exc).__name__, str(exc))
                except Exception as exc:
                    outcomes["gc"] = (type(exc).__name__, str(exc))

            threads = [threading.Thread(target=compact_worker), threading.Thread(target=gc_worker)]
            for thread in threads:
                thread.start()
            gate.wait()
            for thread in threads:
                thread.join(10)
                self.assertFalse(thread.is_alive(), "compaction/GC race deadlocked")

            # The authoritative invariant is stronger than either thread's return value.
            result = layer.verify_restart()
            self.assertEqual(result["sequence"], 6)
            q = layer.store._con()
            try:
                base_archive_id = q.execute(
                    "SELECT archive_id FROM signed_compaction_base WHERE singleton=1"
                ).fetchone()[0]
            finally:
                q.close()
            if base_archive_id is not None:
                artifact, manifest = layer._archive_paths(base_archive_id)
                self.assertTrue(artifact.exists() and manifest.exists())
                self.assertEqual(scavenger.scan(), ())
                self.assertEqual(layer.audit_archive(base_archive_id)["end_sequence"], 6)
            else:
                # GC may win before compaction's commit boundary; that is safe because
                # the full signed history remains live and restartable.
                self.assertEqual(layer.live_transition_count(), 6)


if __name__ == "__main__":
    unittest.main()
