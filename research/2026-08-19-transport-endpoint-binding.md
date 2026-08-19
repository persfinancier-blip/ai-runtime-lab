# Transport Endpoint Binding Against DNS Rebinding, SSRF, and Redirect Drift

Date: 2026-08-19  
Issue: #44 / LAB-023

## Question

How can an egress executor preserve an already-authorized application request while preventing DNS rebinding, redirects, aliases, special-purpose IP literals, and retry-after-UNKNOWN from moving the actual connection onto an unauthorized network endpoint?

## Primary-source mechanisms

### IANA / RFC 6890 + RFC 8190 — special-purpose address classification

Primary sources:
- https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml
- https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml
- https://www.rfc-editor.org/info/rfc6890/
- https://www.rfc-editor.org/rfc/rfc8190.html

Transferable mechanism: endpoint policy must reason about the actual resolved IP, not only the hostname. Loopback, private-use, link-local, unspecified, metadata-local and other non-globally-reachable/special-purpose ranges cannot be treated as equivalent to public Internet endpoints. IPv4-mapped IPv6 must be normalized before classification so `::ffff:127.0.0.1` cannot bypass an IPv4 rule.

### RFC 9110 — redirects change the request target

Primary source:
- https://www.rfc-editor.org/info/rfc9110/

RFC 9110 defines `Location` as a URI-reference and automatic redirects replace the target URI. It also warns that automatic redirection requires care. The security implication for LAB-023 is that each redirect is a new transport target, not a continuation implicitly covered by the previously checked endpoint.

LAB-022 binds the authorized canonical destination. Therefore LAB-023 does **not** silently broaden a permit across hosts: cross-host redirect requires new authorization. Same-host redirect may proceed, but DNS and endpoint class are revalidated.

### RFC 3986 — host syntax and normalization

Primary source:
- https://www.rfc-editor.org/info/rfc3986/

RFC 3986 distinguishes registered names, IPv4 literals, and IPv6 literals and defines normalization rules. Endpoint checks need normalized host/IP forms before comparison; security cannot depend on a particular textual spelling.

### AWS EC2 IMDS — concrete SSRF-sensitive local endpoints

Primary sources:
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-limiting-access.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html

AWS documents the local metadata endpoints `169.254.169.254` and IPv6 `fd00:ec2::254`, and explicitly recommends network controls that reject unauthorized access. These are concrete examples of endpoints a generic public egress path must not reach merely because a hostname resolves there.

## Synthesized transport contract

Keep four identities separate:

1. **Application authorization identity** — LAB-022 permit/request: payload digest, canonical destination, purpose, policy generation, effect key.
2. **Hostname/origin identity** — the authorized HTTPS hostname.
3. **Resolution result** — DNS/alias chain plus all returned IP endpoints at a moment in time.
4. **Actual connection endpoint** — the specific IP to which the socket is opened.

Correctness rules:

- preserve the exact LAB-022 request/effect identity;
- classify every IP result after normalization;
- reject a resolution set if **any** candidate endpoint violates the public-egress policy, avoiding resolver-choice ambiguity;
- revalidate after every redirect;
- do not let DNS alias names acquire application authority merely by appearing in the resolution chain; validate the resulting endpoint instead;
- re-resolve immediately before connection and connect to the just-validated IP rather than resolving the hostname again inside the connector;
- require new authorization for cross-host redirect;
- after `UNKNOWN`, reconcile the same stable effect identity before any new resolution/retry; do not broaden the transport endpoint silently.

## Unsafe baseline

The seeded design checks one DNS result and later resolves the hostname again during connection. The first lookup returns `93.184.216.34`; the second returns `127.0.0.1`.

Observed expected failure:

```text
AssertionError: '127.0.0.1' != '93.184.216.34'
unsafe resolve-once design connected to rebound endpoint
FAILED (failures=1)
```

This falsifies resolve-once/check-then-connect.

## Corrected experiment

Prototype: `experiments/transport_binding/`

Observed local results after audit fix:

- corrected deterministic suite: **13/13 passed**;
- `python -m compileall -q experiments`: passed;
- unsafe expected-failure seed: failed as intended.

Covered cases include public success, public→loopback rebinding, private/link-local/metadata IPv4 and IPv6, IPv4-mapped IPv6, mixed safe/unsafe answer sets, same-host redirect revalidation, cross-host redirect rejection, alias-to-forbidden endpoint, redirect-time rebinding, LAB-022 identity mismatch, and retry-after-UNKNOWN reconciliation without re-resolution.

## Audit finding and correction

The first corrected draft allowed a redirect from `trusted.example` to another allowlisted hostname. That is a transport-policy broadening that conflicts with LAB-022's canonical destination binding. The implementation was tightened: cross-host redirects now require a fresh authorization. Same-host redirects remain allowed and are fully revalidated.

A second audit clarification removed an unnecessary requirement that every CNAME/alias label itself be an application allowlisted host. Alias names are DNS resolution metadata; application authority remains the original hostname. The resulting connection endpoint still must pass the endpoint policy.

## Production implications

A production adapter should:

- use an authoritative current special-purpose IP classification source or equivalent maintained library;
- disable implicit redirect following and apply policy at each hop;
- resolve under policy control, validate all candidate addresses, and pass a chosen validated IP directly to the socket/HTTP transport;
- preserve TLS SNI and certificate verification for the authorized hostname even when connecting to a pinned IP;
- control proxy behavior so a proxy cannot independently re-resolve or reroute around endpoint policy;
- record resolution/redirect/selected-endpoint observations as evidence;
- reconcile `UNKNOWN` using the existing effect identity before a retry performs any fresh resolution;
- require new trusted authorization when a redirect changes host/origin.

## Non-goals

- no DNSSEC implementation;
- no general SSRF proxy/service mesh;
- no full HTTP/TLS stack;
- no claim that application endpoint checks replace OS/network egress controls;
- no universal definition that every globally-routable address is suitable for every product policy.

## Stop-condition assessment

The required donor mechanisms were compared, the unsafe design was falsified, and the bounded fake transport matrix passes after audit correction. Remaining work is exact-source publication/audit/integration.
