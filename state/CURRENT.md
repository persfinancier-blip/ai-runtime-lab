# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-082 — make LAB-081's historical verification-only provider state cryptographic by retaining Ed25519 public verification material in durable history while keeping private signing capability outside the database.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-081.
- Active: Issue #155 / LAB-082 — IN_PROGRESS.
- Branch: `lab/082-asymmetric-provider-history`.
- Draft PR #156 created normally this run; head `b1d3badf770f2152685108fca57a4c86aeb13cd0`.

## Last completed step

Re-read the operating contract/state/resume prompt and resumed LAB-082. Reconstructed the exact published protocol, corrected test, and unsafe-test blobs through the GitHub connector. Retried the previously blocked normal PR operation; draft PR #156 was created successfully. Per-run shell checkout was probed and still fails before checkout because `github.com` DNS cannot resolve, so no exact published-source execution is claimed for this run.

A fresh patch audit confirms the current five-file slice is still an isolated asymmetric reference subsystem rather than the LAB-081/LAB-080 supported integration. Whole-store rollback/bootstrap freshness must remain bound to the existing external-anchor layer; the isolated SQLite history must not be promoted as independently rollback-proof.

## Evidence produced

- Issue #155 updated IN_PROGRESS.
- Draft PR #156: open, draft; head `b1d3badf770f2152685108fca57a4c86aeb13cd0`.
- Exact branch blobs reconstructed via connector:
  - protocol `a2fc3456233930d94aaaca5fe57b1debd50cbdab`;
  - corrected tests `f737f71559e90e9a748fc3bd3d3e0cf90872a898`;
  - unsafe seed `f8d4cb7a30eee2373fa0c1ecdeef4d2edfdbe0ce`.
- Prior observed pre-publication evidence remains: corrected suite 16/16, unsafe symmetric baseline failed as expected, compileall passed.
- Current-run direct `git clone --branch lab/082-asymmetric-provider-history` failed with `Could not resolve host: github.com`; do not convert prior local results into exact-branch execution evidence.

## Known blockers / constraints

- No owner/product blocker.
- Direct shell GitHub checkout is unavailable in this run; connector reconstruction is the supported fallback.
- Exact published branch bytes are identified, but exact-source execution of the current PR head remains a merge gate.
- LAB-082 has not yet replaced/adapted LAB-081's historical HMAC verification behind the supported LAB-080 shared-anchor serialization surface.
- Ed25519 removes signing capability from durable historical material, but this reference does not provide HSM/KMS custody, provider consensus, cross-provider failover, PKI certificate issuance, or compromise recovery.

## Exact next action

Keep PR #156 draft. Build the integration behind merged LAB-081/LAB-080: current LAB-036 observations may be authenticated at execution time, but durable historical verification must use Ed25519 public material/signatures so no historical HMAC/private signing key is required after rotation. Preserve the same SQLite PREPARED-vs-rotation serialization and restart semantics. Add mixed-generation, restart, race, private-material-absence, receipt/capability rebinding, corruption, and whole-store rollback/bootstrap-boundary regressions.

Then reconstruct/execute exact PR-head bytes through connector fallback, run LAB-082 plus LAB-081/LAB-080/LAB-036 regressions and compileall, perform a fresh remote audit, and only mark ready/merge if clean.

## Backlog

- #155 / LAB-082 — asymmetric provider receipts and cryptographic verification-only history — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
