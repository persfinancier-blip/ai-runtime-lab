# Final-request freeze / transport interposition integrity + lazy-signing admission V1

Status: `FINAL_REQUEST_FREEZE_TRANSPORT_INTERPOSITION_INTEGRITY_LAZY_SIGNING_V1_FROZEN`

Date: 2026-09-05

Related: LAB-093/#178; composes with `PROVIDER_SEMANTIC_REQUEST_EXTRACTOR_POST_SIGNING_EQUIVALENCE_ATTESTATION_V1_FROZEN`, `PROVIDER_WIRE_REQUEST_REPLAY_CAPSULE_DETERMINISTIC_ADAPTER_COMPATIBILITY_V1_FROZEN`, effective-authority lease/retry contracts, and LAB-090..100 global provenance/recovery contracts.

## Objective

Close the remaining TOCTOU gap between a successful provider-semantic equivalence attestation and the first external byte/RPC frame that can create or advance a consequential provider effect.

A PASS over a request object is insufficient if anything closer to the network can still mutate authority-relevant semantics: redirect logic, retry middleware, endpoint resolvers, lazy signing, HTTP/gRPC interceptors, proxy routing, late serialization, compression, streaming wrappers, DNS/service discovery, or transport adapters.

The V1 rule is therefore:

> No consequential I/O may occur unless the exact request representation that crossed the semantic-attestation boundary is frozen, the final network-adjacent interposition point proves that no authority-relevant transformation remains, and the one-shot send transition is durably bound to that frozen representation.

Unknown or unobservable post-attestation mutation removes SEND/RETRY authority. It never degrades to best effort.

## Primary-source donors

- RFC 9110 HTTP Semantics: automatic redirects can construct a new request and some redirect statuses historically allow method changes; 307/308 preserve method but still target a different URI. Redirect following is therefore a new semantic-decision boundary, not a transparent transport detail. https://www.rfc-editor.org/rfc/rfc9110.html
- gRPC Interceptors guide: interceptor order is significant, and interceptors closer to the network have more control over what is actually sent. The LAB send gate must therefore sit at the last supported client-side point before transport, not merely in application middleware. https://grpc.io/docs/guides/interceptors/
- AWS SDK for Go v2 middleware documentation: request processing is explicitly staged through Initialize, Serialize, Build, Finalize and Deserialize middleware, and custom middleware can modify client requests. A semantic check before the final mutation-capable stage is not sufficient. https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/middleware.html
- AWS SDK retry documentation: SDK clients can retry failed requests automatically. For consequential replay, SDK-owned automatic retry is itself authority-relevant and must be disabled, externally fenced, or made visible to the LAB attempt state machine. https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html

## Core invariants

1. **Attested means frozen, not merely observed.** A PASS attestation identifies an immutable `FrozenFinalRequestV1`; no semantic mutation is allowed afterward.
2. **One authority transition, one transport attempt.** `SEND_STARTED` / `RETRY_STARTED` CAS is bound to exactly one frozen request identity and exactly one transport-attempt identity.
3. **Network-adjacent dominance.** Every path capable of creating provider I/O must pass through the admitted final-send gate after all semantic mutation-capable middleware.
4. **No hidden retry.** A transport/SDK layer may not autonomously issue a second consequential request under the same LAB attempt unless that behavior is explicitly represented as the same provider-idempotent retry and admitted by the retry contract.
5. **Redirects are not transport-transparent.** Consequential redirects are denied by default. Any allowed redirect must be represented as an explicitly attested provider-semantic equivalent destination and must not mint new effect authority.
6. **Late signing is permitted only when isolated.** A lazy signer may run after freeze only if its declared output fields are classified `AUTH_REFRESHABLE` and a final observation proves it did not alter semantic fields, body, destination scope or provider identity.
7. **Streaming cannot outrun proof.** If authority-relevant payload semantics cannot be known and frozen before the provider can observe consequential bytes, the operation is not admitted for historical mutation replay.
8. **Crash after send transition is UNKNOWN-safe.** Once durable `SEND_STARTED` or `RETRY_STARTED` exists, any crash/timeout before authoritative outcome is treated under the existing UNKNOWN/reconciliation contract; local absence of a response is not permission to create a new attempt identity.

