# LAB-017 — bounded state-space exploration

## Donor mechanisms

1. **TLA+/TLC**: explicit-state model checking explores reachable states of a finite model and checks safety/liveness properties. Transfer: define state, actions and invariants independently from implementation details; treat counterexample traces as first-class regression artifacts. Primary: Leslie Lamport TLA+ Tools / TLC documentation.
2. **Apalache**: symbolic bounded model checking checks all executions up to a configured finite length and explicitly warns that absence of a violation within the bound is incomplete. Transfer: always publish the bound and never call bounded success a proof. Primary: Apalache documentation, `check`/symbolic model checking.
3. **Jepsen/Knossos**: verifies experimentally observed concurrent histories against a consistency model. Transfer: preserve short operation histories/traces so implementation executions can later be checked against the abstract kernel rather than trusting final state alone. Primary: `jepsen-io/knossos`.
4. **Hypothesis rule-based state machines**: generates sequences of rules, checks invariants after steps, and shrinks failures to short reproducing programs. Transfer: supplement exhaustive shallow exploration with seeded schedules and keep minimal replayable traces. Primary: Hypothesis stateful testing docs.

## Model

Actions cover claim, durable intent, known/unknown effect outcome, reconciliation, evidence append/invalidation, completion, duplicate delivery and obsolete-worker mutation. Invariants require intent-before-effect, idempotent effect identity, fresh evidence for DONE, terminal monotonicity, and rejection of stale authoritative mutation.

## Results

Local standard-library execution on 2026-08-19:
- corrected model: depth 8, 314 queued states, no invariant violation;
- seeded randomized supplement: seed 17017, 1000 schedules x 20 actions, no corrected-model violation;
- unsafe split completion rediscovered in 5 actions: intent, effect_ok, append_evidence, invalidate, complete;
- unsafe terminal reopen rediscovered in 5 actions: intent, effect_ok, append_evidence, complete, duplicate;
- stale-authority unsafe variant rediscovered in 4 actions: claim, intent, effect_ok, stale_mutate;
- unittest suite: 5/5 passed.

An audit of the model found an initially over-permissive transition that allowed another effect call from CONFIRMED. That defect was corrected before publication by restricting effect execution to INTENT/UNKNOWN.

## Decision

Keep a small executable abstract correctness model beside implementation tests. Every newly discovered cross-layer defect should be reduced to an action/invariant counterexample and retained as a regression. Bounded exploration is a falsification tool and regression amplifier, not a proof of universal correctness.

## Non-goals

No general model checker, no unbounded proof, no storage/network timing model, and no replacement for implementation-level concurrency tests.
