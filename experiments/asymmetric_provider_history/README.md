# LAB-082 — asymmetric provider history

Ed25519 reference model that separates current private signing capability from durable historical public verification material.

Run:

```bash
python -m unittest experiments.asymmetric_provider_history.tests.test_protocol -v
```

Unsafe symmetric baseline (expected failure):

```bash
python -m unittest experiments.asymmetric_provider_history.tests.unsafe_symmetric_expected_failure -v
```

The durable SQLite database stores Ed25519 public keys, transition signatures, and receipt signatures. It does not store provider private signing keys. This is a reference custody boundary, not an HSM/KMS implementation.
