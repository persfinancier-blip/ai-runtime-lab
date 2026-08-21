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
- Active PR: none yet.

## Last completed step

LAB-068 was repaired, exact-source validated, audited and merged. Its final creation order is `PREPARED lease -> empty 0600 object + fsync -> opaque Linux file-handle identity -> ALLOCATED -> secret write/fsync -> READY`; partial-write crashes are reclaimable by exact object identity, while READY/HANDED_OFF additionally require keyed content identity. Exact/regression matrix was 56/56 plus the expected unsafe failure.

LAB-069 then proved a stronger path-compatible transport for compatible Linux tools: sealed anonymous `memfd`, `MFD_CLOEXEC` by default, explicit descriptor inheritance, no raw secret in argv/environment/evidence, stale-generation rejection and explicit LAB-068 fallback. Audit fixed incomplete sealing-capability detection and required **target-specific** procfd compatibility instead of treating a generic Python probe as authority for another tool. Exact LAB-069/LAB-027/LAB-068 matrix passed 39/39; unsafe ordinary named-path lifetime seed failed as expected.

Immediately after LAB-069 merge, a real subprocess probe exposed the next boundary: a target launched with `pass_fds=(fd,)` observed the credential FD as inheritable and deliberately passed it to a grandchild, which successfully read the secret. Parent-side `MFD_CLOEXEC` therefore does not imply single-target authority after intentional inheritance; sealing prevents mutation, not redistribution of read capability.

## Evidence produced

- LAB-068 final protocol blob: `601d4de1fb0a64fb8d5055b6e956c8dfe476ffd5`; corrected tests `9afa8fda985116cfafccb9b186e3592e5c27e61b`; 13/13 corrected, LAB-027 12/12, relevant process/namespace regressions 31/31, combined 56/56.
- LAB-069 final protocol blob: `fcb2035f71f5931dcad96ad48f649ba35edb1a81`; corrected tests `54186e46aba329adda3afe87d43ce147d54baa26`; unsafe seed `4a814d768c57345d5160d8b07b532e0f3bfbaa70`.
- LAB-069 corrected suite 14/14, exact LAB-027 12/12, exact LAB-068 13/13, combined 39/39; compileall passed.
- LAB-069 unsafe named-file lifetime seed failed as expected because a normal filesystem entry outlived all open transport descriptors.
- LAB-070 initial real-process evidence: target `os.get_inheritable(fd) == True` after `pass_fds`; target passed the same FD to a grandchild; grandchild read the credential bytes.
- Issue #131 records the full LAB-070 failure matrix and non-goals.

## Known blockers / constraints

- No external blocker.
- Once an untrusted process can read plaintext, no memfd/descriptor mechanism can prevent that process from copying bytes through other channels that policy permits. LAB-070 must not claim DRM-like secrecy.
- `MFD_CLOEXEC` protects default exec inheritance before deliberate handoff; `pass_fds` intentionally creates child authority and may make the descriptor inheritable in that child.
- Current runtime previously lacked writable cgroup delegation; single-process/process-tree guarantees must be based only on mechanisms actually re-probed and observed in the LAB-070 run.
- Descriptor sealing provides immutability, not revocation. Credential generation rotation is not authority to revoke a descriptor already held by a live authorized process/tree.
- LAB-068 remains the fail-closed named-file fallback where target-specific procfd compatibility is absent; neither LAB-068 nor LAB-069 alone solves malicious descendant exfiltration.
- Direct shell GitHub DNS has been unavailable in recent runs; GitHub connector reconstruction remains the supported exact-source fallback.

## Exact next action

Continue Issue #131 on `lab/070-memfd-descendant-authority`. Re-probe current runtime process-confinement capabilities rather than reusing old assumptions. Build a real target+grandchild harness that first preserves the observed unsafe propagation. Then implement two explicit policy modes: (1) `SINGLE_PROCESS`, which may be selected only if the runtime can actually prevent/contain descendant creation or retention; otherwise return an explicit unsupported/fail-closed result, and (2) `SUPERVISED_TREE`, which binds credential lifetime to an observed process tree and detects an unauthorized surviving descendant after the nominal target exits. Compose liveness with LAB-031/032 and enforcement/capability observations with LAB-028/030. Record raw-secret-free evidence, run exact LAB-070 plus LAB-069/LAB-030/LAB-031 regressions, perform a separate patch audit, fix findings and rerun before integration.

## Backlog

- #131 / LAB-070 — memfd descriptor propagation, descendant authority and lifetime conformance — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
