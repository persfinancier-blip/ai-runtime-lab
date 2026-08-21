# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-072 — finish proof that concurrent/restarted broker workers serialize one mediated effect behind LAB-071 kernel sender authority, with SQL as the single durable credential-generation authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-071.
- Active Issue #135 / LAB-072 — IN_PROGRESS.
- Active branch: `lab/072-transactional-broker-journal`.
- Draft PR #136 `[LAB-072] Transactional broker request journal`.
- PR HEAD observed at run start: `e003c9be35b2ac0a07b4a371fad2ff7ad636c531`; GitHub reports mergeable, draft intentionally.

## Last completed step

The exact current published bytes for the LAB-072 journal core and restart helper were reconstructed through the GitHub connector because shell DNS still cannot resolve `github.com`. Local `git hash-object` matched the GitHub blob IDs for `protocol.py`, `reopen.py`, `test_protocol.py`, and `test_reopen.py`. Those exact files then passed the journal + restart suites 16/16, including the existing-only/no-file-creation restart regression.

A fresh source audit then found a new merge blocker: `TransactionalJournal.verify_durable()` accepts any persisted `request_digest` of length 64 and does not require lowercase hexadecimal SHA-256 encoding. A corrupted 64-character non-hex digest can therefore pass restart verification even though it is the durable request/idempotency identity.

## Evidence produced

- Direct `git clone` / remote probe still fails in the shell because `github.com` DNS resolution is unavailable.
- Exact GitHub/local blob matches:
  - `protocol.py`: `6066d90b3032eeefc0f2dbbd272c09a9a716b5b2`
  - `reopen.py`: `4e0b5a8e3434db38d898e78c83804551d2db3f47`
  - `test_protocol.py`: `656284062a96b7915e3283b181c58bd7a8e9281d`
  - `test_reopen.py`: `50fcead0c9bf3045ca3f15ab2bb9550f2a86102b`
- Exact journal + reopen tests: 16/16 passed.
- Issue #135 updated with the malformed-digest audit finding and required regression.
- No merge was attempted; PR #136 remains draft.

## Known blockers / constraints

- No owner-level blocker.
- Merge blocker: durable request digest parsing is not fail-closed; require exact lowercase hex SHA-256 validation and regression coverage.
- Full exact integration gate still includes LAB-072 process integration plus LAB-071/LAB-015/LAB-031 regressions and compileall.
- Manual reformat/reconstruction is not accepted as exact-source evidence; blob identities must match GitHub.
- The idempotent sink remains an adapter contract; external systems without stable idempotency/reconciliation cannot inherit the same UNKNOWN semantics.
- SQLite is a local serialization reference, not distributed consensus or a PostgreSQL performance claim.

## Exact next action

Resume Issue #135 / draft PR #136. Patch `TransactionalJournal.verify_durable()` so every persisted `request_digest` must be exactly 64 lowercase hexadecimal characters, and add a regression that corrupts a stored digest to 64 non-hex characters and requires `CorruptJournal` on verification/reopen. Publish the fix to the existing branch, reconstruct the new exact branch bytes, verify Git blob identities, and rerun journal + reopen. Then complete exact LAB-072 process integration, LAB-071/LAB-015/LAB-031 regressions and compileall. Perform a fresh full PR patch audit and fix/rerun any finding. Only after a clean gate should PR #136 be marked ready, merged, Issue #135 closed, and the next highest-value unblocked task selected.

## Backlog

- #135 / LAB-072 — concurrent broker request serialization + transactional effect journal — IN_PROGRESS; draft PR #136.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
