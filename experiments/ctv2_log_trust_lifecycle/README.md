# CT v2 Authenticated Log Trust Lifecycle

Reference prototype for LAB-047.

It removes LAB-046's caller-supplied `trusted_logs` / `operator_id` authority. A pinned trust root authenticates an exact versioned snapshot containing:

- `LogID -> verification_profile` binding;
- authoritative operator group;
- lifecycle state (`ACTIVE`, `RETIRED`, `DISTRUSTED`);
- lifecycle timestamp;
- snapshot version/generation, issue time, expiry and exact content identity.

The evaluator counts only `ACTIVE` logs from the exact authenticated snapshot identified by `snapshot_id`. Unknown, retired and distrusted logs do not contribute to future thresholds. Historical snapshots remain addressable so prior decisions retain the operator/lifecycle facts that existed when they were made.

## Run

```bash
python -m unittest discover -s experiments/ctv2_log_trust_lifecycle/tests -p 'test_*.py' -v
python -m compileall -q experiments/ctv2_log_trust_lifecycle
```

Unsafe baseline (expected to fail):

```bash
python -m unittest experiments.ctv2_log_trust_lifecycle.tests.unsafe_self_asserted_expected_failure
```

## Security boundary

The HMAC in this prototype is a deterministic stand-in for authenticated trust-metadata distribution. It demonstrates authorization/freshness/binding semantics, not a production Chrome or TUF implementation.

The prototype does **not** define browser/vendor CT compliance thresholds. RFC 9162 leaves log discovery/trust/distrust and the quantity/form of accepted SCT evidence to local policy.
