# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-082 — replace LAB-081 durable historical HMAC verification material with Ed25519 public verification-only history while preserving LAB-080 shared-anchor serialization/restart semantics and the existing external rollback boundary.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-081.
- Active: Issue #155 / LAB-082 — IN_PROGRESS.
- Branch: `lab/082-asymmetric-provider-history`.
- Draft PR #156: open and intentionally draft.
- Current branch/PR HEAD: `1ac3447260ce8e9b8f61f7c53039dd19cc97f37d`.
- Latest compare against `main`: branch `ahead 12 / behind 3`; all 9 branch changes are new LAB-082 paths. PR metadata currently reports `mergeable=false`, so final integration must re-evaluate after the exact-source gate rather than assuming mergeability.

## Last completed step

Integrated the LAB-082 Ed25519 history behind the real LAB-080 SQLite shared-anchor boundary instead of leaving it as an isolated reference subsystem. Reservation reads the provider head in the same `BEGIN IMMEDIATE` transaction that appends PREPARED work; provider rotation rejects unresolved PREPARED work and advances the asymmetric head under that same SQL serialization boundary.

Current LAB-036 HMAC observations are used only for execution-time authentication. Once reconciliation is authenticated, the current Ed25519 signer signs exact provider/generation/position/request evidence. CONFIRMED history can then be verified after rotation/restart from public Ed25519 material without retaining the old LAB-036 HMAC key.

A separate concurrency audit found that two workers can reconcile the same committed request using different fresh challenges, producing two different but valid signatures. A new audited `SupportedAsymmetricHistoricalSharedAnchorLedger` now treats the first valid exact-request-bound durable receipt as canonical and converges later workers onto it. It also accepts a concurrent PREPARED→CONFIRMED advance only when request identity and receipt binding match exactly.

## Evidence produced

- New branch integration: `experiments/asymmetric_provider_history/integration.py`.
- New audited supported surface: `experiments/asymmetric_provider_history/supported.py`.
- New cross-layer tests: `tests/test_integration.py` and `tests/test_supported.py`.
- README and research note updated with the real integration boundary and non-goals.
- Issue #155 and PR #156 descriptions updated to match actual state.
- PR #156 remains open/draft with 9 changed LAB-082 files; branch comparison is ahead 12 / behind 3.
- Previously observed isolated pre-integration evidence remains only: corrected protocol suite 16/16, unsafe symmetric baseline failed as expected, compileall passed.
- Direct GitHub shell access was re-probed in this run and still fails before checkout: `Could not resolve host: github.com`.
- No exact-source execution is claimed for the new integrated PR-head bytes.

## Known blockers / constraints

- No owner/product blocker.
- Exact-source regression execution of the integrated/current PR head remains the primary merge gate.
- Direct shell checkout is unavailable in this runtime; reconstruct exact bytes via GitHub connector and verify Git blob identities before execution.
- The branch is behind current `main` by 3 commits. Its changed paths are currently all new LAB-082 paths, but re-check compare/mergeability after validation before integration.
- The base integration class is experimental; the audited consumption surface is `SupportedAsymmetricHistoricalSharedAnchorLedger`.
- Ed25519 removes signing capability from durable historical storage itself, but does not claim that an independently retained old private key cannot sign.
- Whole-store rollback/bootstrap freshness remains delegated to LAB-034–037 and later external/shared-anchor layers; an internally consistent old DB plus matching old trust can still pass local LAB-082 verification.

## Exact next action

Re-fetch PR #156 and its exact current HEAD. Reconstruct exact executable bytes through the GitHub connector and verify each Git blob identity. Execute:

1. LAB-082 `test_protocol`, `test_integration`, and `test_supported`;
2. LAB-082 unsafe symmetric expected-failure seed;
3. merged LAB-081 provider-generation-history regressions;
4. merged LAB-080 shared-anchor-intent-ledger regressions;
5. merged LAB-036 anchor-attestation regressions;
6. `python -m compileall -q experiments` (or the bounded relevant experiment paths if full-tree runtime is excessive).

Then perform a fresh full remote patch audit and re-run `main...branch` comparison. If all exact-source tests are clean and HEAD is unchanged, resolve any non-content base divergence through a normal supported path, mark PR #156 ready, squash-merge, close Issue #155 DONE, and select the next highest-value unblocked research gap. If execution exposes a defect, fix it on the branch, add a regression, and repeat the exact-source gate before merge.

## Backlog

- #155 / LAB-082 — asymmetric provider receipts and cryptographic verification-only history — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
