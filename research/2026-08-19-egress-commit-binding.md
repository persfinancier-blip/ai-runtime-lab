# LAB-022 — Commit-time egress authorization binding and redirect TOCTOU

## Question
How can an agent prove that the exact protected disclosure authorized during policy evaluation is still the exact request committed to an external sink after redirects, mutations, retries, and policy changes?

## Primary-source donor mechanisms

### IETF DPoP (RFC 9449)
DPoP sender-constrains an authorization token and requires each proof to match the current HTTP method (`htm`) and URI (`htu`). It also uses unique proof identifiers and replay controls. Transferable mechanism: authorization should be checked against the concrete request at use time, not only at token issuance.

Source: https://datatracker.ietf.org/doc/html/rfc9449

### AWS Signature Version 4
SigV4 constructs a canonical request from method, canonical URI/query, selected headers, and payload hash, then signs the hash of that canonical request. Transferable mechanism: bind authority to canonical destination/request identity and payload bytes, so mutation after preparation invalidates authorization.

Source: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv-create-signed-request.html

### W3C capability URL guidance
Capability guidance emphasizes unguessability, expiry, revocation, canonical resources, and explicit handling of redirects. Transferable mechanism: capabilities need bounded lifetime and revocation/rebinding semantics; redirects cannot silently broaden the authority represented by a capability.

Source: https://www.w3.org/TR/capability-urls/

Supporting security guidance: OAuth 2.0 Security BCP (RFC 9700) recommends sender-constrained tokens where appropriate and reinforces that bearer possession alone is insufficient for high-assurance use.

## State model

`PREPARE` validates LAB-020 authority and LAB-021 disclosure policy, then issues an authenticated permit containing:
- permit/version/issuer identity;
- payload SHA-256 digest;
- canonical HTTPS destination;
- purpose;
- policy generation;
- authorization generation and authorization id;
- nonce + expiry;
- stable effect/idempotency key.

`COMMIT` canonicalizes the actual destination and revalidates every field against the current payload, purpose, policy generation, and cryptographically authenticated trusted-control authorization. Any mismatch blocks before side effect.

`UNKNOWN` outcome does not create a broader permit. LAB-005 semantics reconcile the same effect key. Exact duplicate delivery returns the same receipt and does not duplicate the external effect.

## Unsafe seed
A conventional `check(destination) -> later use(destination)` design can validate `trusted.example`, then use `attacker.example` after a redirect/mutation. The retained unsafe test expects the original trusted destination and therefore fails when the redirected sink is actually committed.

## Audit finding fixed before publication
The first local implementation represented trusted authorization with a structurally forgeable boolean. That would regress LAB-020/021. It was replaced with an authenticated trusted-control authorization object; forged structural authorization is now rejected by a deterministic test.

## Composition
- **LAB-005:** stable `effect_key` + unknown-outcome reconciliation prevents retry from broadening or duplicating the authorized effect.
- **LAB-015:** production permit consumption/effect intent should commit transactionally; this prototype models the invariant but is not a distributed transactional store.
- **LAB-020:** only authenticated trusted control-plane authority can issue protected-disclosure authorization; data-plane/tool output cannot mint authority.
- **LAB-021:** taint/classification decides whether disclosure requires authorization; LAB-022 binds that authorization to the exact commit-time request.

## Local evidence
- Corrected commit-binding suite: 14/14 tests passed.
- `python -m compileall -q experiments` passed.
- Unsafe redirect TOCTOU seed failed as intended: actual committed destination was `https://attacker.example/upload`, contradicting the previously checked trusted destination.

## Non-goals
No general service mesh, network proxy, cryptographic capability framework, DNS pinning system, or covert-channel defense. Canonical URL equality does not prove network-layer endpoint identity; production HTTP executors must also control redirect following and destination resolution at the transport boundary.
