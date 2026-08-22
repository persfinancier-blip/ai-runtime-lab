# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-079 — compose the authenticated LAB-078 migration checkpoint with the existing LAB-034–037 external monotonic-anchor boundary so a whole-store rollback cannot erase or rewind a completed migration while remaining internally consistent.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-078.
- Active: Issue #149 / LAB-079 — IN_PROGRESS.
- Active branch: `lab/079-migration-anchor-binding`.
- Active draft PR: #150 `[LAB-079] Bind migration checkpoint to authenticated monotonic anchor`.
- Current audited PR HEAD after first slice: `0db2709534cf29c7df629950e4bf1549684df542`.

## Last completed step

Located and inspected the existing anchor mechanisms instead of creating a new trust root: LAB-035 `anchor_catchup` provides monotonic catch-up/UNKNOWN semantics and LAB-036 `anchor_attestation` provides authenticated provider/generation/challenge observations. LAB-078 exposes the exact supported migration checkpoint/mixed-history verifier.

Built the first LAB-079 composition slice. It stores a migration binding sequence in the same SQLite database as LAB-078, binds that sequence to the exact checkpoint ID/cutoff/terminal authority digest, and requires LAB-036 authenticated external position confirmation before migration authority becomes consequential. Whole-store rollback rewinds the SQLite sequence while the external anchor remains ahead, which is detected on restart. SQL-committed-but-unanchored migration remains `PENDING`; timeout-after-anchor-commit uses stable request identity for reconciliation. Provider/generation mismatch, same-position checkpoint substitution, unavailable anchor, anchor rollback, and unexplained anchor-ahead states fail closed.

Draft PR #150 was opened. A first remote patch inspection found no immediate file-scope blocker, but the PR is intentionally not ready because the current execution evidence uses deterministic reference fixtures rather than the exact merged LAB-078/LAB-036 dependency stack.

## Evidence produced

- `experiments/migration_anchor_binding/protocol.py`
- `experiments/migration_anchor_binding/supported.py`
- `experiments/migration_anchor_binding/tests/test_protocol.py`
- `experiments/migration_anchor_binding/tests/unsafe_local_only_expected_failure.py`
- `experiments/migration_anchor_binding/README.md`
- `research/2026-08-22-migration-anchor-binding.md`
- Corrected reference matrix: 11/11 passed.
- Unsafe local-only rollback seed: failed as expected.
- `python -m compileall -q experiments/migration_anchor_binding`: passed.
- Direct shell clone probe failed with `Could not resolve host: github.com`; connector reconstruction remains the exact-source fallback.
- Draft PR #150 at HEAD `0db2709534cf29c7df629950e4bf1549684df542`.

## Known blockers / constraints

- No owner/product blocker.
- PR #150 is not merge-ready yet: exact real integration with merged LAB-078 and LAB-036 has not been executed in this slice.
- Direct shell GitHub DNS is unavailable in this runtime; GitHub connector reconstruction is the supported exact-source fallback.
- A migration checkpoint that exists locally but lacks confirmed external binding is intentionally non-consequential.
- This slice fails closed when the external anchor is ahead by an unexplained later position; a future shared-ledger composition may relax that only by proving all intervening intents.
- Do not conflate rollback detection with distributed consensus, backup durability, or a new anchor trust root.

## Exact next action

Reconstruct exact PR #150 executable/test bytes plus the merged LAB-078 `SupportedMigrationCoordinator` and LAB-036 `AttestedCatchup` dependency files through the GitHub connector, verify each local reconstruction with `git hash-object`, and run a real integration test against the actual LAB-078 SQLite schema. Specifically: create a real LAB-078 migration, bind it through an authenticated LAB-036 provider, snapshot/restore the SQLite DB to a pre-migration state while leaving the external anchor ahead, and require rollback detection; then cover SQL-commit-before-anchor catch-up, timeout-after-anchor-commit reconciliation, provider/key-generation rejection, same-position checkpoint substitution, current-anchor unavailable, restart, and a post-migration LAB-077 threshold successor. Run LAB-079 + LAB-078 + LAB-036 regressions and compileall, perform a fresh full PR patch audit, fix anything found, and only then mark PR #150 ready/merge.

## Backlog

- #149 / LAB-079 — migration checkpoint monotonic-anchor binding and rollback conformance — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
