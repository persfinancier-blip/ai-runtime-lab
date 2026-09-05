# Transport-attempt egress observation / first-I/O proof + ambiguity classifier V1

Status: **TRANSPORT_ATTEMPT_EGRESS_OBSERVATION_FIRST_IO_AMBIGUITY_CLASSIFIER_V1_FROZEN**

Date: 2026-09-05

Scope: LAB-093 follow-up. Read-only/offline design evidence only. No production behavior, provider send, behavioral PASS, or readiness claim is created by this note.

## Objective

Close the remaining ambiguity at the final transport boundary: distinguish the narrow class of failures that can be proven to have happened before any provider-visible request bytes/frames could leave the admitted transport path from all cases that must remain `UNKNOWN`.

This composes with the already frozen `SEND_STARTED`, final-request freeze, semantic extractor, replay capsule, retry-authority and manual-reconciliation contracts.

## Core safety rule

`FAILED_BEFORE_IO` is a **proof state**, not an inference from an exception, timeout, missing response, cancellation, process death, or zero application-level acknowledgement.

A transport attempt may be classified `FAILED_BEFORE_IO` only when authenticated, transport-adjacent evidence proves all of the following for the exact frozen request/attempt identity:

1. no request HEADERS/request-line/application DATA for that attempt were accepted by any component that can forward them toward the provider;
2. no lower layer with independent buffering/retry/forward authority accepted provider-semantic bytes/frames;
3. no proxy/service-mesh/HTTP2 connection/gRPC channel that could have independently forwarded the attempt had accepted it;
4. the observation point is declared in the active authority dependency manifest and dominates every egress path for the attempt;
5. the evidence itself was durably bound to the exact `TransportAttemptV1` and final-request digest.

If any predicate is unknown, the classifier returns `UNKNOWN`, not `FAILED_BEFORE_IO`.

## Why ordinary send outcomes are insufficient

Linux `send()` returns the number of bytes accepted by the local socket path; it explicitly provides no delivery-failure guarantee. Successful or partial writes therefore prove at least local egress acceptance, not provider processing. A later error does not retract those bytes.

OpenSSL `SSL_write()` can perform handshake/transport work internally, can report partial application-data writes when enabled, and retryable failures can require repeating the same data. An `SSL_write` error by itself is therefore not proof that zero ciphertext carrying request data was emitted.

HTTP/2 is multiplexed. A connection or stream reset can race with frames already sent or queued. RFC 9113 explicitly requires peers to tolerate frames that were sent/enqueued before `RST_STREAM`; open streams on connection failure cannot simply be assumed unprocessed. Two protocol-level exceptions are useful because the protocol itself supplies stronger evidence: `REFUSED_STREAM` means the server guarantees the stream was not processed, and GOAWAY identifies streams above the last processed stream as safe to retry. Those are provider/protocol processing guarantees, not generic socket-negative evidence.

Primary donors:
- Linux `send(2)`: https://man7.org/linux/man-pages/man2/send.2.html
- Linux `write(2)`: https://man7.org/linux/man-pages/man2/write.2.html
- OpenSSL `SSL_write`: https://docs.openssl.org/3.2/man3/SSL_write/
- RFC 9113 HTTP/2: https://www.rfc-editor.org/rfc/rfc9113

## Frozen classifier states

`TransportEgressClassV1`:

- `FAILED_BEFORE_IO`
- `EGRESS_ACCEPTED_UNKNOWN_PROVIDER_STATE`
- `PROTOCOL_CERTIFIED_NOT_PROCESSED`
- `PROTOCOL_CERTIFIED_MAY_HAVE_PROCESSED`
- `UNKNOWN`

Only `FAILED_BEFORE_IO` and, where the pinned provider-capability contract explicitly admits it, `PROTOCOL_CERTIFIED_NOT_PROCESSED` may feed a retry planner as evidence that the exact prior attempt did not produce provider processing.

Neither state creates a fresh business effect identity. Historical retry must still obey the retry-authority/replay-capsule/provider-idempotency contracts.

## Durable observation objects

### `TransportEgressObservationV1`

Required fields:

- `transport_attempt_id`
- `frozen_final_request_digest`
- `authority_generation`
- `manifest_generation`
- `observer_declaration_digest`
- `protocol` (`HTTP1`, `HTTP2`, `GRPC`, other explicitly admitted protocol)
- `connection_identity`
- `stream_identity` when applicable
- `proxy_hop_identity` / declared direct path
- `event_kind`
- `monotonic_sequence`
- `observed_octets_or_frames`
- `observation_scope`
- `timestamp_evidence`
- `parent_provenance_id`

Observations are append-only. They never overwrite an earlier `SEND_STARTED`, first-write, partial-write, frame-accepted or ambiguity event.

### `EgressObserverDeclarationV1`

An observer is admissible only when its declaration pins:

