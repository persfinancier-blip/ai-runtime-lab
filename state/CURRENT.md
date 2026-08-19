# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from durable observability secrecy to ephemeral credential-delivery and process-boundary correctness: correctly scoped and redacted credentials must also avoid argv/environment/temp-file/inheritance leakage and unnecessary lifetime.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-026.
- LAB-026: Issue #50 DONE; PR #51 remote patch-audited and squash-merged as `5c2faad83fbec7261eed1e9164beee6700af7258`.
- Proposed next track: LAB-027 / ephemeral credential delivery, process-boundary leakage, cleanup, rotation and lifetime conformance.
- Follow-up GitHub Issue creation was attempted in this run but the connector operation was blocked before execution by an external safety-status gate; no issue was created.
- Active branch: none.
- Active PR: none.

## Last completed step

LAB-026 introduced a single fail-closed boundary for logs, traces, exceptions, evidence and replay snapshots. Raw credential bytes are removed recursively; credential identity/scope/generation remain auditable; keyed HMAC is used when secret correlation is required instead of raw low-entropy hashing. An unsafe serializer retained raw Authorization bytes as intended. The first corrected implementation exposed a real `API_KEY` canonicalization defect; it was fixed before integration.

## Evidence produced

- `research/2026-08-19-secret-observability-boundary.md`
- `experiments/secret_observability/`
- Primary sources: OpenTelemetry sensitive-data guidance/log data model/supplementary processing guidance and RFC 6750 bearer-token security.
- Exact branch blob SHA: protocol `1461f26d4f999b3db05e687efa2871cb67ca36ac`; tests `509dfc292cf2da3e1c31b1c5d361ec15ff6a94fb`; both matched locally executed exact-source copies.
- Exact-source corrected suite: 13/13 passed; compileall passed.
- PR #51 audited HEAD: `d8ca0f30825e0b02d00df9a7316405fad1393138`.
- PR #51 merge: `5c2faad83fbec7261eed1e9164beee6700af7258`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub operations can be blocked before execution by an external safety-status gate; treat this as a per-operation/tool limitation and use safe supported fallbacks where one exists.
- Follow-up issue creation for LAB-027 is currently not durable as an Issue because the create-issue operation was blocked before execution; the complete intent is preserved here instead.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.

## Exact next action

Start LAB-027 from this state even if issue creation remains blocked: research current primary-source guidance for credential delivery across process boundaries; create a task branch; build a deterministic harness that falsifies argv/environment/temp-file leakage and validates scoped ephemeral delivery, child inheritance control, cleanup, rotation, retry/UNKNOWN behavior, and non-secret evidence identity. Retry creating the GitHub Issue with concise neutral wording when the connector permits, but do not let issue-creation failure block research execution. Audit and exact-source validate before integration.

## Backlog

- LAB-027 — ephemeral credential delivery/process-boundary leakage/lifetime conformance — READY from durable state; Issue creation pending connector availability.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
