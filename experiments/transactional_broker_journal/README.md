# LAB-072 transactional broker journal

SQLite serializes local request reservation and credential rotation. External effects remain a separate idempotent sink keyed by a stable effect identity; a committed-but-unobserved effect is reconciled rather than replayed under a new identity.

Credential rotation fails closed while the current generation still has unresolved `INTENT` or `UNKNOWN` requests. Otherwise a previously authorized old-generation intent could be executed after rotation with the wrong secret generation.

`authorized.py` puts durable reservation behind LAB-071's real process-instance authority boundary: kernel `SCM_CREDENTIALS` plus PID/starttime/pidfd validation must succeed before a new journal row or sink effect is possible. LAB-072 SQL is the single durable credential-generation authority; LAB-071 is reused for sender identity only, avoiding a split generation authority across JSON and SQL stores.

Run the journal suite:

```bash
python -m unittest experiments.transactional_broker_journal.tests.test_protocol -v
```

Run Linux process-level authority/concurrency integration:

```bash
python -m unittest experiments.transactional_broker_journal.tests.test_authorized_process_integration -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.transactional_broker_journal.tests.unsafe_concurrent_expected_failure -v
```

This is a local reference model, not distributed consensus and not a claim of universal exactly-once side effects. External systems without stable idempotency/reconciliation need a different fail-closed UNKNOWN policy.
