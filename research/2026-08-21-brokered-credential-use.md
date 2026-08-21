# LAB-071 — Brokered credential use and per-message sender identity

## Research question

Can credential authority be revoked at operation time if the target never receives raw credential bytes and instead asks a trusted local broker to perform narrowly scoped credentialed operations?

## Donor semantics

Linux `unix(7)` defines three relevant mechanisms:

- `SCM_RIGHTS` transfers open file descriptors; the receiver effectively gets a duplicated open-file capability. LAB-070 already showed why possession of such a transferred descriptor cannot be treated as revocable single-process authority.
- `SO_PEERCRED` reports credentials associated with creation/connection of a UNIX socket. That is connection-time identity and can be the wrong authority boundary when a connected/socketpair FD is later transferred.
- `SO_PASSCRED` causes each received message to carry `SCM_CREDENTIALS` for the **sending process**. The kernel checks explicitly supplied credentials subject to capability rules; an ordinary unprivileged sender therefore cannot simply assert another PID/UID/GID.

Primary reference: https://man7.org/linux/man-pages/man7/unix.7.html

LAB-031 supplies the other required mechanism: numeric PID alone is not process-instance authority. The broker therefore keeps a pidfd opened when the permit is created, checks that it still targets the authorized PID and is live, and rechecks `/proc/<pid>/stat` starttime before each consequential operation.

## Experiment result

A real target process received one end of an AF_UNIX datagram socket. It sent one request itself, then deliberately passed the same socket FD to a grandchild. With `SO_PASSCRED` enabled on the broker end:

- target message carried the target PID;
- grandchild message carried a different grandchild PID;
- a connection/socket-possession-only baseline accepted both;
- the corrected broker accepted the target and rejected the grandchild.

The corrected broker keeps raw secret bytes in-process and emits only a receipt. Authorization additionally binds task, operation scope, credential generation, request ID/content, and target process instance. Rotation invalidates future requests under the old generation while the original process remains alive. Duplicate requests with identical content are idempotent; reusing one request ID with different content is rejected. A timeout injected after effect commit can be reconciled by exact request identity without duplicating the effect.

## Security boundary

This is not a general secret manager or a portable IPC protocol. `SCM_CREDENTIALS` is Linux-specific and privileged senders with relevant capabilities have different credential-spoofing rules; an untrusted target must not receive those capabilities.

The broker prevents raw credential disclosure on the corrected path and can revoke future mediated operations. It cannot prevent an authorized target from leaking the *result* or business data that a permitted operation legitimately returns. It also does not erase any data the target already received.
