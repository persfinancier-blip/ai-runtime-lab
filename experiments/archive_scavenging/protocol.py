from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ScavengeError(RuntimeError):
    pass


class StaleRetentionGeneration(ScavengeError):
    pass


class CandidateBecameReachable(ScavengeError):
    pass


class ContentAddressSubstitution(ScavengeError):
    pass


@dataclass(frozen=True)
class Candidate:
    archive_id: str
    observed_generation: int
    first_seen_generation: int
    artifact: bool
    manifest: bool


class ArchiveScavenger:
    """Generation-fenced mark/sweep for LAB-062 content-addressed archives.

    Reachability comes only from the signed compaction layer's authenticated
    previous_archive_id chain. Filesystem names are candidates, never authority.
    When LAB-066 namespace authority is available, every enumeration and destructive
    boundary re-proves it rather than trusting a restart-time cached observation.
    """

    def __init__(self, layer, grace_generations=2):
        if type(grace_generations) is not int or grace_generations < 1:
            raise ValueError("grace")
        self.layer = layer
        self.grace = grace_generations
        q = layer.store._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS archive_retention_state(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  generation INTEGER NOT NULL);
                INSERT OR IGNORE INTO archive_retention_state VALUES(1,0);
                CREATE TABLE IF NOT EXISTS archive_orphan_candidates(
                  archive_id TEXT PRIMARY KEY,
                  first_seen_generation INTEGER NOT NULL,
                  last_seen_generation INTEGER NOT NULL);
                """
            )
        finally:
            q.close()

    def _require_namespace_authority(self):
        require = getattr(self.layer, "require_namespace_authority", None)
        if require is None:
            return None
        return require()

    def generation(self):
        q = self.layer.store._con()
        try:
            return q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
        finally:
            q.close()

    def advance_generation(self):
        q = self.layer.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            q.execute("UPDATE archive_retention_state SET generation=generation+1")
            value = q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
            q.commit()
            return value
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _reachable(self, q):
        # On SignedPrunableHistory this is the LAB-062 authenticated archive walk.
        return set(self.layer._reachable_archive_ids(q))

    def _fs(self):
        self._require_namespace_authority()
        out = {}
        for path in self.layer.archive_dir.iterdir():
            name = path.name
            if name.endswith(".manifest.json"):
                archive_id = name[:-14]
                kind = "manifest"
            elif name.endswith(".json"):
                archive_id = name[:-5]
                kind = "artifact"
            else:
                continue
            # Ignore attacker-controlled/unrecognised names rather than deleting
            # them under a content-addressed retention policy.
            if HEX64.fullmatch(archive_id):
                out.setdefault(archive_id, set()).add(kind)
        return out

    def scan(self):
        self._require_namespace_authority()
        q = self.layer.store._con()
        try:
            q.execute("BEGIN")
            reachable = self._reachable(q)
            generation = q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
            fs = self._fs()
            out = []
            for archive_id, kinds in sorted(fs.items()):
                if archive_id in reachable:
                    q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?", (archive_id,))
                    continue
                row = q.execute(
                    "SELECT first_seen_generation FROM archive_orphan_candidates WHERE archive_id=?",
                    (archive_id,),
                ).fetchone()
                first = generation if row is None else row[0]
                q.execute(
                    "INSERT INTO archive_orphan_candidates VALUES(?,?,?) "
                    "ON CONFLICT(archive_id) DO UPDATE SET last_seen_generation=excluded.last_seen_generation",
                    (archive_id, first, generation),
                )
                out.append(
                    Candidate(
                        archive_id,
                        generation,
                        first,
                        "artifact" in kinds,
                        "manifest" in kinds,
                    )
                )
            for (archive_id,) in q.execute("SELECT archive_id FROM archive_orphan_candidates").fetchall():
                if archive_id not in fs or archive_id in reachable:
                    q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?", (archive_id,))
            q.commit()
            return tuple(out)
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _validate(self, q, archive_id, artifact_path, manifest_path):
        if not manifest_path.exists():
            # Artifact-only crash debris has no manifest to authenticate; its
            # content-address filename is only a deletion candidate after grace.
            return
        try:
            body = json.loads(manifest_path.read_text())
        except Exception as exc:
            raise ContentAddressSubstitution("unparseable manifest") from exc
        if body.get("archive_id") != archive_id:
            raise ContentAddressSubstitution("filename/manifest archive id")

        # Prefer LAB-062's real parser + history binding when available. The
        # fallback exists only for the small isolated algorithm tests.
        if hasattr(self.layer, "_verify_manifest_identity"):
            try:
                from experiments.signed_history_compaction.core import ArchiveManifest
                manifest = ArchiveManifest.parse(body)
                self.layer._verify_manifest_identity(q, manifest)
            except Exception as exc:
                raise ContentAddressSubstitution("authenticated manifest identity") from exc
            expected_artifact = manifest.artifact_sha256
        else:
            if not self.layer._gc_manifest_identity(body):
                raise ContentAddressSubstitution("manifest content identity")
            expected_artifact = body.get("artifact_sha256")

        if artifact_path.exists():
            actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if actual != expected_artifact:
                raise ContentAddressSubstitution("artifact digest")

    def delete_candidate(self, candidate, expected_generation=None):
        if not isinstance(candidate, Candidate):
            raise TypeError("candidate")
        self._require_namespace_authority()
        q = self.layer.store._con()
        try:
            # This write lock serializes final reachability check + unlink
            # against LAB-062's compaction commit transaction.
            q.execute("BEGIN IMMEDIATE")
            # Re-prove after acquiring the serialization boundary, immediately
            # before any filesystem validation/unlink decision.
            self._require_namespace_authority()
            generation = q.execute("SELECT generation FROM archive_retention_state").fetchone()[0]
            if expected_generation is not None and generation != expected_generation:
                raise StaleRetentionGeneration("generation changed")
            row = q.execute(
                "SELECT first_seen_generation FROM archive_orphan_candidates WHERE archive_id=?",
                (candidate.archive_id,),
            ).fetchone()
            if row is None:
                q.commit()
                return "ALREADY_GONE"
            if generation - row[0] < self.grace:
                raise StaleRetentionGeneration("grace")
            if candidate.archive_id in self._reachable(q):
                q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?", (candidate.archive_id,))
                q.commit()
                raise CandidateBecameReachable(candidate.archive_id)

            artifact_path, manifest_path = self.layer._archive_paths(candidate.archive_id)
            self._validate(q, candidate.archive_id, artifact_path, manifest_path)
            self._require_namespace_authority()
            for path in (artifact_path, manifest_path):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            q.execute("DELETE FROM archive_orphan_candidates WHERE archive_id=?", (candidate.archive_id,))
            q.commit()
            return "DELETED"
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def scavenge(self, expected_generation=None):
        out = {}
        for candidate in self.scan():
            try:
                out[candidate.archive_id] = self.delete_candidate(candidate, expected_generation)
            except StaleRetentionGeneration:
                out[candidate.archive_id] = "RETAINED_GRACE"
            except CandidateBecameReachable:
                out[candidate.archive_id] = "REACHABLE"
        return out


class UnsafeEagerDelete:
    def delete(self, layer, archive_id):
        for path in layer._archive_paths(archive_id):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
