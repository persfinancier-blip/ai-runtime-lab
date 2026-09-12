# LAB-099 exact precursor DDL derivability audit

Date: 2026-09-12
Issue: #184
Related staging PR: #186
Pinned implementation reference: PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`

## Decision

`LAB099_EXACT_PRECURSOR_DDL_NOT_DERIVABLE_FROM_FROZEN_CONTRACTS_V1`

The already-frozen LAB-099 semantic contracts do **not** determine one byte-exact SQLite DDL identity for the provider-activation reservation precursor relation. No literal precursor DDL may be invented merely to unblock the RED-intent fixture adapter.

Until an exact physical schema identity is independently frozen, `lab099_precursor_fixture_adapter` must remain fail-closed with no DDL/mutation plan, and the reference-vector relation-definition digest remains a synthetic DIGEST32 test value rather than production schema evidence.

## Source evidence

At pinned PR #177, LAB-090 defines `_ACTIVATION_TABLE_SQL` as a literal `CREATE TABLE provider_generation_activations(...)` string and `_ACTIVATION_TRIGGER_SQL` as a literal trigger string. `_init_activation_schema()` creates those objects and then reads `sqlite_master.sql`; it compares `_normalized_sql(sql)` against the normalized literal constants and fails with `HistoricalVerificationError` on mismatch.

Therefore the exact physical spelling selected by the implementation is already security/correctness-visible. Whitespace is normalized, but the following are not semantics-free once frozen into the literal SQL identity:

- relation and trigger names;
- column names and column order;
- SQLite declared types (`TEXT`, `INTEGER`, `BLOB`, etc.);
- whether authority material is stored as canonical-body blobs, decomposed columns, or both;
- `PRIMARY KEY`, `UNIQUE`, `NOT NULL`, and `CHECK` placement/spelling;
- whether sibling-reservation exclusion is a table constraint or separately named unique index;
- whether authenticators are stored in the precursor row or a separate relation;
- foreign-key choices;
- rowid / `WITHOUT ROWID` choice;
- any trigger/index objects included in the physical schema identity.

The frozen LAB-099 relation contract requires the *semantics*—pre-transition existence, uniqueness by `activation_id`, uniqueness by logical-DB/provenance-parent/epoch, dual authority binding, explicit authenticated cutover, no ordinary-startup auto-DDL, and fail-closed handling of missing/mismatched schema—but it did not freeze those physical choices.

## Why existing LAB-092 / LAB-090 machinery does not resolve the ambiguity

The existing LAB-092 V1 migration fact is scoped to the original provider-generation activation schema and cannot be reinterpreted as precursor authority. Separately, the LAB-090 implementation demonstrates a verifier mechanism for an already-chosen physical schema (`sqlite_master.sql` compared with literal SQL); it does not supply a canonical algorithm that maps a semantic relation contract to one unique SQL definition.

Thus reusing `_normalized_sql()` would only verify whichever precursor DDL was first chosen. It cannot prove that the choice itself follows from previously frozen contracts.

## Security consequence

Choosing any one of the multiple valid physical layouts now would create new authority-bearing protocol bytes while presenting them as if they were implied by prior decisions. That would weaken auditability and would also make the PREPARED cutover's `relation_definition_digest` depend on an undocumented implementation choice.

The safe state is therefore:

1. keep PR #186 test-only;
2. do not connect precursor DDL mutation plans;
3. do not add production LAB-099 behavior;
4. continue treating unknown/absent precursor schema identity as unauthorized/fail-closed;
5. make any future exact DDL freeze an explicit, separately reviewable protocol decision with byte-exact schema identity and RED coverage before implementation.

## What remains derivable without choosing DDL

The following verifier boundary *is* already derivable and can be tested independently of the final physical layout:

- LAB-092 V1 marker alone never authorizes precursor mutations;
- a precursor cutover PREPARED record must bind one exact relation-definition digest;
- CONFIRMED must bind the exact PREPARED digest;
- a different/missing physical-schema digest after PREPARED/CONFIRMED is fail-closed;
- stale/forked parent+epoch cannot acquire mutation authority;
- post-CONFIRMED absence cannot downgrade to legacy LAB-090 semantics.

This is the next safe RED-owned surface while the literal DDL remains implementation-gated.
