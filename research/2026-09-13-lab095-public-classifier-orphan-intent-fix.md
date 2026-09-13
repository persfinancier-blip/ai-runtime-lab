# LAB-095 public classifier orphan-intent consistency fix

Date: 2026-09-13

## Context

`database_identity_migration._classify_locked()` had already been hardened so zero custody plus an existing LAB-095 `IDENTITY_INTENT_ID` is `CORRUPT`. The public read-only `database_identity.classify_identity_custody()` still returned `ABSENT` immediately for zero custody rows and therefore disagreed with migration recovery semantics.

That disagreement matters because a persisted PREPARED or CONFIRMED identity intent is authority-bearing migration evidence. Treating it as `ABSENT` allows a caller to make a fresh-install decision from an impossible partial state.

## Change

Draft PR #187 / branch `lab-095-database-identity-red-intent` now:

- adds `_identity_intent_present()` as a read-only lookup for the exact LAB-095 intent id;
- returns `CORRUPT` when an identity intent exists with zero custody rows;
- also returns `CORRUPT` when the identity intent exists but the custody relation itself is absent;
- preserves `ABSENT` for a genuine zero-custody/no-identity-intent state;
- does not synthesize, repair, or mutate authority from the classifier.

Production commit: `c521e0f8cf49040faf2caac5e8a13d65cb4afea0`.
Production blob: `13d4b8cfb056d28969252e28905e9d20a30cb3c2`.

Regression file: `experiments/provider_generation_history/tests/test_database_identity_orphan_intent_classifier.py`.
Final regression commit: `0fc0b5233607254424ec833476b0a1e077a4ff9c`.
Regression blob: `86b4f19450c7486d5ba5a1b869c918c2a24ebbb1`.

## Validation actually executed

The preferred LAB-086 materialization path was probed first in this run. `git clone` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

A focused local SQLite semantic probe then executed the same public-classifier decision logic for four states:

1. custody table exists, zero rows, no identity intent -> `ABSENT`;
2. zero custody + orphan PREPARED identity intent -> `CORRUPT`;
3. zero custody + orphan CONFIRMED identity intent -> `CORRUPT`;
4. orphan PREPARED identity intent with no custody relation -> `CORRUPT`.

All four passed. The probe source also passed `py_compile`.

This is narrow semantic evidence, not a claim that the exact repository regression suite or downstream LAB-080/LAB-081/LAB-090/LAB-092 gates are GREEN. The full exact dependency closure is still unavailable through shell network transport in this runtime.

## Audit

The fix is intentionally read-only and fail-closed. It does not accept caller-supplied nonce/digest authority, does not mutate shared-anchor state, and does not reinterpret an unrelated anchor intent as LAB-095 authority. SQLite failures during the lookup continue to classify `CORRUPT` through the existing outer error handler.

## Next action

After the mandatory LAB-086 materialization probe, execute the already-committed LAB-095 crash-before-commit, partial-state, concurrent-installer, and legacy-prefix migration regressions on the smallest byte-exact closure that can be safely materialized. Then execute DB-A -> DB-B path-binding and LAB-080/LAB-081/LAB-090/LAB-092 downstream gates before any integration.
