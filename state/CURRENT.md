# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-072 — finish proof that concurrent/restarted broker workers serialize one mediated effect behind LAB-071 kernel sender authority, with SQL as the single durable credential-generation authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-071.
- Active Issue #135 / LAB-072 — IN_PROGRESS.
- Active branch: `lab/072-transactional-broker-journal`.
- Draft PR #136 `[LAB-072] Transactional broker request journal`.
- Current PR HEAD: `e0e2c454535e81086d35cf79e2e2c4df8afa3b86`; GitHub reports mergeable, draft intentionally.

## Last completed step

A fresh audit found that LAB-072 claimed SQL was the sole durable credential-generation authority while restart still required callers to supply the current generation. After rotation, a restarted broker using the bootstrap value could not reopen the journal.

The branch now adds `reopen_journal()`: restart reads generation from the existing SQL `broker_meta`, refuses missing/corrupt state instead of silently bootstrapping, constructs the journal with that durable generation and runs `verify_durable()`.

## Evidence produced

- Direct `git clone` attempted in this runtime and failed because `github.com` DNS resolution is unavailable.
- Current branch `protocol.py` fetched via GitHub connector and reconstructed exactly; local `git hash-object` = `6066d90b3032eeefc0f2dbbd272c09a9a716b5b2`, matching GitHub.
- Exact protocol plus restart-helper regressions: 16/16 passed (13 existing journal tests + 3 new reopen tests).
- Compileall for `experiments/transactional_broker_journal` passed.
- New branch commits: `afebead67c0df2d0b7647f6abfa56aa151b32f76` (`reopen.py`) and `e0e2c454535e81086d35cf79e2e2c4df8afa3b86` (`test_reopen.py`).

## Known blockers / constraints

- No owner-level blocker.
- PR #136 remains draft because the full current integration HEAD has not yet been executed from exact published bytes.
- Manual reformat/reconstruction is not accepted as exact-source evidence; blob identities must match GitHub.
- Remaining exact execution covers `authorized.py`, process-integration tests, LAB-071, LAB-015, LAB-031 and compileall.
- The idempotent sink remains an adapter contract; external systems without stable idempotency/reconciliation cannot inherit the same UNKNOWN semantics.
- SQLite is a local serialization reference, not distributed consensus or a PostgreSQL performance claim.

## Exact next action

Resume Issue #135 / draft PR #136 at HEAD `e0e2c454535e81086d35cf79e2e2c4df8afa3b86`. Reconstruct exact executable bytes for `authorized.py`, `test_authorized_process_integration.py`, LAB-071 dependencies/tests, LAB-015 and LAB-031 regressions through the GitHub connector and verify every local file with `git hash-object` against GitHub blob IDs. Execute those exact suites plus compileall. Then perform a fresh full PR patch audit; fix and rerun any finding. Only if all exact-source evidence is clean should PR #136 be marked ready, merged, Issue #135 closed, and the next highest-value unblocked task selected.

## Backlog

- #135 / LAB-072 — concurrent broker request serialization + transactional effect journal — IN_PROGRESS; draft PR #136.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
