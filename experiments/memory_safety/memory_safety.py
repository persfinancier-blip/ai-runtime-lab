import json, hashlib
from dataclasses import dataclass, asdict
from pathlib import Path

TRUST = {"untrusted": 0, "self_report": 1, "corroborated": 2, "verified": 3}

@dataclass
class Memory:
    id: str
    topic: str
    value: str
    similarity: float
    trust: str = "untrusted"
    status: str = "ACTIVE"
    supersedes: str | None = None
    evidence_id: str | None = None
    reason: str | None = None

    @classmethod
    def make(cls, topic, value, similarity, **kwargs):
        identity = hashlib.sha256(f"{topic}\0{value}".encode()).hexdigest()[:16]
        return cls(identity, topic, value, similarity, **kwargs)

class MemoryStore:
    def __init__(self, path):
        self.path = Path(path)
        self.items = {}

    def add(self, memory):
        self.items[memory.id] = memory
        self.save()
        return memory

    def supersede(self, old_id, replacement, min_trust="corroborated"):
        if replacement.status != "ACTIVE" or TRUST[replacement.trust] < TRUST[min_trust]:
            raise ValueError("replacement is not eligible to supersede authoritative memory")
        replacement.supersedes = old_id
        self.items[replacement.id] = replacement
        self.items[old_id].status = "SUPERSEDED"
        self.save()
        return replacement

    def quarantine(self, memory_id, reason):
        self.items[memory_id].status = "QUARANTINED"
        self.items[memory_id].reason = reason
        self.save()

    def retract(self, memory_id, evidence_id):
        self.items[memory_id].status = "RETRACTED"
        self.items[memory_id].evidence_id = evidence_id
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items.values()], sort_keys=True, indent=2))

    @classmethod
    def load(cls, path):
        store = cls(path)
        if Path(path).exists():
            for raw in json.loads(Path(path).read_text()):
                store.items[raw["id"]] = Memory(**raw)
        return store

    def naive(self, topic):
        return sorted((m for m in self.items.values() if m.topic == topic), key=lambda m: m.similarity, reverse=True)

    def authoritative(self, topic, min_trust="corroborated"):
        eligible = [m for m in self.items.values() if m.topic == topic and m.status == "ACTIVE" and TRUST[m.trust] >= TRUST[min_trust]]
        return sorted(eligible, key=lambda m: (TRUST[m.trust], m.similarity, m.id), reverse=True)
