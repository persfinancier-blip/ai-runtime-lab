# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from a correct child-process authority policy model to real platform-enforcement adapter conformance: requested security dimensions must fail closed when the current runtime cannot actually enforce them.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-028.
- LAB-028: Issue #54 DONE; PR #55 remote patch-audited and squash-merged as `753ffe73be282f0c396873bd8f071c4b042bcf04`.
- Next: Issue #56 / LAB-029 `Kernel sandbox adapter conformance and fail-closed degradation` — READY.

## Last completed step

LAB-028 compared Linux no_new_privs/Landlock, Python subprocess descriptor controls, and Windows AppContainer/LPAC; built a deterministic sandbox permit binding task/workspace, sandbox generation, credential generation, read/write roots, exec, FD, local-socket and network capabilities. Unsafe broad authority failed its safety assertion; corrected local suite passed 9/9. Runtime probes observed Linux 6.18.35, `unshare` present, user namespace probe failing EINVAL, network namespace probe failing EPERM, and no exposed `/sys/kernel/security/landlock`; no unsupported kernel-enforcement claim was made.

## Evidence produced

- `research/2026-08-19-child-sandbox-authority.md`
- `experiments/child_sandbox/`
- LAB-028 merge: `753ffe73be282f0c396873bd8f071c4b042bcf04`.
- Primary sources: Linux kernel no_new_privs and Landlock docs; Python 3.14 subprocess docs; Microsoft AppContainer/LPAC docs.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- This runtime did not expose usable namespace/Landlock enforcement in the probes above; LAB-029 must treat that as observed capability data, not silently downgrade security requirements.
- OS/kernel sandbox mechanisms differ across Linux/Windows/macOS.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.

## Exact next action

Start Issue #56 / LAB-029. Create a branch, define an observed enforcement-capability report and adapter contract, probe Linux mechanisms available in the run, map Windows AppContainer/LPAC from primary docs without claiming execution, and build deterministic tests proving REQUIRED sandbox dimensions fail closed under unavailable/partial/stale enforcement. Seed an unsafe adapter that falsely reports enforcement, then audit, exact-source validate and integrate.

## Backlog

- #56 / LAB-029 — kernel sandbox adapter conformance/fail-closed degradation — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
