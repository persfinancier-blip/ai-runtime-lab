# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from authenticated durable launch records to rollback-resistant durable freshness state. LAB-033 is complete; LAB-034 must make replay/authority watermarks transactional and explicitly define what ordinary SQL cannot guarantee under full storage snapshot rollback.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-033.
- Completed Issue #63 / LAB-033.
- Merged PR #64 / LAB-033, squash merge `8444cac994b0cee366a5fe5c0dfb1fd7a17afbeb`.
- Active next: Issue #65 / LAB-034 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-033 built a canonical HMAC-authenticated launch-record envelope and verified it before LAB-032 liveness reacquisition. The corrected matrix passed 13/13 after a remote audit found and fixed JSON metadata type confusion (`true == 1` in Python schema-version comparison). The unsafe unsigned structural-trust seed failed as expected because a forged PID was accepted. PR #64 was remote patch-audited and squash-merged.

## Evidence produced

- `experiments/launch_record_integrity/protocol.py`
- `experiments/launch_record_integrity/tests/test_protocol.py`
- `experiments/launch_record_integrity/tests/unsafe_unsigned_expected_failure.py`
- `research/2026-08-19-launch-record-integrity.md`
- Corrected deterministic suite: 13/13 passed.
- Unsafe unsigned baseline: expected failure.
- `python -m compileall -q experiments` passed.
- Pre-audit published protocol blob matched locally executed source; post-audit remote patch was separately inspected before merge.
- Primary mechanisms recorded from RFC 2104 HMAC, RFC 8785 JSON canonicalization, and RFC 9421 replay guidance.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- HMAC authenticates record content but does not create freshness by itself.
- LAB-033 replay protection currently depends on a trusted authority/generation/sequence watermark. If an attacker/storage failure rolls back both the signed record and that watermark, ordinary verification can accept stale authority.
- Ordinary transactional SQL can prevent many split-commit/concurrent-writer failures but cannot by itself prove that the whole database has not been reverted to an older snapshot; that boundary must be measured and documented rather than hidden.
- LAB-032 fresh pidfd/starttime reconciliation remains mandatory after record authenticity/freshness checks.

## Exact next action

Start Issue #65 / LAB-034. Build an SQLite transactional reference for authority epoch/key generation/task sequence watermarks; reproduce an unsafe split-commit/rollback design; test restart, stale/concurrent writer, older authenticated record, atomic rotation, duplicate current verification, crash between record+watermark updates, and simulated full snapshot rollback. Add an optional external monotonic-anchor abstraction solely to demonstrate the boundary SQL cannot cover; anchor mismatch must fail closed and no raw anchor/key secret may enter evidence. Research primary transactional/rollback sources, run deterministic tests and a separate audit, then integrate only on observed validation.

## Backlog

- #65 / LAB-034 — trusted replay-watermark durability + rollback resistance — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
