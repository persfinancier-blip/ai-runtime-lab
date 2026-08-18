# Memory Safety Experiment

Deterministic LAB-011 prototype for contamination quarantine, evidence-backed retraction, supersession, and trust-first retrieval.

Run from repository root:

```bash
python -m unittest experiments.memory_safety.test_memory_safety -v
```

The intentionally unsafe baseline is `MemoryStore.naive()`: it ranks by similarity alone and is asserted in the test suite to select a high-similarity contaminated memory. `authoritative()` instead filters lifecycle status and trust before ranking.

This prototype models semantics only. Production persistence should use the append-only evidence/history mechanisms established in LAB-007 rather than treating this JSON snapshot as the audit ledger.
