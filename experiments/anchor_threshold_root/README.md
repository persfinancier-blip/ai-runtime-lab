# Threshold Trust-Root Reference Prototype

LAB-038 models verifier-root rotation and compromise recovery without building a general PKI.

## Normal rotation

A candidate root activates only when the same canonical rotation payload is authenticated by both the configured threshold of the currently trusted root and the configured threshold of the candidate root. Signer identities are unique; revoked signers cannot contribute.

## Break-glass recovery

Recovery does **not** use current provider/root keys as authority. A separately pinned recovery authority has its own key set, threshold, generation, and revocation list. Recovery must advance the root version by exactly one and the authority epoch by exactly one. Old receipts become non-current after recovery.

## Persistence

`AtomicRootStore` writes exactly one activated root with temp-file + fsync + replace semantics. If durable persistence fails, the in-memory root is not activated.

## Reference-only cryptography

HMAC is used only to make the experiment deterministic with the Python standard library. Production verifier state should contain public verification material or references to protected verification services, never private provider signing keys.

## Run

```bash
PYTHONPATH=. python -m unittest discover -s experiments/anchor_threshold_root/tests -p 'test_*.py' -v
```

Unsafe baseline (expected to fail):

```bash
PYTHONPATH=. python -m unittest experiments.anchor_threshold_root.tests.unsafe_single_signer_expected_failure
```
