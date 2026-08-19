# Current Lab State

Last updated: 2026-08-19

## Active objective

Finish LAB-030 integration after exact-source and remote patch audit, then choose the highest-value next gap exposed by real post-launch sandboxing.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-029.
- Active: Issue #58 / LAB-030 `Linux sandbox launcher enforcement and post-launch attestation`.
- Branch: `lab/030-linux-sandbox-launcher`.
- PR: to be created after exact-source artifact validation.

## Last completed step

Built and locally exercised a real Linux child launcher. Fresh probes observed userns, `no_new_privs` and seccomp available; network and mount namespace creation remained unavailable. The child verified `NoNewPrivs: 1`, seccomp filter mode, a deterministically denied syscall, user namespace separation and default-deny FD inheritance. Audit fixed three defects: opaque-only probe evidence, a backend-omission test that only hit signature validation, and missing seccomp audit-architecture validation.

## Evidence produced

- `research/2026-08-19-linux-sandbox-launcher.md`.
- `experiments/linux_sandbox_launcher/`.
- Corrected local tests: 11/11 passed.
- Unsafe parent-intent-only seed: expected failure.
- `python -m compileall -q experiments`: passed.
- Primary docs: Linux `no_new_privs`, seccomp filter API/seccomp(2), Python subprocess FD controls.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; connector publication + local exact-source execution is the supported path.
- Current runtime supports userns but not network or mount namespaces; REQUIRED network/filesystem confinement must remain fail-closed.
- Prototype seccomp program is x86_64-specific and deliberately minimal; it is not a production syscall policy.
- User namespace alone is not filesystem/network confinement.
- HMAC launch receipts depend on protecting the launcher signing key.
- PostgreSQL-specific validation and open-model serving remain deferred for representative environments.

## Exact next action

Fetch the published LAB-030 executable/test files through the GitHub connector, compare Git blob/content hashes with the executed local sources, rerun the corrected suite on exact fetched source if any mismatch appears, create the LAB-030 PR, perform remote patch audit, fix any defect, then integrate and close Issue #58. After closure, select the highest-value new issue exposed by the remaining boundary: launcher-policy-to-real-resource confinement and/or attestation freshness/revocation across child lifetime.

## Backlog

- #58 / LAB-030 — IN_PROGRESS, exact-source/audit/integration remains.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
