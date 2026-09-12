# LAB-091 status collation reachability audit

Date: 2026-08-29
Branch: `lab/091-mutable-shared-anchor-writer`
Issue: #170
PR: #173

## Question

After closing the demonstrated receipt-collation exactness gap, determine whether declaring `shared_anchor_intents.status TEXT COLLATE NOCASE` creates a second supported-path bypass in the v2/v3/v4 PREPARED/CONFIRMED guards.

## Result

No additional reachable bypass was demonstrated on the final supported writer, so no speculative guard patch was added.

## Reachability analysis

The raw SQL predicates in `full_operation_guards.py` contain comparisons such as `NEW.status!='PREPARED'`, `OLD.status!='PREPARED'`, and `NEW.status!='CONFIRMED'`. A NOCASE declaration can change those comparison results in isolation. That observation alone is not enough to establish a supported-path bypass.

The final writer constrains the write path in several independent ways:

1. `reserve()` validates the incoming `Intent` and constructs the durable row itself with literal status `PREPARED`; callers do not supply the status field.
2. The intent-insert one-shot permit is bound to `intent_row_token(*row)` for that canonical row, and the SQL statement itself hard-codes `'PREPARED'`.
3. Confirmation constructs the permit's new row token with literal status `CONFIRMED`, and the SQL statement itself hard-codes `SET status='CONFIRMED'`.
4. A preexisting non-canonical durable row is checked during final first-adoption/restart by `validate_existing_mutable_state_locked()` while the writer reservation is held.
5. Unknown persisted triggers on protected tables are rejected by `validate_protected_trigger_surface()`, closing the previously demonstrated confused-deputy path for injecting alternate writes inside an authorized statement.
6. The one-shot permit value comparison is a Python tuple equality check, not a SQLite collation-sensitive SQL comparison.

Therefore a NOCASE status declaration can make an individual trigger predicate less byte-exact, but the supported final writer does not provide a demonstrated way to cause lowercase/mixed-case status bytes to be written while satisfying the exact permit and adoption surfaces.

## Evidence boundary

This is a reachability/audit result, not a proof that arbitrary same-process SQL is sandboxed. LAB-091 continues to rely on LAB-087 for the writable process/filesystem boundary. Direct same-privilege code that can deliberately mint internal one-shot permits is outside the standalone LAB-091 claim.

## Decision

Do not add broad `COLLATE BINARY` churn to every status predicate without a demonstrated supported-path exploit. Retain the targeted receipt fix, where durable receipt-column collations directly widened cross-table matching of otherwise authorized operations.

## Next fallback audit

If LAB-086 publication and final-stack execution remain unavailable, audit other durable SQLite schema properties only when they can influence values the supported writer does not itself canonicalize, especially provider-history lookup/matching and schema features that execute implicitly inside authorized statements.
