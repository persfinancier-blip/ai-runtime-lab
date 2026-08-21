# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-066 — reconstruct archive namespace authority after process restart without silently trusting pathname, recycled inode/mount identifiers, or byte-identical replacement; support explicit generation-bound relocation and fail-closed detached-artifact handling.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-065.
- Active Issue #123 / LAB-066 — IN_PROGRESS.
- Active branch: `lab/066-namespace-reacquisition`.
- Draft PR #124 / LAB-066 — HEAD `58635a7ab26226bc88e7d024044563e61a58a468`.

## Last completed step

Integrated the authenticated continuity record into real `SignedPrunableHistory` on PR #124. The history now persists `archive_namespace_continuity`, authenticates the stored record on restart, attempts strong reacquisition before consequential compaction, and exposes explicit reacquisition status/generation. Authenticated migration uses an exact predecessor record/generation CAS before advancing namespace generation.

A separate audit caught an important restart bug in the first integration: the existing LAB-065 constructor always created a missing archive directory before LAB-066 could classify it, which would turn a detached/missing authoritative object into a newly-created pathname object. The constructor now probes for a persisted continuity row first and only creates the archive directory on first initialization; restart never recreates a missing authoritative namespace before reacquisition.

Added real SignedPrunableHistory integration tests for unchanged restart, byte-identical directory replacement blocking compaction, and symlink replacement. Direct shell clone was probed again in this run and failed with `Could not resolve host: github.com`; exact-source regression execution therefore remains a required connector-reconstruction gate, not assumed evidence.

## Evidence produced

- Existing isolated LAB-066 suite before this integration: 10/10 passed; unsafe path+bytes baseline failed as expected; compileall passed.
- New branch integration: `experiments/namespace_reacquisition/integration.py`.
- Real `experiments/signed_history_compaction/protocol.py` now includes `RestartNamespaceContinuityMixin` and restart-safe no-recreate behavior.
- New real integration tests: `experiments/namespace_reacquisition/tests/test_signed_compaction_restart_integration.py`.
- Audit defect fixed: missing/detached restart no longer silently creates a replacement archive directory.
- PR #124 remains draft/non-mergeable; no merge attempted without exact-source regression evidence.

## Known blockers / constraints

- No owner-level blocker.
- Direct shell GitHub DNS remains unavailable in this run; GitHub connector reconstruction is the supported exact-source fallback.
- `open_by_handle_at` is not usable in the observed runtime without `CAP_DAC_READ_SEARCH`; do not silently weaken detached recovery to pathname trust.
- Opaque handles are filesystem-dependent and can become stale; mount IDs and `st_dev/st_ino` are not universal persistent cross-boot identities.
- LAB-063 scavenger is not yet fenced by `require_namespace_authority()`; this is the remaining cross-layer correctness gap.
- Namespace generation is persisted and migration-fenced, but LAB-065 publication receipts/evidence do not yet carry the generation; bind it before declaring DONE.
- Whole-store rollback/freshness remains LAB-034–037. Local cleanup is not forensic secure erasure.

## Exact next action

Resume PR #124. First fence LAB-063 `scan` and destructive cleanup on `layer.require_namespace_authority()` when the layer exposes it, so detached/replaced namespaces cannot be enumerated or erased. Then bind `namespace_generation` into LAB-065 publication evidence/receipts and reject stale-generation publication at pre-SQL-commit verification. Add missing/detached restart, authenticated relocation, stale-generation, and scavenger-refusal integration tests. Reconstruct the exact PR HEAD source through the GitHub connector if shell DNS remains unavailable; run LAB-066 plus LAB-065/LAB-062/LAB-063 regressions and compileall; perform a separate remote patch audit; merge only if all gates are clean.

## Backlog

- #123 / LAB-066 — restart namespace reacquisition and detached-artifact reconciliation — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
