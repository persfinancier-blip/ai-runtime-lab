# LAB-091 schema-expression reentrancy audit

Date: 2026-08-29

## Question

Can a preexisting durable SQLite schema expression on a LAB-091 protected table execute inside an otherwise authorized statement and obtain/use the connection-local one-shot permit before the LAB-091 `BEFORE` guard consumes it?

This follows the persisted-trigger confused-deputy finding, but tests a different SQLite execution surface: table `CHECK`, generated-column/index expressions, and column defaults.

## Exact branch sources inspected

Branch: `lab/091-mutable-shared-anchor-writer`

- `operation_permit.py` blob `637784a5cb61a024a1df3e0e983887b6d0a838be` registers `lab091_consume_permit` as a normal (non-deterministic) SQLite UDF. The only side effect is clearing the current exact Python-side permit after a matching call.
- `full_operation_guards.py` blob `529ee8094d04b0cc9bb208f3fce8f85b2bc6db0f` consumes the exact permit from LAB-091 `BEFORE INSERT/UPDATE` triggers.
- `state_machine_udfs.py` blob `8c1d6d0cd075285aed3a90ac337b60b60c1d608b` additionally registers only the pure deterministic-request-ID computation UDF.
- `adoption_validation.py` blob `1731648b4e65b1c5984d4f93b78c45d5a066dd95` validates identity/index semantics and existing rows but does not claim an exact canonical `CREATE TABLE` SQL text.

## Executed SQLite mechanism probes

Executed locally with Python `sqlite3` against the runtime SQLite engine.

### CHECK ordering

A table `CHECK(f(x))` and a `BEFORE INSERT` trigger calling `g(x)` produced call order:

`BEFORE trigger -> CHECK expression`

Therefore an extra durable `CHECK` expression cannot call `lab091_consume_permit` before the LAB-091 `BEFORE` trigger. By the time `CHECK` executes, a successful guard has already consumed the one-shot permit. No authority bypass was established.

### Generated columns and expression indexes

A non-deterministic application UDF was rejected from both surfaces:

- generated column: `OperationalError: non-deterministic functions prohibited in generated columns`
- expression index: `OperationalError: non-deterministic functions prohibited in index expressions`

`lab091_consume_permit` is registered without `deterministic=True`, so these durable expression surfaces cannot directly embed that permit-consuming UDF under the observed SQLite semantics.

### Column DEFAULT ordering

SQLite accepted a parenthesized application-UDF default expression. For an omitted column, observed order was:

`DEFAULT expression -> BEFORE trigger`

Thus a legacy table with an extra omitted column can execute a schema default before the LAB-091 guard. If that default names `lab091_consume_permit` with the exact currently-issued tuple, it can consume the permit early and make the subsequent LAB-091 guard abort.

This is a fail-closed availability/compatibility effect, not a demonstrated write-authority bypass:

- SQL has no UDF that can grant/set a permit;
- `lab091_consume_permit` only clears an already-issued exact permit;
- the only other LAB-091 UDF inspected here is pure request-ID computation;
- after early consumption, the protected `BEFORE` guard sees no permit and aborts the statement.

## Decision

Do **not** add a speculative schema-expression guard in this run.

The current evidence narrows the surface:

1. `CHECK` does not preempt the LAB-091 `BEFORE` permit guard.
2. generated columns/expression indexes cannot embed the non-deterministic permit UDF.
3. extra column defaults can preempt the guard but currently yield denial/fail-closed behavior only; no unauthorized mutation path was reproduced.

This matches the current repository rule: add schema hardening only for a demonstrated reachable mutation/conformance defect under the actual supported connection semantics.

## Follow-up

If a future supported writer omits a column whose default can invoke a side-effecting registered UDF, or if LAB-091 gains any SQL UDF capable of granting/mutating authority/state rather than only consuming/checking it, revisit exact schema-expression validation immediately.
