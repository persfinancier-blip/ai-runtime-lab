# LAB-093 — supported delegation surface and LAB-087 broker reuse

Date: 2026-09-04

## Question

After proving that a component delegated only a supported ledger can recover the raw external mutation capability through `ledger.attested`, what is the smallest coherent authority boundary that prevents that recovery without pretending Python attribute privacy is a sandbox?

## Sources inspected

- `AGENTS.md` and `state/CURRENT.md`.
- LAB-093 / issue #178.
- LAB-087 / issue #166 and merged implementation:
  - `experiments/sqlite_schema_control/protocol.py` blob `5c999166c2155baa5ce3f644c36efe0e01e4e3fe`;
  - `experiments/sqlite_schema_control/process_boundary.py` blob `87456dfcbeac0c0e795fc0bcdeb3502cf57fcdd0`.
- Current provider-history integration:
  - `experiments/provider_generation_history/integration.py` blob `a6937db161f33a41a04829661dd301c52b250015`.
- Supported LAB-080 surface:
  - `experiments/shared_anchor_intent_ledger/supported.py` blob `22a05c04831f65c1d7fe9077df3bb780c4008e09`.
- Draft LAB-090 PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`.

Direct `git clone --no-checkout` was re-probed in this run and failed before repository access with `Could not resolve host: github.com`; no exact behavioral execution is claimed here.

## Finding 1 — LAB-087 is the correct trust-boundary owner, but its current API is DB-specific

LAB-087 already defines the security model needed for a real least-capability claim:

1. the broker process retains the only writable SQLite handle;
2. workers receive only a narrowed read-only `RestrictedConnection`;
3. filesystem ownership/modes prevent a distinct worker identity from reopening or replacing the database writable;
4. same-process Python introspection is explicitly outside the boundary.

This is exactly the architectural reason a rename such as `attested -> _attested` is insufficient for LAB-093. If the consumer is in the same Python trust domain as the ledger object, the reachable object graph is not a security boundary.

However, LAB-087's concrete façade today is only `RestrictedConnection`. It does not broker shared-anchor ledger operations and does not mediate the external provider/activation capability.

## Finding 2 — the supported ledger API mixes delegation-safe commands with broker-only authority

`HistoricalSharedAnchorLedger` / the LAB-090 descendant contain two qualitatively different surfaces.

### Candidate delegated commands

These can be represented as value-only request/response messages without exposing provider or DB handles:

- reserve an exact `Intent`;
- execute an exact `Intent`;
- read an entry / reconcile an already-owned request where policy permits;
- read verification/status projections;
- request durable verification and receive a boolean/typed failure.

The consumer needs the *result* of these operations, not the underlying `AttestedCatchup`, provider object, SQLite connection, history helper, activation state, or verification keys.

### Broker-only authority

These must remain unreachable from a narrower delegated component unless separately authorized:

- `AttestedCatchup` and its `provider`;
- provider `increment` / reconcile primitives;
- LAB-090 `prepare_activation`, `commit_activation`, `release_activation`, `abort_activation`, `activation_status`;
- direct provider-generation rotation helpers;
- raw writable SQLite connection;
- `_current_locked`, `_rotate_locked`, receipt-store and other internal history mutation/verification helpers;
- mutable bootstrap/path/provider-history strategy objects covered by LAB-094/095/096.

The existing in-process ledger cannot enforce this distinction because `self.attested` and `self.provider_history` remain reachable strategy/capability objects and the ledger itself performs external effects through them.

## Finding 3 — the coherent LAB-093 target is a broker-owned ledger, not a read-only wrapper around a live ledger object

The supported shape should be:

```text
narrow worker/component
    |
    | value-only LedgerCommand / LedgerResult
    v
broker process (LAB-087 trust domain)
    |- owns supported ledger object
    |- owns writable SQLite handle / path authority
    |- owns AttestedCatchup + external provider capability
    |- owns LAB-090 activation capability
    |- performs reserve/execute/reconcile/rotate only after command authorization
    v
SQLite + external provider
```

The worker must never receive the live ledger Python object. Otherwise a façade that simply forwards to a hidden ledger while retaining that ledger in a reachable attribute merely moves the same object-graph leak one hop.

A process boundary is therefore not optional for a security claim against arbitrary Python introspection. An in-process façade may still be useful as API hygiene, but it can only claim accidental-misuse reduction for fully trusted callers.

## Minimal capability protocol

A first supported delegated protocol should be intentionally smaller than the full ledger API.

### Value-only command envelope

Required fields should be immutable/serializable values, for example:

- `operation`: closed enum such as `RESERVE`, `EXECUTE`, `ENTRY`, `VERIFY_DURABLE`;
- exact intent fields when relevant (`intent_id`, `component_id`, `intent_type`, `payload_digest`);
- explicit timeout-after-commit flag only where the supported contract already permits it;
- caller/component identity supplied by the broker's authenticated channel, not trusted from an arbitrary object reference.

### Value-only response

Return only immutable data already present in canonical result types:

- `LedgerEntry` fields or an equivalent immutable DTO;
- stable receipt binding/status;
- typed failure category;
- verification boolean/details that do not expose signing/provider mutation handles.

### Deliberately absent

Do not expose:

- provider object or provider id -> provider lookup capability;
- `AttestedCatchup` / verifier/keyring object;
- activation ticket mutation methods;
- raw SQL or arbitrary method names;
- generic `getattr`/RPC reflection;
- file paths or writable DB handles;
- provider-history helper object.

## Rotation / administrative operations

`rotate_provider` should not be part of the first narrow-worker façade. It is qualitatively stronger than ordinary intent execution because it changes the trusted external provider generation and, under LAB-090, drives activation fencing.

If delegation of rotation is later required, it needs a separate administrator capability/message type and must compose with LAB-090/LAB-100 provider-implementation authority. Do not smuggle it through a generic `CALL(method, args)` broker command.

## Composition with LAB-094 / 095 / 096

LAB-093 should not be fixed as four independent underscore renames.

The broker should construct and retain one authority graph:

- canonical DB identity/path;
- immutable bootstrap trust root;
- one provider-history strategy object;
- one exact/trusted attested/provider capability;
- LAB-090 activation capability;
- supported ledger facade/command dispatcher.

Workers see none of those nodes. This naturally composes the retained-authority findings from LAB-094/095/096 with LAB-093's delegated-capability finding.

## Required regression-first proof when exact execution is available

1. Construct a supported ledger/provider inside the broker trust domain.
2. Delegate only the value-only command endpoint to a worker process/user.
3. Prove the worker can perform the permitted `RESERVE`/`EXECUTE` path and receive immutable results.
4. Prove the worker cannot recover a live ledger, `AttestedCatchup`, provider, activation state, history helper, writable DB connection, or broker filesystem path from the endpoint/result object graph.
5. Attempt direct provider increment/activation and writable SQLite access from the worker identity; both must fail for independent reasons.
6. Kill/restart the worker while keeping broker/provider state and prove no authority state is reconstructed or widened in the worker.
7. Retain LAB-087 filesystem/process tests and LAB-080/081/090 downstream behavior.

A negative control should show that giving the worker the live ledger object in-process still permits recovery through reachable Python state; this documents why the process boundary owns the security claim.

## Decision

`LAB093_BROKER_BOUNDARY_REUSE_SELECTED`.

The minimal coherent implementation direction is to extend/reuse LAB-087's broker/process trust boundary with a value-only shared-anchor ledger command façade. Do not implement `_attested` renaming as a security fix, and do not delegate the live ledger object to a lower-trust component.

This is architecture/source evidence only. Exact RED/GREEN implementation remains pending until executable source is available.
