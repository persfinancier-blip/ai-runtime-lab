# CT v2 signed-tree-head authentication chain

Date: 2026-08-20  
Issue: #82 / LAB-043  
Branch: `lab/043-ctv2-sth-chain`

## Question

How do we replace pre-trusted checkpoint roots with authenticated RFC 9162 `signed_tree_head_v2` artifacts and preserve exact binding through the existing compact consistency-proof chain?

## Primary-source findings

RFC 9162 defines a log by immutable parameters including its signature algorithm, public key and OID Log ID. The Log ID is the DER OBJECT IDENTIFIER value bytes, excluding ASN.1 tag and length, carried as `opaque LogID<2..127>`.

A `TreeHeadDataV2` contains `timestamp`, `tree_size`, `root_hash` and ordered unique STH extensions. The root-hash length must match the log's `HASH_SIZE`.

A `signed_tree_head_v2` is a `TransItem` containing `LogID`, the `TreeHeadDataV2`, and an opaque signature. Critically, RFC 9162 §4.10 states that the signature is computed over the **tree_head field**, using the signature algorithm declared in the log parameters. The Log ID is therefore bound separately to the immutable profile and key rather than being part of the signature input itself.

RFC 9162's signature registry includes `ed25519 (0x0807)`, aligned with the TLS SignatureScheme code point defined by RFC 8446. The executable reference profile uses Ed25519 because the `cryptography` implementation is observed available in this runtime.

Primary sources:
- RFC 9162 §§4.1, 4.4, 4.5, 4.9, 4.10, 4.11: https://www.rfc-editor.org/rfc/rfc9162.html
- RFC 8446 §4.2.3 SignatureScheme registry: https://www.rfc-editor.org/rfc/rfc8446.html

## Implemented binding chain

`experiments/ctv2_sth_chain/protocol.py` implements:

1. complete `TransItem<signed_tree_head_v2>` decoding with exact type and no trailing bytes;
2. strict `LogID` length/minimal OID-value validation;
3. exact `TreeHeadDataV2` encoding/decoding with HASH_SIZE-bound root and ordered unique extensions;
4. immutable `LogProfile` binding of Log ID, hash size, signature scheme and public key;
5. Ed25519 verification over the exact encoded `tree_head` bytes;
6. conversion only of authenticated STHs into LAB-042 `WitnessCheckpoint` inputs;
7. exact Log ID and old/new size binding in the LAB-042 consistency envelope;
8. LAB-041 compact Merkle verification of both authenticated roots.

A new STH must have a strictly newer timestamp than the old STH, matching RFC 9162's subsequent-update requirement.

## Unsafe baseline

`tests/unsafe_parsed_expected_failure.py` deliberately corrupts a valid STH signature and then uses `unsafe_trust_parsed_fields()`, which only parses the wire object. The parsed fields remain plausible, demonstrating that strict parsing alone is not authentication. The safety assertion therefore fails as expected.

A corrected regression test independently confirms that `authenticate_sth()` rejects the same corrupted-signature case.

## Validation observed in this run

Exact branch source was reconstructed from the GitHub connector and checked with Git blob identity:

- `experiments/ctv2_sth_chain/protocol.py` local `git hash-object` = GitHub blob `3fe61a780678e80125b8f1fbb93dc890e686f976`.
- `experiments/ctv2_sth_chain/tests/test_protocol.py` local `git hash-object` = GitHub blob `4045edd3b92299aaf8cd29a32b6982e5a4eb4912`.

Observed before the final two test files were published:

- exact branch suite: **16/16 passed**;
- `python -m compileall -q experiments/ctv2_sth_chain` passed;
- unsafe parsed-only baseline failed as expected because a corrupted signature was not authenticated.

The LAB-041 compact verifier and LAB-042 strict consistency-wire decoder are already independently validated completed artifacts in `main`; the end-to-end LAB-043 suite exercises their interfaces with authenticated STH roots.

## Audit findings

The cryptographic/wire implementation itself did not require a protocol change in this audit. The material defect was deliverable inconsistency: README documented an unsafe seed that had not actually been committed. That seed is now present, and a corrected corrupted-signature regression was added so the unsafe demonstration has a matching positive security assertion.

## Security boundary and non-goals

This LAB proves artifact authentication and append-only growth for an already configured log profile. It does **not** solve:

- discovery/distribution or rotation of CT log profiles and public keys;
- general algorithm agility beyond the executable Ed25519 reference profile;
- HTTP/base64 CT client/server behavior;
- witness quorum/gossip transport, already separated in LAB-040;
- certificate-policy compliance or SCT inclusion policy.

## Decision

An STH root becomes authoritative only after strict wire decoding, immutable log-profile binding and signature verification. A consistency proof is then meaningful only when bound to the exact authenticated old/new STH Log ID and tree-size pair and when it reconstructs both authenticated roots.
