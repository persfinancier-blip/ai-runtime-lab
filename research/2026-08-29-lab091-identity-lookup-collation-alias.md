# LAB-091 identity lookup collation alias

Date: 2026-08-29

## Scope

Fallback audit while LAB-086 exact hidden-rowid publication remains blocked by the lack of a supported byte-preserving composition/transfer path.

Target: protected LAB-091 identity lookups under legacy SQLite schemas that pass the current identity-index adoption check.

## Finding

`adoption_validation._unique_key_sets()` correctly requires canonical BINARY comparison semantics on the UNIQUE index used to establish an identity key. However, this does not prove that the *column's default collation* is BINARY.

A legacy table can declare, for example:

```sql
intent_id TEXT COLLATE NOCASE NOT NULL
```

and separately provide:

```sql
CREATE UNIQUE INDEX legacy_intent_id_binary
ON shared_anchor_intents(intent_id COLLATE BINARY);
```

The current LAB-091 identity check accepts `("intent_id",)` because the identity index is BINARY. The supported writer nevertheless contains ordinary predicates such as:

```sql
WHERE intent_id=?
```

Those predicates inherit the legacy column collation and therefore alias byte-distinct identities such as `Alpha` and `alpha`.

This matters because `Intent.validate()` only requires a non-empty string; intent identity is otherwise byte-sensitive. A supported `reserve(Intent("alpha", ...))` can therefore observe the existing `Alpha` row as if it were the same identity. Depending on the payload, this becomes either a false idempotent hit or a false `IntentConflict`, rather than a distinct identity.

The same audit class applies to other protected lookup keys (`request_id`, `component_id`) until all supported predicates are proven byte-explicit or adoption proves canonical column comparison semantics.

## Reproduction actually executed

A local sqlite3 semantic harness was executed with:

- `intent_id TEXT COLLATE NOCASE`;
- a separate `UNIQUE(intent_id COLLATE BINARY)` index;
- one persisted row with identity `Alpha`.

Observed:

1. the current `_unique_key_sets()` algorithm recognizes `("intent_id",)` as a BINARY identity key;
2. `SELECT ... WHERE intent_id=?` with parameter `alpha` returns the `Alpha` row;
3. `SELECT ... WHERE intent_id COLLATE BINARY=?` with `alpha` returns no row.

Result: reproduced.

This was a focused semantic reproduction using the same `_unique_key_sets()` algorithm copied from the published branch source; it is not represented as byte-for-byte branch pytest execution.

## Durable regression artifact

Added on `lab/091-mutable-shared-anchor-writer`:

- `experiments/mutable_shared_anchor_writer/tests/test_identity_lookup_collation_reproduction.py`
- commit `1eb30e021667990352c431112da04185148f7931`

The test records the exact SQLite mechanism and the mismatch between BINARY identity-index acceptance and ordinary inherited lookup collation.

## Decision

Do not add a speculative schema parser. The safest correction is to inventory identity-sensitive SQL on the final supported surface and make byte identity explicit with `COLLATE BINARY` at lookup/CAS predicates where identity comparison is intended. Then add full regressions for case-distinct `intent_id`, `request_id`, and `component_id` legacy schemas and rerun adoption/alternate-write/convergence gates.

The bug is a real supported-path compatibility/correctness defect, not a same-privilege DDL bypass: the legacy schema is accepted by current LAB-091 adoption checks, after which supported methods can alias distinct identifiers.
