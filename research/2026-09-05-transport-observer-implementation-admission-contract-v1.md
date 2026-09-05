# Transport Observer Implementation / Admission Contract V1

Status: `TRANSPORT_OBSERVER_IMPLEMENTATION_ADMISSION_V1_FROZEN`
Date: 2026-09-05
Scope: LAB-093 follow-up; depends on the frozen transport-attempt egress/ambiguity classifier and final-request-freeze contracts.

## Objective

Define an implementable, fail-closed observer boundary for consequential provider attempts so the runtime can distinguish only those failures that are provably pre-I/O from attempts that must remain `UNKNOWN`, without holding a SQL transaction open around network I/O and without letting the observer introduce hidden retries, buffering, reentrancy, duplicate sends, or deadlocks.

This contract is deliberately conservative. It prefers false `UNKNOWN` over a false claim of `FAILED_BEFORE_IO`.

## Core invariant

A runtime may emit `FAILED_BEFORE_IO` only when the failure is durably known to have happened before entering any forwarding-capable sink for the consequential request.

Once a durable `SINK_ENTERED` record exists, a crash, timeout, cancellation, generic socket/TLS/HTTP error, missing observer callback, or missing response MUST NOT be interpreted as proof that no provider-visible I/O occurred. The attempt remains at least `UNKNOWN` unless a separately admitted protocol-certified non-processing proof applies.

The observer therefore does **not** try to make the first actual network write and a SQL commit atomic. That is not generally achievable without coupling database and transport resources. Instead it makes the ambiguity boundary explicit and durable *before* entering a mutation-capable transport sink.

## Minimal durable state machine

For one immutable transport-attempt identity:

`PREPARED -> ARMED -> SINK_ENTERED -> EGRESS_OBSERVED -> RESPONSE_OBSERVED / TERMINAL_UNKNOWN`

Additional terminal proof state:

`PREPARED/ARMED -> FAILED_BEFORE_IO`

Protocol-certified recovery may append:

`SINK_ENTERED/EGRESS_OBSERVED -> CERTIFIED_NOT_PROCESSED`

Rules:

1. `PREPARED` binds operation/effect/attempt, replay capsule digest, final frozen-request digest, authority generation, adapter generation, observer-profile generation, provider scope, and transport target.
2. `ARMED` proves the observer/profile admission checks passed and hidden retry/redirect/hedge paths are disabled or authority-visible.
3. `SINK_ENTERED` MUST be committed durably before calling the first forwarding-capable transport operation for this attempt. No database transaction remains open while the network call executes.
4. After `SINK_ENTERED`, absence of later observer records is not negative evidence.
5. `EGRESS_OBSERVED` is positive evidence that the admitted transport layer accepted provider-semantic bytes or frames for forwarding. It may strengthen `UNKNOWN`; it is not required to reach `UNKNOWN` after `SINK_ENTERED`.
6. `FAILED_BEFORE_IO` is legal only if no `SINK_ENTERED` exists and the failure path is entirely above the admitted forwarding-capable sink.
7. An admitted protocol-specific proof such as HTTP/2 `REFUSED_STREAM`, or a GOAWAY proving a stream ID was above the peer's last processed stream ID, may append `CERTIFIED_NOT_PROCESSED`. Generic RST_STREAM/reset/timeout/cancellation does not qualify.

## Why `SINK_ENTERED` is before I/O

Trying to persist `first_write=true` only after `send()` returns has an unavoidable crash window: the process can write bytes and die before persisting the observation. On restart, the missing record would then be dangerously ambiguous.

The V1 design closes that gap by persisting a conservative boundary before entering the sink. This can over-classify failures as `UNKNOWN`, but it cannot convert a potentially sent effect into a false pre-I/O failure.

A blocking SQL transaction MUST NOT be held around socket/TLS/HTTP/gRPC I/O. The required ordering is:

1. short transaction: append `SINK_ENTERED`, commit;
2. release all DB locks/transactions;
3. execute one admitted transport attempt;
4. short transaction: append positive observation / response / terminal evidence;
5. reconcile on restart from the append-only attempt history.

