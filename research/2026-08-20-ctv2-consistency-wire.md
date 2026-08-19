# LAB-042 — CT v2 consistency-proof wire binding

## Question

Can the compact consistency proof from LAB-041 be transported as an RFC 9162 CT v2 `TransItem` without introducing parser ambiguity or allowing a valid Merkle path to be rebound to another log/checkpoint pair?

## Primary provenance

RFC 9162 §1.2 says its structures use the TLS 1.3 presentation-language conventions from RFC 8446 §3. RFC 9162 §4.4 defines `opaque LogID<2..127>` as the DER OBJECT IDENTIFIER value bytes (tag/length excluded). §4.5 assigns `consistency_proof_v2 = 0x0105` and places the selected data directly after the two-byte `VersionedTransType`. §4.9 defines `NodeHash<32..2^8-1>` and requires its length to equal the log HASH_SIZE. §4.11 defines `ConsistencyProofDataV2` as LogID, two uint64 tree sizes, and `NodeHash consistency_path<0..2^16-1>`.

## Reference encoding

- `VersionedTransType`: 2-byte network-order `0x0105`.
- `LogID<2..127>`: 1-byte length + DER OID value bytes; malformed/non-minimal DER subidentifiers fail closed.
- `tree_size_1`, `tree_size_2`: 8-byte network-order unsigned integers.
- `consistency_path<0..65535>`: 2-byte byte-length followed by serialized `NodeHash` values.
- each `NodeHash<32..255>`: 1-byte length + hash bytes, and decoded length must equal configured HASH_SIZE.
- the top-level decoder consumes the entire supplied byte string; trailing bytes are rejected.

The independent fixture test constructs those fields directly with `struct.pack`, rather than calling the encoder under test.

## Binding rule

Wire parsing is not proof verification. Before LAB-041 is invoked, the adapter requires `proof.log_id == old.log_id == new.log_id` and exact equality of both proof tree sizes with the witnessed checkpoints. Only then are compact nodes passed to LAB-041 `verify_consistency`. An end-to-end test generates a real LAB-041 compact proof for 3→7 leaves, serializes it, decodes/binds it, and verifies the two roots without leaf material at the wire boundary.

## Failure injection

The unsafe seed parses only the declared proof-vector prefix and ignores bytes that follow it. Appended attacker-controlled bytes therefore remain accepted, demonstrating why strict top-level consumption is necessary.

## Observed local evidence

- corrected deterministic suite after integration audit: 14/14 tests passed;
- unsafe trailing-byte seed: expected failure;
- `python -m compileall -q experiments/ctv2_consistency_wire`: passed;
- tests cover round-trip, independent literal fixture, wrong type, truncation, trailing bytes, node HASH_SIZE mismatch, vector-boundary corruption, LogID bounds/canonical DER, vector maximum, exact checkpoint binding, swapped sizes, LAB-041 end-to-end compact proof verification, and uint64/type boundaries.

The Python runtime emitted unrelated `artifact_tool` spreadsheet warmup diagnostics during subprocess startup; the test and compile exit statuses above were observed independently. The end-to-end local run used an interface-compatible local copy of the already independently exact-source-validated LAB-041 algorithm because direct GitHub clone DNS remained unavailable in this runtime; the published adapter imports the repository LAB-041 module directly.

## Audit findings

Audit tightened `LogID` from mere length checking to canonical DER-OID-value validation, because RFC 9162 defines it as an OID encoding rather than arbitrary bytes. The decoder also treats HASH_SIZE as a trusted log-profile input rather than inferring it from attacker-controlled node lengths. A second audit added an end-to-end adapter test rather than relying only on a spy verifier.

## Scope boundary

This is a proof-envelope and binding reference, not a full CT client/server. STH signature validation, log-parameter discovery, HTTP/base64 transport, witness quorum/gossip, algorithm negotiation, and network behavior remain outside scope. Merkle semantics are delegated to LAB-041.
