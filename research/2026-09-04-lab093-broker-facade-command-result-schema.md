# LAB-093 — broker façade command/result schema and authorization boundary

Date: 2026-09-04

## Scope

This note freezes the first regression target for the LAB-093 least-capability façade selected in `2026-09-04-lab093-supported-delegation-surface-and-broker-reuse.md`.

It is deliberately **not production code** and claims no RED/GREEN execution. Direct `git clone --no-checkout` was re-probed in this run and failed before repository access with `Could not resolve host: github.com`.

The source contracts inspected here are:

- `experiments/shared_anchor_intent_ledger/protocol.py` — current `Intent`, `LedgerEntry`, `SharedAnchorLedger.reserve`, `entry`, `execute`, `verify_component`;
- `experiments/shared_anchor_intent_ledger/supported.py` — `SupportedSharedAnchorLedger.verify_durable`;
- `experiments/sqlite_schema_control/protocol.py` — LAB-087's explicit broker-owned writable handle / restricted-worker contract;
- `experiments/sqlite_schema_control/process_boundary.py` — LAB-087's Unix UID/GID/filesystem boundary.

## Source-driven correction to the previous candidate surface

The actual LAB-080 API makes one important distinction explicit:

- `entry(intent_id)` is a read projection;
- `verify_durable()` verifies durable state at restart and returns `True` on success;
- `verify_component(component_id)` is **not merely a read**. It performs authenticated external reads/reconciliation and may advance `component_anchor_watermarks` in SQLite after exact-row revalidation.

Therefore `verify_component` must **not** be smuggled into the first narrow façade under a generic `VERIFY` name. It is a consequential broker operation and needs a separately justified capability if it is ever delegated.

The first façade remains exactly:

`RESERVE | EXECUTE | ENTRY | VERIFY_DURABLE`

## Protocol identity

Protocol version: `LAB093_LEDGER_BROKER_V1`.

There is no generic method-call command, no method-name string, no `getattr`, no raw SQL command and no provider/admin escape hatch.

The wire objects are value-only. An implementation may use JSON, a typed pipe/message transport or another deterministic serialization, but the worker-facing schema must be equivalent to the closed forms below.

## Broker-issued authorization context

Authorization is **not supplied by the command body**. The broker obtains it from the authenticated process/channel that owns the endpoint.

A delegated endpoint is bound when created to an immutable authorization context:

```text
principal_id           non-empty broker-authenticated identity
component_id           one exact component identity
allowed_operations     subset of {RESERVE, EXECUTE, ENTRY, VERIFY_DURABLE}
allowed_intent_types    subset of canonical ALLOWED_INTENT_TYPES
```

For V1 there is no wildcard component and no caller-selected principal. A worker cannot widen its authority by placing another `principal_id`, `component_id`, operation or intent type in a message.

The broker must reject before touching SQLite/provider state when:

1. operation is outside the endpoint's `allowed_operations`;
2. an intent's `component_id` differs from the bound component;
3. an intent type is outside both the broker grant and canonical `ALLOWED_INTENT_TYPES`;
4. an `ENTRY` resolves to an entry owned by another component;
5. the message has unknown fields, wrong types, missing required fields or a non-canonical digest.

The authorization context itself is broker memory/configuration, not returned to the worker as a mutable policy object.

## Command envelope

Every request has only:

```text
version      = "LAB093_LEDGER_BROKER_V1"
command_id   non-empty opaque transport/audit id
operation    closed enum
body         exact operation body
```

`command_id` is transport/audit correlation only. It never substitutes for the ledger's canonical request identity, which remains derived by `SharedAnchorLedger._request_id(position, intent...)`.

### RESERVE

```text
operation = RESERVE
body = {
  intent_id:       non-empty string,
  component_id:    exact bound component,
  intent_type:     canonical allowed type,
  payload:         object/dict,
  payload_digest:  64-char lowercase hex
}
```

The broker reconstructs canonical `Intent(intent_id, component_id, intent_type, payload)`, validates it, recomputes `Intent.payload_digest`, and requires exact equality with `payload_digest` before calling `ledger.reserve(intent)`.

The duplicate digest on the wire is intentional: the worker can bind what it meant to send, while the broker remains the authority on canonical digest construction. No caller-provided provider id, generation, position, predecessor, request id, status or receipt is accepted.

### EXECUTE

Same intent body as `RESERVE`, plus:

```text
timeout_after_commit: bool = false
```

No other execution/provider option exists in V1. The broker calls only the supported `ledger.execute(intent, timeout_after_commit=...)` surface.

A retry with the same semantic `Intent` relies on the ledger's existing intent/request idempotency. The broker transport must not synthesize a new ledger request id from `command_id`.

### ENTRY

```text
operation = ENTRY
body = {
  intent_id: non-empty string
}
```

The broker calls `ledger.entry(intent_id)` and returns the result only if `entry.component_id` equals the endpoint-bound component. Cross-component lookup is refused even though the underlying ledger object can physically read it.

### VERIFY_DURABLE

```text
operation = VERIFY_DURABLE
body = {}
```

The broker calls only `SupportedSharedAnchorLedger.verify_durable()` (or an exact descendant that preserves the accepted supported contract). V1 does not map this name to `verify_component`.

## Success result envelope

```text
version      = "LAB093_LEDGER_BROKER_V1"
command_id   exact echoed correlation id
operation    exact operation
ok           = true
result       closed result body
```

