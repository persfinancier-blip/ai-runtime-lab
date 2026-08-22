# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-076 — remove LAB-075's remaining static single-key sink-registry authority assumption by making registry signing authority versioned, restart-persistent, rotation/revocation-aware, threshold-authorized, and bound to historical registry entries without reviving old signing authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-075.
- LAB-075 Issue #141 — DONE.
- LAB-075 PR #142 squash-merged as `d16b7a14f33090cb57b4b1b241a5e279a1b979df`.
- Active: Issue #143 / LAB-076 — IN_PROGRESS.
- Active branch: `lab/076-registry-authority-lifecycle-v2`.
- Active draft PR: #144 `[LAB-076] Durable sink-registry authority lifecycle`.
- Current observed PR HEAD during this run before the final documentation commit sequence: `41a5a81e2e703c9c23a7c95bbb2a3ec56c6c865c`; re-fetch HEAD before validation because additional supported/research commits were added afterward.

## Last completed step

A first coherent LAB-076 authority lifecycle was implemented by reusing the existing threshold-root/recovery primitives rather than inventing another trust system. Normal rotation requires old-root + new-root threshold proof; break-glass recovery uses a separate recovery quorum and advances the authority epoch. Authority history, current head, transition proofs, recovery-authority descriptor, and accepted-entry historical bindings are persisted in SQLite.

The first isolated lifecycle suite passed 11/11. A security audit then found that `RecoveryAuthority` is a frozen dataclass whose `keys` mapping is still mutable: the first implementation persisted only its digest while `recover()` continued using the caller-owned object. The implementation was corrected to persist the exact recovery descriptor by content ID and always load it from SQL for recovery/restart verification. A mutation regression was added; the corrected isolated lifecycle suite passed 12/12 and compileall passed.

The lifecycle was then wired directly into the audited LAB-075 journal/worker surface using the same SQLite database. New registry publication now performs current-authority verification, exact historical-authority binding, registry generation/predecessor validation, registry-row validation and registry-head activation under one `BEGIN IMMEDIATE` transaction, serializing it against authority rotation. Already-published current registry heads remain historically verifiable after signer rotation, while a never-before-published successor requires current authority.

A second integration audit found that a standalone lifecycle `accept_entry()` could pre-authorize an entry before rotation and later try to publish it as if it were historical. The integration now distinguishes lifecycle binding from actual registry publication: historical authority is sufficient only when the LAB-075 registry row already exists. A pre-authorized-but-unpublished entry must still pass current authority, and a published row missing its historical binding fails closed. A regression was added.

An explicit `experiments/sink_registry_authority_lifecycle/supported.py` surface was added so callers do not assemble unaudited verifier/worker compositions.

## Evidence produced

- Draft PR #144 is open and mergeable; it remains draft intentionally.
- Published LAB-076 paths include:
  - `experiments/sink_registry_authority_lifecycle/protocol.py`
  - `experiments/sink_registry_authority_lifecycle/integration.py`
  - `experiments/sink_registry_authority_lifecycle/supported.py`
  - protocol, real-integration and audit regression tests
  - unsafe self-swap expected-failure seed
  - `research/2026-08-22-sink-registry-authority-lifecycle.md`
- Isolated lifecycle corrected suite after durable-recovery fix: 12/12 passed.
- Unsafe ambient-authority self-swap seed: failed as expected in the unsafe design.
- Isolated lifecycle compileall: passed before the later integration files were published.
- Remote patch audit found and fixed two substantive defects in this run: mutable ambient recovery authority and stale pre-authorized orphan publication.
- TUF root-update continuity is the normal-rotation donor; existing LAB threshold/recovery primitives are reused.

## Known blockers / constraints

- No owner/product blocker.
- Direct GitHub clone/raw download is unavailable in the current runtime due DNS; connector reconstruction remains the supported fallback.
- The current integrated PR #144 head has **not yet** been executed as exact published source. Do not merge based on the earlier isolated 12/12 result.
- Exact-source regressions still required: LAB-076 protocol/integration plus LAB-075/074/073/072 and compileall.
- Historical authority is verification-only. It must never become current publication authority again.
- A lifecycle binding that was never actually published into the LAB-075 registry is not historical publication authority.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.
- Recovery-authority rotation is already owned by LAB-057; LAB-076 keeps the recovery quorum pinned rather than duplicating that subsystem.
- Distributed PKI/consensus, service discovery, and transport security remain out of scope.

## Exact next action

Re-fetch PR #144 and record its exact current HEAD and changed-file blob identities. Restore the exact published executable files through the GitHub connector if direct clone still fails. Execute the current PR-head LAB-076 protocol, real-integration, and integration-audit suites; run the unsafe self-swap seed and confirm expected failure; run the merged LAB-075/074/073/072 regression suites and compileall over the affected modules. Then perform a fresh full remote patch audit, paying special attention to mixed-snapshot durable verification and any path that could reinterpret a historical authority as publication authority. If exact-source tests and audit are clean, update Issue #143 acceptance evidence, mark PR #144 ready, squash-merge it normally, close LAB-076 DONE, and choose the next highest-value unblocked correctness gap.

## Backlog

- #143 / LAB-076 — sink-registry authority lifecycle, rotation, and restart conformance — IN_PROGRESS; draft PR #144.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
