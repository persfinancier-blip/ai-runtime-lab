# LAB-093 — endpoint/channel lifecycle and restart authority contract

Date: 2026-09-04

## Scope

This note freezes the endpoint-construction, channel-authentication and restart-authority contract for `LAB093_LEDGER_BROKER_V1`, following the command/result schema in `research/2026-09-04-lab093-broker-facade-command-result-schema.md`.

It is deliberately architecture/regression evidence only. No production implementation or RED/GREEN execution is claimed. A fresh `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` was attempted in this run and failed before repository access with `Could not resolve host: github.com`.

The retained local security owner is LAB-087:

- `experiments/sqlite_schema_control/process_boundary.py` establishes a broker-owned database/directory and a distinct worker UID/GID boundary with worker read/traverse but no write permission;
- `experiments/sqlite_schema_control/protocol.py` states explicitly that the broker/process owns the only writable handle and that same-process Python introspection is not the security boundary.

The V1 façade therefore must preserve that process separation instead of trying to make Python attribute privacy carry authority.

## Primary design decision

`LAB093_LEDGER_BROKER_V1` uses **one broker-created connected Unix-domain channel per worker process incarnation**.

For the first supported Linux implementation the preferred primitive is:

```text
socketpair(AF_UNIX, SOCK_SEQPACKET | close-on-exec discipline)
```

or the closest Python-supported equivalent that preserves the same properties. `SOCK_SEQPACKET` is preferred because one request/result remains one bounded message; no generic network listener, path-bound reconnect socket or shared accept loop is required for V1.

The broker creates the pair before launching the lower-trust worker, retains the broker end, and transfers only the worker end as an explicitly allowed inherited descriptor. The channel carries only the closed command/result protocol frozen in the prior note. No database/provider/history/activation/keyring descriptor is transferred.

Why Unix-domain connected sockets are appropriate here: Linux exposes connected peer credentials through `SO_PEERCRED`; the credentials reflect the peer at connect/listen/socketpair establishment. That is useful corroborating evidence for the already-selected LAB-087 process identity boundary. It is **not** a replacement for broker launch-time authorization.

## No reconnect listener in V1

V1 intentionally has **no** ambient filesystem socket, abstract-namespace listener, TCP listener, worker-chosen reconnect address or bearer reconnect token.

A shared listener creates additional questions that V1 does not need to solve:

- who may connect;
- whether PID/UID reuse is sufficient identity;
- stale socket pathname ownership/unlink races;
- whether a stolen reconnect token can widen a worker;
- how a post-crash connection chooses an authorization context.

The answer for V1 is simpler: a worker that loses its broker-created channel loses the delegated capability. A fresh worker incarnation receives a fresh channel from the broker under a fresh launch decision.

## Immutable endpoint authorization context

The immutable authorization context frozen in the prior note remains:

```text
principal_id
component_id
allowed_operations
allowed_intent_types
```

It is created by the broker **before the worker can send commands** and attached to the broker-side endpoint object.

The critical rule is:

> authorization is selected by the live broker-owned channel object, never by a worker-supplied field and never by a recyclable operating-system identifier.

Specifically, the broker must not select or recover authorization by:

- request `principal_id` / `component_id` fields;
- worker-supplied endpoint/session/token id;
- raw integer file descriptor number;
- PID alone;
- UID/GID alone;
- socket pathname;
- last endpoint used by the same component;
- a persisted worker-side reconnect token.

`SO_PEERCRED` `(pid, uid, gid)` is checked against the process that the broker intentionally launched and against LAB-087's expected worker identity. It is corroboration/fail-closed mismatch detection, not the database key from which authority is reconstructed.

## Endpoint instance identity

Each broker endpoint has an internal non-worker-selectable instance identity, conceptually:

```text
EndpointInstance {
    endpoint_nonce: fresh cryptographically random value,
    broker_epoch:   fresh broker-process incarnation value,
    peer_pid:       launch-time / SO_PEERCRED observed PID,
    peer_uid:       exact expected worker UID,
    peer_gid:       exact expected worker GID,
    authorization:  immutable AuthorizationContext,
    state:          OPEN | REVOKED | CLOSED
}
```

The nonce/epoch are broker bookkeeping and audit values. They do **not** become bearer credentials and need not appear in worker command bodies.

The live mapping is keyed by the broker endpoint object/open socket instance, not by its integer fd. If the OS later reuses the same integer fd for a different socket, no old authorization mapping is inherited.

