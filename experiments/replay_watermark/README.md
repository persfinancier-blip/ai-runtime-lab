# Replay Watermark Reference

LAB-034 reference prototype for transactional replay/freshness state.

The SQL layer atomically advances authority/key/global sequence and the per-task accepted record. An optional external monotonic anchor is deliberately outside the database: it exists only to detect rollback of the entire database to an older internally consistent snapshot.

Run corrected tests:

```bash
python -m unittest discover -s experiments/replay_watermark/tests -p 'test_protocol.py' -v
```

The unsafe split-commit seed is excluded from normal discovery and is expected to fail:

```bash
python -m unittest experiments.replay_watermark.tests.unsafe_split_expected_failure
```

Non-goals: distributed consensus, TPM implementation, remote KMS implementation, or a claim that SQLite itself provides full-storage anti-rollback protection.