## Observer API

The runtime-facing API is intentionally small and append-only.

```text
ObserverProfileV1 {
  profile_id,
  profile_generation,
  implementation_digest,
  runtime_version_range,
  transport_kind,
  forwarding_sink_definition,
  hidden_retry_policy,
  redirect_policy,
  buffering_policy,
  reentrancy_policy,
  multiplexing_identity_rule,
  proxy_boundary_rule,
  evidence_fields,
  conformance_fixture_digest,
  signer_set,
  signature
}

TransportAttemptObservationV1 {
  attempt_id,
  event_seq,
  event_type,
  monotonic_process_counter,
  observer_profile_generation,
  frozen_request_digest,
  connection_identity?,
  stream_identity?,
  accepted_octets_or_frames?,
  provider_scope,
  timestamp_for_audit_only,
  parent_provenance,
  event_digest
}
```

`timestamp_for_audit_only` MUST NOT be used to reconstruct causal ordering. Causality comes from attempt identity, event sequence, parent linkage, and durable append order.

## Admission rule

An observer profile is admitted only when all of the following are true:

- it identifies the exact first forwarding-capable sink that dominates every consequential send path for the bound runtime/adapter generation;
- it proves that redirects, retries, hedges, connection replays, proxy retries, and middleware retries are either disabled or surfaced as separate authority-visible transport attempts;
- it cannot modify provider-semantic request material;
- it cannot buffer and later emit request material after reporting a negative outcome;
- its callback path cannot recursively call the same provider/transport surface;
- its callback path is non-blocking with respect to locks required by the network stack;
- it does not perform synchronous SQL writes while holding transport-library internal locks;
- it binds multiplexed observations to exact HTTP/2/gRPC stream identity;
- it has a frozen fault-injection fixture set that passes for the exact implementation/runtime versions;
- drift in transport library, adapter, proxy topology, or observer implementation invalidates the declaration until re-admission.

A generic statement such as "we monkeypatch socket.send" is not sufficient admission evidence for libraries that can bypass Python socket methods, use C extensions, alternate event loops, kernel TLS, subprocesses, native gRPC core, or a proxy sidecar.

## Hook profile A — Python socket / plain TCP

Admitted target: code paths proven to reach CPython `socket.send`, `sendall`, `sendmsg`, or another explicitly enumerated socket method without a lower hidden forwarding layer.

Rules:

- persist `SINK_ENTERED` before invoking the selected socket operation;
- `send()` returning `n > 0` can append positive `EGRESS_OBSERVED(n)` for that call;
- `sendall()` success only proves all bytes were accepted by the local socket API; on error Python does not expose how much was already sent, so an error after `SINK_ENTERED` remains `UNKNOWN`;
- partial `send()` followed by failure is `UNKNOWN`;
- connection reuse requires a stable connection identity plus exact attempt framing; a failure on a reused socket cannot be inferred pre-I/O merely because the current request received no response;
- process-global monkeypatching is forbidden as production proof unless every bypass is independently excluded and the patch itself is version-pinned and conformance-tested.

## Hook profile B — Python SSL / TLS

The SSL layer has its own framing and buffering above TCP. Observing only plaintext application bytes above SSL is not equivalent to observing ciphertext egress.

V1 rules:

- `SINK_ENTERED` is persisted immediately before the admitted SSL forwarding call;
- successful `SSLSocket.send`/`write` acceptance is positive local-forwarding evidence, not provider receipt evidence;
- `SSLWantReadError`, `SSLWantWriteError`, timeout, generic `SSLError`, connection reset, or cancellation after `SINK_ENTERED` remain `UNKNOWN` unless the profile proves a stronger local no-write condition for that exact OpenSSL/Python version;
- TLS renegotiation/handshake behavior means a read can cause writes and a write can cause reads; observer admission must account for library behavior rather than assume one application call maps to one wire write;
- kernel TLS or native sendfile paths are separate profiles, not implicitly covered by a userspace SSL hook;
- TLS 0-RTT/early-data support is disabled for consequential mutations unless an explicit profile models replay and first-egress semantics.

