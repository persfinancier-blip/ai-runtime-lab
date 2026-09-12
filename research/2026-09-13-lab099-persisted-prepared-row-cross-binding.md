# LAB-099 persisted PREPARED row cross-binding slice

Date: 2026-09-13

## Context

LAB-086 remains priority #1. This run re-probed direct exact repository materialization first:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

The failure occurred before repository code execution. GitHub connector reads/writes remained available, but no supported byte-exact connector-to-local-executor mount/materialization primitive for the complete pinned LAB-086 closure was exposed. Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security, or current-main conflict PASS is claimed.

Per `state/CURRENT.md`, fallback work remained restricted to test-owned LAB-099 staging on draft PR #186.

## Objective

Wire the previously frozen side-effect-free PREPARED materialization/shared-anchor cross-binding oracle into the actual SQLite rows emitted by `install_atomic_prepared_cutover()`, then freeze fixture-level durable tamper cases for:

- confirmation nonce;
- PREPARED digest;
- provider generation;
- predecessor position;
- position;
- request ID.

No production `activation_reservation_provenance` behavior may be added until an executable repository RED is observed.

## Implementation

Branch: `lab-099-precursor-cutover-red-intent`

Added:

1. `experiments/provider_generation_history/tests/lab099_prepared_fixture_row_verifier.py`
   - reads exactly one `provider_activation_reservation_cutovers` row by the expected frozen PREPARED digest;
   - reads exactly one matching `shared_anchor_intents` row by the materialized anchor intent ID;
   - requires the durable shared-anchor reserved tail to equal the PREPARED row position;
   - derives predecessor position only from that durable tail (`reserved_position - 1`), while provider identity/generation remain supplied by the runtime attestation verifier rather than trusted from the recovery row;
   - delegates semantic/byte-exact checks to `lab099_prepared_cross_binding_reference.verify_prepared_cross_binding()`;
   - converts oracle mismatches into a test-owned fail-closed `PreparedFixtureRowVerificationError`;
   - exposes one narrow allowlisted test-only tamper helper for the six frozen corruption dimensions.

2. `experiments/provider_generation_history/tests/red_intent_lab099_prepared_row_cross_binding.py`
   - remains non-discoverable by default (`red_intent_*.py`);
   - builds the same real LAB-092-complete fixture used by the existing LAB-099 RED-intent contract;
   - calls `install_atomic_prepared_cutover()` and then requires read-back verification of the persisted materialization/shared-anchor PREPARED pair;
   - rebuilds a fresh fixture for each corruption case and requires verification to fail closed after each isolated durable mutation.

Branch commits:

- `1838c94f6e4331851b0068af06cdcd4ebfffc6c5` — persisted-row verifier;
- `c62cc02397c9e80383d95808ff4de71461c98b5e` — non-discoverable persisted-row/tamper contract.

Published blobs:

- `lab099_prepared_fixture_row_verifier.py`: `b21341bfe986a06fb0a91f18423383f6344dfc4e`;
- `red_intent_lab099_prepared_row_cross_binding.py`: `c67180993d7a766180bb17f68382b978f9efdfef`.

## Validation actually performed

Because exact repository materialization is still unavailable, the new branch files were not imported as part of the full repository closure and no repository RED/GREEN claim is made.

A standalone local SQLite mechanics check was executed for the new read-back invariant:

- created a minimal materialization row, matching shared-anchor PREPARED row, and singleton reserved tail;
- exact read-back returned predecessor `reserved_position - 1` and accepted the matching row shape;
- incrementing the persisted PREPARED `position` while leaving the durable reserved tail unchanged was rejected by the explicit position/tail cross-check.

Observed result: `standalone row read / tail cross-check PASS`.

The published files were fetched back through GitHub after write; the returned blobs are listed above. PR #186 remains open and draft. Compare against pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c` reports `ahead_by=17`, `behind_by=0`. The PR file list still contains only paths under `experiments/provider_generation_history/tests/`; no production LAB-099 file was added.

## Audit

Security/correctness boundaries preserved:

- persisted materialization is not allowed to self-assert provider authority;
- provider ID/generation come from the externally supplied attestation verifier;
- shared-anchor predecessor is tied to the durable reserved tail and the oracle still requires exact `position = predecessor + 1` plus exact request-ID binding;
- changed PREPARED digest fails even before semantic verification because the expected frozen digest no longer resolves to exactly one materialization row;
- changed nonce/provider generation/predecessor/position/request ID reach the oracle/tail checks and fail closed;
- all mutations are test-only, allowlisted, single-row, transactionally committed, and never exposed by production code;
- the existing frozen canonical PREPARED digest, DDL identities, payload digest, and anchor identity are not changed by this slice.

No new product/security decision was required.

## Next action

LAB-086 first: probe exact materialization again. If it becomes available, execute the pinned complete LAB-086 gate exactly as recorded in `state/CURRENT.md` before further LAB-099 work.

If it remains unavailable, continue PR #186 test-only work by auditing the CONFIRMED recovery boundary next: freeze a persisted-row read-back verifier that cross-binds the exact PREPARED materialization to a `CONFIRMED` shared-anchor entry with externally reauthenticated `receipt_binding` and the frozen CONFIRMED head/event vector. Add isolated negative durable mutations for receipt binding, confirmed position/head binding, and exact PREPARED digest ancestry. Do not add production LAB-099 behavior until the repository RED-intent suite can execute and an actual RED is observed.