## Descriptor reuse rule

Descriptor reuse is handled by lifecycle, not by comparing integers:

1. on EOF, protocol violation, explicit revocation, worker exit or channel error, set the endpoint state to `REVOKED` and remove its authorization mapping;
2. only then close the socket;
3. never retain a mapping `fd_number -> AuthorizationContext` across close;
4. a newly created channel receives a new `EndpointInstance`, new nonce and current broker epoch even if the OS reuses the same fd integer;
5. an in-flight request may complete only for the endpoint instance on which it was received; a response must not be routed by a later lookup of the fd integer.

Negative property: `close(old fd=7) -> socketpair() returns new fd=7` must not transfer the old component/operation grant.

## Message/framing rules

The previous closed command/result schema remains authoritative. Lifecycle adds these transport constraints:

- one bounded protocol object per `SOCK_SEQPACKET` message;
- maximum encoded request/response size is configured broker-side and oversized/truncated messages fail closed;
- decoder rejects trailing/duplicate/unknown fields under the frozen schema;
- request bodies never carry file descriptors or ancillary `SCM_RIGHTS` capabilities;
- the broker rejects unexpected ancillary descriptors/credentials rather than installing them into its capability graph;
- no worker message can request `dup`, `SCM_RIGHTS`, provider handle export, SQLite handle export or a second channel.

V1 does not need worker-supplied `SCM_CREDENTIALS`: the broker reads connected peer identity using `SO_PEERCRED` and trusts only the process it launched under the LAB-087 boundary.

## Worker launch lifecycle

Conceptual sequence:

```text
broker constructs/verifies supported ledger authority graph
broker verifies LAB-087 filesystem/process boundary
broker creates fresh EndpointInstance + socketpair
broker launches exact worker identity with only worker socket end intentionally inherited
broker closes its duplicate of worker end
broker checks SO_PEERCRED / observed child identity against launch decision
endpoint becomes OPEN
worker may send LAB093_LEDGER_BROKER_V1 commands
```

Before `OPEN`, commands are refused. A peer-identity mismatch revokes the endpoint before any SQLite/provider operation.

No writable SQLite descriptor, raw provider/AttestedCatchup object, activation handle, provider-history strategy, signing/keyring object, protected path handle or broker control socket crosses the launch boundary.

## Worker restart authority

Worker restart creates **no authority continuity by itself**.

When a worker exits/crashes/restarts:

1. old endpoint becomes REVOKED/CLOSED;
2. all queued not-yet-dispatched commands on that endpoint are discarded/refused;
3. broker creates a new worker process incarnation and a new socketpair;
4. broker obtains the new authorization context from its own trusted launch/configuration decision, not from old worker memory;
5. new endpoint has a new nonce and current broker epoch;
6. the worker may retry semantic ledger requests through the normal LAB-080 intent/request idempotency rules.

The endpoint does not persist provider or ledger authority. Recreating a worker channel recreates only the **delegation view**.

A worker restart cannot request a wider operation set than the broker assigned, cannot present an old endpoint nonce as proof, and cannot recover the previous live ledger Python object.

## Broker restart authority

Broker restart is stronger and must not be treated as endpoint restoration.

On broker restart:

1. all prior endpoint instances are dead by definition; increment/newly randomize `broker_epoch`;
2. reconstruct the supported ledger/provider/history/activation authority graph only from canonical trusted configuration/identity inputs;
3. run the accepted durable verification gate before serving any delegated command;
4. verify/reinstall the LAB-087 process/filesystem confinement as required by its accepted contract;
5. if durable verification or confinement fails, create no OPEN endpoint;
6. launch/relaunch workers with entirely fresh socketpairs and fresh authorization contexts.

There is no `resume_endpoint(old_nonce)` operation.

Critically, broker restart may reconstruct **broker authority only through the canonical supported constructors and verification gates**. It may not reconstruct authority from worker-supplied serialized ledger/provider objects, endpoint state, cached responses, activation tickets or reconnect tokens.

This composes with LAB-094/095/096/097/098/099/100: those tasks define the correctness of the broker-owned authority graph; LAB-093 merely prevents that graph from crossing into the worker.

## Crash and in-flight command semantics

The channel must not invent exactly-once semantics above LAB-080.

