# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-067 — prove a real authenticated, generation-bound retirement lifecycle for superseded LAB-066 archive namespace generations without giving current-generation LAB-063 scavenging implicit authority over historical/detached namespaces.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-066.
- LAB-066 Issue #123 DONE; PR #124 squash-merged as `6eabf19baa76e231d366e9a43d0a788d5421623b` after exact-source 58/58 regression evidence.
- Active Issue #125 / LAB-067 — IN_PROGRESS.
- Active branch: `lab/067-namespace-retirement`.
- Draft PR #126 — current audited working HEAD `21e77f976ec1c05177072d3ec4ae7aa73b627eda`; GitHub reports mergeable, but it intentionally remains draft until exact-source execution.

## Last completed step

Resumed the unfinished LAB-067 first slice and integrated it with real `SignedPrunableHistory`/LAB-066 continuity rather than leaving it as an isolated authority model.

The branch now persists a PREPARED migration intent before LAB-066 relocation, then predecessor→successor namespace lineage and `RETIRED_PENDING` state. Permit issuance re-audits the full currently reachable signed archive chain in the successor namespace and binds its commitment, exact predecessor/successor continuity IDs, both generations, and retirement-policy generation. Cleanup strongly reacquires the exact superseded namespace object and unlinks only content-addressed archive files relative to a held directory FD. Authorization is durable before cleanup and a retirement receipt/watermark is durable afterward. LAB-063 remains scoped to the current-generation namespace handle.

A separate audit found and fixed two real design defects before merge eligibility:
1. if continuity CAS committed but the process crashed before lineage finalization, restart could preinsert the current successor as a standalone ACTIVE row and then lose the predecessor through `INSERT OR IGNORE`; concrete `SignedPrunableHistory` reconciliation now verifies immutable row bytes and explicitly repairs predecessor/status/commitment;
2. allowing gen2→gen3 while gen1 remained `RETIRED_PENDING` could strand gen1 outside the one-step permit path; another relocation is now fail-closed until the pending predecessor has a retirement receipt.

Expanded real integration tests were added for signed-chain audit, restart receipt persistence, continuity-CAS crash reconciliation, crash-after-authorize, crash-after-cleanup, byte-identical and symlink replacement, unsupported strong reopen, incomplete successor chain, stale policy/commitment, current-generation protection, and LAB-063 generation fencing.

## Evidence produced

- Existing isolated LAB-067 authority model remains at `experiments/namespace_retirement/protocol.py` with prior observed corrected evidence 10/10, unsafe baseline failure, and compileall pass.
- New real integration: `experiments/namespace_retirement/integration.py`.
- New real integration tests: `experiments/namespace_retirement/tests/test_signed_integration.py`.
- Concrete composition update: `experiments/signed_history_compaction/protocol.py`.
- Research/README updated to describe the real lifecycle and remaining execution gate.
- Draft PR #126 remote patch inspection found and fixed the two defects above.
- Direct `git clone` was re-probed in this invocation and still failed with `Could not resolve host: github.com`.

## Known blockers / constraints

- No owner-level blocker and no known remaining content defect from current remote inspection.
- PR #126 remains intentionally draft because the newly integrated exact branch bytes have not yet been executed. Prior 10/10 evidence covers only the isolated reference slice and must not be misrepresented as real-integration evidence.
- Direct shell GitHub DNS is unavailable in the observed runtime. Use connector reconstruction as the supported exact-source fallback if this persists.
- Strong reacquisition remains fail-closed when the exact old object cannot be re-proven; never weaken retirement to pathname/byte equality.
- The implementation intentionally leaves the emptied retired directory object in place. Removing the pathname itself would reintroduce an unlink-by-path TOCTOU race; this work is storage reclamation, not forensic erasure.
- Whole-store rollback/freshness remains delegated to LAB-034–037.

## Exact next action

Resume draft PR #126 at HEAD `21e77f976ec1c05177072d3ec4ae7aa73b627eda`. First re-fetch PR metadata in case the head moved. Probe normal clone once; if DNS remains unavailable, reconstruct the exact executable branch files through the GitHub connector and verify each local file with `git hash-object` against its GitHub blob SHA. Execute: (1) real LAB-067 `test_signed_integration.py`; (2) isolated LAB-067 corrected/unsafe suites; (3) LAB-066 namespace-reacquisition protocol + signed-compaction restart integration regressions; (4) LAB-063 scavenger protocol + signed integration regressions; and (5) compileall for the affected experiment tree. Fix every observed failure, rerun the full matrix, then perform a fresh remote patch audit. Only after exact-source execution and a clean audit may PR #126 be marked ready and integrated; otherwise keep Issue #125 IN_PROGRESS with the precise failing case.

## Backlog

- #125 / LAB-067 — authenticated namespace retirement and detached-generation cleanup — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
