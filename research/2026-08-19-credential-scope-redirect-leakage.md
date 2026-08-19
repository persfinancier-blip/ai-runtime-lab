# Origin/proxy credential scope and redirect leakage conformance

Date: 2026-08-19  
Issue: #48 / LAB-025  
Branch: `lab/025-credential-scope`

## Question

After LAB-022 through LAB-024 bind request payload, destination, endpoint, TLS identity and proxy path, how do we prevent authentication material from silently crossing an authority boundary during redirect, proxy fallback, credential rotation or retry?

## Primary-source mechanisms

### HTTP origin authentication and protection spaces — RFC 9110

Primary source: https://www.rfc-editor.org/rfc/rfc9110.html

Transferable mechanisms:

- an HTTP origin is the normalized `(scheme, host, port)` triple;
- `Authorization` authenticates to an origin server, while `Proxy-Authorization` authenticates to a proxy;
- a protection space is bounded by origin plus authentication realm;
- `Proxy-Authorization` applies to the next inbound proxy and is conceptually distinct from origin credentials;
- automatic redirects require care: origin/resource/proxy-specific fields such as `Authorization`, `Cookie`, and `Proxy-Authorization` are candidates for removal/recomputation rather than blind forwarding.

Implication: origin and proxy credentials need separate stores and separate materialization paths. A redirect or route change creates a new credential-selection decision.

### Cookie scope — RFC 6265 and current 6265bis work

Primary sources:

- https://www.rfc-editor.org/rfc/rfc6265.html
- https://datatracker.ietf.org/doc/draft-ietf-httpbis-rfc6265bis/

Transferable mechanisms:

- cookie return is constrained by host/domain and path matching;
- `Secure` limits sending to secure channels;
- path matching is structured rather than arbitrary string-prefix authority;
- current HTTPbis work continues to treat cookies as scoped state rather than generic headers to copy across requests.

Implication: session material is not equivalent to `Authorization`. It needs independent scope checks at each redirected target. The prototype deliberately models only host-only cookies, secure-only behavior and path matching; it does not pretend to be a browser cookie jar.

### Sender-constrained credentials — RFC 9449 DPoP

Primary source: https://datatracker.ietf.org/doc/html/rfc9449

Transferable mechanism:

DPoP demonstrates that possession of a bearer-like credential can be constrained by binding proof to request properties and a client key. The broader lesson for the lab is that credential possession alone is weaker than credential + request binding.

Implication: the prototype supports an optional request fingerprint on origin credentials. The fingerprint includes payload digest, purpose, stable effect identity and transport route fingerprint. This is not an implementation of DPoP; it reuses the sender/request-binding principle.

## Minimal credential-scope model

### Origin credentials

Bound to:

- canonical scheme/host/port;
- optional path scope;
- credential generation;
- optionally the current request/effect fingerprint.

### Cookies/session state

Bound separately to:

- host;
- structured path scope;
- secure-channel requirement;
- cookie generation.

### Proxy credentials

Bound to:

- proxy identity;
- proxy route generation;
- proxy credential generation.

They are materialized into a distinct proxy-header map. They are never placed in the origin header map.

### Request/effect composition

A permit is bound to:

- payload digest;
- purpose;
- effect ID;
- route fingerprint from the transport layer;
- request generation;
- canonical origin;
- exact credential IDs and generations.

A proxy route is additionally checked against the request route fingerprint, so a proxy credential cannot authorize a different transport path.

## Redirect and retry rules

1. Cross-origin redirect invalidates the old origin credential permit; credentials must be selected again for the new origin.
2. Same-origin redirect may reuse only credentials whose path/scope still matches the new resource.
3. Proxy fallback requires a new route binding and separately scoped proxy credential.
4. Credential rotation invalidates an existing permit by generation mismatch.
5. If an external side effect is `UNKNOWN`, no new credential/route permit may be issued until reconciliation. This preserves LAB-005/LAB-022 effect identity and prevents a retry from turning an uncertain commit into a new credential path.

## Unsafe baseline

`UnsafeForwarder` blindly copies request headers across a redirect. The seed sends:

- `Authorization: Bearer SECRET`
- `Cookie: sid=secret`
- `Proxy-Authorization: Basic PROXY`

and redirects to `https://attacker.example/`.

Observed result: the expected-safety test fails because all three secret-bearing headers are still present. This falsifies naive header forwarding.

## Corrected deterministic evidence

Observed locally on 2026-08-19:

```text
Ran 16 tests in 0.005s
OK
```

`python -m compileall -q experiments` also passed.

The matrix covers:

- same-origin Authorization + cookie;
- cross-origin redirect rejection;
- same-origin path-scope reevaluation;
- separate proxy/origin header materialization;
- origin credential cannot become proxy auth;
- proxy fallback requires new route/credential;
- origin credential rotation;
- proxy credential rotation;
- request generation staleness;
- `UNKNOWN` reconciliation gate;
- sender/request-bound credential;
- secure/host cookie scope;
- route/effect contribution to request fingerprint;
- cookie path segment-boundary regression;
- `UNKNOWN` blocking a changed-route permit;
- proxy route fingerprint mismatch rejection.

## Audit findings fixed before publication

The first implementation passed most cases but the audit found four contract defects:

1. an unknown proxy credential ID silently degraded to no proxy auth instead of failing closed;
2. path-scope violations were conflated with credential rotation/staleness;
3. cookie path scope used naive `startswith`, so `/private2` could match `/private`;
4. `UNKNOWN` blocked resume but did not block issuing a fresh permit on a changed route.

All four were corrected and covered by regression tests. A fifth composition check was added so the explicit proxy ID/generation must match the LAB-024-style route fingerprint.

## What remains distinct

- **Origin credential**: proves/authorizes a client toward one origin/protection scope.
- **Cookie/session material**: scoped state with different matching rules.
- **Proxy credential**: authenticates only to a selected proxy hop.
- **Transport identity**: proves where the connection actually goes; it does not grant application credentials.
- **Effect identity**: stable identity for idempotency/reconciliation; it does not itself authorize credential disclosure.

None of these authorities may be substituted for another.

## Non-goals and limitations

- no browser-grade Domain/SameSite/public-suffix cookie implementation;
- no OAuth authorization server or token refresh protocol;
- no real proxy or HTTP client;
- no storage-backed secret manager;
- no claim that path scope alone is a security boundary for arbitrary server-side credentials;
- no claim of sender-constrained security equivalent to actual DPoP cryptography.

## Stop-condition assessment

Three primary-source mechanism families were compared. The unsafe forwarding design was falsified. The corrected bounded matrix passes after audit fixes. LAB-025 is ready for exact-source publication validation and remote patch audit.