## Hook profile C — HTTP/1.1 pools

An HTTP/1 pool adds connection reuse, request serialization, redirects, and often retry logic.

Rules:

- the observer must sit after final request serialization and after automatic redirect/retry decisions have been disabled or exposed;
- `SINK_ENTERED` is per provider attempt, not per high-level `request()` call;
- urllib3-style retry defaults MUST be explicitly set to a frozen no-hidden-retry configuration for consequential requests; otherwise the profile is not admitted;
- automatic redirects are disabled for consequential requests unless every redirected request is separately frozen, authorized, observed, and assigned a transport-attempt identity;
- response parser failure after request transmission is not pre-I/O evidence;
- a pooled connection failure before the request-specific sink is entered may be `FAILED_BEFORE_IO`; a failure after entering the request-specific sink is `UNKNOWN` absent stronger proof.

## Hook profile D — HTTP/2 and gRPC

Multiplexing requires stream-level attribution. Connection-level observation alone is insufficient.

Rules:

- every consequential attempt binds an exact HTTP/2 stream ID or equivalent gRPC-core call/stream identity;
- `SINK_ENTERED` is persisted before the library is allowed to enqueue HEADERS/DATA for that stream into a forwarding-capable connection writer;
- positive observations identify the exact stream and frame class; a write on a different stream is irrelevant;
- generic `RST_STREAM`, transport reset, deadline exceeded, cancellation, `UNAVAILABLE`, or connection loss after `SINK_ENTERED` are not proof of non-processing;
- HTTP/2 `REFUSED_STREAM` is admissible as protocol-certified non-processing only when received/authenticated through the admitted connection and bound to the exact stream;
- GOAWAY may certify non-processing only for streams strictly greater than the advertised last-stream-id, as specified by RFC 9113;
- gRPC retries and request hedging MUST be disabled for consequential mutations unless each retry/hedge is represented as an authority-visible attempt. Hedging that sends multiple concurrent copies is incompatible with one-shot authority unless the provider contract and authority model explicitly admit those copies.

## Hook profile E — forward proxy / service mesh / sidecar

A proxy is a forwarding-capable actor. Client-side socket success can prove only acceptance by the next hop, not provider receipt.

Rules:

- the profile declares whether the proxy itself is inside or outside the trusted observer boundary;
- if the proxy can retry, redirect, buffer, replay, route to alternate upstreams, or survive the client process, it is part of the authority dependency manifest;
- a client may append `EGRESS_OBSERVED_TO_PROXY`, but this cannot be interpreted as final-provider delivery;
- once an admitted proxy accepts the consequential request, client crash or cancellation is `UNKNOWN` unless the proxy exposes authenticated per-attempt upstream evidence;
- proxy-generated retries are forbidden unless surfaced as separate provider attempts with the same replay-capsule restrictions;
- topology/config drift invalidates the profile.

## Hidden retry and duplicate-send prohibition

The observer must never be the component that decides to retry.

Forbidden inside observer callbacks:

- calling `send`, `request`, `write`, `flush`, RPC retry, or provider SDK methods;
- reconnecting and replaying buffered bytes;
- following redirects;
- invoking a logging/telemetry transport that recursively uses the same consequential network path;
- performing synchronous health checks that acquire the same pool/connection lock;
- waiting on the main authority/ledger lock from a callback executed under transport-library locks.

Observer callbacks may only construct bounded evidence and enqueue/append it through a non-reentrant evidence path. If that evidence path is unavailable after `SINK_ENTERED`, the attempt remains `UNKNOWN`; loss of observation never makes it pre-I/O.

## Reentrancy / deadlock requirements

Production admission MUST prove:

1. no observer callback can synchronously reacquire the provider adapter lock held by the caller;
2. no callback can synchronously reacquire a connection-pool lock held by the transport;
3. no callback keeps a SQLite write transaction open across network I/O;
4. evidence persistence uses a bounded independent queue or a short post-call transaction;
5. queue-full / persistence-failure behavior is fail-closed for new consequential authority, but does not rewrite an already entered attempt as pre-I/O;
6. callback recursion is detected by attempt-local guard and treated as observer failure/quarantine, never by silently skipping evidence.

