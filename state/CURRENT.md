# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-067 — add an authenticated, generation-bound retirement lifecycle for superseded archive namespace generations after LAB-066 relocation, without giving current-generation scavenging implicit authority over historical/detached namespaces.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-066.
- LAB-066 Issue #123 DONE; PR #124 squash-merged as `6eabf19baa76e231d366e9a43d0a788d5421623b` after exact-source 58/58 regression evidence.
- Active Issue #125 / LAB-067 — IN_PROGRESS.
- Active branch: `lab/067-namespace-retirement`.
- Draft PR #126 — HEAD `f3047139e022927234a643cf0a3bfb63f5988f2e` at first slice publication.

## Last completed step

Recovered repository truth after LAB-066 merge and started LAB-067. Direct shell clone was re-probed and still failed DNS (`Could not resolve host: github.com`), so GitHub connector remains the supported source/write fallback.

Built and published the first LAB-067 authority-policy slice. It defines an authenticated retirement permit binding exact predecessor/successor record IDs, both namespace generations, the successor archive-chain commitment and policy generation. The policy protects the current generation, requires the successor to be current and auditable, requires strong reacquisition of the superseded object immediately before destructive cleanup, and emits an idempotent retirement receipt/watermark. A deliberately unsafe pathname-only cleanup baseline demonstrates deletion without namespace authority.

## Evidence produced

- `experiments/namespace_retirement/protocol.py`
- `experiments/namespace_retirement/tests/test_protocol.py`
- `experiments/namespace_retirement/tests/unsafe_path_expected_failure.py`
- `experiments/namespace_retirement/README.md`
- `research/2026-08-21-namespace-retirement.md`
- Isolated corrected suite: 10/10 passed.
- Unsafe baseline: failed as expected because pathname-only cleanup deleted the protected directory.
- `compileall` passed.
- Branch was ahead 6 / behind 0 when draft PR #126 was opened; all six paths were new.

## Known blockers / constraints

- No owner-level blocker.
- Draft PR #126 is intentionally not merge-ready: the current code is an isolated authority model, not yet real `SignedPrunableHistory` / LAB-063 integration.
- Strong reacquisition remains fail-closed when `open_by_handle_at` is unavailable; do not weaken detached retirement to pathname/byte trust.
- Old namespace bytes are storage-reclamation candidates only; deletion is not forensic secure erasure.
- Whole-store rollback/freshness remains delegated to LAB-034–037.
- Direct shell GitHub DNS is unavailable in the observed runtime; connector reconstruction is required for exact-source validation if this persists.

## Exact next action

Resume Issue #125 / draft PR #126. Extend the real LAB-066 `RestartNamespaceContinuityMixin` so successful relocation durably records authenticated predecessor→successor lineage and a `RETIRED_PENDING` retirement row before/with the generation CAS. Add a real retirement integration layer that: (1) verifies the exact current successor continuity row; (2) audits the complete reachable committed archive chain in the successor namespace; (3) strongly reacquires the exact superseded continuity object, never pathname/bytes alone; (4) uses a permit bound to predecessor/successor IDs, generations, chain commitment and policy generation; (5) records idempotent durable retirement watermark/receipt; and (6) fences LAB-063 cleanup so current-generation authority cannot erase retired-generation paths implicitly. Add real tests for stale permit, wrong pair, byte-identical replacement, symlink replacement, current-generation target, incomplete successor chain, crash/retry and unsupported strong reopen. Then reconstruct exact PR source through connector if clone remains unavailable, run LAB-067 plus LAB-066/LAB-063 regressions and compileall, perform a separate remote patch audit, and merge only if all gates are clean.

## Backlog

- #125 / LAB-067 — authenticated namespace retirement and detached-generation cleanup — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