- implementation/library/version/build digest;
- exact hook location relative to serializer, signer, retry middleware, proxy connector and socket/TLS writer;
- whether callback means `before enqueue`, `accepted into local buffer`, `ciphertext emitted`, `frame queued`, `frame handed to proxy`, or protocol acknowledgement;
- whether hidden buffering/retry is possible after the callback;
- connection reuse/multiplexing semantics;
- supported negative-proof claim.

A callback named `on_send`, `request_sent`, `write_failed`, etc. has zero negative-proof authority unless this declaration establishes its semantics.

## State-machine composition

Durable ordering remains:

`LEASE_CONSUMED -> SEND_STARTED -> egress observations -> terminal/local error or provider outcome`

`SEND_STARTED` is always written before invoking the transport path.

### `FAILED_BEFORE_IO`

Allowed only if a trusted observation proves the attempt failed before the first egress-capable acceptance point and there is no contradictory later observation.

Examples that may qualify after adapter-specific proof:

- local validation/serialization/signing failure before the final send gate;
- DNS/connect failure on a fresh direct connection where no request-data-capable early-data mechanism is enabled;
- TLS handshake failure before any admitted application-data/0-RTT request emission;
- local authority/quarantine rejection before network invocation.

A generic `connect()`/TLS error does not qualify if TCP Fast Open, TLS 0-RTT, CONNECT proxy buffering, custom transport middleware or another mechanism can carry request bytes before the reported failure.

### `EGRESS_ACCEPTED_UNKNOWN_PROVIDER_STATE`

Mandatory after any positive evidence that request-semantic bytes/frames were accepted by a forwarding-capable layer, including:

- `send/write/writev` reports one or more request bytes accepted;
- TLS layer reports request application data written/partially written;
- HTTP/1 request headers/body accepted into a transport that may flush asynchronously;
- HTTP/2 HEADERS or DATA for the stream queued/accepted below the final authority-visible gate;
- request accepted by CONNECT/forward proxy or service mesh;
- gRPC call handed to a transport layer that may independently write/retry/hedge.

A later reset, cancellation, timeout or process crash does not downgrade this state.

### `PROTOCOL_CERTIFIED_NOT_PROCESSED`

This is not inferred locally. It requires an authenticated protocol/provider signal whose pinned semantics guarantee non-processing for the exact stream/request identity.

V1 donor examples:

- HTTP/2 `REFUSED_STREAM`, whose semantics state the stream was closed before any processing occurred;
- HTTP/2 GOAWAY for a client-initiated stream whose ID is strictly greater than the peer's last-stream-id, where RFC 9113 guarantees those streams are safe to retry.

These signals still do not justify creating a new effect identity. The historical provider token/request identity remains pinned.

### `UNKNOWN`

Mandatory for all unresolved cases, including:

- local exception with uncertain hidden buffering;
- missing response;
- timeout after `SEND_STARTED`;
- process crash after `SEND_STARTED` without a complete negative proof record;
- HTTP/1 connection close/reset after any request bytes could have been emitted;
- reused connection failure where prior buffered writes/peer receipt are not independently known;
- HTTP/2 `RST_STREAM` without a protocol guarantee equivalent to `REFUSED_STREAM`;
- cancellation after a transport may have queued bytes;
- proxy accepted request but upstream forwarding result is unknown;
- TLS error after request application data may have entered TLS records;
- evidence loss, observer drift, undeclared middleware or contradictory observations.

## Protocol-specific frozen rules

### HTTP/1.1

A successful/partial socket or TLS write of any request line/header/body material crosses the ambiguity boundary. Connection close/reset afterward is `UNKNOWN` with respect to provider processing.

For buffered clients, application-level `send()` completion is not the observation boundary unless the declaration proves no hidden buffering below it. The lowest mutation/queue capable layer must be observed.

### HTTP/2

Track connection + stream identity separately. Connection reuse means a TCP/TLS write is insufficient to attribute bytes to one request unless the observer can identify the exact HEADERS/DATA frame sequence.

- HEADERS/DATA queued below the final gate => ambiguity crossed.
- `RST_STREAM` generally does not prove non-processing; frames can already be in flight or queued.
- `REFUSED_STREAM` may be admitted as protocol-certified non-processing.
- GOAWAY only certifies streams above the advertised last-stream-id as unprocessed; lower/equal streams remain potentially processed.

### gRPC

gRPC inherits HTTP/2 transport ambiguity. An application cancellation/status alone is not non-processing evidence. The observer must bind the exact RPC to its HTTP/2 stream and final transport path. Hidden retries/hedging remain prohibited unless every attempt is separately authority-visible under prior contracts.

### Proxy/service mesh

A proxy is a consequential forwarding boundary. If the client receives evidence only that the proxy accepted the request, upstream provider state is still unknown unless the proxy emits an authenticated, semantically pinned negative-processing proof admitted by the provider-capability contract.

Proxy CONNECT establishment failure may qualify as pre-I/O only if no request-semantic data/early data could have been sent through or before tunnel establishment.

### TLS

Handshake failure is not automatically pre-I/O. TLS 1.3 early data/0-RTT, library buffering and write-driven handshakes must be represented in the observer declaration. If request application data may have been converted into ciphertext/queued, classify `UNKNOWN` absent stronger evidence.