- If the broker receives no complete request, no ledger call occurs.
- If a complete request is authorized and dispatched, subsequent channel loss does not roll back a durable ledger/provider effect.
- If the worker loses the response and retries after restart, semantic duplicate handling is delegated to the canonical `Intent` / ledger-derived request idempotency, never to the transport `command_id` or endpoint nonce.
- `command_id` remains correlation only.
- `timeout_after_commit` retains the underlying supported ledger's UNKNOWN/reconciliation semantics; endpoint restart must not translate UNKNOWN into an unconditional new external mutation.

## Revocation semantics

The broker may revoke an endpoint at any time. Revocation means:

- state changes to `REVOKED` before further dispatch;
- no new command is authorized;
- queued messages are not dispatched;
- the worker socket is closed after mapping removal;
- a later worker incarnation receives a fresh authorization decision rather than implicit continuation.

V1 does not claim mid-call cancellation of an already-entered atomic ledger operation. The regression contract must distinguish `revoked-before-dispatch` from `revoked-after-dispatch`; the latter is governed by the ledger's own durable/idempotent outcome semantics.

## Negative-control / RED-first lifecycle matrix

These cases extend the previously frozen 20-case façade matrix. When exact execution becomes available, tests must begin RED where the current system still exposes a live in-process ledger or lacks the endpoint boundary.

### Construction and peer identity

1. broker creates one endpoint for worker A/component A; A can invoke only the bound allowed operation/type set;
2. peer UID/GID mismatch fails before any ledger/provider access;
3. peer PID/launch-instance mismatch fails closed even when UID/GID matches;
4. worker cannot open or discover a generic reconnect listener because V1 has none;
5. unexpected passed file descriptor/ancillary capability is rejected and closed, not retained.

### Descriptor/socket reuse

6. close endpoint A, force/reproduce fd-number reuse for endpoint B, prove B receives only B's authorization;
7. late response/completion from an A request cannot be routed to B because routing is bound to endpoint instance, not integer fd;
8. stale A endpoint nonce/command data cannot reopen or widen B;
9. EOF/protocol failure removes authorization mapping before socket close/reuse.

### Worker restart

10. worker A crash destroys A endpoint; a restarted worker receives a new socketpair/nonce;
11. restarted worker cannot ask for old or wider authorization in its first message;
12. retry of an already-durable semantic Intent after restart relies on ledger idempotency and does not allocate a second position/provider increment;
13. old worker process/socket cannot remain concurrently authorized after broker records that incarnation revoked.

### Broker restart

14. broker restart invalidates every old endpoint/broker epoch;
15. no endpoint opens until `verify_durable()` and LAB-087 confinement checks pass;
16. a deliberately corrupted durable ledger causes broker startup delegation to fail closed with zero worker command execution;
17. broker does not deserialize worker-owned ledger/provider/endpoint authority to recover service;
18. after clean broker restart, worker gets a fresh endpoint but same intended least-capability grant only from trusted broker configuration.

### In-flight/revocation

19. revoke-before-dispatch causes zero DB/provider mutation;
20. channel loss after durable commit plus lost response does not cause unconditional re-execution on retry;
21. UNKNOWN/timeout-after-commit survives endpoint loss as canonical reconciliation state, not transport success/failure guess;
22. oversized, truncated or malformed message is refused with zero broker authority mutation.

### Negative control

23. same worker code handed a live ledger object in-process can reach retained capability graph / mutation surfaces; the process-channel version cannot. This is the required demonstration that Python name privacy is not the LAB-093 security boundary.

## Supported-boundary audit checklist

Before a future LAB-093 implementation can become READY:

- no worker-visible live ledger/provider/history/activation/keyring object;
- no generic listener/reconnect bearer in V1;
- endpoint grant selected from broker-owned channel instance only;
- `SO_PEERCRED` matches the intended launched process identity;
- no fd-integer keyed authorization surviving close;
- no `SCM_RIGHTS` transfer into the worker-facing protocol;
- worker restart reconstructs delegation only;
- broker restart re-verifies durable authority before delegation;
- retry correctness remains owned by LAB-080 semantic idempotency;
- LAB-087 worker still cannot open the protected DB writable;
- later LAB-090/LAB-100 provider authority remains broker-only.

## Decision

`LAB093_ENDPOINT_LIFECYCLE_V1_FROZEN`.

The first implementation should remain Linux-specific and reuse the accepted LAB-087 Unix process/filesystem boundary. Portability or remote workers require a separate authenticated transport design; they must not weaken V1 by adding an ambient reconnect listener or worker-carried bearer token before that need is proven.