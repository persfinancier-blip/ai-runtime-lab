# LAB-091 restrictive UNIQUE adoption gap

Date: 2026-08-30

## Context

LAB-091 intentionally permits first adoption of some legacy SQLite table layouts when the effective durable/write semantics remain compatible with the canonical LAB-080/LAB-082 schema. Earlier hardening required canonical BINARY identity indexes and changed final supported identity lookups to explicit `COLLATE BINARY`.

That was not sufficient to prove write compatibility.

## Reproduced reachable failure

A legacy `shared_anchor_intents` table can declare:

```sql
intent_id TEXT COLLATE NOCASE PRIMARY KEY
```

and also carry a separate full-table BINARY unique index:

```sql
CREATE UNIQUE INDEX intent_id_binary_overlay
ON shared_anchor_intents(intent_id COLLATE BINARY);
```

The previous LAB-091 identity validator accepts the BINARY overlay as proof of canonical byte-distinct identity. Final supported lookup logic also correctly uses BINARY comparison, so an existing `Alpha` does not alias a requested `alpha` during lookup.

However, the old NOCASE primary-key constraint still participates in INSERT conflict handling. A normal supported-shape insert of `alpha` after `Alpha` therefore fails with SQLite `UNIQUE constraint failed`, even though byte-exact LAB-091 identity semantics require those IDs to remain distinct.

This is a reachable compatibility failure through the supported writer after a successful adoption, not merely a raw-SQL bypass.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now extends schema-domain adoption validation with a UNIQUE write-contract gate.

For LAB-091-owned mutable tables, every persisted UNIQUE index must:

- be a full-table index, not partial;
- contain only real columns, not expression terms;
- correspond to one of the canonical unique keys for that table;
- use BINARY collation for indexed terms.

This rejects the NOCASE-primary-key/BINARY-overlay construction and also rejects extra UNIQUE constraints that could make a future supported write fail even when all canonical identity indexes are present.

Published commits:

- `bbe3b62858366f1c40bc7364b78596ee15ac2a56` — validator hardening (`adoption_schema_domains.py` blob `db16ee7783e259b7d9f2764f9fae593b8e69c1f7`);
- `2297ad975b6e4ea03a90efa531a477119fdc301e` — regression `test_adoption_restrictive_unique_regression.py`.

## Executed evidence in this run

A local SQLite mechanism probe executed the same PRAGMA/index-contract logic against three schemas:

- canonical unique contract: accepted;
- NOCASE `intent_id` primary key + BINARY overlay: rejected as non-BINARY unique identity;
- canonical schema + extra unique `payload_digest`: rejected as an extra restrictive unique key.

The same probe inserted `Alpha`, then attempted the otherwise supported-shape case-distinct `alpha`; SQLite rejected the second insert because the retained NOCASE primary key remained authoritative for conflict detection.

This is mechanism evidence only. Exact byte-for-byte branch pytest execution was **not** performed because executable GitHub transport was re-probed in this run and `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed with `Could not resolve host: github.com`.

## Audit notes

A separate static pass examined remaining default-collation comparisons in LAB-091 v2/v4 triggers. Case-only identity mutations can make SQLite `IS NOT` / `!=` inherit NOCASE under a legacy column declaration, but no supported writer path was found that mutates those identity columns: supported confirmation and watermark-update SQL change only status/binding or position, and adoption rejects unknown persisted triggers. No speculative trigger patch was made without a reachable supported failure.

LAB-086 remains higher priority and unchanged. Its retained 949-line security-critical patch still lacks a supported byte-preserving composition bridge in this runtime; manual/model reserialization remains prohibited by the durable handoff.
