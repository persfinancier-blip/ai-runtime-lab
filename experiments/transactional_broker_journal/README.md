# LAB-072 transactional broker journal

SQLite serializes local request reservation and credential rotation. External effects remain a separate idempotent sink keyed by a stable effect identity; a committed-but-unobserved effect is reconciled rather than replayed under a new identity.

Credential rotation fails closed while the current generation still has unresolved `INTENT` or `UNKNOWN` requests. Otherwise a previously authorized old-generation intent could be executed after rotation with the wrong secret generation.

This is a local reference model, not distributed consensus and not a claim of universal exactly-once side effects.

Run:

```bash
python -m unittest experiments.transactional_broker_journal.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.transactional_broker_journal.tests.unsafe_concurrent_expected_failure -v
```
