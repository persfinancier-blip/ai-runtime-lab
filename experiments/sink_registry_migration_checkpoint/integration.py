from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass


class RealMigrationError(RuntimeError):
    pass


class RealMigrationPending(RealMigrationError):
    pass


class RealMigrationSubstitution(RealMigrationError):
    pass


class RealMigrationThreshold(RealMigrationError):
    pass


class RealMigrationNotEstablished(RealMigrationError):
    pass


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _sha(obj) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


@dataclass(frozen=True)
class RealMigrationCheckpoint:
    schema_version: int
    terminal_authority_id: str
    terminal_authority_version: int
    terminal_authority_epoch: int
    legacy_history_digest: str
    legacy_entry_count: int
    legacy_entry_ids_digest: str
    registry_heads_digest: str
    capability_heads_digest: str
    credential_generation: int
    confirmed_requests_digest: str
    cutoff_sequence: int

    @property
    def canonical(self):
        return asdict(self)

    @property
    def checkpoint_id(self):
        return _sha(self.canonical)


@dataclass(frozen=True)
class CheckpointSignature:
    signer_id: str
    signature: str


@dataclass(frozen=True)
class RealMigrationProof:
    checkpoint_id: str
    authority_id: str
    authority_version: int
    signatures: tuple[CheckpointSignature, ...]


def sign_checkpoint(checkpoint: RealMigrationCheckpoint, signer_key: bytes) -> CheckpointSignature:
    signer_id = hashlib.sha256(signer_key).hexdigest()[:16]
    signature = hmac.new(signer_key, _canon(checkpoint.canonical), hashlib.sha256).hexdigest()
    return CheckpointSignature(signer_id, signature)


def _verify_threshold(root, checkpoint: RealMigrationCheckpoint, proof: RealMigrationProof):
    root.validate()
    if proof.checkpoint_id != checkpoint.checkpoint_id:
        raise RealMigrationSubstitution("checkpoint/proof mismatch")
    if proof.authority_version != root.version:
        raise RealMigrationThreshold("proof authority version mismatch")
    seen = set()
    valid = 0
    for item in proof.signatures:
        if item.signer_id in seen:
            raise RealMigrationThreshold("duplicate signer")
        seen.add(item.signer_id)
        if item.signer_id in root.revoked:
            raise RealMigrationThreshold("revoked signer")
        key_hex = root.keys.get(item.signer_id)
        if key_hex is None:
            raise RealMigrationThreshold("unknown signer")
        expected = hmac.new(
            bytes.fromhex(key_hex), _canon(checkpoint.canonical), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, item.signature):
            raise RealMigrationThreshold("invalid checkpoint signature")
        valid += 1
    if valid < root.threshold:
        raise RealMigrationThreshold(f"threshold not met: {valid}/{root.threshold}")


