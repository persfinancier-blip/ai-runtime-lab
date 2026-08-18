# Cross-layer Correctness Kernel — composition findings

Date: 2026-08-18  
Issue: #26 / LAB-014  
Branch: `lab/014-correctness-kernel`

## Question

Do the individually validated correctness mechanisms from LAB-005 through LAB-013 remain safe when combined, or do ordering/authority mistakes create new failure modes?

## Method

This issue does not add another donor survey. It composes already accepted mechanisms and stress-tests their boundaries. The kernel imports existing experiment interfaces where practical rather than re-implementing their semantics.

Reused directly:
- LAB-005 durable run state, UNKNOWN reconciliation, idempotency and fencing;
- LAB-006 claim/evidence verifier;
- LAB-007 append-only evidence ledger, invalidation and supersession checks;
- LAB-008 capability planner and hard-before-preference route filtering;
- LAB-011 memory trust/quarantine filter;
- LAB-012 escalation policy.

LAB-013 topology is represented only as a selected routing mode. The point of LAB-014 is to prove topology cannot become an authority bypass; its internal benchmark logic is not duplicated.

## Seeded composition bug

An intentionally unsafe downstream check treated a highly trusted memory narrative containing `done successfully` as sufficient completion authority.

Executed:

```bash
python -m unittest experiments.correctness_kernel.tests.unsafe_seed_expected_failure
```

Observed result: expected failure.

```text
AssertionError: True is not false : seeded bug: downstream completion trusted advisory narrative
FAILED (failures=1)
```

This demonstrates a composition failure even though the memory subsystem itself behaved correctly: the bug was ordering/authority misuse downstream.

## Corrected invariant matrix

Executed:

```bash
python -m unittest discover -s experiments/correctness_kernel/tests -p 'test_*.py' -v
```

Observed result: **10/10 tests passed**.

Also executed:

```bash
python -m compileall -q experiments/correctness_kernel
```

Observed result: success.

Scenarios:

1. UNKNOWN side effect is reconciled before receipt evidence can support completion;
2. currently accepted evidence invalidated later revokes the completion decision;
3. quarantined memory cannot enter authoritative control context;
4. capability fallback preserves work/artifact/idempotency/evidence identity;
5. payment/legal/identity/secret authority boundary dominates an available preferred route;
6. manager/handoff topology cannot bypass BLOCK/ESCALATE semantics;
7. an obsolete fence after reroute cannot commit an external effect;
8. restart/reload plus the same observations yields the same deterministic safe next action;
9. narrative memory may influence planning but cannot satisfy completion evidence requirements;
10. replay with the same effect key remains idempotent.

## Composition invariants

### Authority invariants

These are non-negotiable correctness/safety constraints:

- terminal completion requires current valid ledger evidence **and** deterministic claim verification for the current artifact/requirements;
- UNKNOWN side effects must be reconciled before retry/completion;
- evidence invalidation/supersession propagates into completion decisions;
- memory is advisory context, never proof that a side effect happened or a task completed;
- BLOCK / ESCALATE / PROBE decisions dominate capability preference and topology convenience;
- stale fencing blocks obsolete owners from external mutation;
- fallback/replay preserves logical work, effect-key and evidence identity.

### Optimization/policy preferences

These may choose among already safe alternatives but cannot weaken authority invariants:

- preferred capability route;
- single vs manager vs handoff topology;
- memory similarity ranking among eligible current/trusted records;
- structural/coordination cost.

## Minimal reference order

```text
durable state load/claim
  -> UNKNOWN reconciliation
  -> authority/escalation policy
  -> trusted/current advisory-memory filter
  -> capability negotiation
  -> topology optimization within allowed envelope
  -> fenced/idempotent execution
  -> append observation/receipt
  -> resolve invalidation/supersession
  -> current-artifact claim verification
  -> terminal completion decision
```

The key lesson is that **authority flows downward, preferences do not flow upward**. A downstream optimization layer must not reinterpret advisory output as authoritative evidence.

## Important dependency constraints

1. Reconciliation precedes evidence issuance: an UNKNOWN outcome is not evidence of success.
2. Evidence validity is checked at decision time, not only when evidence was first observed.
3. Escalation/authorization is evaluated before route/topology convenience.
4. Capability fallback may change transport but not logical identity.
5. New attempt/topology ownership must advance fencing before external mutation.
6. Memory selection can suggest what to inspect or route, but cannot synthesize receipts or completion proof.
7. Completion is derived, not sticky: invalidation makes a previously true completion decision false until re-verified.

## Limits

- The experiments remain standard-library/single-process reference mechanisms, not a production transactional system.
- JSON/file stores demonstrate semantics but not distributed atomicity.
- Restart determinism here assumes the same authoritative capability observations and policy inputs; changing observations should intentionally change the next action.
- No claim is made that the kernel is a universal workflow architecture.

## Decision

The lab now has evidence that its main correctness primitives can compose under a strict authority order. The next engineering question should shift from inventing more independent primitives to **production-grade atomic persistence/concurrency semantics** or **measured latency/cost overhead of the correctness kernel**, unless representative open-model serving hardware becomes available first.
