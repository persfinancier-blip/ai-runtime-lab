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

## Schema/audit findings

The first implementation used an exact concrete-type check for `Ed25519PrivateKey`; `cryptography` returns a backend implementation satisfying the Ed25519 interface, so that check rejected valid keys. It was corrected to the library's supported `isinstance` interface check.

A separate schema audit added strict integer semantics and canonical lowercase fixed-size hex encodings. This prevents Python `bool == 1` and alternate hex representations from becoming accidental identity aliases in durable state.

## Validation

Observed local reference result before publication:

- corrected suite: 16/16 passed;
- unsafe symmetric baseline: failed as expected because durable historical HMAC material could sign a new effect;
- compileall: passed.

## Integration implication

The next step is to place this asymmetric history behind the merged LAB-081 supported shared-anchor surface so existing LAB-080 serialization/restart semantics are preserved while historical durable state contains public verification material only.

## Non-goals

This does not implement HSM/KMS custody, PKI certificates, provider consensus, cross-provider failover, remote signing services, or compromise recovery. In-memory private key handling remains a runtime responsibility.

## Primary sources

- RFC 8032: https://www.rfc-editor.org/rfc/rfc8032
- TUF specification: https://theupdateframework.github.io/specification/latest/