## Crash and restart classifier

On restart:

- `PREPARED/ARMED` without `SINK_ENTERED`: may be classified `FAILED_BEFORE_IO` only when startup verifies no lower out-of-process forwarding agent could have emitted the request independently;
- any `SINK_ENTERED` without authenticated terminal outcome: `UNKNOWN`;
- `EGRESS_OBSERVED` without terminal outcome: `UNKNOWN`;
- missing observer events after `SINK_ENTERED`: `UNKNOWN` plus observer-health incident;
- `CERTIFIED_NOT_PROCESSED` must validate against the exact admitted protocol proof before enabling same-identity recovery semantics;
- stale observer profile generation or broken provenance: fail closed and quarantine affected consequential surfaces.

## Fault-injection conformance matrix (64 cases)

### Group 1 — pre-sink failures (8)
1. serializer throws before freeze;
2. authority lease rejected;
3. DNS resolution failure before admitted forwarding sink;
4. proxy config rejection before request enqueue;
5. connection pool exhaustion before request-specific sink;
6. TLS policy rejection before consequential request sink;
7. observer admission mismatch before `SINK_ENTERED`;
8. crash after `ARMED` but before `SINK_ENTERED`.

Expected: eligible for `FAILED_BEFORE_IO` only when no forwarding-capable subprocess/proxy already owns the request.

### Group 2 — plain socket ambiguity (8)
9. first `send` accepts all bytes;
10. partial `send` then exception;
11. `sendall` exception with unknown progress;
12. reset after positive send;
13. timeout after positive send;
14. crash immediately after kernel call before positive callback persistence;
15. reused connection closes during current send;
16. observer evidence queue failure after `SINK_ENTERED`.

Expected: 9–16 are never inferred pre-I/O after sink entry; 10–16 are `UNKNOWN` absent terminal provider evidence.

### Group 3 — TLS (8)
17. SSL write success;
18. `SSLWantWriteError` after sink entry;
19. `SSLWantReadError` during write path;
20. TLS alert after possible application-data emission;
21. socket reset underneath SSL;
22. kernel-TLS path bypasses userspace hook;
23. TLS early-data enabled unexpectedly;
24. crash between SSL call and observation persistence.

Expected: bypass/early-data invalidates admission; post-entry ambiguous cases remain `UNKNOWN`.

### Group 4 — HTTP/1 pooling/retry/redirect (8)
25. pooled fresh connection one send;
26. pooled reused connection dies before request sink;
27. pooled reused connection dies after sink entry;
28. library silently retries connect+request;
29. library silently retries read failure;
30. 307/308 redirect attempted;
31. 301/302/303 method-changing redirect attempted;
32. response parse error after successful request write.

Expected: hidden retry/redirect cases fail admission; 27/32 remain `UNKNOWN`; 26 may be pre-I/O only with exact sink proof.

### Group 5 — HTTP/2/gRPC (8)
33. HEADERS/DATA enqueue for exact stream;
34. RST_STREAM generic error;
35. `REFUSED_STREAM` exact stream;
36. GOAWAY with last-stream-id below attempt stream;
37. GOAWAY with last-stream-id equal to attempt stream;
38. connection reset with multiple live streams;
39. gRPC deadline/cancellation after enqueue;
40. gRPC hedging creates second copy.

Expected: 35/36 may become `CERTIFIED_NOT_PROCESSED`; 34/37/38/39 remain ambiguous; 40 invalidates one-shot admission unless modeled as separate authority-visible attempts.

### Group 6 — proxy/service mesh (8)
41. proxy rejects before accepting body;
42. proxy accepts then upstream connection fails;
43. proxy buffers and client crashes;
44. proxy retries alternate upstream;
45. sidecar survives client crash;
46. proxy config hot-reloads routing;
47. proxy returns local timeout after forwarding;
48. proxy emits authenticated upstream non-processing proof.

Expected: once proxy accepts, default is `UNKNOWN`; hidden retry/config drift invalidates admission; only exact authenticated proof can strengthen classification.

