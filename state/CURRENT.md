# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-070 — prove the credential-capability boundary after a sealed LAB-069 memfd is intentionally inherited by a target child: distinguish single-process authority from supervised-process-tree authority and fail closed when descendant propagation cannot be constrained.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-069.
- LAB-068 Issue #127 DONE; PR #128 squash-merged as `284a29df406c0281c5f0161c860ac74371660d3a`.
- LAB-069 Issue #129 DONE; PR #130 squash-merged as `5ba1fdc9738c32c644a06eb807fb09d001a810ba`.
- Active Issue #131 / LAB-070 — IN_PROGRESS.
- Active branch: `lab/070-memfd-descendant-authority`.
- Draft PR: #132 `[LAB-070] Memfd descendant authority and lifetime conformance`.

## Last completed step

The current runtime was re-probed rather than relying on old assumptions: x86_64 seccomp filters work, `unshare -Urp --fork` works, and cgroup v2 is mounted read-only/not delegated.

A real-process LAB-070 prototype was implemented and published. Unsafe target→grandchild credential-FD propagation remains reproducible after deliberate `pass_fds`, proving `MFD_CLOEXEC` is not a single-target authority guarantee after handoff.

Two explicit corrected policy modes now exist:
- `SINGLE_PROCESS`: pre-exec `no_new_privs` + seccomp denies `fork`/`vfork`, makes `clone3` unavailable, and allows classic `clone` only with `CLONE_THREAD`; same-process pthreads therefore remain usable while descendant process creation is blocked. If observed seccomp support is absent, the mode is unsupported/fail-closed.
- `SUPERVISED_TREE`: descendants may intentionally inherit the credential inside a fresh user+PID namespace. The target is namespace PID 1; the real harness verifies a grandchild can hold/read the descriptor while the target lives and is terminated when namespace init exits. If PID namespaces are unavailable, the mode is unsupported/fail-closed.

An audit caught and fixed an initial over-broad seccomp design that would have blocked pthreads by rejecting all `clone` calls. Credential generation rotation is explicitly kept separate from live-descriptor revocation semantics.

## Evidence produced

- Branch protocol blob: `1c80f73bcbe12d3a3fb1e3b520f8cf8d1077297b`.
- Branch corrected-test blob: `d965cd0ecd41acde63f00250e97c426574265203`.
- New experiment: `experiments/memfd_descendant_authority/`.
- Research note: `research/2026-08-21-memfd-descendant-authority.md`.
- Corrected local working-copy real-process suite: 8/8 passed after the pthread audit fix.
- Unsafe CLOEXEC-only seed: failed as expected because target→grandchild propagation succeeded.
- Compileall passed.
- Primary sources recorded: Linux `memfd_create(2)`, `seccomp(2)`, and `pid_namespaces(7)`.
- Draft PR #132 opened; remote patch audit completed with no new content finding in the published slice.

## Known blockers / constraints

- No owner-level/external blocker.
- Direct shell GitHub clone still fails DNS resolution in this runtime, so exact-source reconstruction must use the GitHub connector fallback.
- The published PR-head executable bytes have not yet been fully reconstructed and executed together with the required LAB-069/LAB-030/LAB-031 regressions; PR #132 must remain draft until that gate is satisfied.
- Once an untrusted process can read plaintext, no memfd/descriptor mechanism can prevent that process from copying bytes through other channels that policy permits. LAB-070 must not claim DRM-like secrecy.
- Sealing prevents mutation, not redistribution or revocation.
- Credential generation rotation is not authority to revoke a descriptor already held by a live authorized process/tree.
- cgroup delegation is unavailable here and is not claimed as an enforcement backend.

## Exact next action

Resume Issue #131 / PR #132. Reconstruct the exact current PR-head executable files through GitHub connector responses and verify local `git hash-object` against branch blob IDs (`protocol.py` currently `1c80f73bcbe12d3a3fb1e3b520f8cf8d1077297b`, corrected tests `d965cd0ecd41acde63f00250e97c426574265203`). Execute exact LAB-070 corrected and unsafe suites plus relevant exact LAB-069/LAB-030/LAB-031 regressions and compileall. Then perform a fresh remote patch audit; if clean, mark PR ready, merge using the normal endpoint, close Issue #131 DONE, and select the next highest-value unblocked research gap. If exact-source reconstruction finds byte drift or any regression/audit failure, fix on the branch and rerun before integration.

## Backlog

- #131 / LAB-070 — memfd descriptor propagation, descendant authority and lifetime conformance — IN_PROGRESS; draft PR #132.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