## Object model

### `FrozenFinalRequestV1`

Immutable object created only after semantic extraction/attestation succeeds:

- `attempt_id`
- `lease_id` or `retry_authorization_id`
- `provider_replay_capsule_digest`
- `semantic_extractor_generation_id`
- `semantic_request_digest`
- `final_request_observation_digest`
- exact method/RPC action
- exact provider endpoint identity and admitted routing scope
- exact semantic query/header projection
- exact body identity or admitted immutable stream identity
- refreshable-auth field declaration
- transport-only field declaration
- redirect policy
- retry policy
- proxy policy identity
- TLS/server-name policy identity
- resolver/service-discovery policy identity
- serializer/compressor/framing generation IDs
- final middleware/interceptor stack digest and ordering
- adapter/build/config/plugin generation IDs
- parent global-provenance record.

The object is content-addressed under the repository's canonical V1 encoding and domain separation.

### `FinalSendGateDeclarationV1`

Authenticated declaration for one adapter/provider transport stack:

- exact provider/service/operation/API scope;
- supported client/runtime/library versions;
- exact final hook/interposition location;
- proof that no semantic mutation-capable stage exists after that hook;
- list of allowed post-hook transformations, each classified as auth-refreshable or transport-only;
- redirect handling mode;
- SDK retry mode;
- proxy/resolver/TLS policy;
- lazy signer placement;
- streaming/body replayability class;
- hook implementation/build digest;
- positive and negative conformance fixture digests;
- parent global-provenance record and required authority signatures/quorum.

A declaration is invalidated by middleware order drift, client-library drift, config/plugin drift, endpoint-resolver drift, signing implementation drift, or any new post-hook mutator.

### `TransportAttemptV1`

Durable one-shot record:

- `transport_attempt_id`
- `business_attempt_id`
- `frozen_request_digest`
- `authority_generation`
- `final_send_gate_generation`
- state: `PREPARED -> SEND_STARTED -> {RESPONSE_OBSERVED | UNKNOWN | FAILED_BEFORE_IO}`
- monotonic/CAS sequence
- first-I/O evidence when observable
- terminal response/evidence reference when available
- parent global-provenance record.

`FAILED_BEFORE_IO` is legal only when the final gate can prove no externally visible consequential byte/frame was emitted. Ambiguous socket/TLS write failure after send transition is `UNKNOWN`, not `FAILED_BEFORE_IO`.

## Exact handoff sequence

For a consequential original send or admitted same-identity retry:

1. Load the exact replay capsule, lease/retry authority and current effective-authority/quarantine generations.
2. Build the request through all semantic mutation-capable serializer/endpoint/middleware stages.
3. Run provider-specific semantic extraction on the final observable request.
4. Compare it to the capsule semantic projection; mismatch fails closed.
5. Create `FrozenFinalRequestV1` and authenticated equivalence attestation.
6. Enter the declared final network-adjacent send gate.
7. Re-check current authority/quarantine generation and exact frozen-request identity.
8. Run only admitted late auth/transport transforms. Re-observe their outputs and prove all changed fields belong to the declared refreshable/transport-only set.
9. CAS append `TransportAttemptV1.SEND_STARTED` (or retry equivalent) bound to the frozen request.
10. Immediately invoke exactly one admitted transport send primitive. No application callback, redirect handler, endpoint resolver, general middleware, retry scheduler or mutable serializer may run between CAS and the primitive.
11. Record response/outcome evidence. If execution becomes ambiguous after step 9, transition to `UNKNOWN` and use reconciliation/retry-authority rules; do not mint a new SEND lease.

If the underlying client cannot expose such a boundary, the consequential operation is not admitted for automatic historical replay.

## Redirect policy

Default: `DENY_ALL_CONSEQUENTIAL_REDIRECTS`.

Rationale: RFC 9110 permits user agents to automatically create redirected requests; 301/302 may historically change POST to GET, while 307/308 preserve method but still change target URI. Either behavior can change provider account/region/resource/effect semantics.

An operation may opt into `ATTESTED_REDIRECT_SET` only when:

