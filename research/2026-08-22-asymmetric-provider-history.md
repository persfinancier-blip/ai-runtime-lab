# LAB-082 — Asymmetric provider receipts and verification-only history

## Question

Can LAB-081's execution-policy distinction between current signing authority and historical verification authority be made cryptographic, so durable historical state is physically incapable of creating new valid receipts?

## Donors

- RFC 8032 defines Ed25519 with distinct private signing and public verification keys. The public key is sufficient to verify a signature but is not a signing capability.
- TUF root-update continuity requires root N+1 to be authorized by both the trusted old root and the new root and rejects rollback. LAB-082 transfers that double-authenticated continuity pattern to provider generations.

## Reference protocol

The SQLite history stores only `(provider_id, generation, Ed25519 public key)`, old/new transition signatures, and signed receipt evidence. Private Ed25519 signer objects remain outside the database. A new generation must be exactly N+1 for the same provider and the transition must verify under both the old and new public keys.

Receipts are signed by a runtime `GenerationSigner` only after its public generation ID is proven equal to the durable current head. Historical receipts are verified from persisted public keys only.

This makes the core LAB-081 boundary cryptographic: compromising the durable history reveals verification material but not a private signing capability.

## Shared-anchor integration

LAB-082 is now integrated in the branch behind the existing LAB-080 SQLite serialization boundary rather than as a parallel authority store.

- reservation reads the asymmetric provider head while holding the same `BEGIN IMMEDIATE` transaction that appends a PREPARED shared-anchor intent;
- provider rotation checks for unresolved PREPARED work and advances the asymmetric provider head in that same write transaction;
- LAB-036 HMAC observations are used only to authenticate current execution-time provider behavior;
- after provider reconciliation succeeds, the current runtime Ed25519 signer signs the exact `(provider, generation, position, request, kind, challenge)` evidence;
- CONFIRMED historical rows are verified from the durable Ed25519 receipt and public history, so an old LAB-036 HMAC key is not needed after rotation/restart;
- the supported surface requires both the current LAB-036 provider identity and the current Ed25519 signer identity to match the same durable provider head.

A cross-layer race audit found that two workers can reconcile the same committed request with different fresh challenges. Both receipts are valid, but treating the second signature as content substitution would create a false failure. The audited supported surface therefore treats the first signature-valid, exact-request-bound durable receipt as canonical; later workers re-verify and converge on it. A concurrent confirmation that advances the ledger row to CONFIRMED is also accepted only when its durable receipt binding matches exactly.

## Schema/audit findings

The first implementation used an exact concrete-type check for `Ed25519PrivateKey`; `cryptography` returns a backend implementation satisfying the Ed25519 interface, so that check rejected valid keys. It was corrected to the library's supported `isinstance` interface check.

A separate schema audit added strict integer semantics and canonical lowercase fixed-size hex encodings. This prevents Python `bool == 1` and alternate hex representations from becoming accidental identity aliases in durable state.

The integration audit additionally preserves an explicit boundary around whole-store freshness: an internally consistent old SQLite snapshot plus matching old runtime trust can still pass local history verification. LAB-082 does not re-invent rollback resistance; LAB-034–037 and later external/shared-anchor work remain authoritative for that property.

## Validation state

Previously observed before the integration slice was published:

- isolated corrected suite: 16/16 passed;
- unsafe symmetric baseline: failed as expected because durable historical HMAC material could sign a new effect;
- compileall: passed.

The current PR now includes integration and supported-surface regressions for mixed generations, restart without historical HMAC material, PREPARED-vs-rotation serialization, current-signer enforcement, durable-secret absence, receipt/transition corruption, reservation-vs-rotation races, and concurrent receipt convergence.

These new PR-head bytes have **not yet completed exact-source execution**. Direct `git` access from the current runtime was re-probed and failed before checkout because `github.com` DNS resolution is unavailable. The PR therefore remains draft until exact published bytes are reconstructed through the GitHub connector and the LAB-082 + LAB-081/LAB-080/LAB-036 regression gate is actually executed.

## Non-goals

This does not implement HSM/KMS custody, PKI certificates, provider consensus, cross-provider failover, remote signing services, or compromise recovery. In-memory private key handling remains a runtime responsibility. Public-key history prevents durable verification storage itself from becoming a signing capability; it does not claim that a separately retained old private key is incapable of signing.

## Primary sources

- RFC 8032: https://www.rfc-editor.org/rfc/rfc8032
- TUF specification: https://theupdateframework.github.io/specification/latest/
