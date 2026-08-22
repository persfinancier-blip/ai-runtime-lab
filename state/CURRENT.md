# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-081 — preserve verification of historical shared-anchor receipts across authenticated provider-generation rotation while keeping new-effect authority restricted to the current provider generation.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-080.
- Completed Issue #151 / LAB-080.
- Merged PR #152 / LAB-080 as `ddcc12e56243cfbe5ccdad56baa874e583720223`.
- Next: Issue #153 / LAB-081 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-080 added an authenticated shared monotonic-anchor intent/receipt ledger over LAB-036. Multiple components may share one provider only when every intervening external position is explained by a contiguous CONFIRMED ledger suffix and freshly reauthenticated exact provider requests. A commit-boundary SQL re-read fences ledger mutation before watermark advancement.

The final audit also hardened restart state: the supported boundary now verifies `reserved_position` against the exact contiguous ledger tail, validates PREPARED/watermark structure, and explicitly fails closed when retained entries belong to a historical provider generation that LAB-036 can no longer verify.

PR #152 passed its exact-source execution/audit gate and was squash-merged normally.

## Evidence produced

- LAB-080 merge: `ddcc12e56243cfbe5ccdad56baa874e583720223`.
- Final PR #152 HEAD before merge: `d3ceb7450c2f52b1a3514d8a67a6ea7edaecb9d2`.
- Exact protocol blob: `68834409363c93eee4e9a9a7b9ec076098af0acf`.
- Exact primary tests blob: `d2d127fb67147dda2c5f6786731c0a3310a067e6`.
- Exact restart tests blob: `aa9b0f3784f97b14b59b128a2e7686e94848d377`.
- Exact supported boundary blob: `22a05c04831f65c1d7fe9077df3bb780c4008e09`.
- Exact supported tests blob: `763ee7f6958ed6fda1adde402452fedde5046ea1`.
- Merged LAB-036 dependency blob executed locally: `15d8b7cf8ff093490ccb75679030d3a0fe41e401`.
- Corrected exact-source LAB-080 suite: 18/18 passed.
- Unsafe monotonic-only seed failed as expected.
- Compileall passed.
- Race regression proved mutation of an externally verified ledger slice is detected before watermark commit.

## Known blockers / constraints

- No owner/product blocker.
- LAB-080 intentionally fails closed across provider-generation rotation because LAB-036 verifies only the currently configured provider key/generation. This is now the highest-value correctness/availability gap.
- Historical verification must not allow an old/revoked provider generation to authorize new increments.
- Provider-generation lifecycle is not provider consensus, cross-provider failover, HSM custody, or general PKI.

## Exact next action

Start Issue #153 / LAB-081. Create a branch and reproduce the current-key-only availability cliff plus an unsafe caller-supplied historical-key baseline. Build a durable authenticated provider-generation history that separates current publication/effect authority from historical receipt verification. Integrate it with LAB-080 so old CONFIRMED receipts remain verifiable after rotation while only the current generation can create new anchor requests. Cover rollback, same-generation key substitution, missing/corrupt transition proof, cross-provider substitution, rotation around PREPARED work, restart, and a ledger containing CONFIRMED entries from both old and new generations. Run exact-source LAB-081 + LAB-080 + LAB-036 regressions and audit before integration.

## Backlog

- #153 / LAB-081 — historical anchor-provider generation continuity and receipt verification — READY.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
