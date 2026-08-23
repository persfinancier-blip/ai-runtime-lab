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

The current invocation re-fetched AGENTS.md, SELF_RESUME.md, Issue #161, PR #164 metadata and the complete three-file patch. PR #164 remains unchanged, draft, mergeable, and exactly at the previously audited HEAD.

A fresh lock-graph audit checked the new outer `BEGIN IMMEDIATE` boundary against the lower LAB-085 verifier. `SupportedRecoveryAuthorityLifecycleLedger.verify_durable()` opens only a separate read transaction for its lower-history pass; the final/intermediate surfaces therefore fence concurrent writers without introducing a nested write transaction. No new content defect was found in the three-file patch.

The invocation also re-probed exact-source acquisition instead of assuming prior network behavior. Shell DNS currently fails for `github.com`, `raw.githubusercontent.com`, and `api.github.com`. Direct TLS attempts to multiple known GitHub frontend IPs while preserving `github.com` hostname/SNI also failed to connect. GitHub connector access remains healthy. A connector-base64 reconstruction probe successfully recreated `experiments/provider_threshold_rotation/strict.py` locally and `git hash-object` matched GitHub blob `9e96b19e4e83f045b1155b9b41894fd26762227e`, proving the exact-byte fallback route works, although the full dependency/test tree is not yet reconstructed.

Issue #161 received a durable continuation comment recording the unchanged PR HEAD, lock-graph audit, current runtime network observations, and unchanged exact-source merge gate.

## Evidence produced

- PR #164 current HEAD remains `dbc5e440378e4bb6e6ed29600362645c0c47b722`; GitHub reports `mergeable=true`, `draft=true`.
- Fresh PR #164 patch audit: exactly `final_supported.py`, `public_custody_supported.py`, and `tests/test_public_custody_supported.py`; no unrelated paths or new blocking defect.
- Fresh lock-graph audit: lower `SupportedRecoveryAuthorityLifecycleLedger.verify_durable()` uses a read transaction; no nested write-lock defect found under the new outer `BEGIN IMMEDIATE` boundary.
- Current-run network probe: GitHub DNS unavailable; direct TLS-by-IP with SNI also unavailable; connector remains available.
- Connector exact-byte proof: reconstructed `provider_threshold_rotation/strict.py` hashes to GitHub blob `9e96b19e4e83f045b1155b9b41894fd26762227e`.
- GitHub recursive tree for PR #164 HEAD was successfully retrieved, so all exact path/blob identities are available for staged reconstruction.
- Issue #161 continuation comment ID `5385736463` records these observations.
- Prior immutable evidence remains historical only, not rewritten as current-head execution: LAB-085 38/38; LAB-080/082/083/084 87/87; focused custody 8/8; unsafe seed expected failure; compileall passed.

## Known blockers / constraints

- The full exact-source current-head regression stack has not yet executed in this invocation. Do not merge PR #164 or mark LAB-085 DONE before that gate.
- Direct shell GitHub networking is unavailable in the current runtime. Connector reconstruction is the safe supported exact-source route.
- Connector reconstruction is exact but must be done path-by-path/chunk-by-chunk for larger files; every completed local file must be checked with `git hash-object` against the recursive-tree/blob identity before execution.
- Historical LAB-084 break-glass proofs before the authenticated custody cutoff remain HMAC-verifiable compatibility history. LAB-086 owns their migration only after LAB-085 closes.
- Whole-store rollback freshness remains a separate external-anchor responsibility.

## Exact next action

Continue staged connector reconstruction of PR #164 HEAD `dbc5e440378e4bb6e6ed29600362645c0c47b722` and the exact merged LAB-080/082/083/084 executable/test dependencies, using the recursive Git tree as the authoritative blob manifest. Verify every reconstructed file with `git hash-object`. Execute the LAB-085 corrected suite including `test_intermediate_verification_holds_one_write_excluding_interval`, then LAB-080/082/083/084 regressions, LAB-085 unsafe seed, and compileall. If any test fails, fix and repeat. If all are clean, perform one final remote patch audit, mark PR #164 ready, merge normally with expected HEAD, verify merged file blob identities, close Issue #161 DONE, and only then begin Issue #163 / LAB-086.

## Backlog

- #161 / LAB-085 — IN_PROGRESS; post-merge concurrency defect patched in draft PR #164, exact-source gate pending.
- #163 / LAB-086 — READY only after LAB-085 DONE; migrate historical LAB-084 HMAC recovery proofs to asymmetric/public-verification history.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
