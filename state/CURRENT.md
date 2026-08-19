# Current Lab State

Last updated: 2026-08-19

## Active objective

Execute LAB-023: bind authorized egress not only to canonical URL/request identity but also to the actual allowed transport endpoint across DNS resolution, redirects, retries, and connection establishment.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-022.
- LAB-022: Issue #42 DONE; PR #43 remote patch-audited and squash-merged as `a6850d12540b1ce93c7a79b7eb275deac7b62ee6`.
- Next issue: #44 / LAB-023 transport endpoint binding against DNS rebinding, SSRF, and redirect-chain drift — READY.
- Active branch: none yet for LAB-023.
- Active PR: none.

## Last completed step

LAB-022 compared RFC 9449 DPoP request binding, AWS SigV4 canonical request/payload signing, W3C capability guidance, and RFC 9700 supporting security guidance. It built a deterministic trusted-control prepare→commit permit harness bound to payload digest, canonical destination, purpose, policy generation, authenticated authorization generation/id, expiry/nonce, and stable effect identity.

The corrected exact-source suite passed 14/14 tests and compileall. The retained unsafe check-then-use seed failed as intended by committing to `attacker.example` after `trusted.example` had been checked. Audit before publication found and fixed a cross-layer regression: trusted authorization was initially represented by a forgeable structural trust flag; it was replaced with authenticated trusted-control authorization and a forged-authorization rejection test.

## Evidence produced

- `research/2026-08-19-egress-commit-binding.md`
- `experiments/egress_commit/`
- LAB-022 corrected suite: 14/14 passed.
- LAB-022 unsafe redirect TOCTOU seed: failed as intended.
- Exact-source protocol blob: `07fe1bf97bde7c8e2efd8adf0066b386c26e832c`.
- Exact-source test blob: `3d4d76416d0a8c9f001eb19574ce196d034a2af0`.
- PR #43 merge: `a6850d12540b1ce93c7a79b7eb275deac7b62ee6`.
- Issue #44 / LAB-023 created as the next executable security/correctness gap.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub merge endpoint can be blocked before execution; audited small/file-scoped conflict-free changes may use the documented Contents API fallback.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.
- LAB-022 proves application-level request binding, not network endpoint identity. Canonical URL equality alone does not defeat DNS rebinding, SSRF private-address resolution, redirect-chain drift, proxy behavior, or transport-level endpoint substitution.

## Exact next action

Select Issue #44 / LAB-023. Research at least three current primary-source SSRF/DNS-rebinding/redirect/endpoint-binding mechanisms. Create a task branch and deterministic fake resolver/redirector/connector harness. Falsify a resolve-once/check-then-connect design, then enforce revalidation of every resolution/redirect/connection endpoint including IPv4/IPv6 special ranges and retry-after-UNKNOWN. Preserve LAB-022 permit/effect identity, run the bounded matrix, audit the result, and integrate only after exact-source validation.

## Backlog

- #44 / LAB-023 — READY, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
