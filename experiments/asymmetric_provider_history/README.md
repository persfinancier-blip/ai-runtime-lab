# LAB-082 — asymmetric provider history

Ed25519 reference and integration model that separates current private signing capability from durable historical public verification material.

The supported cross-layer surface is `SupportedAsymmetricHistoricalSharedAnchorLedger`. It keeps the LAB-080 SQLite reservation/rotation serialization boundary while using LAB-036 HMAC observations only for current execution-time authentication. After an effect is observed, the current runtime Ed25519 signer signs the exact provider/generation/position/request receipt fields; durable historical verification then requires only Ed25519 public material and signatures.

Run the isolated protocol suite:

```bash
python -m unittest experiments.asymmetric_provider_history.tests.test_protocol -v
```

Run integration and supported-surface regressions:

```bash
python -m unittest \
  experiments.asymmetric_provider_history.tests.test_integration \
  experiments.asymmetric_provider_history.tests.test_supported -v
```

Unsafe symmetric baseline (expected failure):

```bash
python -m unittest experiments.asymmetric_provider_history.tests.unsafe_symmetric_expected_failure -v
```

The durable SQLite database stores Ed25519 public keys, transition signatures, and receipt signatures. It does not store provider private signing keys or historical LAB-036 HMAC keys. Concurrent reconciliation uses the first valid durable Ed25519 receipt as the canonical receipt for a request so fresh challenge/signature differences do not become false substitution failures.

This is a reference custody boundary, not an HSM/KMS implementation. It also does not independently prove whole-store freshness: rollback of an internally consistent database snapshot remains governed by the existing external monotonic-anchor/bootstrap trust work from LAB-034–037 and later shared-anchor layers.
