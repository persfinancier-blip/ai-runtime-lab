# LAB-099 PREPARED cross-binding verifier

Date: 2026-09-12

## Objective

Advance LAB-099 RED-intent staging without introducing production behavior while LAB-086 exact repository materialization remains unavailable.

The target boundary is the crash-after-atomic-PREPARED state: the durable `provider_activation_reservation_cutovers` materialization row and the matching `shared_anchor_intents` PREPARED row must describe one exact frozen authority and no stale or rebound variant may be resumable.

## Runtime capability observation

The required LAB-086 probe was attempted first in this run:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

This occurred before repository code execution. No new LAB-086 behavioral, unsafe-seed, compileall, security, or conflict PASS is claimed.

## Implemented test-only boundary

Draft PR #186 now contains:

`experiments/provider_generation_history/tests/lab099_prepared_cross_binding_reference.py`

The verifier is side-effect free and imports only the existing test-owned LAB-099 authority/storage reference modules. It does not touch SQLite and is not imported by production code.

`verify_prepared_cross_binding(...)` requires all of the following to agree exactly:

- materialized PREPARED canonical bytes and SHA-256 digest;
- frozen PREPARED semantic fields: logical DB identity, target schema-set identity/version, predecessor provenance head and epoch;
- exact 32-byte confirmation nonce;
- deterministic cutover anchor intent identity;
- anchor payload digest recomputed from exact PREPARED digest + nonce;
- expected provider ID and generation;
- expected predecessor shared-anchor position and exact successor position;
- deterministic shared-anchor request ID;
- PREPARED status with `receipt_binding IS NULL`.

The self-check includes negative cases for:

1. changed confirmation nonce;
2. changed PREPARED digest;
3. stale provider generation expectation;
4. stale shared-anchor predecessor/tail expectation.

Each negative case must fail closed with `PreparedCrossBindingError`.

## Validation actually executed

Before publication:

- `python -m py_compile` on the authored verifier: PASS;
- isolated functional self-check with compatible test doubles for the two imported reference modules: PASS, including all four negative cases.

After publication:

- branch commit: `9fe1d87b6d1e9740163a529834a9ca36107624df`;
- GitHub blob for the verifier: `1979346f2372f7daf8a0a2dcc31743ab22e50c1a`;
- local `git hash-object` of the exact published text: `1979346f2372f7daf8a0a2dcc31743ab22e50c1a` — byte-exact match.

This is test-owned oracle validation only. The repository RED-intent suite has not executed; no production LAB-099 RED/GREEN claim is made.

## Audit

The verifier deliberately takes the current durable provider generation and shared-anchor predecessor position as explicit expected authority inputs rather than trusting values recovered from the materialization row itself. This keeps stale provider/tail replays fail-closed and avoids converting a mutable local recovery row into authority.

No production `activation_reservation_provenance` code, fixture mutation plan, provider call, or mutable authentication subsystem was added.

## Result / next boundary

PR #186 remains draft/test-only. Relative to pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, the branch is now ahead 15 / behind 0.

The next safe fallback is to wire this verifier into the crash-after-atomic-PREPARED RED-intent fixture path so it reads the actual two SQLite rows produced by `install_atomic_prepared_cutover()` and proves that only their exact frozen cross-binding is resumable; add row-level tamper variants for nonce/digest/provider/tail/request ID without adding production behavior until repository RED can be observed.