- the provider primary contract explicitly documents the redirect behavior;
- every allowed destination is pinned to an authenticated provider endpoint-equivalence set;
- method/body/idempotency token and all semantic fields are preserved exactly according to the extractor;
- credential forwarding is independently safe for the redirected origin;
- redirect count is bounded;
- the redirected request is re-extracted at the network-adjacent gate before any redirected consequential bytes are sent;
- redirects never create a new LAB attempt or provider token.

Cross-provider, cross-account, cross-region, downgrade-to-insecure, unlisted-host or resolver-surprise redirects fail closed.

## Retry-layer policy

Default: disable SDK/HTTP automatic retries for consequential operations and let the LAB attempt state machine own retry authorization.

If a provider SDK cannot disable internal retry, admission requires proof that:

- every internal retry reuses the exact provider-side idempotency identity;
- retryable error classes and max attempts are pinned;
- each wire attempt is observable and linked under one LAB `transport_attempt_id` or modeled as explicit child wire attempts;
- no middleware regenerates semantic defaults/token/body/destination;
- expiry of provider idempotency retention stops retries before a new effect could be created;
- quarantine/revocation can prevent any not-yet-started additional wire attempt.

A hidden client retry that can occur after `SEND_STARTED` without LAB observation is an admission failure.

## Lazy signing and credentials

Late credential acquisition/signing is allowed only after semantic freeze when all of the following hold:

- signer inputs are derived from the frozen method/URI/query/semantic headers/body digest;
- signer may change only explicitly declared auth-refreshable fields;
- resulting provider account/tenant/principal scope remains equivalent to the capsule's admitted scope;
- credential rotation cannot change idempotency namespace/effect ownership;
- a post-signing extractor check confirms semantic equality;
- signer or credential-provider callbacks cannot alter endpoint, body, query or semantic headers.

If signing itself selects region/service/endpoint or rewrites semantic headers, it belongs before freeze.

## HTTP middleware / transport adapters

The final hook must be below every layer that can modify:

- method/URL/query;
- semantic headers;
- cookies if provider-semantic;
- body or content coding;
- checksums/provider version fields;
- endpoint/account/region selection;
- idempotency token;
- redirect policy;
- request duplication/retry behavior.

Connection pooling, TCP segmentation, HTTP/2 frame boundaries and equivalent framing may remain below the hook only when declared transport-only. Any layer able to synthesize a new HTTP request remains above the gate or is separately attested.

## gRPC

The gRPC guide explicitly notes interceptor ordering and that network-near interceptors have more control over what is sent. Therefore:

- application-level interceptor PASS is insufficient;
- all client interceptors and call-credential behavior that can modify authority-relevant metadata/message/destination must precede the final observation;
- the admitted final hook must observe exact RPC method, authority/target, semantic metadata, message projection/bytes according to the extractor, deadline semantics when provider-relevant, compression settings and call credentials scope;
- transparent retries, hedging and service-config routing are disabled unless explicitly modeled and proven same-identity safe;
- one logical RPC producing multiple concurrent hedged network attempts is prohibited for consequential operations unless the provider contract itself proves deduplicated exactly-once effect semantics and the LAB models every wire attempt.

## Proxy, resolver, DNS and connection boundaries

DNS IP churn alone need not be semantic if the authenticated TLS/server-name/provider endpoint identity is unchanged. But the freeze must bind the *routing policy*, not an arbitrary resolved IP, unless provider semantics require exact IP.

Before admission, declare:

- logical provider hostname/service authority;
- permitted proxy identity/set;
- TLS SNI/server-name and certificate validation policy;
- allowed scheme/port;
- resolver/service-discovery generation;
- whether account/region/tenant routing is encoded below application-visible URL.

A proxy or service mesh that can rewrite destination, headers, body, retries or redirects is not transport-only and must be inside the attested dependency surface.

## Streaming / one-pass bodies

Three admitted classes:

1. `IMMUTABLE_REPLAYABLE`: complete body already exists as immutable bytes/content-addressed chunks; semantic digest known before send.
2. `TWO_PASS_BOUND`: pass one computes/validates semantic identity; pass two is cryptographically or content-addressably guaranteed to read the same bytes.
3. `PROVIDER_COMMIT_FENCED_STREAM`: provider protocol exposes an independently safe upload/prepare stage where transmitted chunks cannot create the consequential effect until a separately attested commit operation.

