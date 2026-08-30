# LAB-091 table-options / schema-expression negative audit

Date: 2026-08-30

## Objective

Continue the first-adoption compatibility audit only where a persisted SQLite schema feature can be shown to break a canonical supported LAB-091 write or weaken an established security invariant. The current handoff explicitly forbids speculative guards without a reachable reproduction.

## Runtime/tool observation

The preferred LAB-086 path was probed first in this run. Local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` still fails with `Could not resolve host: github.com`, while the GitHub connector remains readable/writable. No byte-preserving bridge appeared that can compose the exact 949-line LAB-086 predecessor with the retained hidden-rowid patch and transfer the exact result into a Contents API write without model/manual whole-file reserialization. No LAB-086 branch mutation was attempted.

## Candidate persisted schema surfaces inspected

The current LAB-091 adoption stack was re-read at exact PR #173 head `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5`, especially:

- `restart_safe_schema.py` canonical mutable-table definitions;
- `adoption_schema_domains.py` affinity / NOT NULL / UNIQUE / CHECK validation;
- `adoption_extra_columns.py` extra required/generated/function-default rejection;
- `adoption_foreign_keys.py` inherited FK rejection;
- `adoption_column_collations.py` unavailable canonical-column collation rejection;
- `adoption_secondary_indexes.py` persisted secondary-index checks;
- `adoption_trigger_surface.py` exact trigger-surface enforcement;
- `adoption_validation.py` retroactive state-machine validation;
- v2/v3/v4 guards in `full_operation_guards.py`, `cross_table_guards.py`, and `history_binding_guards.py`.

The next unclassified table-level/schema-expression candidates were then probed locally with the canonical LAB-080 write shape:

1. canonical tables;
2. `STRICT` tables;
3. `WITHOUT ROWID` tables;
4. built-in `NOCASE` on the `status` column;
5. `PRIMARY KEY ON CONFLICT REPLACE` on `intent_id`.

Each probe executed a canonical singleton insert, canonical PREPARED intent insert, tail advance, and exact PREPARED -> CONFIRMED update. All five variants completed successfully and retained the expected final row `('CONFIRMED', 'b')`.

Observed matrix:

- canonical: PASS;
- STRICT: PASS;
- WITHOUT ROWID: PASS;
- status `COLLATE NOCASE`: PASS for canonical supported values;
- primary-key `ON CONFLICT REPLACE`: PASS for conflict-free canonical supported values.

## Audit conclusion

No new reachable supported-write failure was reproduced on these surfaces, so **no new LAB-091 guard or schema rejection was added**.

This is intentional:

- `STRICT` does not reject the canonical value classes used by the currently inspected LAB-080/LAB-082 path (text values are strings, generation/position fields are integers, nullable receipt binding remains nullable).
- `WITHOUT ROWID` does not break the observed canonical PK-based insert/update shapes.
- built-in `NOCASE` can broaden comparison semantics, but the existing-state validator rejects non-canonical status strings and the supported writer/permit path uses exact canonical status values; this run did not establish a reachable supported failure or permit bypass from that table option alone.
- a conflict algorithm such as `ON CONFLICT REPLACE` does not affect conflict-free supported writes; identity/position collision attack surfaces are already independently rejected by LAB-091 BINARY existence guards before the permit is consumed. No new counterexample was established here.

Therefore the anti-speculation rule remains the correct boundary: retain these as audited non-findings rather than hardening every non-canonical SQLite table option by policy.

## Exact next search surface

If LAB-086 exact publication remains tool-blocked and whole-branch PR #173 execution is still unavailable, continue only with persisted schema features whose expressions are implicitly evaluated during a canonical write and can be concretely reproduced as either:

1. a canonical supported write failing after successful adoption, or
2. an exact LAB-091 state-machine/security invariant being bypassed despite the one-shot permit and existing v2/v3/v4 guards.

Do not add a blanket `STRICT`/`WITHOUT ROWID`/built-in-collation/conflict-clause rejection based on this audit.