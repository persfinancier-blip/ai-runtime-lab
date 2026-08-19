# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from safe credential delivery to child-process least privilege: a credential may cross the process boundary safely while the receiving process still has excessive ambient filesystem, execution, local-socket, HOME/config, or descriptor authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-027.
- LAB-027: Issue #52 DONE; PR #53 remote patch-audited and squash-merged as `eb49db534f7dd2aa50ba38a4d5da8424030dd24e`.
- Active: Issue #54 / LAB-028 `Child-process ambient authority and local sandbox conformance`.
- Active branch: `lab/028-child-sandbox-authority`.
- Active PR: none yet.

## Last completed step

LAB-027 built and validated a deterministic credential-delivery contract. Unsafe argv/environment baselines leaked raw secret material as expected. The corrected exact-source suite passed 12/12 plus compileall. Published protocol/test/unsafe-seed Git blob SHA matched locally executed source. The audit recorded that named-temp-file cleanup is not forensic erasure and does not survive SIGKILL/power loss; production preference is dedicated OS credential facility, narrow memory-backed FD/pipe, explicit handle allowlist, with a 0600 temp file only as a constrained fallback.

## Evidence produced

- `research/2026-08-19-ephemeral-credential-delivery.md`
- `experiments/ephemeral_credentials/`
- LAB-027 merge: `eb49db534f7dd2aa50ba38a4d5da8424030dd24e`.
- Primary sources used: Linux `proc_pid_cmdline(5)`, `proc_pid_environ(5)`, `environ(7)`, `execve(2)`; POSIX exec descriptor semantics; Python `subprocess` descriptor controls; Linux memfd security documentation.
- Exact executable blob SHA: protocol `22f1941ffa9a79ac6d483ba79f8cdde698b45366`; corrected tests `30bbad0e82ca9532e1894418fa0cebea20712521`; unsafe seed `a0919ef4e45fe7454800a0e756e6d914051a3d4b`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unreliable/unavailable; GitHub connector plus local execution is the supported path.
- OS/kernel sandbox mechanisms differ across Linux/Windows/macOS; LAB-028 must separate deterministic policy-model guarantees from actually observed kernel enforcement.
- Privileged namespace/cgroup setup must not be assumed available in this runtime.
- PostgreSQL-specific locking/performance validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.

## Exact next action

Resume Issue #54 on `lab/028-child-sandbox-authority`. Research current primary-source least-privilege process mechanisms (Linux `no_new_privs`, seccomp, Landlock/namespaces as available, plus a cross-platform/runtime analogue). Build a deterministic capability/sandbox permit model that binds task/workspace/sandbox generation and LAB-027 credential generation, with explicit filesystem-read/write, exec, local-socket/network and FD capabilities. Seed a broad-authority baseline, run the required failure matrix, perform separate audit, exact-source validate, then integrate only after patch audit.

## Backlog

- #54 / LAB-028 — child-process ambient authority/local sandbox conformance — IN_PROGRESS.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up if LAB-028 does not subsume it.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
