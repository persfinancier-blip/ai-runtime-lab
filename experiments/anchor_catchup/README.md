# External monotonic-anchor catch-up reference

LAB-035 reference prototype for the recoverable gap between a committed DB sequence and an independent monotonic anti-rollback anchor.

## Safety contract

1. A DB commit atomically creates one authenticated `PENDING` anchor intent for the new global sequence.
2. While any intent is pending, no later publication or authority/key rotation may advance the DB sequence.
3. Catch-up reads the external anchor before any increment.
4. The only automatically recoverable lag is exactly one (`anchor == DB sequence - 1`).
5. If increment returns an unknown outcome, never blindly retry; restart/retry begins with a fresh anchor read.
6. `anchor > DB` is rollback/restore evidence and fails closed.
7. `anchor < DB - 1`, missing/forged proof, unavailable anchor, or stale authority/key also fail closed.
8. Rotation is itself a new sequence with a new-key proof and must be anchored before consequential continuation.

The simulator is intentionally TPM-counter-like: increments are `+1`, not arbitrary `set(max)` operations.

## Run

```bash
python -m unittest discover -s experiments/anchor_catchup/tests -p 'test_protocol.py' -v
python -m compileall -q experiments
```

The deliberately unsafe baseline is outside normal passing discovery:

```bash
python -m unittest experiments.anchor_catchup.tests.unsafe_blind_retry_expected_failure -v
```

It is expected to fail because timeout-after-commit followed by blind retry increments the external counter twice.

## Non-goals

No real TPM/KMS provider, distributed consensus, multi-position catch-up, or PostgreSQL locking/performance claim is made here. SQLite and the deterministic anchor adapter model semantics only.
