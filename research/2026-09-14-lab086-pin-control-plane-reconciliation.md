# LAB-086 pin / control-plane reconciliation

Date: 2026-09-14

## Result

The durable LAB-086 executable pin in `state/CURRENT.md` had drifted behind the published exact-gate manifest.

The authoritative manifest `research/2026-08-27-lab086-exact-gate-manifest.md` pins the remaining complete LAB-086 branch-local gate to:

`1fa85a0e34c9ae67da57f1e64dadccf211feacc0`

and explicitly supersedes `1f90830fca21e2f43fc241012cdd34fd187ba96d`. The superseding commit changes the stale regression schema in `test_thaw_history_key_collision_regression.py`; the LAB-086 runtime hardening in `strict_fence.py` is unchanged from `1f90830f...`.

## Per-run transport observation

The mandatory LAB-086 probe was attempted first. Direct shell Git materialization still fails before repository execution with:

`Could not resolve host: github.com`

and exit 128.

This is a transport/materialization observation only. No LAB-086 requirement is weakened and no new complete-gate PASS is claimed.

## Connector fallback audit

The GitHub connector can read the recursive tree and exact UTF-8 blobs for `1fa85a0e...`, but the complete gate requires the full branch-local LAB-080 -> LAB-086 real-ledger dependency chain plus every `test_*.py` under `experiments/asymmetric_break_glass_history/tests`, the unsafe expected-failure seed, and compileall.

The connector does not expose an automatic byte-preserving mount of those blobs into the executable filesystem in this run. Manual reconstruction of that large closure would introduce truncation/reserialization risk. Therefore the complete LAB-086 gate was not represented as executable evidence.

The previously proven small-closure discipline remains valid: connector exact content + published blob SHA -> isolated file -> `git hash-object` equality -> execute only after every file matches. It may be used again only for closures small enough to reconstruct without truncation or manual reserialization risk.

## LAB-095 fallback observation

PR #187 remains the permitted fallback. Its committed recovery suite `experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py` contains the retained cases for:

- crash-before-commit rollback;
- orphan CONFIRMED identity intent rejection before nonce generation;
- concurrent installers converging on one nonce/request;
- legacy history reserving exactly the next shared-anchor position.

These cases remain pending exact executable closure in this run; their presence in the branch is not counted as behavioral PASS evidence.

A fresh PR #187 metadata read reported the PR open/draft at head `835a81914c5234e68ef436e30c9837331d262432` and currently mergeable/clean. This is only a point-in-time GitHub metadata observation; the PR stays draft until retained exact/downstream gates and a fresh security/conflict audit are complete.

## Durable decision

`state/CURRENT.md` must use `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` for all future LAB-086 complete-gate attempts. The old `1f90830f...` pin remains historical evidence for the runtime hardening commit, not the executable source-of-truth for the remaining full gate.
