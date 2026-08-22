from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path


class MigrationError(RuntimeError): pass
class MigrationPendingEffects(MigrationError): pass
class MigrationSubstitution(MigrationError): pass
class MigrationStaleAuthority(MigrationError): pass
class MigrationThresholdError(MigrationError): pass
class MigrationRollback(MigrationError): pass


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def key_id(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()[:16]


@dataclass(frozen=True)
class Root:
    authority_id: str
    version: int
    epoch: int
    threshold: int
    keys: dict[str, str]
    revoked: tuple[str, ...] = ()

    @property
    def descriptor(self):
        return {"version": self.version, "epoch": self.epoch, "threshold": self.threshold, "keys": dict(sorted(self.keys.items())), "revoked": sorted(self.revoked)}

    def validate(self):
        if not self.authority_id or type(self.version) is not int or self.version < 1:
            raise MigrationSubstitution("invalid root")
        if self.authority_id != sha(self.descriptor):
            raise MigrationSubstitution("root content-address mismatch")
        if type(self.epoch) is not int or self.epoch < 1:
            raise MigrationSubstitution("invalid root epoch")
        active = set(self.keys) - set(self.revoked)
        if type(self.threshold) is not int or self.threshold < 1 or self.threshold > len(active):
            raise MigrationSubstitution("invalid root threshold")


@dataclass(frozen=True)
class Signature:
    signer_id: str
    signature: str


@dataclass(frozen=True)
class MigrationCheckpoint:
    schema_version: int
    history_digest: str
    legacy_entry_count: int
    terminal_authority_id: str
    terminal_authority_version: int
    terminal_authority_epoch: int
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
        return sha(self.canonical)


@dataclass(frozen=True)
class MigrationProof:
    checkpoint_id: str
    authority_id: str
    authority_version: int
    signatures: tuple[Signature, ...]


def sign_checkpoint(checkpoint: MigrationCheckpoint, key: bytes) -> Signature:
    return Signature(key_id(key), hmac.new(key, canon(checkpoint.canonical), hashlib.sha256).hexdigest())


def verify_threshold(root: Root, checkpoint: MigrationCheckpoint, proof: MigrationProof):
    root.validate()
    if proof.checkpoint_id != checkpoint.checkpoint_id:
        raise MigrationSubstitution("checkpoint/proof identity mismatch")
    if proof.authority_id != root.authority_id or proof.authority_version != root.version:
        raise MigrationStaleAuthority("proof does not name current threshold authority")
    seen = set(); valid = 0
    for sig in proof.signatures:
        if sig.signer_id in seen:
            raise MigrationThresholdError("duplicate signer")
        seen.add(sig.signer_id)
        if sig.signer_id in root.revoked:
            raise MigrationThresholdError("revoked signer")
        hx = root.keys.get(sig.signer_id)
        if hx is None:
            raise MigrationThresholdError("unknown signer")
        expected = hmac.new(bytes.fromhex(hx), canon(checkpoint.canonical), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig.signature):
            raise MigrationThresholdError("invalid checkpoint signature")
        valid += 1
    if valid < root.threshold:
        raise MigrationThresholdError(f"threshold not met: {valid}/{root.threshold}")
    return True


class MigrationStore:
    """Reference LAB-078 ceremony over the existing broker/registry SQL shape.

    Legacy single-signature rows remain verification-only. The migration row is a
    threshold-authorized commitment to the exact legacy prefix and terminal heads.
    No legacy row is copied into registry_threshold_publications.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        q = self._con(); self._schema(q); q.close()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    @staticmethod
    def _schema(q):
        q.executescript("""
        CREATE TABLE IF NOT EXISTS registry_authority_head(singleton INTEGER PRIMARY KEY CHECK(singleton=1), authority_id TEXT NOT NULL, version INTEGER NOT NULL, epoch INTEGER NOT NULL, threshold INTEGER NOT NULL, keys_json TEXT NOT NULL, revoked_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sink_registry_entries(entry_digest TEXT PRIMARY KEY, sink_id TEXT NOT NULL, generation INTEGER NOT NULL, adapter_digest TEXT NOT NULL, endpoint_origin TEXT NOT NULL, operation_profile TEXT NOT NULL, predecessor_entry_digest TEXT, issuer_id TEXT NOT NULL, issuer_generation INTEGER NOT NULL, signature TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS registry_authorized_entries(entry_digest TEXT PRIMARY KEY, entry_json TEXT NOT NULL, authority_id TEXT NOT NULL, authority_version INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sink_registry_heads(sink_id TEXT PRIMARY KEY, entry_digest TEXT NOT NULL, generation INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sink_capability_heads(sink_id TEXT PRIMARY KEY, capability_generation INTEGER NOT NULL, claim_digest TEXT NOT NULL, probe_generation INTEGER NOT NULL, issuer_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS broker_meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1), credential_generation INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS broker_requests(request_id TEXT PRIMARY KEY, request_digest TEXT NOT NULL, status TEXT NOT NULL, receipt TEXT);
        CREATE TABLE IF NOT EXISTS registry_threshold_publications(entry_digest TEXT PRIMARY KEY, proof_json TEXT NOT NULL, proof_digest TEXT NOT NULL, authority_id TEXT NOT NULL, authority_version INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS registry_migration_checkpoint(singleton INTEGER PRIMARY KEY CHECK(singleton=1), checkpoint_id TEXT NOT NULL, checkpoint_json TEXT NOT NULL, proof_json TEXT NOT NULL, root_json TEXT NOT NULL, authority_id TEXT NOT NULL, authority_version INTEGER NOT NULL, cutoff_sequence INTEGER NOT NULL);
        """)

    @staticmethod
    def _root_locked(q) -> Root:
        row = q.execute("SELECT authority_id,version,epoch,threshold,keys_json,revoked_json FROM registry_authority_head WHERE singleton=1").fetchone()
        if row is None: raise MigrationSubstitution("missing authority head")
        root = Root(row[0], row[1], row[2], row[3], dict(json.loads(row[4])), tuple(json.loads(row[5])))
        root.validate(); return root

    @staticmethod
    def _rows(q, sql):
        return [list(r) for r in q.execute(sql).fetchall()]

    def _snapshot_locked(self, q, *, cutoff_sequence: int) -> MigrationCheckpoint:
        if type(cutoff_sequence) is not int or cutoff_sequence < 0:
            raise MigrationSubstitution("invalid cutoff sequence")
        root = self._root_locked(q)
        pending = q.execute("SELECT COUNT(*) FROM broker_requests WHERE status IN ('INTENT','UNKNOWN')").fetchone()[0]
        if pending:
            raise MigrationPendingEffects(f"{pending} unresolved broker request(s)")
        legacy_rows = self._rows(q, "SELECT entry_digest,entry_json,authority_id,authority_version FROM registry_authorized_entries ORDER BY entry_digest")
        registry_rows = self._rows(q, "SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature FROM sink_registry_entries ORDER BY entry_digest")
        if {r[0] for r in legacy_rows} != {r[0] for r in registry_rows}:
            raise MigrationSubstitution("legacy registry/history prefix mismatch")
        if q.execute("SELECT COUNT(*) FROM registry_threshold_publications").fetchone()[0]:
            raise MigrationSubstitution("threshold suffix exists before migration checkpoint")
        heads = self._rows(q, "SELECT sink_id,entry_digest,generation FROM sink_registry_heads ORDER BY sink_id")
        caps = self._rows(q, "SELECT sink_id,capability_generation,claim_digest,probe_generation,issuer_id FROM sink_capability_heads ORDER BY sink_id")
        generation = q.execute("SELECT credential_generation FROM broker_meta WHERE singleton=1").fetchone()
        if generation is None or type(generation[0]) is not int or generation[0] < 1:
            raise MigrationSubstitution("invalid credential generation")
        confirmed = self._rows(q, "SELECT request_id,request_digest,receipt FROM broker_requests WHERE status='CONFIRMED' ORDER BY request_id")
        history_digest = sha({"registry_rows": registry_rows, "legacy_bindings": legacy_rows})
        return MigrationCheckpoint(1, history_digest, len(registry_rows), root.authority_id, root.version, root.epoch, sha(heads), sha(caps), generation[0], sha(confirmed), cutoff_sequence)

    def preview(self, *, cutoff_sequence: int) -> MigrationCheckpoint:
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            cp = self._snapshot_locked(q, cutoff_sequence=cutoff_sequence)
            q.rollback(); return cp
        finally: q.close()

    @staticmethod
    def _proof_json(proof: MigrationProof):
        return json.dumps({"checkpoint_id":proof.checkpoint_id,"authority_id":proof.authority_id,"authority_version":proof.authority_version,"signatures":[asdict(s) for s in sorted(proof.signatures,key=lambda x:x.signer_id)]}, sort_keys=True, separators=(",",":"))

    def migrate(self, checkpoint: MigrationCheckpoint, proof: MigrationProof):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            if q.execute("SELECT COUNT(*) FROM registry_migration_checkpoint").fetchone()[0]:
                row=q.execute("SELECT checkpoint_id,checkpoint_json,proof_json FROM registry_migration_checkpoint WHERE singleton=1").fetchone()
                if row != (checkpoint.checkpoint_id, json.dumps(checkpoint.canonical,sort_keys=True,separators=(",",":")), self._proof_json(proof)):
                    raise MigrationSubstitution("same migration slot has different checkpoint")
                q.commit(); return checkpoint.checkpoint_id
            actual = self._snapshot_locked(q, cutoff_sequence=checkpoint.cutoff_sequence)
            if actual != checkpoint:
                raise MigrationSubstitution("checkpoint does not match exact current legacy state")
            root = self._root_locked(q)
            verify_threshold(root, checkpoint, proof)
            cp_json=json.dumps(checkpoint.canonical,sort_keys=True,separators=(",",":")); pj=self._proof_json(proof)
            root_json=json.dumps(root.descriptor,sort_keys=True,separators=(",",":"))
            q.execute("INSERT INTO registry_migration_checkpoint VALUES(1,?,?,?,?,?,?,?)",(checkpoint.checkpoint_id,cp_json,pj,root_json,root.authority_id,root.version,checkpoint.cutoff_sequence))
            q.commit(); return checkpoint.checkpoint_id
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def verify(self):
        q=self._con()
        try:
            q.execute("BEGIN")
            row=q.execute("SELECT checkpoint_id,checkpoint_json,proof_json,root_json,authority_id,authority_version,cutoff_sequence FROM registry_migration_checkpoint WHERE singleton=1").fetchone()
            if row is None: raise MigrationRollback("migration checkpoint missing")
            data=json.loads(row[1]); cp=MigrationCheckpoint(**data)
            if cp.checkpoint_id!=row[0] or cp.cutoff_sequence!=row[6]: raise MigrationSubstitution("checkpoint identity mismatch")
            p=json.loads(row[2]); proof=MigrationProof(p["checkpoint_id"],p["authority_id"],p["authority_version"],tuple(Signature(x["signer_id"],x["signature"]) for x in p["signatures"]))
            rd=json.loads(row[3]); historical_root=Root(row[4], rd["version"], rd["epoch"], rd["threshold"], dict(rd["keys"]), tuple(rd.get("revoked",[])))
            historical_root.validate()
            if proof.authority_id!=row[4] or proof.authority_version!=row[5]: raise MigrationSubstitution("proof relational mismatch")
            verify_threshold(historical_root,cp,proof)
            legacy_rows=self._rows(q,"SELECT entry_digest,entry_json,authority_id,authority_version FROM registry_authorized_entries ORDER BY entry_digest")
            registry_rows=self._rows(q,"SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature FROM sink_registry_entries WHERE entry_digest NOT IN (SELECT entry_digest FROM registry_threshold_publications) ORDER BY entry_digest")
            if len(registry_rows)!=cp.legacy_entry_count or sha({"registry_rows":registry_rows,"legacy_bindings":legacy_rows})!=cp.history_digest:
                raise MigrationSubstitution("legacy prefix changed after migration")
            return True
        finally:q.close()


class UnsafeAutoPromotion:
    """Deliberately unsafe: copies legacy single-signature rows into the threshold table."""
    @staticmethod
    def promote(q):
        rows=q.execute("SELECT entry_digest,authority_id,authority_version FROM registry_authorized_entries").fetchall()
        for d,aid,v in rows:
            q.execute("INSERT OR REPLACE INTO registry_threshold_publications VALUES(?,?,?,?,?)",(d,'{}','0'*64,aid,v))
        return len(rows)