### LedgerEntryDTO

`RESERVE`, `EXECUTE` and `ENTRY` return a value-only DTO containing exactly the canonical frozen `LedgerEntry` fields:

```text
intent_id
component_id
intent_type
payload_digest
provider_id
provider_generation
predecessor_position
position
request_id
status
receipt_binding
```

These are values, not a live `LedgerEntry` object with attached strategies, and certainly not a ledger/provider reference.

`VERIFY_DURABLE` returns only:

```text
{ verified: true }
```

It does not return a connection, path, verifier, keyring, provider status object or internal row collection.

## Error result envelope

The worker receives stable categories, not raw internal exception objects:

```text
version      = "LAB093_LEDGER_BROKER_V1"
command_id   correlation id when parseable
operation    operation when parseable
ok           = false
error = {
  category: closed enum,
  message: bounded non-secret diagnostic
}
```

V1 categories map the current canonical failures without exposing object graphs:

- `INVALID_REQUEST`
- `UNAUTHORIZED_OPERATION`
- `INTENT_CONFLICT`
- `INTENT_GAP`
- `INTENT_SUBSTITUTION`
- `PENDING_INTENT`
- `PROVIDER_MISMATCH`
- `UNEXPLAINED_ADVANCE`
- `INTERNAL_FAILURE`

Raw exception objects, tracebacks, filesystem paths, SQL text/rows, provider observations, activation tickets, verifier/key objects and writable handles are never serialized to the worker.

## Explicitly broker-only in V1

The worker endpoint has no message capable of naming or recovering:

- the live ledger Python object;
- `AttestedCatchup`;
- `attested.provider` or provider `increment` / `reconcile_increment` primitives;
- provider identity -> provider-object lookup;
- LAB-090 `prepare_activation`, `commit_activation`, `release_activation`, `abort_activation`, `activation_status`;
- `verify_component` / component watermark advancement;
- provider generation rotation/history mutation helpers;
- verifier/keyring/signing objects;
- writable SQLite connection;
- SQLite path or protected parent-directory path;
- raw SQL;
- arbitrary callable/method names;
- bootstrap/history/activation strategy objects.

Provider rotation remains a distinct future administrator capability. It cannot be added to this façade by extending `operation` with a generic `CALL`.

## Broker dispatch invariant

Conceptually the dispatcher is a closed switch:

```text
validate envelope
resolve immutable channel authorization
authorize exact operation + component + intent type
reconstruct and validate canonical values
switch operation:
    RESERVE        -> ledger.reserve(intent)
    EXECUTE        -> ledger.execute(intent, timeout_after_commit=flag)
    ENTRY          -> ledger.entry(intent_id) + component ownership check
    VERIFY_DURABLE -> ledger.verify_durable()
serialize value-only DTO/result
```

There is no reflection fallback. An unknown operation is a refusal, never a dynamic attribute lookup.

## Regression-first matrix before production implementation

When exact execution is available, implementation must begin with RED tests for at least these cases:

1. permitted `RESERVE` succeeds through broker and returns only `LedgerEntryDTO` values;
2. permitted `EXECUTE` succeeds and preserves the ledger-derived request id/idempotency semantics;
3. same semantic retry does not create a second ledger position/provider increment;
4. `ENTRY` for the bound component succeeds;
5. cross-component `ENTRY` is refused even if the row exists;
6. intent whose `component_id` differs from the endpoint binding is refused before DB/provider mutation;
7. disallowed intent type is refused before DB/provider mutation;
8. disallowed operation is refused before DB/provider mutation;
9. unknown operation cannot reach `getattr`/reflection;
10. unknown/extra fields and wrong types fail closed;
11. supplied `payload_digest` mismatch is refused before reserve/execute;
12. `VERIFY_DURABLE` succeeds without exposing durable rows/connection/path;
13. `verify_component`, rotation and activation operation names are absent/refused;
14. response/error object graph contains no live ledger, attested/provider, activation/history helper, verifier/keyring, SQLite connection or filesystem path object;
15. worker process cannot independently open the protected database writable under the retained LAB-087 Unix identity/permissions proof;
16. worker cannot invoke provider mutation directly because no provider capability crosses the channel;
17. worker restart reconstructs only the endpoint/channel, never provider/ledger authority;
18. broker restart re-runs the accepted durable verification before serving delegated commands;
19. existing LAB-080/081 behavior remains green;
20. LAB-090/LAB-100 activation/provider-authority regressions remain green once that line is executable/current.

A negative control must explicitly demonstrate that handing the same worker a live ledger object in-process fails the LAB-093 property by making the retained capability graph reachable. That control documents why Python name privacy is not the security boundary.

## Composition rule

LAB-093 V1 owns only *delegation*. It does not redefine:

- LAB-080 ledger semantics;
- LAB-087 filesystem/process confinement;
- LAB-090 activation fencing;
- LAB-092 provenance;
- LAB-094/095/096 retained authority objects;
- LAB-100 provider implementation authority.

The broker may own all of those capabilities, but the delegated endpoint receives only the closed V1 command surface above.

## Decision

`LAB093_BROKER_FACADE_V1_SCHEMA_FROZEN`.

This is the exact RED-test target for the first LAB-093 implementation slice. No production code should be written until exact-source execution is available and this matrix can first fail for the expected capability-exposure reasons.