# LAB-073 sink capability contract

Retry and UNKNOWN behavior is derived from an authenticated capability attestation issued by a trusted behavioral-probe boundary, never from adapter-provided booleans.

A mutating sink gets automatic retry authority only when stable request-bound idempotency is verified and a finite retention window remains valid. `SAFE_RETRY_RECONCILE` additionally requires reconciliation by the same key. Idempotency without reconciliation does **not** automatically repeat an already-UNKNOWN operation inside the generic broker.

Corrected suite:

```bash
python -m unittest experiments.sink_capability_contract.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.sink_capability_contract.tests.unsafe_generic_retry_expected_failure -v
```
