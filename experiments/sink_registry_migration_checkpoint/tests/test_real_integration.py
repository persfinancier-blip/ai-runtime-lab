import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from experiments.sink_registry_migration_checkpoint.integration import (
    RealMigrationCoordinator,
    RealMigrationPending,
    RealMigrationProof,
    RealMigrationSubstitution,
    RealMigrationThreshold,
    sign_checkpoint,
)


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def kid(key):
    return hashlib.sha256(key).hexdigest()[:16]


@dataclass(frozen=True)
class Root:
    provider_id: str
    version: int
    authority_epoch: int
    threshold: int
    keys: dict
    revoked: tuple = ()

    def validate(self):
        if self.threshold < 1:
            raise RuntimeError("bad root")


def root_body(r):
    return json.dumps(
        {
            "provider_id": r.provider_id,
            "version": r.version,
            "authority_epoch": r.authority_epoch,
            "threshold": r.threshold,
            "keys": dict(sorted(r.keys.items())),
            "revoked": sorted(r.revoked),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def root_id(r):
    return hashlib.sha256(root_body(r).encode()).hexdigest()


@dataclass(frozen=True)
class Entry:
    sink_id: str
    generation: int
    adapter_digest: str
    endpoint_origin: str
    operation_profile: str
    predecessor_entry_digest: str | None
    issuer_id: str
    issuer_generation: int
    signature: str

    @property
    def unsigned(self):
        return {
            "sink_id": self.sink_id,
            "generation": self.generation,
            "adapter_digest": self.adapter_digest,
            "endpoint_origin": self.endpoint_origin,
            "operation_profile": self.operation_profile,
            "predecessor_entry_digest": self.predecessor_entry_digest,
            "issuer_id": self.issuer_id,
            "issuer_generation": self.issuer_generation,
        }

    @property
    def entry_digest(self):
        return hashlib.sha256(canon({**self.unsigned, "signature": self.signature})).hexdigest()


class Journal:
    def __init__(self, path):
        self.path = str(path)

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q


class Lifecycle:
    def __init__(self, path):
        self.path = str(path)

    def _load_root(self, q, aid):
        row = q.execute(
            "SELECT body FROM registry_authorities WHERE authority_id=?", (aid,)
        ).fetchone()
        if not row:
            raise RuntimeError("missing root")
        x = json.loads(row[0])
        root = Root(
            x["provider_id"],
            x["version"],
            x["authority_epoch"],
            x["threshold"],
            dict(x["keys"]),
            tuple(x.get("revoked", [])),
        )
        if root_id(root) != aid:
            raise RuntimeError("root substitution")
        return root

    def _verify_against(self, entry, root):
        key_hex = root.keys.get(entry.issuer_id)
        if key_hex is None or entry.issuer_generation != root.version:
            raise RuntimeError("issuer")
        expected = hmac.new(
            bytes.fromhex(key_hex), canon(entry.unsigned), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, entry.signature):
            raise RuntimeError("entry signature")
        return entry


@dataclass(frozen=True)
class Historical:
    entry: Entry


class Registry:
    def __init__(self, path, lifecycle):
        self.journal = Journal(path)
        self.lifecycle = lifecycle

    def _row_entry(self, row):
        _, sink, generation, adapter, endpoint, operation, predecessor, issuer, issuer_generation, signature = row
        return Entry(
            sink,
            generation,
            adapter,
            endpoint,
            operation,
            predecessor,
            issuer,
            issuer_generation,
            signature,
        )

    def _load_entry(self, q, digest):
        row = q.execute(
            "SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,"
            "operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature "
            "FROM sink_registry_entries WHERE entry_digest=?",
            (digest,),
        ).fetchone()
        if not row:
            raise RuntimeError("missing entry")
        return self._row_entry(row)

    def _historical_locked(self, q, digest):
        row = q.execute(
            "SELECT proof_json,authority_id,authority_version "
            "FROM registry_threshold_publications WHERE entry_digest=?",
            (digest,),
        ).fetchone()
        if not row:
            return None
        entry = self._load_entry(q, digest)
        root = self.lifecycle._load_root(q, row[1])
        if root.version != row[2]:
            raise RuntimeError("proof version")
        proof = json.loads(row[0])
        valid = 0
        for signature in proof["signatures"]:
            key_hex = root.keys.get(signature["signer_id"])
            if key_hex and hmac.compare_digest(
                hmac.new(
                    bytes.fromhex(key_hex), canon(entry.unsigned), hashlib.sha256
                ).hexdigest(),
                signature["signature"],
            ):
                valid += 1
        if valid < root.threshold:
            raise RuntimeError("threshold")
        return Historical(entry)


class RealIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "db.sqlite"
        q = sqlite3.connect(self.path)
        q.executescript(
            """
            CREATE TABLE registry_authorities(authority_id TEXT PRIMARY KEY,version INTEGER,epoch INTEGER,body TEXT,transition_kind TEXT,predecessor_id TEXT,proof_old TEXT,proof_new TEXT,proof_recovery TEXT);
            CREATE TABLE registry_authority_head(singleton INTEGER PRIMARY KEY,authority_id TEXT,version INTEGER,epoch INTEGER);
            CREATE TABLE registry_authorized_entries(entry_digest TEXT PRIMARY KEY,entry_json TEXT,authority_id TEXT,authority_version INTEGER);
            CREATE TABLE sink_registry_entries(entry_digest TEXT PRIMARY KEY,sink_id TEXT,generation INTEGER,adapter_digest TEXT,endpoint_origin TEXT,operation_profile TEXT,predecessor_entry_digest TEXT,issuer_id TEXT,issuer_generation INTEGER,signature TEXT);
            CREATE TABLE sink_registry_heads(sink_id TEXT PRIMARY KEY,entry_digest TEXT,generation INTEGER);
            CREATE TABLE sink_capability_heads(sink_id TEXT PRIMARY KEY,capability_generation INTEGER,claim_digest TEXT,probe_generation INTEGER,issuer_id TEXT);
            CREATE TABLE broker_meta(singleton INTEGER PRIMARY KEY,credential_generation INTEGER);
            CREATE TABLE broker_requests(request_id TEXT PRIMARY KEY,request_digest TEXT,status TEXT,receipt TEXT,registry_entry_digest TEXT,registry_generation INTEGER);
            CREATE TABLE registry_threshold_publications(entry_digest TEXT PRIMARY KEY,proof_json TEXT,proof_digest TEXT,authority_id TEXT,authority_version INTEGER);
            """
        )
        self.keys = [b"k1", b"k2", b"k3"]
        key_map = {kid(key): key.hex() for key in self.keys}
        self.root = Root("registry-A", 1, 1, 2, key_map)
        authority_id = root_id(self.root)
        q.execute(
            "INSERT INTO registry_authorities VALUES(?,?,?,?,?,?,?,?,?)",
            (authority_id, 1, 1, root_body(self.root), "bootstrap", None, "[]", "[]", "[]"),
        )
        q.execute(
            "INSERT INTO registry_authority_head VALUES(1,?,?,?)",
            (authority_id, 1, 1),
        )
        q.execute("INSERT INTO broker_meta VALUES(1,1)")
        q.execute(
            "INSERT INTO sink_capability_heads VALUES('sink-A',1,'c1',1,'probe')"
        )
        unsigned = {
            "sink_id": "sink-A",
            "generation": 1,
            "adapter_digest": "a1",
            "endpoint_origin": "https://one",
            "operation_profile": "write",
            "predecessor_entry_digest": None,
            "issuer_id": kid(self.keys[0]),
            "issuer_generation": 1,
        }
        signature = hmac.new(
            self.keys[0], canon(unsigned), hashlib.sha256
        ).hexdigest()
        self.legacy = Entry(**unsigned, signature=signature)
        raw = json.dumps(
            {**self.legacy.unsigned, "signature": signature},
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = self.legacy.entry_digest
        q.execute(
            "INSERT INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                digest,
                "sink-A",
                1,
                "a1",
                "https://one",
                "write",
                None,
                kid(self.keys[0]),
                1,
                signature,
            ),
        )
        q.execute(
            "INSERT INTO registry_authorized_entries VALUES(?,?,?,?)",
            (digest, raw, authority_id, 1),
        )
        q.execute(
            "INSERT INTO sink_registry_heads VALUES('sink-A',?,1)", (digest,)
        )
        q.execute(
            "INSERT INTO broker_requests VALUES('done','rd','CONFIRMED','receipt',?,1)",
            (digest,),
        )
        q.commit()
        q.close()
        self.lifecycle = Lifecycle(self.path)
        self.registry = Registry(self.path, self.lifecycle)
        self.coordinator = RealMigrationCoordinator(self.registry)

    def tearDown(self):
        self.tmp.cleanup()

    def proof(self, checkpoint, keys=None):
        keys = keys or self.keys[:2]
        return RealMigrationProof(
            checkpoint.checkpoint_id,
            checkpoint.terminal_authority_id,
            checkpoint.terminal_authority_version,
            tuple(sign_checkpoint(checkpoint, key) for key in keys),
        )

    def migrate(self):
        checkpoint = self.coordinator.preview(cutoff_sequence=1)
        self.coordinator.migrate(checkpoint, self.proof(checkpoint))
        return checkpoint

    def test_real_schema_migration_and_restart(self):
        self.migrate()
        self.assertTrue(self.coordinator.verify_mixed_history())
        self.assertTrue(
            RealMigrationCoordinator(self.registry).verify_mixed_history()
        )

    def test_one_signer_rejected(self):
        checkpoint = self.coordinator.preview(cutoff_sequence=1)
        with self.assertRaises(RealMigrationThreshold):
            self.coordinator.migrate(
                checkpoint, self.proof(checkpoint, self.keys[:1])
            )

    def test_pending_refused(self):
        q = sqlite3.connect(self.path)
        q.execute(
            "INSERT INTO broker_requests VALUES('p','x','UNKNOWN',NULL,?,1)",
            (self.legacy.entry_digest,),
        )
        q.commit()
        q.close()
        with self.assertRaises(RealMigrationPending):
            self.coordinator.preview(cutoff_sequence=1)

    def test_root_rotation_race_rejected(self):
        checkpoint = self.coordinator.preview(cutoff_sequence=1)
        old_proof = self.proof(checkpoint)
        q = sqlite3.connect(self.path)
        new_keys = [b"n1", b"n2", b"n3"]
        new_root = Root(
            "registry-A", 2, 1, 2, {kid(key): key.hex() for key in new_keys}
        )
        new_id = root_id(new_root)
        q.execute(
            "INSERT INTO registry_authorities VALUES(?,?,?,?,?,?,?,?,?)",
            (
                new_id,
                2,
                1,
                root_body(new_root),
                "rotation",
                root_id(self.root),
                "[]",
                "[]",
                "[]",
            ),
        )
        q.execute(
            "UPDATE registry_authority_head SET authority_id=?,version=2,epoch=1",
            (new_id,),
        )
        q.commit()
        q.close()
        with self.assertRaises(RealMigrationSubstitution):
            self.coordinator.migrate(checkpoint, old_proof)

    def test_legacy_substitution_after_checkpoint_rejected(self):
        self.migrate()
        q = sqlite3.connect(self.path)
        q.execute("UPDATE sink_registry_entries SET endpoint_origin='https://evil'")
        q.commit()
        q.close()
        with self.assertRaises(Exception):
            self.coordinator.verify_mixed_history()

    def test_synthetic_promotion_rejected(self):
        self.migrate()
        q = sqlite3.connect(self.path)
        q.execute(
            "INSERT INTO registry_threshold_publications VALUES(?,?,?,?,?)",
            (
                self.legacy.entry_digest,
                '{"signatures":[]}',
                "x",
                root_id(self.root),
                1,
            ),
        )
        q.commit()
        q.close()
        with self.assertRaises(RealMigrationSubstitution):
            self.coordinator.verify_mixed_history()

    def test_first_threshold_successor_after_migration(self):
        self.migrate()
        unsigned = {
            "sink_id": "sink-A",
            "generation": 2,
            "adapter_digest": "a2",
            "endpoint_origin": "https://two",
            "operation_profile": "write",
            "predecessor_entry_digest": self.legacy.entry_digest,
            "issuer_id": "threshold:" + root_id(self.root),
            "issuer_generation": 1,
        }
        signatures = [
            {
                "signer_id": kid(key),
                "signature": hmac.new(
                    key, canon(unsigned), hashlib.sha256
                ).hexdigest(),
            }
            for key in self.keys[:2]
        ]
        proof = json.dumps(
            {"signatures": signatures}, sort_keys=True, separators=(",", ":")
        )
        proof_digest = hashlib.sha256(proof.encode()).hexdigest()
        entry = Entry(**unsigned, signature=proof_digest)
        digest = entry.entry_digest
        q = sqlite3.connect(self.path)
        q.execute(
            "INSERT INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                digest,
                entry.sink_id,
                entry.generation,
                entry.adapter_digest,
                entry.endpoint_origin,
                entry.operation_profile,
                entry.predecessor_entry_digest,
                entry.issuer_id,
                entry.issuer_generation,
                entry.signature,
            ),
        )
        q.execute(
            "INSERT INTO registry_threshold_publications VALUES(?,?,?,?,?)",
            (digest, proof, proof_digest, root_id(self.root), 1),
        )
        q.execute(
            "UPDATE sink_registry_heads SET entry_digest=?,generation=2 WHERE sink_id='sink-A'",
            (digest,),
        )
        q.commit()
        q.close()
        self.assertTrue(self.coordinator.verify_mixed_history())

    def test_confirmed_receipt_remains_historical(self):
        self.migrate()
        q = sqlite3.connect(self.path)
        row = q.execute(
            "SELECT status,receipt FROM broker_requests WHERE request_id='done'"
        ).fetchone()
        q.close()
        self.assertEqual(row, ("CONFIRMED", "receipt"))
        self.assertTrue(self.coordinator.verify_mixed_history())


if __name__ == "__main__":
    unittest.main()
