# Append-only Evidence Ledger

A standard-library reference experiment for durable claim-to-observation evidence.

Records are canonical JSON bodies with SHA-256 content identity. The JSONL ledger also assigns a monotonic sequence and chains each entry to the previous record. Reload recomputes identities and chain hashes, so mutation/reordering is rejected.

Observations bind a result to an exact artifact digest and producer identity. `trusted_observer` models the trust boundary for this experiment: executor assertions are records, but the verifier refuses to treat them as independent proof. Production trust must come from authenticated producer identity/attestation, not a caller-controlled boolean.

Invalidation and supersession append new records; history is never edited. Duplicate canonical records return the same content ID and are not appended twice.

Run:

```bash
python -m unittest discover -s experiments/evidence_ledger/tests -p 'test_*.py' -v
```

Expected matrix: restart/reload, duplicate/idempotency, tamper, stale artifact, dangling reference, invalidation, supersession, untrusted producer, and valid evidence.

Non-goals: general database, telemetry system, replicated log, signature PKI, or proof that a producer is honest. The hash chain detects mutation relative to a trusted head/checkpoint; by itself it does not prevent an attacker who can rewrite the entire file from recomputing the chain.
