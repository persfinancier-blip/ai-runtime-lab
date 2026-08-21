# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-071 — test whether credential authority can become revocable at operation time by keeping raw secret bytes inside a trusted broker and authenticating every mediated request using kernel-observed per-message sender identity instead of transferring plaintext credential capability to the target process.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-070.
- LAB-070 Issue #131 DONE.
- LAB-070 PR #132 squash-merged as `6a242b96761d0df6c74ed325658a0fa52139d2c5`.
- Active Issue #133 / LAB-071 — IN_PROGRESS.
- Active branch: `lab/071-brokered-credential-use`.
- Active PR: none yet.

## Last completed step

LAB-070's exact-source merge gate was closed. The exact PR-head executable files were reconstructed through GitHub connector content, their local `git hash-object` values matched the published branch blobs, and the real-process corrected/unsafe suites were executed directly. Exact regressions for LAB-069, LAB-030, and LAB-031 were also reconstructed from current `main` and executed. A fresh remote patch audit found no blocking defect; PR #132 was marked ready and squash-merged normally.

The next gap was then selected from LAB-070's proven boundary: generation rotation cannot revoke a readable credential FD already held by a live process, and once plaintext is read no kernel descriptor mechanism can stop copying through another allowed channel. Issue #133 / LAB-071 was created and branch `lab/071-brokered-credential-use` was started.

Current primary-source evidence for the new direction: Linux `unix(7)` specifies that `SO_PASSCRED` attaches `SCM_CREDENTIALS` containing the credentials of the sending process to each received message, while `SO_PEERCRED` is connection-time peer identity and `SCM_RIGHTS` transfers file descriptors like `dup(2)`. This gives a falsifiable hypothesis: a trusted broker can keep the secret and reject a grandchild using a transferred request socket because per-message kernel sender identity changes.

## Evidence produced

- LAB-070 exact PR-head protocol blob: `1c80f73bcbe12d3a3fb1e3b520f8cf8d1077297b`.
- LAB-070 exact corrected-test blob: `d965cd0ecd41acde63f00250e97c426574265203`.
- LAB-070 corrected exact suite: 8/8 passed.
- LAB-070 unsafe CLOEXEC-only seed: failed as expected because target→grandchild propagation succeeded.
- LAB-069 exact regression: 14/14 passed.
- LAB-030 exact regression: 11/11 passed.
- LAB-031 exact regression: 8/8 passed.
- Compileall passed for the exact reconstructed sources/regressions.
- Fresh PR #132 remote patch audit: no blocking finding at head `7f7ab2f056c52c0fd47083ca3221079438b37f76`.
- PR #132 normal squash merge: `6a242b96761d0df6c74ed325658a0fa52139d2c5`.
- Issue #131 updated with final validation evidence and closed DONE.
- Issue #133 / LAB-071 created and moved IN_PROGRESS.
- Branch `lab/071-brokered-credential-use` created from current `main`.

## Known blockers / constraints

- No owner-level/external blocker.
- Direct shell GitHub clone has been unreliable due DNS in this runtime; connector-based exact-source reconstruction remains the supported fallback.
- `SCM_CREDENTIALS` / `SO_PASSCRED` behavior is Linux-specific and must not be presented as portable IPC authentication.
- The corrected broker design must not trust caller-supplied PID/UID/GID fields; only kernel-provided ancillary credentials are admissible.
- Numeric PID alone is not process-instance authority; LAB-031 pidfd/starttime rules must be reused for the consequential authorization decision.
- Privileged processes can have broader ability to specify credentials; the experiment must record the privilege/capability boundary and run the untrusted target without authority that could forge another process identity.
- A broker can withhold raw credential and revoke future operations, but it cannot prevent an authorized target from leaking results/data that policy legitimately returns to it.

## Exact next action

Resume Issue #133 / branch `lab/071-brokered-credential-use`. Build the smallest real-process prototype around an AF_UNIX datagram/socketpair with broker-side `SO_PASSCRED`. First reproduce an unsafe connection/socket-only policy where a target passes the request FD to a grandchild and the broker accepts it. Then implement per-message `SCM_CREDENTIALS` verification bound to task, operation/scope, credential generation, request identity, and target process instance using LAB-031-style PID/starttime/pidfd validation. Prove a legitimate target request succeeds, a transferred FD used by the grandchild is rejected, rotation rejects subsequent old-generation requests while the original target remains alive, duplicate/UNKNOWN retry is idempotent, and raw secret never leaves broker evidence. Run exact relevant LAB-069/LAB-070/LAB-031 regressions, perform a remote patch audit, and only then integrate.

## Backlog

- #133 / LAB-071 — brokered credential use, per-message sender identity, and revocable operation authority — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
