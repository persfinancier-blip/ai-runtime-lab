# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from transport endpoint + TLS/proxy identity binding to credential-scope correctness: origin credentials, cookies/session material and proxy credentials must not leak or change authority across redirect, fallback, rotation or retry.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-024.
- LAB-024: Issue #46 DONE; PR #47 remote patch-audited and squash-merged as `5ac3af8c17a81c66f5e5a1f3b7e4acb6542fc75a`.
- Next issue: #48 / LAB-025 Origin/proxy credential scope and redirect leakage conformance — READY.
- Active branch: none yet for LAB-025.
- Active PR: none.

## Last completed step

LAB-024 compared RFC 9525 service identity, RFC 6066/RFC 8446 SNI semantics and RFC 9110/RFC 9112 CONNECT authority. It built a deterministic fake TLS/proxy harness binding LAB-022 request identity and LAB-023 endpoint evidence to TLS SNI/certificate DNS-ID, route kind, proxy identity/policy generation, CONNECT authority, proxy-side resolution and stable effect identity.

Two unsafe seeds failed as intended: IP-only trust accepted a wrong TLS identity at the correct IP, and certificate-only trust accepted CONNECT/proxy endpoint drift. The corrected exact-source suite passed 14/14 plus compileall. Audit found and fixed two cross-layer defects: route fingerprint initially omitted payload/purpose/authorization generation, and endpoint evidence origin was not checked against authorized origin.

## Evidence produced

- `research/2026-08-19-tls-origin-proxy-binding.md`
- `experiments/tls_proxy_binding/`
- LAB-024 corrected suite: 14/14 passed.
- LAB-024 unsafe seeds: 2/2 failed as intended.
- Exact-source protocol blob: `cc4828b2f112263412309316fac57016c37d9189`.
- Exact-source corrected test blob: `dd75509153481063e28a032ffb409e7345b00990`.
- Exact-source unsafe seed blob: `1d4355f8dc75daca2d5e4aac8035c70c672c95b9`.
- PR #47 merge: `5ac3af8c17a81c66f5e5a1f3b7e4acb6542fc75a`.
- Issue #48 / LAB-025 created as the next executable security/correctness gap.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub merge endpoint can be blocked before execution; audited small/file-scoped conflict-free changes may use the documented Contents API fallback.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.
- LAB-024 is a deterministic adapter contract, not a real TLS/CA/proxy implementation; production adapters still need runtime-specific conformance.

## Exact next action

Select Issue #48 / LAB-025. Research at least three primary-source credential-scope mechanisms (HTTP Authorization/proxy auth, redirects, cookies or sender-constrained tokens). Create a task branch and deterministic credential-routing harness with separate origin/proxy credentials. Falsify naive header forwarding across authority changes, then bind credential use to canonical authority/path/proxy generation and request/effect identity. Test redirect, fallback, credential rotation and retry-after-UNKNOWN; audit, exact-source validate and integrate only after the bounded matrix passes.

## Backlog

- #48 / LAB-025 — READY, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
