# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-079 — compose the LAB-078 authenticated migration checkpoint with the existing LAB-034–037 external monotonic-anchor boundary so a whole-store rollback cannot erase or rewind a completed migration while remaining internally consistent.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-078.
- Completed Issue #147 / LAB-078.
- Merged PR #148 / LAB-078 as `2fc3190ac1ff2fea670b625aaa6eee8716b83d46`.
- Active: Issue #149 / LAB-079 — IN_PROGRESS.
- Active branch: `lab/079-migration-anchor-binding`.
- Active PR: none yet.

## Last completed step

LAB-078 passed its final exact-source gate and was integrated normally. A connector-reconstructed checkout matched 27/27 executable/test files to GitHub Git-blob identities. Observed tests: LAB-078 supported/crash 22/22, LAB-078 reference 10/10, LAB-077 final audit 4/4, LAB-076 supported audit 3/3, LAB-075 protocol+audit regressions 43/43; 82/82 passing test methods in the gate. The unsafe auto-promotion seed failed as expected with `1 != 0`. `python -m compileall -q experiments` passed. A final post-execution patch audit found only one stale research-note sentence, which was corrected before merge without changing executable bytes.

PR #148 was marked ready and squash-merged with expected HEAD `066a84c931327cdc5d826b0ddc3c78f44107aaaa` as `2fc3190ac1ff2fea670b625aaa6eee8716b83d46`. Issue #147 is DONE.

No other open PR remained, so the next correctness bottleneck was selected: LAB-079 migration↔external-anchor composition. Issue #149 was created and branch `lab/079-migration-anchor-binding` was created from current `main`.

## Evidence produced

- LAB-078 final merge: `2fc3190ac1ff2fea670b625aaa6eee8716b83d46`.
- LAB-078 final audited branch HEAD: `066a84c931327cdc5d826b0ddc3c78f44107aaaa`.
- 27/27 exact reconstructed executable/test blobs matched GitHub identities.
- 82/82 observed passing tests in final gate; unsafe legacy auto-promotion failed as expected; compileall passed.
- Issue #149 / LAB-079 created and moved IN_PROGRESS.
- Branch `lab/079-migration-anchor-binding` created from current `main`.

## Known blockers / constraints

- No owner/product blocker.
- Direct shell GitHub DNS may remain unavailable; GitHub connector reconstruction is a proven exact-source fallback.
- LAB-078 local checkpoint authentication does not by itself detect restoring the entire SQL store to a pre-migration but internally valid snapshot.
- LAB-079 must reuse LAB-034–037 monotonic-anchor/authentication mechanisms rather than inventing a second anchor trust root.
- A SQL migration commit that has not yet been durably reflected by the external anchor must not become consequential authority; UNKNOWN anchor outcome needs explicit reconciliation/catch-up.
- Do not conflate rollback detection with distributed consensus or backup durability.

## Exact next action

On `lab/079-migration-anchor-binding`, locate the merged LAB-034–037 anchor implementation and tests, identify the smallest supported authority/observation/catch-up surface, and import/reuse it directly. Reproduce the unsafe baseline by snapshotting the real LAB-078 SQLite database before migration, completing migration locally, then restoring the pre-migration DB while leaving the external anchor at its post-migration position; show that LAB-078 alone cannot distinguish that rollback. Then implement a migration-anchor binding that commits exact LAB-078 checkpoint identity/cutoff/terminal authority to an external monotonic position, with explicit `SQL_COMMITTED_ANCHOR_PENDING`/UNKNOWN reconciliation semantics. Test pre-migration rollback with anchor ahead, crash between SQL commit and anchor advance, timeout-after-anchor-commit, same-position checkpoint substitution, unavailable/stale anchor, clean restart, and post-migration LAB-077 successor. Persist code/research/tests on the branch, open a draft PR, run regressions, audit, and update this handoff.

## Backlog

- #149 / LAB-079 — migration checkpoint monotonic-anchor binding and rollback conformance — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
