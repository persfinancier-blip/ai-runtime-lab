# Cross-layer Correctness Kernel — composition findings

Date: 2026-08-18  
Issue: #26 / LAB-014  
Branch: `lab/014-correctness-kernel`

## Question

Do the independently validated correctness mechanisms from LAB-005 through LAB-013 remain safe when combined, or do ordering/authority mistakes create new failure modes?

## Method

This issue composes already accepted mechanisms and stress-tests their boundaries rather than adding another donor survey. The kernel imports existing experiment interfaces where practical instead of re-implementing their semantics.

Reused directly:
- LAB-005 durable run state, UNKNOWN reconciliation, idempotency and fencing;
- LAB-006 claim/evidence verifier;
- LAB-007 append-only evidence ledger, invalidation and supersession checks;
- LAB-008 capability planner and hard-before-preference route filtering;
- LAB-011 memory trust/quarantine/restart persistence;
- LAB-012 escalation policy.

LAB-013 topology is represented only as a selected routing mode. Its benchmark logic is not duplicated because LAB-014 tests that topology cannot become an authority bypass.

## Seeded composition bug

An intentionally unsafe downstream check treated a memory narrative containing `done successfully` as sufficient completion authority.

Executed:

```bash
python -m unittest experiments.correctness_kernel.tests.unsafe_seed_expected_failure
```

Observed result: expected failure.

```text
AssertionError: True is not false : seeded bug: downstream completion trusted advisory narrative
FAILED (failures=1)
```

The memory subsystem itself behaved as designed; the composition error was downstream authority misuse.

## Audit defects found and corrected

### 1. Ledger/verifier semantic-binding gap

The first corrected kernel verified ledger IDs and claim-verifier objects separately. A caller could therefore reuse a valid ledger ID while supplying a verifier-side `Evidence` object with fabricated requirement coverage or altered semantics.

Fix:
- evidence ID must resolve in the ledger and remain current;
- kind, artifact digest, observed/trusted status and outcome must match the ledger observation;
- requirement coverage is committed into the observation `output_digest` as a canonical digest and must match the verifier-side requirement tuple.

A forged requirement mapping is now rejected deterministically.

### 2. Restart dropped memory quarantine state

The initial composition constructed `MemoryStore(path)` on restart instead of using LAB-011's durable `MemoryStore.load(path)`. That discarded persisted quarantine/retraction state from the in-memory view and could change later decisions.

Fix: kernel startup now loads the durable memory store. A restart regression proves a quarantined record remains quarantined and excluded from authoritative memory after reconstruction.

## Corrected invariant matrix

Executed locally:

```bash
python -m unittest discover -s experiments/correctness_kernel/tests -p 'test_*.py' -v
```

Observed result after both audit fixes: **12/12 tests passed**.

Also executed:

```bash
python -m compileall -q experiments/correctness_kernel
```

Observed result: success.

A direct `git clone` was attempted to execute the final branch against an exact checkout, but this runtime's local container could not resolve `github.com`. Exact-source validation therefore uses GitHub connector file/patch inspection; local execution uses interface-compatible copies of the already fetched experiment modules.

Scenarios:

1. UNKNOWN side effect is reconciled before receipt evidence can support completion;
2. currently accepted evidence invalidated later revokes completion;
3. quarantined memory cannot enter authoritative control context;
4. capability fallback preserves work/artifact/idempotency/evidence identity;
5. payment/legal/identity/secret authority boundary dominates an available preferred route;
6. manager/handoff topology cannot bypass BLOCK/ESCALATE semantics;
7. an obsolete fence after reroute cannot commit an external effect;
8. persisted memory quarantine survives restart/reload;
9. restart plus the same authoritative observations yields the same deterministic safe next action;
10. narrative memory may influence planning but cannot satisfy completion evidence requirements;
11. a valid ledger ID cannot be reused with fabricated verifier-side requirement semantics;
12. replay with the same effect key remains idempotent.

## Composition invariants

### Authority invariants

These are non-negotiable correctness/safety constraints:

- terminal completion requires current valid ledger evidence **and** deterministic claim verification for the current artifact/requirements;
- verifier-side evidence semantics must be bound to the authoritative ledger record;
- UNKNOWN side effects must be reconciled before retry/completion;
- evidence invalidation/supersession propagates into completion decisions;
- durable quarantine/retraction state must survive restart;
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
durable state + durable memory load
  -> claim/fence current attempt
  -> UNKNOWN reconciliation
  -> authority/escalation policy
  -> trusted/current advisory-memory filter
  -> capability negotiation
  -> topology optimization within allowed envelope
  -> fenced/idempotent execution
  -> append observation/receipt
  -> resolve invalidation/supersession
  -> bind verifier-view semantics to ledger record
  -> current-artifact claim verification
  -> terminal completion decision
```

The central rule is: **authority flows downward; preferences do not flow upward**. A downstream optimization layer cannot reinterpret advisory output as authoritative evidence.

## Important dependency constraints

1. Reconciliation precedes evidence issuance: an UNKNOWN outcome is not success evidence.
2. Durable safety state must be reconstructed before a new decision is made.
3. Evidence validity is checked at decision time, not only when evidence was first observed.
4. Claim/verifier semantics are checked against the ledger record before requirement proof is accepted.
5. Escalation/authorization is evaluated before route/topology convenience.
6. Capability fallback may change transport but not logical identity.
7. New attempt/topology ownership advances fencing before external mutation.
8. Memory can suggest what to inspect or route, but cannot synthesize receipts or completion proof.
9. Completion is derived, not sticky: invalidation makes a previously true completion decision false until re-verified.

## Limits

- The experiments remain standard-library/single-process reference mechanisms, not a production transactional system.
- JSON/file stores demonstrate semantics but not distributed atomicity.
- Restart determinism assumes the same authoritative capability observations and policy inputs; changed observations should intentionally change the next action.
- Direct container DNS/network access to GitHub remained unavailable, so the exact branch could not be cloned locally in this run.
- No claim is made that the kernel is a universal workflow architecture.

## Decision

The main correctness primitives now compose under an explicit authority order, and the experiment exposed two composition-only defects that individual component tests could not reveal. The highest-value next step is no longer another independent correctness primitive: it is **production-grade atomic persistence/concurrency semantics** for run state, evidence, leases/fences and completion transitions, followed by measured correctness overhead/latency once a transactional prototype exists.