### Group 7 — reentrancy/deadlock/evidence loss (8)
49. callback tries provider SDK recursion;
50. callback reacquires adapter lock;
51. callback blocks on pool lock;
52. callback performs SQLite write while transport lock held;
53. evidence queue full before new attempt admission;
54. evidence queue full after `SINK_ENTERED`;
55. observer callback throws;
56. observer process/thread dies while attempt active.

Expected: no duplicate send; new authority quarantined when evidence subsystem is unhealthy; already entered attempt remains `UNKNOWN`.

### Group 8 — restart/drift/provenance (8)
57. restart sees `ARMED` only;
58. restart sees `SINK_ENTERED` only;
59. restart sees positive egress but no response;
60. observer implementation digest changed;
61. transport library version outside admitted range;
62. proxy topology changed;
63. stream identity cannot be reconstructed;
64. observation parent/global provenance verification fails.

Expected: 57 may be pre-I/O only after exact independence proof; 58/59 are `UNKNOWN`; 60–64 fail closed/quarantine affected consequential surfaces.

## RED-first implementation sequence

No production observer should be added until executable tests exist for the selected first transport profile.

Recommended first implementation slice:

1. pure classifier tests for `PREPARED/ARMED/SINK_ENTERED/EGRESS_OBSERVED` crash ordering;
2. local socketpair fault injector proving partial-write/sendall-error ambiguity;
3. fake HTTP/1 pool with explicit hidden-retry detector;
4. HTTP/2 in-memory frame fixture for stream identity, REFUSED_STREAM and GOAWAY cases;
5. callback reentrancy/deadlock sentinel tests;
6. restart fixture over durable SQLite append records;
7. only then add the minimal observer implementation for one transport profile;
8. keep all other profiles read-only/unadmitted until their own fixtures pass.

## Donors / primary references

- Python socket documentation: `sendall()` retries until all data is sent or error, but on error there is no way to determine how much data was successfully sent. https://docs.python.org/3/library/socket.html
- Python SSL documentation: SSL sockets have framing distinct from normal sockets; `SSLSocket.write()` may return partial progress / WANT_READ / WANT_WRITE behavior and TLS activity can cross read/write directions. https://docs.python.org/3/library/ssl.html
- urllib3 connection-pool documentation: pools can reuse connections and expose retry/redirect behavior; retry policy must be explicitly controlled. https://urllib3.readthedocs.io/en/latest/reference/urllib3.connectionpool.html
- RFC 9113 HTTP/2: `REFUSED_STREAM` means no processing occurred; GOAWAY last-stream-id establishes which higher-numbered streams were not/will not be processed. https://www.rfc-editor.org/rfc/rfc9113.html
- gRPC request hedging documentation: hedging deliberately sends multiple copies and therefore cannot remain hidden beneath one-shot consequential authority. https://grpc.io/docs/guides/request-hedging/

## Frozen decisions

1. The durable pre-I/O boundary is `SINK_ENTERED-before-call`, not `first-write-after-call`.
2. No SQL transaction spans network I/O.
3. Missing positive observation after sink entry never means no send.
4. Hidden retries/redirects/hedges are admission failures, not implementation details.
5. Multiplexed protocols require exact stream attribution.
6. Proxy acceptance expands ambiguity unless the proxy exposes authenticated attempt-specific upstream evidence.
7. Observer callbacks are evidence-only and may not send, retry, redirect, reconnect, or recursively enter provider paths.
8. Profile/version/topology drift fail-closes consequential authority until re-admission.
9. V1 intentionally sacrifices some availability to make false pre-I/O classification structurally impossible.
10. Production implementation remains blocked on executable RED/GREEN for the first selected transport profile.

## Next distinct evidence task

Freeze an **observer evidence durability / bounded queue / recovery-journal contract** that specifies how pre-call `SINK_ENTERED` and post-call observation records are persisted under SQLite lock contention, process crash, disk-full, torn write, queue overflow, and multi-process writers without letting evidence backpressure deadlock the provider path or silently drop authority-relevant events. Then turn the first socket-profile subset into executable RED tests when exact source execution is available.
