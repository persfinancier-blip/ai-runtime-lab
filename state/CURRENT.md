# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from credential routing/scope correctness to secret-material observability correctness: credentials that are correctly authorized for transport must still never escape through logs, traces, exceptions, evidence, or replay state.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-025.
- LAB-025: Issue #48 DONE; PR #49 remote patch-audited and squash-merged as `975b901c3b40c3a0c4a5803e3c7c9952cea436af`.
- Next issue: #50 / LAB-026 Secret-material observability, redaction, and evidence-boundary conformance — READY.
- Active branch: none yet for LAB-026.
- Active PR: none.

## Last completed step

LAB-025 separated origin Authorization, cookie/session state, Proxy-Authorization, transport route identity, and effect identity. It requires credentials to be selected again for the current authority/route rather than copied across redirect/fallback. The corrected exact-source suite passed 16/16 plus compileall; the unsafe baseline leaked Authorization, Cookie and Proxy-Authorization as intended. Remote patch audit confirmed five bounded new files and PR #49 was squash-merged.

## Evidence produced

- `research/2026-08-19-credential-scope-redirect-leakage.md`
- `experiments/credential_scope/`
- LAB-025 corrected suite: 16/16 passed.
- LAB-025 unsafe forwarding seed: failed as intended.
- PR #49 audited HEAD: `4fdbe9274c4cf5c1271ba3136694a40a4533810b`.
- PR #49 merge: `975b901c3b40c3a0c4a5803e3c7c9952cea436af`.
- Primary-source claims rechecked in the integration run against RFC 9110, RFC 6265 and RFC 9449.
- Issue #50 / LAB-026 created as the next executable security/correctness gap.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub merge endpoint can be blocked before execution; audited small/file-scoped conflict-free changes may use the documented Contents API fallback.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.
- LAB-025 is a deterministic credential-routing contract, not a browser cookie jar, OAuth server, secret manager, or real HTTP/proxy implementation.

## Exact next action

Select Issue #50 / LAB-026. Research at least three primary-source mechanisms for secret-safe telemetry/credential handling. Create a task branch and deterministic observability/evidence harness fed with LAB-025-style credential material. Falsify raw serialization/logging, then implement a single fail-closed redaction boundary covering structured nested fields, case variants, exceptions and replay snapshots; use keyed non-reversible secret identity where correlation is required. Run the bounded matrix, audit, exact-source validate, and integrate only after no raw secret bytes can enter durable observability/evidence outputs.

## Backlog

- #50 / LAB-026 — READY, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