## Contradiction rule

Positive egress evidence dominates negative local evidence.

Examples:

- `socket_write(bytes>0)` followed by `connection_reset` => `EGRESS_ACCEPTED_UNKNOWN_PROVIDER_STATE`.
- `http2_headers_queued` followed by local cancellation => `EGRESS_ACCEPTED_UNKNOWN_PROVIDER_STATE`.
- `proxy_accept` followed by client timeout => `UNKNOWN`/egress-accepted, never failed-before-I/O.
- `pre_enqueue_failure` plus any later authenticated first-write event => fail closed as evidence conflict; do not accept the negative classification.

## Crash and restart

An attempt with durable `SEND_STARTED` and no terminal egress proof is `UNKNOWN` on restart.

Absence of a first-write record is not proof of no write because a crash can happen after I/O and before logging. A negative proof is admissible only when the observation mechanism makes the ordering durable/atomic enough to prove that the network-capable action could not occur first. If the implementation cannot provide that ordering, it cannot emit `FAILED_BEFORE_IO` after restart.

No recovery path may synthesize a missing observation.

## Conformance matrix — 64 RED-first cases

Freeze eight families with eight cases each. Production implementation must first demonstrate RED for unsafe/missing-observer behavior, then GREEN after implementation.

1. **Pre-I/O/local gate**: validation failure; serializer failure; signer failure; quarantine rejection; DNS failure fresh connection; connect refusal; proxy-connect failure; TLS handshake pre-app-data failure.
2. **Partial writes**: one-byte socket write then reset; partial header; partial body; writev partial; TLS partial write; async buffer acceptance; write success then immediate close; error after earlier successful write.
3. **HTTP/1 reuse**: reused idle connection reset before enqueue; reset after enqueue; stale pooled socket; client-side cancellation; response timeout; server close after request write; buffered writer exception; contradictory negative/positive observations.
4. **HTTP/2**: HEADERS queued then RST; DATA partial then RST; `REFUSED_STREAM`; GOAWAY stream above last-stream-id; GOAWAY stream equal/below last-stream-id; connection termination with open stream; reused multiplexed connection; local cancel after HEADERS.
5. **gRPC**: cancel before transport admission; cancel after stream creation; deadline after HEADERS; stream reset; channel failure; transparent retry attempted; hedged duplicate attempt; RPC status without egress evidence.
6. **TLS/early data**: handshake failure no early data; 0-RTT request attempted; lazy handshake during write; `WANT_READ/WANT_WRITE`; partial-write mode; ciphertext buffer acceptance then error; credential rotation during handshake; resumed session with undeclared early-data behavior.
7. **Proxy/intermediary**: local CONNECT failure; proxy accepts CONNECT only; forward proxy accepts request; proxy returns 502 after possible forward; service mesh retry attempt; proxy buffers then client disconnects; proxy authenticated not-forwarded proof; undeclared proxy insertion.
8. **Crash/evidence integrity**: crash before final send gate; crash after `SEND_STARTED` before observed write; crash after first write before evidence commit; crash after evidence commit; observer event loss; sequence rollback; observer version drift; conflicting replicated observations.

Expected conservative outcome: any fixture in which provider-visible forwarding cannot be ruled out deterministically must resolve to `UNKNOWN` or an egress-accepted unknown state.

## Security invariants

1. `FAILED_BEFORE_IO` cannot be inferred from absence of response/logs.
2. `FAILED_BEFORE_IO` cannot be inferred from an application exception alone.
3. Any authenticated positive egress observation prevents later negative reclassification.
4. Missing observation after `SEND_STARTED` is `UNKNOWN` after crash/restart.
5. Protocol-certified non-processing is admitted only from a pinned provider/protocol capability declaration.
6. No egress classification mints a new business effect/provider request identity.
7. Reused connections, multiplexing, retries, hedging, proxies and early-data behavior must be explicit dependencies.
8. Observer code/version/hook position is part of the authenticated authority manifest.
9. Evidence is append-only and parent-linked into the shared LAB-097..100 provenance chain.
10. Runtime drift or undeclared egress paths fail closed/read-only.

## Audit result

The safe model is deliberately asymmetric: positive evidence that bytes/frames entered a forwarding-capable path is easy to accept and pushes the attempt toward `UNKNOWN`; negative evidence sufficient for `FAILED_BEFORE_IO` is rare and requires a declared observation point that dominates every egress path. This avoids the dangerous inference that a local failure means the provider saw nothing.

No production implementation should begin until executable source access permits exact RED/GREEN of the frozen matrix.

## Next distinct evidence task

Freeze a **transport observer implementation/admission contract**: define implementable hook profiles for Python sockets/SSL, HTTP/1 pools, HTTP/2/gRPC transports and proxy paths; specify durable event ordering without placing a blocking SQL transaction around network I/O; and prove the observer cannot itself create hidden retries, buffering, reentrancy or deadlocks. Include a minimal observer API, per-library capability declarations and executable fault-injection fixture requirements.