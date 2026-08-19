# TLS origin authentication and proxy-path binding conformance

Date: 2026-08-19  
Issue: #46 / LAB-024  
Branch: `lab/024-tls-proxy-binding`

## Question

After application authorization (LAB-022) and DNS/endpoint validation (LAB-023), what additional identities must remain bound so HTTPS or an explicit HTTP CONNECT proxy cannot silently redirect an authorized effect to a different TLS origin, tunnel authority or proxy-resolved endpoint?

## Primary-source donor mechanisms

### RFC 9525 — Service Identity in TLS

Source: https://www.rfc-editor.org/rfc/rfc9525.html

Transferable mechanisms: clients construct reference identifiers from the service identity they intended to contact; DNS services are authenticated with DNS-ID subjectAltName values rather than the legacy Common Name; service identity remains distinct from the DNS resolution path; wildcard matching is constrained.

Implication: LAB-023's validated IP is necessary but insufficient. For an HTTPS DNS origin, the TLS reference name remains the authorized origin hostname and the certificate must authenticate that name.

### RFC 6066 + RFC 8446 — TLS Server Name Indication

Sources:
- https://www.rfc-editor.org/rfc/rfc6066.html
- https://www.rfc-editor.org/rfc/rfc8446.html

Transferable mechanisms: SNI lets a client state the server name it is contacting so a multi-tenant endpoint can select the correct certificate/security context; RFC 6066's `host_name` is the DNS hostname understood by the client; TLS 1.3 continues to use `server_name` and clients should send it for name-identified services.

Implication: when connecting to a pinned validated IP, a real TLS adapter still needs to send the authorized origin hostname as SNI and verify the peer certificate against that same reference hostname.

### RFC 9110 / RFC 9112 — CONNECT authority

Sources:
- https://www.rfc-editor.org/rfc/rfc9110.html#name-connect
- https://www.rfc-editor.org/rfc/rfc9112.html#name-authority-form

Transferable mechanisms: CONNECT asks a proxy to create a tunnel to the destination identified by the request target; the request target is specifically `host:port` authority form; after successful CONNECT the proxy blind-forwards tunnel data and TLS commonly authenticates the origin end-to-end.

Implication: proxy routing is a separate authority boundary. CONNECT authority must equal the authorized origin authority, and proxy identity/policy generation must be part of the permit. Proxy-side resolution must match already validated endpoint evidence or force revalidation/re-authorization.

## Synthesized identity model

All layers are required and distinct:

1. application authority — payload digest, origin, purpose, authorization generation, effect id;
2. connection endpoint — validated origin-to-IP evidence and endpoint generation from LAB-023;
3. TLS reference identity — authorized DNS origin used for SNI and certificate DNS-ID matching;
4. proxy authority — route kind, proxy identity/endpoint, proxy policy generation and CONNECT host:port;
5. effect identity — stable effect id plus a route fingerprint covering every security-relevant layer.

Trust must not flow upward from a later layer. A certificate for the right host does not authorize an unapproved proxy path; a correct IP does not authenticate the TLS origin; an allowlisted proxy does not authorize a different CONNECT target.

## Unsafe baselines

Two deliberately incomplete transports were executed:

- IP-only accepted the validated socket IP while ignoring SNI/certificate identity; it accepted `attacker.example` at the correct IP and failed its safety assertion.
- certificate-only proxy accepted a matching certificate while ignoring CONNECT authority and proxy-side resolution; it accepted a tunnel targeting `attacker.example` / `127.0.0.1` and failed its safety assertion.

Observed unsafe result: **2/2 seeded safety tests failed as intended**.

## Corrected bounded matrix

Final corrected local suite after audit: **14/14 tests passed** plus `compileall`.

Covered: valid pinned endpoint + SNI + certificate; wrong SNI; wrong certificate; wrong socket endpoint; endpoint evidence tied to another origin; CONNECT target drift; proxy-side DNS drift; proxy identity/endpoint/generation drift; direct-to-proxy fallback; UNKNOWN reconciliation on the same route; rejection after route-generation drift; effect-id reuse with changed payload/purpose; and constrained single-label wildcard matching.

## Audit defects found and fixed

The first corrected implementation still had two cross-layer weaknesses:

1. route fingerprint omitted payload digest, purpose and authorization generation, allowing theoretical reuse of an effect id with changed application semantics;
2. endpoint evidence's origin hostname was not checked against the authorized origin.

Both were fixed before publication and regression tests were added.

## Production implications

A production transport adapter should expose or enforce enough information to verify at commit time: intended reference hostname/port, SNI actually used, certificate SAN identity for that hostname, actual connected IP equal to validated endpoint evidence, proxy endpoint and policy generation, CONNECT authority equal to intended origin, no silent proxy-side endpoint broadening, and exact-route reconciliation after UNKNOWN before any route change.

If a client library hides one of these boundaries, that capability should remain unproven until an adapter can observe or constrain it.

## Non-goals

No X.509 chain validator, revocation/CT implementation, TLS stack, real HTTP proxy, proxy authentication, kernel egress enforcement or production networking is implemented here. This is an adapter-level conformance contract.

## Stop condition

Three primary-source mechanism families were compared, both unsafe baselines were falsified, the corrected bounded matrix passes, and audit fixes are covered by regression tests. LAB-024 is ready for remote patch audit and exact-source validation.