# LAB-061 — authenticated transition-history pruning

The live store is compacted only behind the latest authenticated checkpoint. The archive artifact is written and fsynced before the destructive SQL transaction. The SQL transaction then revalidates the checkpoint/archive bytes, records the new live-history base and deletes the prefix atomically.

Normal restart uses only `compaction_base + retained suffix`; archive bytes are not runtime authority. `audit_archive()` separately verifies the content-addressed archive artifact and rolling prefix commitment.

Run:

```bash
python -m unittest experiments.transition_history_pruning.tests.test_protocol -v
python -m compileall -q experiments/transition_history_pruning
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.transition_history_pruning.tests.unsafe_delete_first_expected_failure -v
```

Deletion from SQLite is **not forensic erasure**. Whole-store rollback freshness remains an external-anchor problem (LAB-034–037).
