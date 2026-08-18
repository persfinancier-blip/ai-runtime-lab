# Capability Negotiation and Safe Fallback Planning

Date: 2026-08-18  
Issue: #14 / LAB-008  
Branch: `lab/008-capability-planner`

## Research question

How should an autonomous runtime select an execution route from capabilities observed in the current run, prefer the best route when available, fall back safely when it is not, and refuse alternatives that weaken required safety/correctness properties?

## Donor mechanisms

### 1. Model Context Protocol — explicit initialization capabilities

Primary source: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle

Transferable mechanisms:
- protocol version and capabilities are exchanged explicitly at initialization;
- optional operations are only valid when the corresponding capability is declared;
- capability negotiation is session-scoped rather than an eternal property of an implementation;
- incompatible protocol versions must not be silently treated as compatible.

Implication: observations should be explicit, versioned, and scoped to the current execution context.

### 2. Terraform plugin protocol — compatibility metadata before selection

Primary source: https://developer.hashicorp.com/terraform/plugin/terraform-plugin-protocol

Transferable mechanisms:
- plugin protocol versions are compatibility boundaries;
- discovery metadata participates in deciding which provider/plugin version can be selected;
- major/minor protocol evolution has defined compatibility semantics rather than optimistic guessing.

Implication: planner inputs need schema/protocol compatibility gates before preference ranking.

### 3. Kubernetes Discovery API / resourceVersion — discover current surface and reason about freshness

Primary sources:
- https://kubernetes.io/docs/concepts/overview/kubernetes-api/
- https://kubernetes.io/docs/reference/using-api/api-concepts

Transferable mechanisms:
- clients discover resources/verbs exposed by the current server rather than hard-coding all availability;
- version/freshness information (`resourceVersion`) lets clients reason about whether observed state is current enough for an operation;
- discovery and execution are separate concerns.

Implication: a capability observation needs freshness semantics and must not be reused indefinitely.

## Synthesized protocol

A capability observation contains:
- schema version;
- stable capability identity;
- route and operation;
- observation time and TTL;
- available/unavailable result;
- relevant properties such as safety, auditability, atomicity, or supported semantics;
- evidence reference proving the observation.

A requirement contains:
- schema version;
- requested operation;
- **hard** properties that every route must satisfy;
- weighted **preferences** that only rank already-safe candidates.

A route contains declared semantics and links to a capability observation. The planner:
1. rejects incompatible operation/schema;
2. rejects missing, unavailable, or stale observations;
3. rejects any route violating a hard property;
4. scores only remaining routes by preferences/base priority;
5. uses a deterministic lexical tie-break;
6. returns selected evidence plus machine-readable rejection reasons and a stable explanation hash.

## Failure-injection experiment

Prototype: `experiments/capability_planner/`

Commands executed locally:

```bash
python -m unittest discover -s experiments/capability_planner/tests -v
python -m compileall -q experiments/capability_planner
```

Observed result: **7/7 tests passed** and compilation completed successfully.

Covered cases:
1. preferred path available -> preferred selected;
2. preferred path unavailable -> safe audited fallback selected;
3. stale observation -> stale route rejected;
4. unsafe fallback with much higher nominal priority -> rejected on hard safety gate;
5. equal candidates -> deterministic lexical tie-breaking;
6. no viable path -> explicit no-plan result with rejection reasons;
7. identical inputs -> stable explanation identity.

## Findings

1. Tool names are insufficient capability descriptions. Planning needs operation-level semantics and properties.
2. Freshness is part of capability correctness. An old successful probe is not proof of current availability.
3. Hard constraints must be evaluated before optimization. A cheaper/faster route cannot buy its way past a safety invariant.
4. Fallback equivalence should be defined by required observable properties, not by implementation similarity.
5. Planner explanations are evidence-bearing decisions: selected observation references and rejected reasons should be persistable and inspectable.
6. `no viable path` is a correct result and must not trigger an unsafe downgrade.

## Integration with earlier lab work

- **LAB-005 durable run state:** may persist the chosen route/explanation ID and later require re-planning when observations expire. It should not embed planner policy as conversational memory.
- **LAB-007 evidence ledger:** can persist capability probe observations and planner explanation records. Hash/evidence identity provides provenance, not authorization.
- **LAB-006 verifier:** can require that terminal claims cite evidence generated through a route that satisfied the task's hard requirements.

These concerns remain separate: run state says where execution is; evidence says what was observed; capability planning decides which route is currently safe and preferred.

## Non-goals

- no general plugin marketplace;
- no automatic credential acquisition;
- no authorization/safety-gate bypass;
- no distributed service discovery system;
- no workflow orchestration engine.

## Stop-condition assessment

Three primary-source donor families were compared and the deterministic planner passes the seeded matrix. Broader capability routing should be deferred until a concrete downstream requirement exposes a missing property or probe mechanism.
