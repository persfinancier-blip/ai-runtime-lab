# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-078 — define and prove an explicit authenticated migration/checkpoint ceremony for moving pre-LAB-077 single-signature sink-registry history onto the threshold-publication supported surface without silently promoting legacy authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-077.
- LAB-077 Issue #145 — DONE.
- LAB-077 PR #146 marked ready and normally squash-merged as `f6f79cf84b3c76763a8bb1dc89068048a312c199` after its unchanged audited/tested head `0bcaf33325a2ea2ac223e137d4839c58526268b9` passed the prior exact-source gate.
- Active: Issue #147 / LAB-078 — IN_PROGRESS.
- No LAB-078 branch/PR yet.

## Last completed step

The external pre-execution draft→ready blocker on PR #146 cleared on retry. The PR head was re-fetched unchanged, GitHub still reported it mergeable, the normal ready transition succeeded, and the normal squash merge succeeded with merge SHA `f6f79cf84b3c76763a8bb1dc89068048a312c199`. Issue #145 was closed completed.

With no other open issue remaining, the highest-value direct correctness gap was selected from LAB-077's explicit migration boundary: existing LAB-076 single-signature registry rows are intentionally not auto-promoted into threshold-authenticated history. LAB-078 will make that upgrade path explicit and authenticated rather than weakening LAB-077.

## Evidence produced

LAB-077 final gate (from the audited unchanged PR head):
- exact-source LAB-077 discovery: 27/27 passed;
- root-rotation/publication threaded race: 20 iterations inside the passing suite;
- LAB-076 regression: 12/12 passed;
- LAB-075 protocol + audit regression: 43 passing test executions;
- LAB-074 capability integration: 18/18 passed;
- unsafe one-signer seed failed as expected;
- compileall passed;
- fresh remote patch audit had no unresolved blocker;
- normal ready transition and squash merge completed in this run.

LAB-078 issue #147 records the initial acceptance matrix: canonical checkpoint binding exact legacy history/heads/generation/cutoff; current threshold authorization; verification-only legacy prefix; threshold-only suffix; restart reconstruction; fail-closed partial/substituted/stale migration; terminal receipt safety; and unsafe auto-promotion baseline.

## Known blockers / constraints

- No owner/product blocker.
- LAB-078 implementation has not started yet.
- Migration must not turn historical LAB-076 single-signature rows into new publication authority.
- Pending INTENT/UNKNOWN state must not silently inherit stronger post-migration authority; CONFIRMED remains receipt-only.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- Direct GitHub clone may be unavailable per-run; connector reconstruction remains an allowed exact-source fallback.

## Exact next action

Inspect the merged LAB-077/LAB-076 SQL schemas and supported worker surfaces and design the smallest canonical migration checkpoint. The checkpoint must bind a deterministic digest of the exact legacy registry/history prefix, terminal LAB-076 authority/root ID and version, registry heads, capability heads, credential generation, and a cutoff sequence. Authorize that checkpoint with the current LAB-077 threshold authority in the same `BEGIN IMMEDIATE` transaction that records migration state, after re-reading the exact authority/head state. Build an unsafe auto-promotion baseline first, then corrected tests for one-signer rejection, omitted/substituted legacy row, stale checkpoint after root rotation, partial migration/restart, pending INTENT/UNKNOWN behavior, CONFIRMED receipt-only behavior, and first threshold-only publication after migration. Persist a branch/PR only after the first corrected slice actually executes.

## Backlog

- #147 / LAB-078 — authenticated migration checkpoint for pre-threshold sink-registry history — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
