import os
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from experiments.archive_scavenging.protocol import ArchiveScavenger
from experiments.namespace_reacquisition.protocol import issue_migration
from experiments.namespace_retirement.integration import (
    RetirementIntegrationError,
    SimulatedRetirementCrash,
)
from experiments.namespace_retirement.protocol import (
    CurrentGenerationProtected,
    NamespaceReplacementDetected,
    StalePermit,
    StrongReacquisitionUnavailable,
)
from experiments.signed_history_compaction.protocol import SignedPrunableHistory
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder


class SignedNamespaceRetirementIntegrationTests(unittest.TestCase):
    def layer(self, builder, archive_dir, cls=SignedPrunableHistory):
        return cls(
            builder.store,
            archive_dir,
            checkpoint_key=b"cp-key",
            external_anchor_id="anchor-A",
        )

    def migrated(self, td, *, compact_first=True):
        td = Path(td)
        builder = ChainBuilder(td / "db").append(4)
        old_dir = td / "archives-v1"
        new_dir = td / "archives-v2"
        new_dir.mkdir()
        layer = self.layer(builder, old_dir)
        first = None
        if compact_first:
            first = layer.compact(layer.create_checkpoint())
        old_record = layer.require_namespace_authority()
        permit = issue_migration(old_record, new_dir, 2, layer.key)
        new_record = layer.migrate_archive_namespace(permit)
        return builder, layer, old_dir, new_dir, old_record, new_record, first

    def test_real_retirement_audits_successor_and_reclaims_only_old_files(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            self.assertIsNotNone(first)
            self.assertTrue(all(p.exists() for p in (old_dir / f"{first.archive_id}.json", old_dir / f"{first.archive_id}.manifest.json")))
            self.assertTrue(all(p.exists() for p in (new_dir / f"{first.archive_id}.json", new_dir / f"{first.archive_id}.manifest.json")))
            permit = layer.issue_namespace_retirement_permit()
            receipt = layer.retire_superseded_namespace(permit)
            self.assertEqual(receipt.status, "RETIRED")
            self.assertEqual(receipt.target_record_id, old.record_id)
            self.assertFalse(any(old_dir.iterdir()))
            self.assertGreater(layer.audit_archive(first.archive_id)["rows_verified"], 0)
            self.assertTrue(all(p.exists() for p in (new_dir / f"{first.archive_id}.json", new_dir / f"{first.archive_id}.manifest.json")))
            self.assertEqual(layer.verify_restart()["sequence"], 4)

    def test_restart_preserves_lineage_and_retirement_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            receipt1 = layer.retire_superseded_namespace(permit)
            restarted = self.layer(builder, new_dir)
            receipt2 = restarted.retire_superseded_namespace(permit)
            self.assertEqual(receipt2, receipt1)
            self.assertEqual(restarted.namespace_generation, 2)

    def test_crash_after_continuity_cas_reconciles_predecessor_lineage(self):
        class CrashDuringLineage(SignedPrunableHistory):
            crashed = False

            def _finalize_migration_lineage_locked(self, q, old, new):
                if not self.crashed:
                    self.crashed = True
                    raise SimulatedRetirementCrash("crash after continuity CAS")
                return super()._finalize_migration_lineage_locked(q, old, new)

        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(4)
            old_dir = td / "archives-v1"
            new_dir = td / "archives-v2"
            new_dir.mkdir()
            layer = self.layer(builder, old_dir, cls=CrashDuringLineage)
            first = layer.compact(layer.create_checkpoint())
            old = layer.require_namespace_authority()
            migration = issue_migration(old, new_dir, 2, layer.key)
            with self.assertRaises(SimulatedRetirementCrash):
                layer.migrate_archive_namespace(migration)
            # LAB-066 continuity CAS already committed. A fresh normal object must
            # reconcile the PREPARED intent and restore exact predecessor lineage.
            restarted = self.layer(builder, new_dir)
            permit = restarted.issue_namespace_retirement_permit()
            self.assertEqual(permit.predecessor_record_id, old.record_id)
            receipt = restarted.retire_superseded_namespace(permit)
            self.assertEqual(receipt.status, "RETIRED")
            self.assertGreater(restarted.audit_archive(first.archive_id)["rows_verified"], 0)

    def test_crash_after_authorize_is_retryable(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            with self.assertRaises(SimulatedRetirementCrash):
                layer.retire_superseded_namespace(permit, fail_after_authorize=True)
            self.assertTrue(any(old_dir.iterdir()))
            restarted = self.layer(builder, new_dir)
            receipt = restarted.retire_superseded_namespace(permit)
            self.assertEqual(receipt.status, "RETIRED")
            self.assertFalse(any(old_dir.iterdir()))

    def test_crash_after_cleanup_is_retryable(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            with self.assertRaises(SimulatedRetirementCrash):
                layer.retire_superseded_namespace(permit, fail_after_cleanup=True)
            self.assertFalse(any(old_dir.iterdir()))
            restarted = self.layer(builder, new_dir)
            receipt = restarted.retire_superseded_namespace(permit)
            self.assertEqual(receipt.status, "RETIRED")

    def test_byte_identical_old_path_replacement_is_not_cleaned(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            detached = Path(td) / "detached-old"
            old_dir.rename(detached)
            shutil.copytree(detached, old_dir)
            with self.assertRaises(NamespaceReplacementDetected):
                layer.retire_superseded_namespace(permit)
            self.assertTrue(any(old_dir.iterdir()))
            self.assertTrue(any(detached.iterdir()))

    def test_symlink_old_path_replacement_is_not_cleaned(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            detached = Path(td) / "detached-old"
            attacker = Path(td) / "attacker"
            attacker.mkdir()
            old_dir.rename(detached)
            os.symlink(attacker, old_dir, target_is_directory=True)
            with self.assertRaises(NamespaceReplacementDetected):
                layer.retire_superseded_namespace(permit)
            self.assertEqual(list(attacker.iterdir()), [])
            self.assertTrue(any(detached.iterdir()))

    def test_unsupported_strong_reopen_fails_closed_without_cleanup(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            with patch(
                "experiments.namespace_retirement.integration.reacquire",
                return_value={"status": "UNSUPPORTED_STRONG_REACQUISITION", "reason": "no capability"},
            ):
                with self.assertRaises(StrongReacquisitionUnavailable):
                    layer.retire_superseded_namespace(permit)
            self.assertTrue(any(old_dir.iterdir()))

    def test_incomplete_successor_archive_chain_blocks_permit(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            (new_dir / f"{first.archive_id}.json").unlink()
            with self.assertRaises(Exception):
                layer.issue_namespace_retirement_permit()
            self.assertTrue(any(old_dir.iterdir()))

    def test_policy_generation_change_stales_existing_permit(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            q = builder.store._con()
            try:
                q.execute("UPDATE archive_namespace_retirement_state SET policy_generation=policy_generation+1")
            finally:
                q.close()
            with self.assertRaises(StalePermit):
                layer.retire_superseded_namespace(permit)
            self.assertTrue(any(old_dir.iterdir()))

    def test_stale_pair_and_chain_commitment_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            permit = layer.issue_namespace_retirement_permit()
            stale = replace(permit, archive_chain_commitment="0" * 64)
            with self.assertRaises(Exception):
                layer.retire_superseded_namespace(stale)
            self.assertTrue(any(old_dir.iterdir()))

    def test_current_generation_is_not_retirement_eligible(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            builder = ChainBuilder(td / "db").append(2)
            layer = self.layer(builder, td / "archives")
            with self.assertRaises(CurrentGenerationProtected):
                layer.issue_namespace_retirement_permit()

    def test_current_generation_scavenger_never_crosses_into_old_namespace(self):
        with tempfile.TemporaryDirectory() as td:
            builder, layer, old_dir, new_dir, old, new, first = self.migrated(td)
            old_before = {p.name for p in old_dir.iterdir()}
            scavenger = ArchiveScavenger(layer, grace_generations=1)
            scavenger.scan()
            scavenger.advance_generation()
            scavenger.scavenge()
            self.assertEqual({p.name for p in old_dir.iterdir()}, old_before)
            self.assertEqual(layer.namespace_generation, 2)


if __name__ == "__main__":
    unittest.main()
