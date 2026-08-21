# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-071 — make credential authority revocable at operation time by retaining raw secret bytes inside a trusted broker and authenticating every mediated request using kernel-observed per-message sender identity rather than transferring plaintext credential capability to the target process.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-070.
- LAB-070 Issue #131 DONE; PR #132 squash-merged as `6a242b96761d0df6c74ed325658a0fa52139d2c5`.
- Active Issue #133 / LAB-071 — IN_PROGRESS.
- Active branch: `lab/071-brokered-credential-use`.
- Draft PR: #134 `[LAB-071] Brokered credential use and revocable operation authority`.
- Current PR-head commit: `ebd9ac6b9b288ff2847fca6b666f5275049c2b35`.

## Last completed step

LAB-070's exact-source merge gate was closed. Exact PR-head files were reconstructed through GitHub connector content and matched published Git blob IDs; LAB-070 passed 8/8, its unsafe propagation seed failed as expected, and exact LAB-069/LAB-030/LAB-031 regressions passed 14/14, 11/11, and 8/8. A fresh remote audit found no blocker and PR #132 merged normally.

LAB-071 was then selected from LAB-070's proven boundary. Current Linux `unix(7)` evidence shows the useful distinction: `SO_PEERCRED` is connection-time peer identity, while broker-side `SO_PASSCRED` supplies `SCM_CREDENTIALS` for the sending process on each received message; `SCM_RIGHTS`/descriptor transfer remains transferable capability.

A real-process prototype was built and published in draft PR #134. The target receives only a request socket, not raw credential bytes. The broker holds the secret, enables `SO_PASSCRED`, and binds requests to kernel sender PID plus a live pidfd/starttime process instance, task, scope, credential generation, and exact request identity/content.

The key hypothesis was observed directly: a target sent one datagram, passed the same socket FD to a grandchild, and the broker observed different kernel sender PIDs for the two messages. The unsafe socket-possession policy accepted both. The corrected broker accepted the authorized target and rejected the grandchild.

An audit improvement was applied before publication: idempotency is now bound to a canonical request digest so one request ID cannot be replayed with changed content; process authority also keeps a live pidfd rather than relying on numeric PID/starttime alone.

## Evidence produced

- LAB-070 exact corrected suite: 8/8 passed; unsafe seed failed as expected.
- LAB-069 exact regression: 14/14 passed.
- LAB-030 exact regression: 11/11 passed.
- LAB-031 exact regression: 8/8 passed.
- LAB-070 PR #132 normal squash merge: `6a242b96761d0df6c74ed325658a0fa52139d2c5`.
- LAB-071 live SCM_CREDENTIALS probe: same transferred AF_UNIX datagram FD produced target PID `733` for the target send and PID `745` for the grandchild send in this runtime.
- LAB-071 corrected local working-copy suite after pidfd/request-digest audit fix: 10/10 passed.
- LAB-071 unsafe socket-possession seed: failed as expected because the grandchild became a second accepted operation.
- LAB-071 compileall: passed.
- New experiment: `experiments/brokered_credential_use/`.
- Research note: `research/2026-08-21-brokered-credential-use.md`.
- Draft PR #134 opened at head `ebd9ac6b9b288ff2847fca6b666f5275049c2b35`.

## Known blockers / constraints

- No owner-level/external blocker.
- PR #134 is intentionally draft; the published PR-head bytes have not yet undergone exact-source reconstruction/regression validation and final remote audit.
- Broker restart/durable permit recovery is not yet implemented. Current pidfds/effect map are in-memory; restart must not silently turn numeric PID or caller-supplied permit fields into authority.
- `SCM_CREDENTIALS` / `SO_PASSCRED` are Linux-specific. Privileged senders with relevant capabilities have different credential-spoofing rules; an untrusted target must not receive those capabilities.
- Numeric PID alone remains non-authoritative; pidfd/starttime validation is required for consequential operations.
- Broker mediation can revoke future credentialed operations but cannot retract data/results already returned to an authorized target.
- The current receipt HMAC models a credentialed external action; this is not a claim that all real external APIs expose or support identical idempotency semantics.

## Exact next action

Resume Issue #133 / PR #134. First reconstruct the exact published PR-head protocol/tests via GitHub connector responses, verify local `git hash-object`, and execute the exact corrected + unsafe LAB-071 suites. Perform a fresh remote patch audit of the published slice. Then close the remaining restart gap narrowly: persist only non-secret permit/effect identity, reacquire target process authority after broker restart using LAB-032-style PID/starttime + fresh pidfd rules, and prove restart never accepts caller-provided numeric PID authority, never duplicates an UNKNOWN/committed mediated effect, and still rejects a transferred socket used by a descendant. Rerun exact LAB-069/LAB-070/LAB-031 regressions and compileall. Only after all acceptance criteria and a second remote audit are clean should PR #134 be marked ready and merged.

## Backlog

- #133 / LAB-071 — brokered credential use, per-message sender identity, and revocable operation authority — IN_PROGRESS; draft PR #134.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
