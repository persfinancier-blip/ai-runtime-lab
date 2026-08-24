# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `d467c050cfcf8101650124f96c41aca33b35c017`.
- PR is open/draft/mergeable; full current-head LAB-086 real-schema gate has not passed.

## Last completed step

Closed the remaining exact LAB-085 public-custody/final regression slice in one connector-reconstructed workspace. Direct shell GitHub transport was reprobed and still fails DNS; GitHub connector reconstruction was used instead.

Every executable/test file needed for this slice was reconstructed from current `main` and checked with local `git hash-object` against its GitHub blob before execution. Newly executed tests:

`python -m unittest experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported experiments.provider_recovery_authority_lifecycle.tests.test_final_supported -v`

Result: **11/11 PASS**. `python -m compileall -q` over reconstructed LAB-036/080/082/083/084/085 dependencies also passed.

Re-fetched PR #165 after the run; current HEAD remains `d467c050cfcf8101650124f96c41aca33b35c017`. Began exact current-head LAB-086 reconstruction and recorded current implementation blobs. No new privilege-escalation blocker was established in the accompanying source audit.

## Evidence produced / reconfirmed

- Newly closed exact LAB-085 tests:
  - `test_public_custody_supported.py` blob `1cd74f1e90cfa4baa943f2025fa107ceb81d324d`.
  - `test_final_supported.py` blob `43eda5cc1e67a35cd2c1fa77f6323393f118dcd7`.
  - Combined result: **11/11 PASS**.
- Exact LAB-085 implementation bytes used included:
  - `protocol.py` `c59723c018da6ce49ff19073697d859d5a9be709`.
  - `supported.py` `df4f17152cddefb66dc7f4e7f76f3112d3ab4733`.
  - `asymmetric_custody.py` `771e2ae8cde15ce06297a9cf4a94c4b3f0d81dd4`.
  - `public_custody_supported.py` `4c338c75f1c61420438fcfe462955bd1a7ed9c92`.
  - `custody_break_glass.py` `f49139d80d13a3716817b79f0733cc0bc5d5bcac`.
  - `final_supported.py` `3baf405499c5d996cd5b4f08d8a710c121247daf`.
- Exact direct dependencies reconstructed and hash-verified in the same workspace included LAB-036, LAB-080, LAB-082, LAB-083 and LAB-084 implementation files.
- Compileall over reconstructed LAB-036/080/082/083/084/085 closure: PASS.
- Cumulative lower-stack exact evidence is now complete for the gate: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, plus the newly executed LAB-085 public/final 11/11; lower unsafe baselines failed as expected.
- Current PR #165 implementation manifest at HEAD `d467c050...`:
  - `final_supported.py` `9f0198d2db85d08ec64f614d6288323c1d642383`.
  - `migration_guard.py` `332995323d8d74fcc0f377d0e74bb0f30b8735c1`.
  - `protocol.py` `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`.
  - `strict_fence.py` `62a9b602edb8692894cad3874ba6d5c211129aa5`.
  - `suffix.py` `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078`.
- Exact standalone LAB-086 12/12 and prior focused fence evidence remain valid for unchanged files, but are not substitutes for the current full real-schema gate.
- LAB-089/#168 is already closed `not_planned`; do not treat it as active backlog.

## Known blockers / constraints

- Remaining LAB-086 merge gate is now only current-head LAB-086 real-schema tests, unsafe legacy-promotion seed, full compileall, and final security/branch-divergence audit.
- Direct shell GitHub transport is unavailable; connector reconstruction works and is not an owner-level blocker.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless a downstream test invalidates the candidate.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Finish connector reconstruction of current PR #165 HEAD `d467c050cfcf8101650124f96c41aca33b35c017` LAB-086 implementation/tests on top of the already reconstructed exact lower stack; verify each executable/test file by Git blob identity.
2. Execute the complete LAB-086 real-schema suite, including migration v4 root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface cases, inherited-history INSERT/UPDATE/DELETE fences, strict conflict algorithms, root-head INSERT/REPLACE/UPDATE/DELETE, final verification snapshot, full lower/public history guards, and rotation races.
3. Execute unsafe legacy-promotion expected-failure seed and full compileall over the complete closure.
4. Perform a fresh full security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. If the gate is clean, mark PR #165 ready and integrate by normal merge when available; otherwise use only the documented audited file-scoped Contents API fallback after exact conflict checking.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; lower-stack exact gate complete, current-head LAB-086 full real-schema gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
