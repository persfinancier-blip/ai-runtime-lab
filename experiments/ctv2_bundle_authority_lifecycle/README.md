# LAB-051 — Bundle authority lifecycle

Reference composition of LAB-050 authenticated policy/trust bundles with the threshold root lifecycle from LAB-037–039.

## Core rule

A new bundle is accepted only against the **active durable root re-read inside the publication transaction**. The bundle binds exact `root_version`, `root_epoch`, `root_digest`, and `signer_id`. An in-memory signer object cannot replace that authority.

Normal root rotation requires both the old-root threshold and the candidate-root threshold over the same transition. Break-glass recovery uses a distinct durable recovery quorum and increments the authority epoch.

## Run

```bash
PYTHONPATH=. python -m unittest discover -s experiments/ctv2_bundle_authority_lifecycle/tests -p 'test_*.py' -v
python -m compileall -q experiments/ctv2_bundle_authority_lifecycle
```

Unsafe seed, expected to fail:

```bash
PYTHONPATH=. python -m unittest experiments.ctv2_bundle_authority_lifecycle.tests.unsafe_self_swap_expected_failure -v
```

## Important boundary

SQLite is used here as a single-node serializable authority boundary. This experiment does not claim multi-replica consensus, HSM-grade keys, or a general PKI. HMAC keys are deterministic reference authenticators only.
