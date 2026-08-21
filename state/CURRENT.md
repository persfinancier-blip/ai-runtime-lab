# Current Lab State

Last updated: 2026-08-21

## Active objective

Finish integrating LAB-072 after exact-source validation and fresh audit; no known content/test blocker remains.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-071.
- Active Issue #135 / LAB-072 — VERIFY.
- Active branch: `lab/072-transactional-broker-journal`.
- Draft PR #136 `[LAB-072] Transactional broker request journal`.
- Audited PR HEAD: `50a771b3cc8adc743372068d016397367b1611b5`.

## Last completed step

A fresh cross-layer audit found that LAB-072 process permits were still checking request credential generation before the SQL journal. That accidentally reintroduced a second generation authority and broke restart semantics: after journal rotation, a freshly reacquired current-generation process permit could not reconcile an exact already-committed historical request.

The branch was fixed so LAB-071 process permits prove only kernel sender process identity plus task/scope. The SQL journal alone decides whether a request is an existing exact retry or a new operation. Added regressions prove a fresh current-generation process permit can reconcile an old committed request, while a genuinely new old-generation request still fails closed.

All exact-source validation and regression gates then passed. A normal draft→ready transition was attempted, but the tool operation was blocked by an external OpenAI safety-status gate before execution. No low-level ref/tree/force mutation or alternate integration bypass was attempted.

## Evidence produced

Exact current executable Git blobs reconstructed through GitHub connector and verified locally with `git hash-object`:
- `authorized.py`: `41e586fd892d211554db9bbbc5e1527960624b00`
- `protocol.py`: `6817459fca8ac37c11cce71865937b8f65567d83`
- `reopen.py`: `4e0b5a8e3434db38d898e78c83804551d2db3f47`
- `test_protocol.py`: `656284062a96b7915e3283b181c58bd7a8e9281d`
- `test_reopen.py`: `1456b2c59b79e65807418d7992bbcf5ac017e322`
- `test_authorized_process_integration.py`: `8963a7fbfb94e40806c11b1f3b767fad6d658d67`
- `test_restart_rotation_authority.py`: `1b68d6b6b20e1f9474ea4f0c2ed2bacea1a90036`
- unsafe seed: `d9c07f28c9f3f23aab5fa4fcee44b269b0013af7`

Observed validation:
- LAB-072 exact corrected suite: 26/26 passed.
- LAB-071 exact regressions: 18/18 passed.
- LAB-015 exact regressions: 13/13 passed.
- LAB-031 exact regressions: 8/8 passed.
- compileall passed.
- Exact unsafe seed failed as intended because check-then-act produced 2 side effects instead of 1.
- Fresh remote patch audit completed; stale README/research/PR claims were corrected.

## Known blockers / constraints

- No owner-level blocker and no known code/test/audit blocker.
- Integration-only blocker: external safety-status gate blocked the normal PR draft→ready operation before execution.
- Do not bypass the gate with low-level refs/trees, force updates, or alternate hidden integration.
- Direct shell DNS to `github.com` remains unavailable in this runtime; GitHub connector exact-byte reconstruction is the proven fallback for validation.
- The idempotent sink remains an adapter contract; external systems without stable idempotency/reconciliation cannot inherit the same UNKNOWN semantics.
- SQLite is a local serialization reference, not distributed consensus or a PostgreSQL performance claim.

## Exact next action

Re-fetch PR #136. Confirm it remains draft, mergeable, and at HEAD `50a771b3cc8adc743372068d016397367b1611b5` with unchanged audited patch. Retry the normal draft→ready transition. If it succeeds, perform normal squash merge with the exact expected HEAD, close Issue #135 DONE, and select the highest-value unblocked next task. If the external safety-status gate blocks again before execution, retain LAB-072 in VERIFY, record the repeated tool-level blocker, and do not bypass it.

## Backlog

- #135 / LAB-072 — concurrent broker request serialization + transactional effect journal — VERIFY; exact validation/audit complete, integration gate only.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
