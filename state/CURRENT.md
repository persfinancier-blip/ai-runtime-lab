# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from application/endpoint egress binding to the remaining transport identity gap: TLS server identity/SNI and explicit proxy/CONNECT paths must preserve the same authorized origin, endpoint and effect identity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-023.
- LAB-023: Issue #44 DONE; PR #45 remote patch-audited and squash-merged as `3baff7361238a452ec38f587f306ab83407e35e6`.
- Next issue: #46 / LAB-024 TLS origin authentication and proxy-path binding conformance — READY.
- Active branch: none yet for LAB-024.
- Active PR: none.

## Last completed step

LAB-023 compared current IANA IPv4/IPv6 special-purpose registries, RFC 6890/8190 address semantics, RFC 9110 redirect semantics, RFC 3986 URI host normalization, and AWS IMDS endpoint guidance. It built a deterministic fake resolver/redirector/connector harness that preserves LAB-022 request/effect identity while validating every DNS result, redirect, and final connection endpoint.

The unsafe resolve-once/check-then-connect seed failed as intended: policy checked public `93.184.216.34`, then the connection path re-resolved the hostname and reached `127.0.0.1`. The corrected suite passed 13/13 tests and compileall. Audit tightened redirect authority so a cross-host redirect requires fresh authorization rather than inheriting the LAB-022 permit.

## Evidence produced

- `research/2026-08-19-transport-endpoint-binding.md`
- `experiments/transport_binding/`
- LAB-023 corrected suite: 13/13 passed.
- LAB-023 unsafe seed: failed as intended on public-to-loopback DNS rebinding.
- Exact-source protocol blob: `c78b9d5121be2cb8892f78227929ff658f578c2d`.
- Exact-source corrected test blob: `5d818c24f37a352af1e5aad02c41ce89010170e2`.
- Exact-source unsafe seed blob: `69f1ba20d90ff67ec7a2cca07656a31583fc0b97`.
- PR #45 merge: `3baff7361238a452ec38f587f306ab83407e35e6`.
- Issue #46 / LAB-024 created as the next executable transport-correctness gap.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- Preferred GitHub merge endpoint can be blocked before execution; audited small/file-scoped conflict-free changes may use the documented Contents API fallback.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.
- LAB-023 proves direct endpoint validation/pinning in a fake transport. It does not prove TLS certificate/SNI binding, proxy CONNECT authority, proxy-side DNS behavior, or OS/network egress enforcement.

## Exact next action

Select Issue #46 / LAB-024. Research at least three current primary-source HTTPS server-identity/SNI/proxy/CONNECT mechanisms. Create a task branch and deterministic fake TLS/proxy harness. Falsify a design that validates only socket endpoint or only certificate identity, then require authorized origin hostname, TLS peer identity, direct/proxy route identity, CONNECT target and proxy policy generation to remain bound to LAB-022 request/effect identity and LAB-023 validated endpoint. Test retry-after-UNKNOWN before any route change, audit, exact-source validate, and integrate only after the bounded matrix passes.

## Backlog

- #46 / LAB-024 — READY, highest-value executable task.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
