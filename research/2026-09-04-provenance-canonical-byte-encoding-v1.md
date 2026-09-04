# Canonical provenance byte encoding V1

Date: 2026-09-04
Status: design/serialization contract frozen; exact RED/GREEN pending
Related: LAB-092/#176, LAB-097/#182, LAB-099/#184, LAB-100/#185, LAB-094..096/#179..181

## Objective

Freeze one byte-level, domain-separated encoding shared by the authenticated provenance contracts already selected for:

- LAB-092 activation-schema migration certificates;
- LAB-097 database initialization certificates;
- LAB-099 activation-ticket digests committed by provider-generation transitions;
- LAB-100 activation-authority descriptors and authority-transition records.

The purpose is to prevent two subsystems from authenticating semantically different values as the same authority fact, or the same authority fact as different digests, because of JSON key ordering, Unicode/number coercion, Python `bool`/`int` equivalence, SQLite affinity, text-vs-integer storage, omitted/default fields, or implementation-specific object serialization.

This note does not change production code. Exact repository execution remains unavailable in this run: direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`.

## Why a custom small encoding instead of JSON or generic object serialization

The existing frozen contracts need only a small set of primitives: opaque bytes, UTF-8 identifiers, non-negative integers, fixed digests, and nested-record digests. A deliberately tiny schema-specific TLV encoding is easier to audit and reproduce in the Python standard library than introducing a broad serializer.

V1 therefore does **not** hash:

- Python `repr()` / dataclass serialization;
- JSON text;
- SQLite textual values;
- SQL source after ad-hoc whitespace normalization;
- dictionaries whose order/default omission is implementation-defined.

If a future implementation adopts deterministic CBOR or another standardized codec, that is a protocol-version transition; it must not silently change V1 bytes.

## Frozen envelope

Every authenticated object is serialized independently as:

```text
MAGIC                  8 bytes  = 59 54 49 4d 50 52 56 31  (ASCII "YTIMPRV1")
DOMAIN_LENGTH          u16be
DOMAIN                 DOMAIN_LENGTH raw ASCII bytes
FIELD_COUNT            u16be
FIELD[0..N-1]          encoded in strictly increasing numeric field-id order
```

Each field is:

```text
FIELD_ID               u16be
TYPE                    u8
VALUE_LENGTH            u32be
VALUE                   VALUE_LENGTH bytes
```

No padding, terminator, platform newline, native-endian integer, or implicit/default field exists in the authenticated byte stream.

### Type codes

```text
0x01 UTF8
0x02 BYTES
0x03 U64
0x04 DIGEST32
```

Rules:

- field ids are schema constants, unique, non-zero, and serialized in strictly increasing order;
- unknown, duplicate, out-of-order, missing-required, or extra fields fail closed;
- all length prefixes are unsigned big-endian and must be minimally represented by their fixed-width prefix type;
- decoders reject trailing bytes;
- each schema has an exact required field set in V1; there are no optional fields whose absence implies a default;
- schema evolution uses a new domain/version, not an ignored extra field.

## Primitive canonicalization

### UTF8

Input must be an actual Python/string-language string value, not bytes or an implicitly converted object. Encode with strict UTF-8. Embedded NUL is allowed at the byte level because length framing is authoritative, but individual schemas may forbid it for identifiers.

V1 performs **no Unicode normalization**. The exact Unicode scalar sequence is identity. A visually equivalent NFC/NFD spelling therefore hashes differently rather than being silently conflated. Authority identifiers SHOULD be restricted by their schema to the narrowest existing character contract (prefer existing ASCII ids where possible).

Malformed Unicode/surrogate input fails before hashing.

### BYTES

Exact opaque byte sequence. No hex/base64 textual conversion is part of the canonical form.

### U64

Exactly eight unsigned big-endian bytes. Accepted semantic input must satisfy:

```text
type(value) is int
0 <= value <= 2**64 - 1
```

`bool`, float, Decimal, numeric text, SQLite REAL, and implicitly coercible objects are rejected even where `int(value)` would succeed.

This is important because the current LAB-090 provider prototype calls `int(expected_position)`; provenance verification must be stricter than that convenience conversion.

### DIGEST32

Exactly 32 opaque bytes. A hex string is presentation only and is never accepted by the canonical encoder without an explicit decode/length check at the boundary.

## Hash construction and domain separation

All V1 object digests are:

```text
SHA-256(canonical_object_bytes)
```

The object domain is inside the hashed envelope. No second `domain || digest` convention is permitted for V1.

Frozen domains:

```text
ytim.lab092.migration-certificate.v1
ytim.lab097.initialization-certificate.v1
ytim.lab099.activation-ticket.v1
ytim.lab100.activation-authority-descriptor.v1
ytim.lab100.activation-authority-transition.v1
ytim.provider-generation-head.v1
ytim.schema-definition.v1
```

A digest from one domain must never be accepted where another domain is required, even if field layouts happen to be byte-identical.

## Schema: LAB-099 activation ticket

Domain: `ytim.lab099.activation-ticket.v1`

Required fields:

```text
1  provider_id                  UTF8
2  provider_generation          U64
3  new_generation_id            UTF8
4  expected_position            U64
5  activation_id                UTF8
6  fence                        U64
7  activation_protocol_version  U64
```

The authenticated provider-generation transition stores only `SHA-256(ticket_bytes)` as its `activation_ticket_digest`, but verification reconstructs the complete canonical ticket from the activation row plus authenticated transition context and requires exact digest equality.

`new_generation_id` is intentionally included even though the current `ActivationTicket` dataclass does not carry it: the digest is transition provenance, not merely a hash of the current Python object shape. This prevents replay of a syntactically valid ticket into another generation transition.

## Schema: LAB-100 activation authority descriptor

Domain: `ytim.lab100.activation-authority-descriptor.v1`

Required fields:

```text
1  implementation_id             UTF8
2  implementation_version        U64
3  protocol_version              U64
4  provider_id                   UTF8
5  provider_generation           U64
6  provider_verification_key_id  UTF8
```

`implementation_version` is a semantic protocol integer in V1, not a free-form display string. If the implementation currently uses a textual release name, registration must map that name to a stable integer semantics version before construction.

## Schema: LAB-100 authority transition

Domain: `ytim.lab100.activation-authority-transition.v1`

Required fields:

```text
1  old_authority_descriptor_digest      DIGEST32
2  new_authority_descriptor_digest      DIGEST32
3  provider_generation_transition_digest DIGEST32
4  activation_state_handoff_digest       DIGEST32
5  transition_protocol_version           U64
6  transition_epoch                      U64
```

A quiescent and unresolved handoff require different domain-separated handoff-record schemas when implemented; `activation_state_handoff_digest` never hashes an untyped dictionary/string blob.

## Schema: LAB-097 initialization certificate

Domain: `ytim.lab097.initialization-certificate.v1`

Required fields:

```text
1  logical_database_identity_digest       DIGEST32
2  bootstrap_generation_id                UTF8
3  bootstrap_descriptor_digest            DIGEST32
4  provider_history_protocol_version       U64
5  initialization_epoch                    U64
6  initialization_nonce                    BYTES
7  initial_authenticated_chain_root_digest DIGEST32
8  activation_authority_descriptor_digest  DIGEST32
```

`initialization_nonce` MUST be exactly 32 bytes in V1. The nonce is generated once by the explicit trusted initialization operation and thereafter verified; ordinary restart never regenerates it.

Binding the activation-authority descriptor here closes a construction gap between the earlier LAB-097 certificate sketch and the later LAB-100 first-class authority model.

## Schema: schema-definition digest

Domain: `ytim.schema-definition.v1`

Required fields:

```text
1  schema_object_kind   UTF8   # e.g. "sqlite-table" or "sqlite-trigger"
2  schema_object_name   UTF8
3  definition_bytes     BYTES
```

For LAB-092 V1, `definition_bytes` are **repository-owned exact canonical DDL bytes**, not SQL fetched from `sqlite_master` and whitespace-normalized. Runtime verification checks both:

1. the installed SQLite definition has the expected exact semantic definition according to the existing strict classifier; and
2. the migration certificate binds the digest of the repository-owned canonical definition bytes used by that classifier/installer.

This avoids pretending SQLite round-tripped SQL text is a canonical serialization format.

## Schema: provider-generation head binding

Domain: `ytim.provider-generation-head.v1`

The head binding must itself be a digest of an exact schema, not a string concatenation. V1 fields:

```text
1  provider_generation_id          UTF8
2  provider_id                     UTF8
3  provider_generation             U64
4  provider_verification_key_id    UTF8
5  authenticated_transition_digest DIGEST32
```

For bootstrap head, where no predecessor transition exists, `authenticated_transition_digest` is the protocol-defined bootstrap-chain-root digest; zero bytes are not an implicit sentinel.

## Schema: LAB-092 migration certificate

Domain: `ytim.lab092.migration-certificate.v1`

Required fields:

```text
1   logical_database_identity_digest          DIGEST32
2   bootstrap_root_digest                     DIGEST32
3   provider_history_descriptor_digest        DIGEST32
4   old_construction_provenance_digest        DIGEST32
5   old_activation_authority_descriptor_digest DIGEST32
6   new_activation_authority_descriptor_digest DIGEST32
7   migration_schema_id                       UTF8
8   migration_schema_version                  U64
9   activation_table_definition_digest        DIGEST32
10  activation_trigger_definition_digest      DIGEST32
11  provider_generation_head_digest           DIGEST32
12  migration_epoch                           U64
13  migration_nonce                           BYTES
```

`migration_nonce` MUST be exactly 32 bytes. Pure schema migration requires fields 5 and 6 to be byte-equal. A migration plus authority upgrade still produces two independent domain-separated transition records linked by digests; this certificate cannot authorize the upgrade by itself.

## SQLite boundary rules

SQLite is storage, never the canonical type system.

Before hashing/verifying a row:

1. read columns without `CAST()` that would normalize attacker-controlled representations;
2. verify storage class and application type match the schema expectation;
3. reject `INTEGER` values outside U64 range;
4. reject REAL numeric equivalents (`1.0`), numeric TEXT (`"1"`), booleans received through application APIs, BLOB/text swaps, and NULL for all required V1 fields;
5. only then construct canonical bytes.

The implementation should add explicit SQLite `typeof(column)` assertions/queries in security-sensitive provenance verification where schema affinity alone can hide representation differences.

## Parser/encoder invariants

One reference encoder/decoder module must own V1 framing. Individual LAB modules supply only schema constants and typed values. They must not duplicate TLV assembly.

Required implementation properties:

- `encode_record(domain, schema, values) -> bytes` performs all type/range/field-set checks;
- `digest_record(...) -> bytes` is the only SHA-256 entrypoint for these provenance objects;
- decoder verifies exact domain before returning any field values;
- no API returns partially decoded authority values after a framing/type/domain failure;
- compare fixed digests with `hmac.compare_digest` where an attacker can influence either operand, even though the digests themselves are not secrets;
- presentation helpers (hex/JSON/debug) operate only after canonical bytes/digests exist and never feed verification.

## Cross-contract anti-confusion invariants

1. Identical field values under two domains produce different digests.
2. Reordering fields is invalid, not an alternate encoding.
3. U64 `1`, text `"1"`, REAL `1.0`, boolean `True`, and bytes `b"1"` cannot converge to one digest.
4. Missing field and explicit zero/empty value are distinct; missing required field is invalid.
5. Unknown extra field is invalid in V1 rather than ignored.
6. Hex text of a DIGEST32 cannot be confused with its raw 32 bytes.
7. A LAB-099 ticket digest cannot be reused as a provider-head, migration, initialization, descriptor, or transition digest.
8. Authority descriptor version change necessarily changes its digest.
9. Migration certificate changes if exact DDL definition digest, provider-generation head, construction provenance, or authority descriptor changes.
10. Initialization certificate changes if logical DB identity, bootstrap, initial chain root, authority descriptor, epoch, or nonce changes.

## RED-first serialization matrix

Freeze these tests before provenance production refactors:

### Framing/type tests

1. reference vector for each V1 domain has exact expected hex bytes and SHA-256 digest;
2. field reorder -> decode/verify fail;
3. duplicate field -> fail;
4. unknown field -> fail;
5. missing field -> fail;
6. trailing bytes -> fail;
7. truncated length/value -> fail;
8. wrong domain with identical fields -> fail;
9. invalid UTF-8 -> fail;
10. surrogate/non-encodable string -> fail;
11. `True` where U64 required -> fail;
12. `1.0` where U64 required -> fail;
13. `"1"` where U64 required -> fail;
14. negative integer -> fail;
15. integer > 2**64-1 -> fail;
16. DIGEST32 length 31/33 -> fail;
17. nonce length != 32 -> fail.

### SQLite coercion tests

18. activation expected_position stored as INTEGER 1 -> canonical PASS;
19. same logical numeric value stored as REAL 1.0 -> fail before digest;
20. numeric TEXT `"1"` -> fail;
21. BLOB/text swap for identifiers -> fail;
22. NULL required ticket field -> fail;
23. coerced/recomputed activation row that is structurally valid but canonical ticket differs -> LAB-099 fail.

### Cross-contract tests

24. same payload fields under LAB-092 vs LAB-097 domains -> different digest;
25. migration certificate copied across logical DB identity -> fail;
26. migration certificate copied across provider-generation head -> fail;
27. initialization certificate copied across activation-authority descriptor -> fail;
28. authority transition with swapped old/new descriptor digests -> fail;
29. activation ticket replayed against another `new_generation_id` -> fail;
30. schema-definition digest changes on one-byte canonical DDL change;
31. SQLite-normalized formatting difference never becomes the certificate's canonical source of truth;
32. old JSON/string-concatenation digest is rejected on V1 provenance rather than silently upgraded.

## Implementation order when exact execution returns

1. Add the standalone canonical encoder/decoder tests and freeze reference vectors first.
2. Observe RED for SQLite numeric/type confusion against current LAB-090/LAB-099 row handling.
3. Implement one shared standard-library-only provenance encoding module.
4. Convert LAB-100 descriptor digest construction first because LAB-097 and LAB-092 consume it.
5. Convert LAB-099 activation-ticket digest and authenticated transition binding.
6. Convert LAB-097 initialization certificate.
7. Convert LAB-092 migration certificate and schema-definition digest.
8. Execute the already frozen LAB-090/LAB-092/LAB-097..100 matrices plus LAB-087/LAB-093 confinement, LAB-080/081 compatibility, compileall, and a separate security audit.

Do not write partial production provenance code that mixes V1 canonical digests with legacy JSON/text digests under the same protocol version.

## Verdict

`PROVENANCE_CANONICAL_BYTE_ENCODING_V1_FROZEN`

The LAB-092, LAB-097, LAB-099, and LAB-100 designs now share one unambiguous byte-level framing, primitive type contract, hash rule, and domain-separation family. Exact implementation remains intentionally RED-first once executable repository source is available.