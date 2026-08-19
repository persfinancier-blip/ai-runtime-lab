# Current Lab State

Last updated: 2026-08-19

## Active objective

Execute LAB-022: prove egress authorization remains valid at the actual sink commit boundary and cannot be bypassed by payload mutation, redirect, stale policy generation, or replay between check and use.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-021.
- LAB-021: Issue #40 DONE; PR #41 remote patch-audited and squash-merged as `359d20087a98a262dc9a500cb1f976d1bacd83fc`.
- Next issue: #42 / LAB-022 commit-time egress authorization binding and redirect TOCTOU harness — READY.
- Active branch: none yet for LAB-022.
- Active PR: none.

## Last completed step

LAB-021 compared current OpenAI source/sink and outbound-restriction guidance, NIST SP 1800-39 data classification/labeling, and Google Sensitive Data Protection label/de-identification mechanisms. It built a deterministic source→transform→sink policy prototype. A deliberately unsafe transform dropped SECRET taint and enabled exfiltration to an untrusted sink; the unsafe test failed as intended.

The corrected suite passed 15/15 tests and compileall. Audit before publication found and fixed three authority/binding defects: forgeable boolean declassification, structurally valid but untrusted disclosure authorization, and disclosure grants not bound to the exact payload. Evidence identity was also hardened from raw content SHA-256 to keyed HMAC references to reduce low-entropy hash-oracle risk. PR #41 was remote patch-audited and merged normally.

## Evidence produced

- `research/2026-08-19-sensitive-data-egress-taint.md`
- `experiments/egress_taint/`
- LAB-021 corrected suite: 15/15 passed.
- LAB-021 unsafe taint-loss seed: failed as intended.
- PR #41 merge: `359d20087a98a262dc9a500cb1f976d1bacd83fc`.
- Issue #42 / LAB-022 created as the next executable correctness/security gap.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub merge endpoint can be blocked before execution; audited small/file-scoped conflict-free changes may use the documented Contents API fallback.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.
- LAB-021 limits labeled-data egress but does not solve covert channels, steganography, timing/metadata leakage, semantic reconstruction, incorrect source classification, or model-level prompt injection.

## Exact next action

Select Issue #42 / LAB-022. Research at least three current primary-source TOCTOU/capability/request-binding mechanisms, create a task branch, implement a deterministic prepare→commit egress permit harness that revalidates payload identity, canonical destination, purpose, policy/authorization generation, issuer, and replay/idempotency at commit, falsify an unsafe check-then-use design, run the required mutation/redirect/replay matrix, audit composition with LAB-005/LAB-015/LAB-020/LAB-021, then integrate only after validation.

## Backlog

- #42 / LAB-022 — READY, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
