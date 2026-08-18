# Cross-layer Correctness Kernel

LAB-014 composes previously validated experiment primitives without turning them into a new workflow engine.

## Reused mechanisms

- LAB-005 `DurableEngine` / `JsonStateStore` / `EffectLedger`: durable intent, UNKNOWN reconciliation, idempotency and fencing.
- LAB-006 deterministic `Verifier`: completion claims must be proven for the current artifact and requirements.
- LAB-007 append-only `Ledger` and ledger verifier: current evidence validity, invalidation and supersession.
- LAB-008 `Planner`: hard route constraints before preferences and safe fallback selection.
- LAB-011 `MemoryStore`: quarantine/retraction/current trust filtering; memory stays advisory.
- LAB-012 `decide`: BLOCK/ESCALATE/PROBE dominate route preference and topology convenience.

Topology is intentionally only a routing input here. LAB-013 already tested topology tradeoffs; this experiment checks that topology cannot acquire authority over safety primitives.

## Composition order

```text
1. load/claim durable run state
2. reconcile UNKNOWN side-effect outcome
3. evaluate escalation / hard authority boundaries
4. filter advisory memory by trust/currentness
5. negotiate a safe capability route
6. choose topology only as an optimization within the allowed route/policy envelope
7. execute with the original logical work/idempotency/evidence identity
8. append observations/receipts to the evidence ledger
9. resolve invalidation/supersession
10. run deterministic claim verification for the current artifact/version
11. allow terminal DONE only if current ledger evidence and verifier both accept
```

Safety invariants are authority constraints; route priority, topology and similarity ranking are preferences. Preferences cannot weaken an authority constraint.

## Run

```bash
python -m unittest discover -s experiments/correctness_kernel/tests -p 'test_*.py' -v
python -m compileall -q experiments/correctness_kernel
```

The deliberately unsafe ordering bug is retained outside passing discovery:

```bash
python -m unittest experiments.correctness_kernel.tests.unsafe_seed_expected_failure
```

It is expected to fail because narrative memory is treated as completion authority.

## Non-goals

This is not a production transaction coordinator, workflow engine, distributed lock service, multi-agent framework or product architecture. It is a deterministic composition/invariant harness.