Generic `ONE_PASS_UNVERIFIED` is forbidden for consequential historical replay. Tee-hashing bytes while they are already leaving the socket does not close TOCTOU because the provider may receive a mutated consequential stream before mismatch is known.

## Cancellation, timeout and partial writes

Cancellation/timeout is not evidence of zero I/O. After durable `SEND_STARTED`:

- failure before the send primitive is invoked can be `FAILED_BEFORE_IO` only with direct final-gate proof;
- connection establishment failure may be `FAILED_BEFORE_IO` only if no HTTP/RPC request bytes were accepted by a remote/proxy endpoint and the transport contract makes that fact observable;
- partial write, response timeout, lost response, HTTP/2 stream reset after write, RPC cancellation after dispatch, or ambiguous proxy failure => `UNKNOWN`;
- UNKNOWN uses read-only oracle / same-identity retry / manual reconciliation contracts only.

## Conformance evidence

Each `FinalSendGateDeclarationV1` requires signed golden fixtures executed against the exact client/runtime generation.

Positive fixtures must show admitted changes remain semantic-equal, e.g. fresh auth signature/timestamp, allowed connection reuse, framing variation, allowed DNS address churn under the same authenticated endpoint.

Negative fixtures must independently prove detection or blocking of:

- method mutation;
- URL/path/query mutation;
- account/region/tenant endpoint mutation;
- semantic header mutation;
- body/default mutation;
- content-coding mutation when semantic;
- idempotency token change;
- middleware added after the declared hook;
- middleware reorder;
- automatic redirect;
- redirect target change;
- credential-scope change;
- proxy rewrite;
- late endpoint resolver change;
- SDK automatic retry/duplicate send;
- gRPC interceptor metadata/message mutation;
- gRPC transparent retry/hedge;
- post-attestation compression mutation;
- one-pass stream mismatch discovered only after emission;
- stale authority/quarantine generation between attestation and send;
- two-worker claim of one frozen request;
- crash before and after durable send transition.

## Frozen RED-first matrix

Freeze 80 cases before implementation:

- 1-8: final-hook dominance and middleware ordering;
- 9-16: immutable frozen-request identity / CAS / replay;
- 17-24: redirects and endpoint-equivalence boundaries;
- 25-32: SDK retry / duplicate-send / backoff behavior;
- 33-40: lazy signing / credential rotation / auth-refreshable fields;
- 41-48: proxy / resolver / DNS / TLS routing policy;
- 49-56: gRPC interceptors / metadata / retry / hedging;
- 57-64: compression / serializer / framing / transport adapters;
- 65-72: streaming / partial write / cancellation / UNKNOWN;
- 73-80: stale worker, quarantine/revocation race, crash/restart and global-provenance recovery.

Every negative fixture must fail before a new consequential provider effect can be authorized. Tests that merely observe a mismatch after bytes were already sent do not count as GREEN except for protocols explicitly classified as provider-commit-fenced streams.

## Security audit conclusions

- Semantic equivalence attestation alone does not close TOCTOU if request mutation remains possible after PASS.
- A generic wrapper around `client.send()` is insufficient unless it is provably below all semantic mutation-capable middleware and above the first irreversible external I/O.
- Redirect following, transparent retries and hedging are effect multipliers and must be authority-visible.
- Late signing is safe only as a constrained refresh of non-semantic authentication material; otherwise it must occur before freeze and be re-attested.
- DNS/connection churn can remain transport-only, but proxies/service meshes/endpoint resolvers that rewrite requests belong inside the authority dependency manifest.
- One-pass streaming is not replay-admissible when equality can only be learned after provider-visible bytes leave the process.
- The strongest safe fallback for an uninstrumentable client stack is read-only reconciliation/manual resolution, not weakening the final-send gate.

## Implementation boundary

This is a frozen design/evidence artifact only. Do not implement production SEND/RETRY behavior until the 80-case RED matrix is executable on the real supported adapter/transport surface and the existing LAB-086/LAB-088/LAB-090..100 dependency gates can run. No production cutover or post-reroot consequential re-admission is authorized by this document.
