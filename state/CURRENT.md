# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-081 — preserve verification of historical shared-anchor receipts across authenticated provider-generation rotation while keeping new-effect authority restricted to the current provider generation.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-080.
- Active: Issue #153 / LAB-081 — IN_PROGRESS.
- Active branch: `lab/081-provider-generation-history`.
- Active draft PR: #154 `[LAB-081] Historical provider generation continuity`.
- Current published PR HEAD observed at creation: `50373e4af6d7dfaeaf342f86cc074dc4f24946a8`.

## Last completed step

A first LAB-081 slice was implemented and published. It introduces durable content-addressed provider-generation descriptors, exact same-provider N→N+1 transition proofs authenticated by both old and new generation keys, a durable current-generation head, historical signed-receipt persistence, current-only new-effect authority, and restart verification of the provider history.

The isolated corrected suite passed 12/12 and compileall passed before publication. The research note records TUF root continuity as the donor mechanism: explicit persisted trust-generation continuity rather than caller-supplied historical keys.

A separate audit then found a cross-layer race in the intended LAB-080 integration: checking for PREPARED shared-anchor work outside the provider-rotation transaction is unsafe because reserve can race between check and head update. A local refactor exposing a transaction-internal `_rotate_locked(...)` passed the same 12/12 tests, but those corrected bytes are not yet published and therefore are not claimed as PR-head evidence.

Direct `git clone` was probed in this run and failed before checkout because `github.com` DNS resolution is unavailable. GitHub connector remains the durable read/write route.

## Evidence produced

- Draft PR #154.
- Branch `lab/081-provider-generation-history`.
- `experiments/provider_generation_history/protocol.py`.
- `experiments/provider_generation_history/tests/test_protocol.py`.
- `experiments/provider_generation_history/README.md`.
- `research/2026-08-22-provider-generation-history.md`.
- Isolated corrected local suite: 12/12 passed.
- Compileall: passed.
- Remote PR patch audit performed on the first published slice.
- Primary donor: TUF root-update continuity (old-root + new-root authorization and rollback rejection).

## Known blockers / constraints

- No owner/product blocker.
- PR #154 must remain draft until the actual LAB-080 integration and exact-source regression gate pass.
- The published first slice does not yet durably capture LAB-036 signed observations at LAB-080 confirmation, so it cannot yet verify mixed old/new LAB-080 ledger history after rotation.
- PREPARED check and provider-generation rotation must be one SQLite write transaction against the shared LAB-080 database; a separate pre-check is a known race.
- Historical generations are verification-only and must never regain new-effect authority.
- Provider-generation lifecycle is not provider consensus, cross-provider failover, HSM custody, or general PKI.

## Exact next action

Resume Issue #153 / PR #154. First publish the transaction-safe `_rotate_locked(...)` refactor. Then implement the real LAB-080 integration surface over exact merged `SupportedSharedAnchorLedger`: use the same database, serialize PREPARED check + generation-head rotation in one `BEGIN IMMEDIATE`, persist the exact signed provider observation when an entry becomes CONFIRMED, and override historical reauthentication so old CONFIRMED receipts are verified with the exact authenticated historical generation while current external reads/new increments still require the current generation. Add a mixed-history test with one old CONFIRMED entry, provider rotation, one new CONFIRMED entry, restart, component verification across both entries, old-generation new-effect rejection, and rotation-vs-PREPARED serialization. Then reconstruct exact PR-head bytes through the GitHub connector, run LAB-081 + LAB-080 + LAB-036 regressions, unsafe baseline and compileall, perform a fresh remote patch audit, and only then consider PR #154 ready for merge.

## Backlog

- #153 / LAB-081 — historical anchor-provider generation continuity and receipt verification — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
