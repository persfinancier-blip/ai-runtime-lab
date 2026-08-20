# LAB-062 signed-history compaction integration

This experiment applies LAB-061 archive/prune semantics directly to LAB-059's threshold-authenticated transition proof schema.

Corrected suite:

```bash
python -m unittest experiments.signed_history_compaction.tests.test_protocol -v
```

Unsafe delete-first seed (expected failure):

```bash
python -m unittest experiments.signed_history_compaction.tests.unsafe_delete_first_expected_failure -v
```

The live restart boundary is an authenticated checkpoint-derived compaction base plus retained signed suffix. Archive bytes are required for explicit forensic archive audit, not ordinary restart. Whole-store rollback freshness remains delegated to the external monotonic-anchor work from LAB-034–037.
