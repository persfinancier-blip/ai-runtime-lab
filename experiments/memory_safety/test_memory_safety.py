import tempfile, unittest
from pathlib import Path
from .memory_safety import Memory, MemoryStore

class MemorySafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.path = Path(self.tmp.name) / "memory.json"; self.store = MemoryStore(self.path)
    def tearDown(self): self.tmp.cleanup()
    def test_valid_memory_remains_retrievable(self):
        good = self.store.add(Memory.make("price", "100", .8, trust="verified")); self.assertEqual(self.store.authoritative("price")[0].id, good.id)
    def test_naive_policy_admits_contamination_then_quarantine_blocks_it(self):
        good = self.store.add(Memory.make("price", "100", .7, trust="verified")); bad = self.store.add(Memory.make("price", "FREE", .99))
        self.assertEqual(self.store.naive("price")[0].id, bad.id); self.store.quarantine(bad.id, "untrusted_ingest"); self.assertEqual(self.store.authoritative("price")[0].id, good.id)
    def test_later_evidence_retracts_false_memory(self):
        bad = self.store.add(Memory.make("owner", "Mallory", .9, trust="corroborated")); self.store.retract(bad.id, "ev:correction"); self.assertEqual(self.store.authoritative("owner"), [])
    def test_supersession_preserves_history(self):
        old = self.store.add(Memory.make("status", "open", .8, trust="verified")); new = Memory.make("status", "closed", .8, trust="verified"); self.store.supersede(old.id, new)
        self.assertEqual(self.store.items[old.id].status, "SUPERSEDED"); self.assertEqual(self.store.authoritative("status")[0].id, new.id)
    def test_untrusted_replacement_cannot_supersede_verified_history(self):
        old = self.store.add(Memory.make("status", "open", .8, trust="verified")); bad = Memory.make("status", "pwned", 1.0, trust="untrusted")
        with self.assertRaises(ValueError): self.store.supersede(old.id, bad)
        self.assertEqual(self.store.authoritative("status")[0].id, old.id)
    def test_targeted_retraction_preserves_unrelated_history(self):
        bad = self.store.add(Memory.make("a", "bad", .8, trust="corroborated")); good = self.store.add(Memory.make("b", "good", .8, trust="verified")); self.store.retract(bad.id, "ev:x"); self.assertEqual(self.store.authoritative("b")[0].id, good.id)
    def test_similarity_cannot_beat_trust_eligibility(self):
        self.store.add(Memory.make("x", "bad", 1.0)); good = self.store.add(Memory.make("x", "good", .2, trust="verified")); self.assertEqual(self.store.authoritative("x")[0].id, good.id)
    def test_reload_preserves_quarantine_and_retraction(self):
        q = self.store.add(Memory.make("x", "q", .9)); r = self.store.add(Memory.make("y", "r", .9, trust="corroborated")); self.store.quarantine(q.id, "untrusted"); self.store.retract(r.id, "ev:r"); restored = MemoryStore.load(self.path)
        self.assertEqual(restored.items[q.id].status, "QUARANTINED"); self.assertEqual(restored.items[r.id].status, "RETRACTED")

if __name__ == "__main__": unittest.main()