class RealMigrationCoordinator:
    """Migration ceremony over the existing LAB-076/LAB-077 SQLite DB.

    `registry` is the audited LAB-077 journal object. It must expose `.journal`
    (the transactional broker journal), `.lifecycle` (LAB-076 durable authority),
    `_historical_locked()` for post-migration threshold publications, and the
    inherited LAB-075 row loader helpers.

    No authority key material is duplicated into the migration table. Historical
    root material is always loaded from LAB-076 `registry_authorities`.
    """

    def __init__(self, registry):
        if not hasattr(registry, "journal") or not hasattr(registry, "lifecycle"):
            raise TypeError("real LAB-077 registry/lifecycle composition required")
        self.registry = registry
        self.journal = registry.journal
        self.lifecycle = registry.lifecycle
        self._init_schema()

    def _con(self):
        return self.journal._con()

    def _init_schema(self):
        q = self._con()
        try:
            q.execute(
                """
                CREATE TABLE IF NOT EXISTS registry_migration_checkpoint_v2(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  checkpoint_id TEXT NOT NULL,
                  checkpoint_json TEXT NOT NULL,
                  proof_json TEXT NOT NULL,
                  authority_id TEXT NOT NULL,
                  authority_version INTEGER NOT NULL,
                  cutoff_sequence INTEGER NOT NULL
                )
                """
            )
            q.commit()
        finally:
            q.close()

    @staticmethod
    def _rows(q, sql):
        return [list(r) for r in q.execute(sql).fetchall()]

    def _current_root_locked(self, q):
        row = q.execute(
            "SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RealMigrationSubstitution("missing LAB-076 authority head")
        root = self.lifecycle._load_root(q, row[0])
        if (root.version, root.authority_epoch) != (row[1], row[2]):
            raise RealMigrationSubstitution("authority head/root mismatch")
        return row[0], root

    def _legacy_rows_locked(self, q):
        bindings = self._rows(
            q,
            "SELECT entry_digest,entry_json,authority_id,authority_version "
            "FROM registry_authorized_entries ORDER BY entry_digest",
        )
        threshold_ids = {
            row[0]
            for row in q.execute(
                "SELECT entry_digest FROM registry_threshold_publications"
            ).fetchall()
        }
        registry = self._rows(
            q,
            "SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,"
            "operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature "
            "FROM sink_registry_entries ORDER BY entry_digest",
        )
        legacy_registry = [row for row in registry if row[0] not in threshold_ids]
        if {r[0] for r in bindings} != {r[0] for r in legacy_registry}:
            raise RealMigrationSubstitution("legacy LAB-076 bindings/registry rows differ")

        for digest, raw, authority_id, authority_version in bindings:
            parsed = json.loads(raw)
            entry = self.registry._row_entry(
                (
                    digest,
                    parsed["sink_id"],
                    parsed["generation"],
                    parsed["adapter_digest"],
                    parsed["endpoint_origin"],
                    parsed["operation_profile"],
                    parsed.get("predecessor_entry_digest"),
                    parsed["issuer_id"],
                    parsed["issuer_generation"],
                    parsed["signature"],
                )
            )
            if entry.entry_digest != digest:
                raise RealMigrationSubstitution("legacy entry digest mismatch")
            root = self.lifecycle._load_root(q, authority_id)
            if root.version != authority_version:
                raise RealMigrationSubstitution("legacy authority version mismatch")
            self.lifecycle._verify_against(entry, root)
        return bindings, legacy_registry

    def _snapshot_locked(self, q, *, cutoff_sequence: int):
        if type(cutoff_sequence) is not int or cutoff_sequence < 0:
            raise RealMigrationSubstitution("invalid cutoff sequence")
        if q.execute(
            "SELECT COUNT(*) FROM broker_requests WHERE status IN ('INTENT','UNKNOWN')"
        ).fetchone()[0]:
            raise RealMigrationPending("pending broker effects block migration")

        authority_id, root = self._current_root_locked(q)
        bindings, legacy_registry = self._legacy_rows_locked(q)
        if q.execute("SELECT COUNT(*) FROM registry_threshold_publications").fetchone()[0]:
            raise RealMigrationSubstitution("threshold suffix already exists before migration")

        heads = self._rows(
            q, "SELECT sink_id,entry_digest,generation FROM sink_registry_heads ORDER BY sink_id"
        )
        caps = self._rows(
            q,
            "SELECT sink_id,capability_generation,claim_digest,probe_generation,issuer_id "
            "FROM sink_capability_heads ORDER BY sink_id",
        )
        gen = q.execute(
            "SELECT credential_generation FROM broker_meta WHERE singleton=1"
        ).fetchone()
        if gen is None or type(gen[0]) is not int or gen[0] < 1:
            raise RealMigrationSubstitution("invalid credential generation")
        confirmed = self._rows(
            q,
            "SELECT request_id,request_digest,receipt,registry_entry_digest,registry_generation "
            "FROM broker_requests WHERE status='CONFIRMED' ORDER BY request_id",
        )
        legacy_ids = sorted(r[0] for r in legacy_registry)
        checkpoint = RealMigrationCheckpoint(
            2,
            authority_id,
            root.version,
            root.authority_epoch,
            _sha({"registry_rows": legacy_registry, "legacy_bindings": bindings}),
            len(legacy_registry),
            _sha(legacy_ids),
            _sha(heads),
            _sha(caps),
            gen[0],
            _sha(confirmed),
            cutoff_sequence,
        )
        return checkpoint, root

    @staticmethod
    def _proof_json(proof):
        return json.dumps(
            {
                "checkpoint_id": proof.checkpoint_id,
                "authority_id": proof.authority_id,
                "authority_version": proof.authority_version,
                "signatures": [
                    asdict(s) for s in sorted(proof.signatures, key=lambda x: x.signer_id)
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def preview(self, *, cutoff_sequence: int):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            cp, _ = self._snapshot_locked(q, cutoff_sequence=cutoff_sequence)
            q.rollback()
            return cp
        finally:
            q.close()

    def migrate(self, checkpoint: RealMigrationCheckpoint, proof: RealMigrationProof):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = q.execute(
                "SELECT checkpoint_id,checkpoint_json,proof_json,authority_id,"
                "authority_version,cutoff_sequence FROM registry_migration_checkpoint_v2 "
                "WHERE singleton=1"
            ).fetchone()
            expected = (
                checkpoint.checkpoint_id,
                json.dumps(checkpoint.canonical, sort_keys=True, separators=(",", ":")),
                self._proof_json(proof),
                proof.authority_id,
                proof.authority_version,
                checkpoint.cutoff_sequence,
            )
            if existing is not None:
                if existing != expected:
                    raise RealMigrationSubstitution("migration slot substitution")
                q.commit()
                return checkpoint.checkpoint_id

            actual, root = self._snapshot_locked(q, cutoff_sequence=checkpoint.cutoff_sequence)
            if actual != checkpoint:
                raise RealMigrationSubstitution("checkpoint no longer matches authoritative state")
            if proof.authority_id != checkpoint.terminal_authority_id:
                raise RealMigrationThreshold("proof names wrong authority")
            _verify_threshold(root, checkpoint, proof)
            q.execute(
                "INSERT INTO registry_migration_checkpoint_v2 VALUES(1,?,?,?,?,?,?)",
                expected,
            )
            q.commit()
            return checkpoint.checkpoint_id
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _load_checkpoint_locked(self, q):
        row = q.execute(
            "SELECT checkpoint_id,checkpoint_json,proof_json,authority_id,"
            "authority_version,cutoff_sequence FROM registry_migration_checkpoint_v2 "
            "WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RealMigrationNotEstablished("migration checkpoint missing")
        data = json.loads(row[1])
        cp = RealMigrationCheckpoint(**data)
        if cp.checkpoint_id != row[0] or cp.cutoff_sequence != row[5]:
            raise RealMigrationSubstitution("checkpoint identity mismatch")
        proof_data = json.loads(row[2])
        proof = RealMigrationProof(
            proof_data["checkpoint_id"],
            proof_data["authority_id"],
            proof_data["authority_version"],
            tuple(
                CheckpointSignature(x["signer_id"], x["signature"])
                for x in proof_data["signatures"]
            ),
        )
        if (proof.authority_id, proof.authority_version) != (row[3], row[4]):
            raise RealMigrationSubstitution("checkpoint proof relational mismatch")
        root = self.lifecycle._load_root(q, row[3])
        _verify_threshold(root, cp, proof)
        if (
            cp.terminal_authority_id != row[3]
            or cp.terminal_authority_version != root.version
            or cp.terminal_authority_epoch != root.authority_epoch
        ):
            raise RealMigrationSubstitution("checkpoint historical root mismatch")
        return cp, proof

    def verify_mixed_history(self):
        """Reverify checkpoint + legacy prefix + every post-checkpoint threshold row."""
        q = self._con()
        try:
            q.execute("BEGIN")
            cp, _ = self._load_checkpoint_locked(q)

            bindings, legacy_registry = self._legacy_rows_locked(q)
            legacy_ids = {r[0] for r in legacy_registry}
            if (
                len(legacy_registry) != cp.legacy_entry_count
                or _sha({"registry_rows": legacy_registry, "legacy_bindings": bindings})
                != cp.legacy_history_digest
                or _sha(sorted(legacy_ids)) != cp.legacy_entry_ids_digest
            ):
                raise RealMigrationSubstitution("legacy prefix changed after migration")

            threshold_ids = {
                r[0]
                for r in q.execute(
                    "SELECT entry_digest FROM registry_threshold_publications"
                ).fetchall()
            }
            if legacy_ids & threshold_ids:
                raise RealMigrationSubstitution(
                    "legacy row was synthetically promoted into threshold history"
                )

            all_registry = {
                r[0]
                for r in q.execute("SELECT entry_digest FROM sink_registry_entries").fetchall()
            }
            if all_registry != legacy_ids | threshold_ids:
                raise RealMigrationSubstitution("registry row is neither legacy nor threshold-authenticated")

            for entry_digest in sorted(threshold_ids):
                historical = self.registry._historical_locked(q, entry_digest)
                if historical is None:
                    raise RealMigrationSubstitution("threshold proof missing")
                stored = self.registry._load_entry(q, entry_digest)
                if historical.entry != stored:
                    raise RealMigrationSubstitution("threshold history/registry mismatch")

            for sink_id, entry_digest, generation in q.execute(
                "SELECT sink_id,entry_digest,generation FROM sink_registry_heads"
            ).fetchall():
                stored = self.registry._load_entry(q, entry_digest)
                if stored.sink_id != sink_id or stored.generation != generation:
                    raise RealMigrationSubstitution("registry head mismatch")
                if entry_digest not in legacy_ids and entry_digest not in threshold_ids:
                    raise RealMigrationSubstitution("head points outside authenticated mixed history")

            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
