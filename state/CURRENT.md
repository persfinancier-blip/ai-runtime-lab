# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-072 — finish proof that concurrent/restarted broker workers serialize one mediated effect behind LAB-071 kernel sender authority, with SQL as the single durable credential-generation authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-071.
- Active Issue #135 / LAB-072 — IN_PROGRESS.
- Active branch: `lab/072-transactional-broker-journal`.
- Draft PR #136 `[LAB-072] Transactional broker request journal`.
- Current PR HEAD: `e003c9be35b2ac0a07b4a371fad2ff7ad636c531`; GitHub reports mergeable, draft intentionally.

## Last completed step

A fresh restart audit found that the first `reopen_journal()` used ordinary `sqlite3.connect(path)`. On a missing path SQLite creates an empty database before the helper raises, contradicting the fail-closed restart/no-bootstrap contract. The branch now opens restart state with SQLite URI `mode=rw`, requiring an existing database, and the regression asserts the missing path remains absent after failure.

Fix commits: `1849abad12527bb9aab2fcbb423360ecaada5aee` (existing-only reopen) and `e003c9be35b2ac0a07b4a371fad2ff7ad636c531` (no-file-creation regression).

## Evidence produced

- `AGENTS.md`, prior `state/CURRENT.md`, `prompts/SELF_RESUME.md`, Issue #135 and PR #136 were reread before work.
- Direct `git ls-remote https://github.com/...` was probed in this runtime and failed because `github.com` DNS resolution is unavailable.
- GitHub connector remains usable; current PR metadata and changed paths were inspected and the restart defect was found by source audit.
- Prior exact-source evidence remains valid only for the pre-fix bytes: published `protocol.py` blob `6066d90b3032eeefc0f2dbbd272c09a9a716b5b2` previously matched executed bytes; prior exact protocol + reopen suite passed 16/16 and compileall.
- No post-fix exact-source test success is claimed yet.

## Known blockers / constraints

- No owner-level blocker.
- PR #136 remains draft because the full current integration HEAD, including the new restart fix, has not yet been executed from exact published bytes.
- Manual reformat/reconstruction is not accepted as exact-source evidence; blob identities must match GitHub.
- Remaining exact execution covers all LAB-072 executable/test files plus LAB-071, LAB-015 and LAB-031 regressions and compileall.
- The idempotent sink remains an adapter contract; external systems without stable idempotency/reconciliation cannot inherit the same UNKNOWN semantics.
- SQLite is a local serialization reference, not distributed consensus or a PostgreSQL performance claim.

## Exact next action

Resume Issue #135 / draft PR #136 at HEAD `e003c9be35b2ac0a07b4a371fad2ff7ad636c531`. Reconstruct exact current executable bytes through the GitHub connector and verify each with `git hash-object`, including the new `reopen.py` blob and no-file-creation regression. Execute LAB-072 unit + process + reopen suites, LAB-071, LAB-015, LAB-031 and compileall. Then perform a fresh full PR patch audit; fix and rerun any finding. Only if all exact-source evidence is clean should PR #136 be marked ready, merged, Issue #135 closed, and the next highest-value unblocked task selected.

## Backlog

- #135 / LAB-072 — concurrent broker request serialization + transactional effect journal — IN_PROGRESS; draft PR #136.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
