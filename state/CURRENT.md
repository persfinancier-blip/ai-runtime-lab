# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-078 — prove an authenticated migration checkpoint that moves pre-LAB-077 single-signature sink-registry history onto the threshold-publication surface without silently promoting legacy authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-077.
- Active: Issue #147 / LAB-078 — IN_PROGRESS.
- Active branch: `lab/078-authenticated-registry-migration`.
- Draft PR: #148 `[LAB-078] Authenticated legacy registry migration checkpoint`.
- Current PR HEAD: `4d4262db741eafa68f8bb5ec2d56cee32068a102`.
- PR is currently mergeable and intentionally remains draft.

## Last completed step

Published an explicit regression for the latest retry-path authority fix. `test_idempotent_retry_reauthenticates_historical_authority` performs one supported migration, corrupts the durable historical root material, and requires an exact retry to fail rather than returning success from row equality alone.

Also reconstructed the exact current `supported.py` bytes through GitHub, verified `git hash-object == d770d1487e91b2bb3b4d78308b89e2dbf0626d8c`, and executed those exact bytes in a focused harness. The harness observed that both fresh/idempotent `migrate()` calls run `verify_mixed_history()` before returning success, durable corruption is rejected, and subclasses fail the exact-type gate.

`compare_commits` shows `main` diverged from the LAB-078 branch only through `state/CURRENT.md`; all nine LAB-078 paths are new/conflict-free. PR #148 became mergeable again after the new test commit.

## Evidence produced

- Prior reference LAB-078 slice: 10/10 passed; unsafe auto-promotion failed as expected; compileall passed in an earlier invocation.
- Prior real-schema integration suite: 8/8 passed in an earlier invocation.
- `integration.py` published blob: `69c74a8f24ac6de002b546023527bd13626ab8c1`.
- Hardened `supported.py` blob: `d770d1487e91b2bb3b4d78308b89e2dbf0626d8c`; exact reconstruction/hash verified this invocation.
- New supported/crash test blob: `ad1d45458bac87d245646c1b63dd7c0b4eb6862e`.
- Focused exact supported-surface execution: PASS for verify-on-success/retry, durable-corruption rejection, and exact-type subclass rejection.
- Current PR #148 HEAD: `4d4262db741eafa68f8bb5ec2d56cee32068a102`; 9 changed files; mergeable; draft.
- Direct GitHub shell checkout remains unavailable because `api.github.com`/`github.com` DNS does not resolve; connector reconstruction is the supported exact-source fallback.

## Known blockers / constraints

- No owner/product blocker.
- PR #148 intentionally remains draft.
- The focused exact `supported.py` harness is useful evidence but does not replace the required full exact-source LAB-078 + merged LAB-077/076/075 regression stack for current HEAD.
- Earlier 10/10 and 8/8 results predate the latest supported/test bytes and therefore are not counted as full proof for current HEAD.
- Pending `INTENT`/`UNKNOWN` must be resolved before migration; `CONFIRMED` is receipt-only history.
- Legacy LAB-076 rows remain verification-only and must never receive synthetic LAB-077 threshold proofs.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.

## Exact next action

Reconstruct the remaining exact executable bytes for PR #148 HEAD `4d4262db741eafa68f8bb5ec2d56cee32068a102` plus merged LAB-077/076/075 dependency/regression modules through the GitHub connector. Verify every reconstructed executable file with `git hash-object` against GitHub blob identity. Execute LAB-078 reference, real-integration, supported/crash (including the new durable-corruption retry regression), LAB-077, LAB-076 and LAB-075 regressions, unsafe auto-promotion seed, and compileall. Then perform a fresh full PR patch audit. Only if that full gate is clean should PR #148 be moved ready/squash-merged (or, if the normal merge endpoint is unavailable, the already audited nine new files may be integrated through the documented Contents API fallback after conflict recheck), Issue #147 closed DONE, and the next highest-value gap selected.

## Backlog

- #147 / LAB-078 — authenticated migration checkpoint — IN_PROGRESS; draft PR #148; full exact dependency/regression stack and final audit remain.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
