from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import asdict
from pathlib import Path

from experiments.filesystem_namespace_binding.protocol import NamespaceHandle
from experiments.namespace_reacquisition.integration import _parse_record
from experiments.namespace_reacquisition.protocol import ContinuityRecord, reacquire, verify_record

from .protocol import (
    CurrentGenerationProtected,
    NamespaceReplacementDetected,
    RetirementPermit,
    RetirementReceipt,
    StalePermit,
    StrongReacquisitionUnavailable,
    digest,
    mac,
    verify_permit,
)

_ARCHIVE_NAME = re.compile(r"^[0-9a-f]{64}\.(?:json|manifest\.json)$")


class RetirementIntegrationError(RuntimeError):
    pass


class SimulatedRetirementCrash(RetirementIntegrationError):
    pass


class NamespaceRetirementMixin:
    """Real LAB-066/LAB-063 retirement integration for SignedPrunableHistory.

    Migration writes a durable PREPARED intent before LAB-066 performs its
    authenticated generation CAS. A restart reconciles an intent against the
    authenticated current continuity row, so a crash between the CAS and lineage
    finalization cannot lose the predecessor object needed for later retirement.
    """

    def _init_namespace_retirement(self):
        q = self.store._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS archive_namespace_records(
                  record_id TEXT PRIMARY KEY,
                  generation INTEGER NOT NULL UNIQUE,
                  body_json TEXT NOT NULL,
                  predecessor_record_id TEXT,
                  status TEXT NOT NULL,
                  migration_chain_commitment TEXT);
                CREATE TABLE IF NOT EXISTS archive_namespace_migration_intents(
                  old_record_id TEXT PRIMARY KEY,
                  old_body_json TEXT NOT NULL,
                  permit_json TEXT NOT NULL,
                  status TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS archive_namespace_retirement_state(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  policy_generation INTEGER NOT NULL,
                  watermark INTEGER NOT NULL);
                INSERT OR IGNORE INTO archive_namespace_retirement_state VALUES(1,1,0);
                CREATE TABLE IF NOT EXISTS archive_namespace_retirements(
                  permit_id TEXT PRIMARY KEY,
                  predecessor_record_id TEXT NOT NULL,
                  successor_record_id TEXT NOT NULL,
                  predecessor_generation INTEGER NOT NULL,
                  successor_generation INTEGER NOT NULL,
                  archive_chain_commitment TEXT NOT NULL,
                  policy_generation INTEGER NOT NULL,
                  permit_json TEXT NOT NULL,
                  status TEXT NOT NULL,
                  files_removed INTEGER NOT NULL DEFAULT 0,
                  watermark INTEGER);
                """
            )
            current = self._namespace_continuity_record
            body = json.dumps(asdict(current), sort_keys=True, separators=(",", ":"))
            q.execute(
                "INSERT OR IGNORE INTO archive_namespace_records VALUES(?,?,?,NULL,'ACTIVE',NULL)",
                (current.record_id, current.namespace_generation, body),
            )
            self._reconcile_namespace_migration_intents_locked(q, current)
        finally:
            q.close()

    def _reconcile_namespace_migration_intents_locked(self, q, current):
        from experiments.namespace_reacquisition.protocol import MigrationPermit, migrate

        rows = q.execute(
            "SELECT old_record_id,old_body_json,permit_json,status "
            "FROM archive_namespace_migration_intents WHERE status='PREPARED'"
        ).fetchall()
        for old_id, old_body, permit_json, _ in rows:
            old = _parse_record(old_body)
            verify_record(old, self.key)
            permit = MigrationPermit(**json.loads(permit_json))
            if current.record_id == old.record_id:
                # The continuity CAS never happened; the durable intent is harmless
                # and may be reused by a retry.
                continue
            if permit.old_record_id != old.record_id:
                raise RetirementIntegrationError("migration intent predecessor mismatch")
            if current.namespace_generation != permit.new_generation:
                raise RetirementIntegrationError("migration intent/current generation mismatch")
            if os.path.abspath(current.archive_path) != os.path.abspath(permit.new_path):
                raise RetirementIntegrationError("migration intent/current path mismatch")
            # Re-run the authenticated transition derivation. The resulting record
            # may carry fresh handle observations, so compare authority fields that
            # the permit controls and trust current's own authenticated record_id.
            migrate(old, permit, self.key)
            self._finalize_migration_lineage_locked(q, old, current)
            q.execute(
                "UPDATE archive_namespace_migration_intents SET status='COMMITTED' WHERE old_record_id=?",
                (old.record_id,),
            )

    def _archive_chain_commitment_locked(self, q):
        base = self._base(q)
        reachable = sorted(self._reachable_archive_ids(q))
        body = {
            "history_id": self.history_id(q),
            "base_sequence": base[0],
            "root_id": base[1],
            "recovery_id": base[2],
            "prefix_commitment": base[3],
            "base_archive_id": base[4],
            "archive_ids": reachable,
        }
        return hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(), tuple(reachable)

    def _audit_current_successor_chain(self):
        self.require_namespace_authority()
        q = self.store._con()
        try:
            q.execute("BEGIN")
            commitment, archive_ids = self._archive_chain_commitment_locked(q)
            q.commit()
        finally:
            q.close()
        for archive_id in archive_ids:
            result = self.audit_archive(archive_id)
            if result.get("archive_id") != archive_id:
                raise RetirementIntegrationError("successor archive audit identity mismatch")
        # Re-prove namespace identity and SQL commitment after filesystem audits.
        self.require_namespace_authority()
        q = self.store._con()
        try:
            q.execute("BEGIN")
            commitment2, archive_ids2 = self._archive_chain_commitment_locked(q)
            q.commit()
        finally:
            q.close()
        if (commitment2, archive_ids2) != (commitment, archive_ids):
            raise RetirementIntegrationError("successor archive chain changed during audit")
        return commitment

    def _finalize_migration_lineage_locked(self, q, old, new):
        old_body = json.dumps(asdict(old), sort_keys=True, separators=(",", ":"))
        new_body = json.dumps(asdict(new), sort_keys=True, separators=(",", ":"))
        q.execute(
            "INSERT OR IGNORE INTO archive_namespace_records VALUES(?,?,?,NULL,'ACTIVE',NULL)",
            (old.record_id, old.namespace_generation, old_body),
        )
        q.execute(
            "UPDATE archive_namespace_records SET status='RETIRED_PENDING' WHERE record_id=?",
            (old.record_id,),
        )
        chain_commitment, _ = self._archive_chain_commitment_locked(q)
        q.execute(
            "INSERT OR IGNORE INTO archive_namespace_records "
            "VALUES(?,?,?,?, 'ACTIVE', ?)",
            (new.record_id, new.namespace_generation, new_body, old.record_id, chain_commitment),
        )
        row = q.execute(
            "SELECT predecessor_record_id,status FROM archive_namespace_records WHERE record_id=?",
            (new.record_id,),
        ).fetchone()
        if row != (old.record_id, "ACTIVE"):
            raise RetirementIntegrationError("successor lineage substitution")

    def migrate_archive_namespace(self, permit):
        old = self.require_namespace_authority()
        intent = json.dumps(asdict(permit), sort_keys=True, separators=(",", ":"))
        old_body = json.dumps(asdict(old), sort_keys=True, separators=(",", ":"))
        q = self.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = q.execute(
                "SELECT old_body_json,permit_json,status FROM archive_namespace_migration_intents "
                "WHERE old_record_id=?",
                (old.record_id,),
            ).fetchone()
            if existing and (existing[0], existing[1]) != (old_body, intent):
                raise RetirementIntegrationError("migration intent substitution")
            q.execute(
                "INSERT OR IGNORE INTO archive_namespace_migration_intents VALUES(?,?,?,'PREPARED')",
                (old.record_id, old_body, intent),
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        new = super().migrate_archive_namespace(permit)
        q = self.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT record_id,generation FROM archive_namespace_continuity WHERE singleton=1"
            ).fetchone()
            if row != (new.record_id, new.namespace_generation):
                raise RetirementIntegrationError("continuity changed before lineage finalization")
            self._finalize_migration_lineage_locked(q, old, new)
            q.execute(
                "UPDATE archive_namespace_migration_intents SET status='COMMITTED' WHERE old_record_id=?",
                (old.record_id,),
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        return new

    def _load_namespace_record_locked(self, q, record_id):
        row = q.execute(
            "SELECT body_json,status,predecessor_record_id FROM archive_namespace_records WHERE record_id=?",
            (record_id,),
        ).fetchone()
        if not row:
            raise StalePermit("namespace record missing")
        record = _parse_record(row[0])
        verify_record(record, self.key)
        if record.record_id != record_id:
            raise StalePermit("namespace record content identity mismatch")
        return record, row[1], row[2]

    def issue_namespace_retirement_permit(self):
        successor = self.require_namespace_authority()
        commitment = self._audit_current_successor_chain()
        q = self.store._con()
        try:
            q.execute("BEGIN")
            current = q.execute(
                "SELECT record_id,generation FROM archive_namespace_continuity WHERE singleton=1"
            ).fetchone()
            if current != (successor.record_id, successor.namespace_generation):
                raise StalePermit("current namespace changed")
            _, status, predecessor_id = self._load_namespace_record_locked(q, successor.record_id)
            if status != "ACTIVE" or predecessor_id is None:
                raise CurrentGenerationProtected("current namespace has no superseded predecessor")
            predecessor, predecessor_status, _ = self._load_namespace_record_locked(q, predecessor_id)
            if predecessor_status != "RETIRED_PENDING":
                raise StalePermit("predecessor is not retirement-pending")
            commitment2, _ = self._archive_chain_commitment_locked(q)
            if commitment2 != commitment:
                raise StalePermit("archive chain changed")
            policy_generation = q.execute(
                "SELECT policy_generation FROM archive_namespace_retirement_state WHERE singleton=1"
            ).fetchone()[0]
            unsigned = {
                "predecessor_record_id": predecessor.record_id,
                "successor_record_id": successor.record_id,
                "predecessor_generation": predecessor.namespace_generation,
                "successor_generation": successor.namespace_generation,
                "archive_chain_commitment": commitment,
                "policy_generation": policy_generation,
            }
            permit = RetirementPermit(**unsigned, mac=mac(self.key, unsigned))
            q.commit()
            return permit
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _strong_old_namespace_handle(self, record):
        status = reacquire(record, self.key, require_strong=True)
        if status.get("status") != "REACQUIRED":
            if status.get("status") == "UNSUPPORTED_STRONG_REACQUISITION":
                raise StrongReacquisitionUnavailable(status.get("reason", "strong reopen unavailable"))
            raise NamespaceReplacementDetected(status.get("status", "namespace replacement"))
        relative = os.fspath(Path(record.archive_path).relative_to(Path("/")))
        handle = NamespaceHandle.authorize_beneath("/", relative)
        if (handle.directory.st_dev, handle.directory.st_ino) != (record.st_dev, record.st_ino):
            handle.close()
            raise NamespaceReplacementDetected("superseded namespace object changed")
        return handle

    @staticmethod
    def _cleanup_retired_archive_files(handle):
        removed = 0
        for name in os.listdir(handle.fd):
            if not _ARCHIVE_NAME.fullmatch(name):
                raise RetirementIntegrationError(
                    f"unexpected entry in superseded archive namespace: {name!r}"
                )
            st = os.stat(name, dir_fd=handle.fd, follow_symlinks=False)
            if not stat.S_ISREG(st.st_mode):
                raise NamespaceReplacementDetected("retirement target contains non-regular entry")
            os.unlink(name, dir_fd=handle.fd)
            removed += 1
        os.fsync(handle.fd)
        return removed

    def retire_superseded_namespace(
        self,
        permit: RetirementPermit,
        *,
        fail_after_authorize=False,
        fail_after_cleanup=False,
    ):
        verify_permit(permit, self.key)
        successor = self.require_namespace_authority()
        if permit.successor_record_id != successor.record_id:
            raise StalePermit("permit successor is no longer current")
        if permit.successor_generation != successor.namespace_generation:
            raise StalePermit("permit successor generation is stale")

        commitment = self._audit_current_successor_chain()
        if permit.archive_chain_commitment != commitment:
            raise StalePermit("permit archive-chain commitment is stale")
        permit_id = digest(permit.unsigned())
        permit_json = json.dumps(asdict(permit), sort_keys=True, separators=(",", ":"))

        q = self.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            current = q.execute(
                "SELECT record_id,generation FROM archive_namespace_continuity WHERE singleton=1"
            ).fetchone()
            if current != (successor.record_id, successor.namespace_generation):
                raise StalePermit("current namespace changed")
            policy_generation = q.execute(
                "SELECT policy_generation FROM archive_namespace_retirement_state WHERE singleton=1"
            ).fetchone()[0]
            if permit.policy_generation != policy_generation:
                raise StalePermit("retirement policy generation changed")
            predecessor, status, _ = self._load_namespace_record_locked(
                q, permit.predecessor_record_id
            )
            if predecessor.namespace_generation != permit.predecessor_generation:
                raise StalePermit("predecessor generation mismatch")
            if predecessor.namespace_generation >= successor.namespace_generation:
                raise CurrentGenerationProtected("cannot retire current/future generation")
            if status == "RETIRED":
                row = q.execute(
                    "SELECT files_removed,watermark,status FROM archive_namespace_retirements "
                    "WHERE permit_id=?",
                    (permit_id,),
                ).fetchone()
                if not row or row[2] != "RETIRED":
                    raise RetirementIntegrationError("retired record missing receipt")
                q.commit()
                return RetirementReceipt(
                    permit_id, predecessor.record_id, predecessor.namespace_generation,
                    "RETIRED", row[0], row[1]
                )
            if status != "RETIRED_PENDING":
                raise StalePermit("predecessor status is not retirement-pending")
            existing = q.execute(
                "SELECT permit_json,status FROM archive_namespace_retirements WHERE permit_id=?",
                (permit_id,),
            ).fetchone()
            if existing and existing[0] != permit_json:
                raise StalePermit("permit id/content substitution")
            q.execute(
                "INSERT OR IGNORE INTO archive_namespace_retirements "
                "VALUES(?,?,?,?,?,?,?,?,'AUTHORIZED',0,NULL)",
                (
                    permit_id, permit.predecessor_record_id, permit.successor_record_id,
                    permit.predecessor_generation, permit.successor_generation,
                    permit.archive_chain_commitment, permit.policy_generation, permit_json,
                ),
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        if fail_after_authorize:
            raise SimulatedRetirementCrash("authorized retirement persisted before cleanup")

        with self._strong_old_namespace_handle(predecessor) as handle:
            removed = self._cleanup_retired_archive_files(handle)
        if fail_after_cleanup:
            raise SimulatedRetirementCrash("cleanup completed before receipt commit")

        # Re-audit the authoritative successor after destructive work and before
        # recording a terminal retirement receipt.
        if self._audit_current_successor_chain() != permit.archive_chain_commitment:
            raise StalePermit("successor chain changed before retirement finalization")
        q = self.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            current = q.execute(
                "SELECT record_id,generation FROM archive_namespace_continuity WHERE singleton=1"
            ).fetchone()
            if current != (permit.successor_record_id, permit.successor_generation):
                raise StalePermit("successor changed before retirement finalization")
            row = q.execute(
                "SELECT status FROM archive_namespace_retirements WHERE permit_id=?",
                (permit_id,),
            ).fetchone()
            if not row:
                raise RetirementIntegrationError("authorized retirement row disappeared")
            if row[0] == "RETIRED":
                receipt = q.execute(
                    "SELECT files_removed,watermark FROM archive_namespace_retirements WHERE permit_id=?",
                    (permit_id,),
                ).fetchone()
                q.commit()
                return RetirementReceipt(
                    permit_id, permit.predecessor_record_id, permit.predecessor_generation,
                    "RETIRED", receipt[0], receipt[1]
                )
            q.execute(
                "UPDATE archive_namespace_retirement_state SET watermark=watermark+1 WHERE singleton=1"
            )
            watermark = q.execute(
                "SELECT watermark FROM archive_namespace_retirement_state WHERE singleton=1"
            ).fetchone()[0]
            q.execute(
                "UPDATE archive_namespace_retirements SET status='RETIRED',files_removed=?,watermark=? "
                "WHERE permit_id=?",
                (removed, watermark, permit_id),
            )
            q.execute(
                "UPDATE archive_namespace_records SET status='RETIRED' WHERE record_id=?",
                (permit.predecessor_record_id,),
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        return RetirementReceipt(
            permit_id, permit.predecessor_record_id, permit.predecessor_generation,
            "RETIRED", removed, watermark
        )
