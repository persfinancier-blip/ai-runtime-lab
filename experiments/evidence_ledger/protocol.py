from __future__ import annotations
import hashlib, json, os
from pathlib import Path

SCHEMA_VERSION = 1

class LedgerError(RuntimeError): pass
class TamperError(LedgerError): pass
class DanglingEvidence(LedgerError): pass

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

class Observation:
    def __init__(self, kind, artifact_digest, producer, trusted_observer, result, command_digest="", output_digest=""):
        self.kind, self.artifact_digest, self.producer = kind, artifact_digest, producer
        self.trusted_observer, self.result = trusted_observer, result
        self.command_digest, self.output_digest = command_digest, output_digest
    def body(self):
        return {"schema_version": SCHEMA_VERSION, "type": "observation", "kind": self.kind,
                "artifact_digest": self.artifact_digest, "producer": self.producer,
                "trusted_observer": self.trusted_observer, "result": self.result,
                "command_digest": self.command_digest, "output_digest": self.output_digest}

class Ledger:
    def __init__(self, path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True); self.path.touch(exist_ok=True); self.reload()
    def append(self, body):
        record_id = digest(body)
        if record_id in self.by_id: return record_id
        previous = self.records[-1]["record_id"] if self.records else None
        entry = {"seq": len(self.records), "record_id": record_id, "prev": previous, "body": body}
        entry["chain_hash"] = digest(entry)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n"); handle.flush(); os.fsync(handle.fileno())
        self.records.append(entry); self.by_id[record_id] = entry
        return record_id
    def observe(self, observation): return self.append(observation.body())
    def invalidate(self, target, reason): return self.append({"schema_version": SCHEMA_VERSION, "type": "invalidation", "target": target, "reason": reason})
    def supersede(self, target, replacement): return self.append({"schema_version": SCHEMA_VERSION, "type": "supersession", "target": target, "replacement": replacement})
    def reload(self):
        self.records, self.by_id, previous = [], {}, None
        for sequence, line in enumerate(self.path.read_text(encoding="utf-8").splitlines()):
            entry = json.loads(line); record_id = digest(entry["body"])
            base = {"seq": sequence, "record_id": record_id, "prev": previous, "body": entry["body"]}
            if entry["seq"] != sequence or entry["record_id"] != record_id or entry["prev"] != previous or entry["chain_hash"] != digest(base):
                raise TamperError(f"invalid record at sequence {sequence}")
            self.records.append(entry); self.by_id[record_id] = entry; previous = record_id
    def resolve(self, record_id):
        if record_id not in self.by_id: raise DanglingEvidence(record_id)
        invalid = {e["body"]["target"] for e in self.records if e["body"]["type"] == "invalidation"}
        superseded = {e["body"]["target"] for e in self.records if e["body"]["type"] == "supersession"}
        return self.by_id[record_id]["body"], record_id in invalid, record_id in superseded

class Verifier:
    def __init__(self, ledger): self.ledger = ledger
    def verify(self, artifact_digest, evidence_ids):
        if not evidence_ids: return False
        for evidence_id in evidence_ids:
            try: body, invalid, superseded = self.ledger.resolve(evidence_id)
            except DanglingEvidence: return False
            if body["type"] != "observation" or invalid or superseded: return False
            if body["artifact_digest"] != artifact_digest or not body["trusted_observer"] or body["result"] != "PASS": return False
        return True
