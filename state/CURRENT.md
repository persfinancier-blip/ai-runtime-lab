# Current Lab State

Last updated: 2026-08-23

## Active objective

Finish LAB-085 by validating and integrating the post-merge concurrency fix in PR #164: intermediate public-custody verification must observe symmetric history, public history, and their binding under one write-excluding SQLite interval.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Previously integrated LAB-085 PR: #162 — squash-merged as `9aa67f3aae9a3cb25aadd50e62c85c29af533980`.
- Active fix branch: `lab/085-postmerge-snapshot-fix`.
- Active draft PR: #164 `[LAB-085] Fence intermediate custody verification to one SQLite snapshot`.
- PR #164 audited/current HEAD: `dbc5e440378e4bb6e6ed29600362645c0c47b722`.
- Follow-up only after LAB-085 is truly DONE: Issue #163 / LAB-086.

## Last completed step

The current invocation re-fetched PR #164, confirmed it is unchanged/mergeable/draft at the audited HEAD, and repeated the lock-graph audit. The new outer `BEGIN IMMEDIATE` fences concurrent writers while lower LAB-085 verification uses separate read transactions; no nested write-lock defect or new patch-content blocker was found.

Direct shell GitHub networking was re-probed and remains unavailable: DNS fails for GitHub hosts and direct TLS-by-known-IP with correct hostname/SNI also failed. GitHub connector access remains healthy, so the run switched to exact path-by-path reconstruction using the PR recursive tree/blob identities as the manifest.

The reconstruction path is now proven, not hypothetical. Exact files are written locally and checked with `git hash-object`; a semantically equivalent but reformatted dependency produced a different blob hash and was rejected rather than counted as evidence. After reconstructing the changed verification surfaces and their required runtime dependencies, the exact PR test modules executed successfully:

- `test_public_custody_supported`: 9/9 passed, including `test_intermediate_verification_holds_one_write_excluding_interval`;
- `test_final_supported`: 2/2 passed, including the final-surface write-excluding barrier regression;
- total exact changed-surface verification in this run: 11/11 passed;
- compileall over the reconstructed LAB-085/LAB-084/LAB-083/LAB-082/LAB-080/LAB-036 source subset completed successfully.

A noisy artifact/spreadsheet warmup hook emitted an unrelated startup traceback during Python invocations, but the unittest and compileall processes themselves returned success; no repository test depended on that warmup.

## Evidence produced

- PR #164 HEAD remains `dbc5e440378e4bb6e6ed29600362645c0c47b722`; GitHub reports `mergeable=true`, `draft=true`.
- Fresh patch audit: exactly `final_supported.py`, `public_custody_supported.py`, and `tests/test_public_custody_supported.py`; no unrelated paths or new blocking defect.
- Fresh lock-graph audit: no nested write-lock defect found under the new write-excluding boundary.
- Exact reconstructed/hash-verified files include:
  - LAB-085 `public_custody_supported.py` → `4c338c75f1c61420438fcfe462955bd1a7ed9c92`;
  - LAB-085 `final_supported.py` → `3baf405499c5d996cd5b4f08d8a710c121247daf`;
  - LAB-085 `asymmetric_custody.py` → `771e2ae8cde15ce06297a9cf4a94c4b3f0d81dd4`;
  - LAB-085 `protocol.py` → `c59723c018da6ce49ff19073697d859d5a9be709`;
  - LAB-085 `supported.py` → `df4f17152cddefb66dc7f4e7f76f3112d3ab4733`;
  - LAB-085 `custody_break_glass.py` → `f49139d80d13a3716817b79f0733cc0bc5d5bcac`;
  - changed LAB-085 test `test_public_custody_supported.py` → `1cd74f1e90cfa4baa943f2025fa107ceb81d324d`;
  - LAB-085 `test_final_supported.py` → `43eda5cc1e67a35cd2c1fa77f6323393f118dcd7`;
  - LAB-084 `protocol.py` → `d464e1335b0cdda9b0387d345e293d766aa0d199`;
  - LAB-084 `supported.py` → `f0b45f52df3182091874694365536b44cda3de4b`;
  - LAB-083 `protocol.py` → `688f3961afd9e7593fbe14c308453cfde67d23a8`;
  - LAB-083 `supported.py` → `59337e73f157dbb2f8437c74b3f496507a0ce989`;
  - LAB-083 `enablement.py` → `49e9a79dfa53268ce1eb32404f488ee720b41df9`;
  - LAB-083 `strict.py` → `9e96b19e4e83f045b1155b9b41894fd26762227e`;
  - LAB-082 `protocol.py` → `a2fc3456233930d94aaaca5fe57b1debd50cbdab`;
  - LAB-082 `integration.py` → `23ae688c22a1b74bde49ac506544778b2659bad6`;
  - LAB-082 `supported.py` → `d61bcd544c001de7108de42aafdc54069d0029bf`;
  - LAB-080 `protocol.py` → `68834409363c93eee4e9a9a7b9ec076098af0acf`;
  - LAB-080 `supported.py` → `22a05c04831f65c1d7fe9077df3bb780c4008e09`;
  - LAB-036 `anchor_attestation/protocol.py` → `15d8b7cf8ff093490ccb75679030d3a0fe41e401`.
- Exact PR-head changed-surface tests observed this run: 11/11 passed.
- Compileall over the currently reconstructed source subset: passed.
- Issue #161 continuation comments `5385736463` and `5385764079` record network/lock/reconstruction observations.
- Prior immutable evidence remains historical only for the not-yet-rerun full lower stack: LAB-085 38/38; LAB-080/082/083/084 87/87; focused custody 8/8; unsafe seed expected failure; compileall passed.

## Known blockers / constraints

- Do not merge PR #164 or mark LAB-085 DONE yet: the conservative gate still requires exact reconstruction/execution of the remaining unchanged LAB-085 tests plus LAB-080/082/083/084 regression tests and LAB-085 unsafe seed.
- Direct shell GitHub networking is unavailable in the current runtime. Connector reconstruction is the safe supported exact-source route.
- Connector reconstruction is exact but path/chunk based; every reconstructed executable/test file must match its Git blob before execution.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain HMAC-verifiable compatibility history. LAB-086 owns their migration only after LAB-085 closes.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Continue connector reconstruction using the Git tree/blob manifest, prioritizing the remaining unchanged LAB-085 test modules (`test_asymmetric_custody.py`, `test_custody_break_glass.py`, `test_protocol.py`, `test_supported_integration.py`, `unsafe_self_swap_expected_failure.py`) and then the LAB-080/082/083/084 test suites. Hash-check every reconstructed file, run the complete LAB-085 corrected suite + lower regressions + unsafe seed + compileall. If all are clean, perform one final remote patch audit, mark PR #164 ready, merge normally with expected HEAD, verify merged file blob identities, close Issue #161 DONE, and only then begin Issue #163 / LAB-086.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; changed verification surfaces exact-tested 11/11, remaining full regression gate pending.
- #163 / LAB-086 — READY only after LAB-085 DONE; migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
