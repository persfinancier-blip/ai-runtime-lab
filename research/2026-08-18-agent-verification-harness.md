# Agent Completion Verification — donor synthesis and experiment

Date: 2026-08-18  
Issue: #11 / LAB-006

## Question

How can an autonomous runtime reject false success using evidence produced by execution rather than trusting the executor's completion narrative?

## Donor mechanisms

### SWE-bench / SWE-bench Verified

Primary sources:
- https://www.swebench.com/
- https://github.com/SWE-bench/SWE-bench

Transferable mechanism: completion is evaluated by a harness against repository state and tests, not by asking the agent whether the issue was solved. SWE-bench Verified is a human-filtered subset and current leaderboard entries are evaluated with a common harness. The useful runtime principle is to make terminal success a verifier decision over observed artifacts/results.

### SLSA provenance and artifact verification

Primary sources:
- https://slsa.dev/spec/v1.2/provenance
- https://slsa.dev/spec/v1.2/verifying-artifacts

Transferable mechanisms: provenance identifies the subject artifact and how it was produced; verification checks that provenance applies to the artifact and matches expectations. The critical transfer is digest-bound evidence: evidence for artifact A must not silently validate mutated artifact B.

### in-toto attestation model

Primary sources:
- https://in-toto.io/
- https://github.com/in-toto/attestation

Transferable mechanism: separate a statement's subject from its predicate/evidence and use stable artifact identity/digests so downstream verification can decide whether an assertion actually applies to the object under evaluation.

## Minimal claim/evidence contract

Schema version: `1`.

`Task` contains the complete requirement set and exact artifact digest under verification. `Evidence` contains stable ID, kind, artifact digest, whether the result was actually observed, outcome, and requirements supported. `Claim` names every requirement it says is complete and explicitly references evidence IDs. `Verdict` is produced by the verifier, never by the executor narrative.

Acceptance requires:
1. supported schema;
2. complete requirement coverage;
3. every referenced evidence ID exists;
4. evidence was observed, not merely planned/reported;
5. evidence artifact digest equals the artifact currently judged;
6. every requirement has current passing evidence;
7. at least one current observed passing test exists.

## Experiment

Local implementation was executed before publication with standard-library Python.

Command:

```bash
python -m unittest -v
```

Observed result: **7/7 tests passed**. `python -m py_compile protocol.py test_protocol.py` also passed.

Seeded trajectories:
- correct implementation + observed passing test: accepted;
- test marked pass but never observed/executed: rejected;
- observed failing test with success claim: rejected;
- passing test from an old artifact digest: rejected;
- headline completion with incomplete requirement set: rejected;
- nonexistent evidence reference: rejected;
- formerly valid evidence after artifact mutation: rejected.

## Findings

1. Completion is a claim; terminal state should be granted by a verifier over evidence, not by the worker that made the claim.
2. Evidence freshness requires binding observations to the exact artifact/version they evaluated.
3. `observed=true` is materially different from a planned command or self-reported result.
4. Requirement coverage and test success are independent gates: a green test does not prove omitted acceptance criteria.
5. Evidence IDs must resolve; dangling references are verification failures.
6. Mutation invalidates old evidence by default unless the verifier has an explicit safe reuse rule.

## Relationship to LAB-005

LAB-005 run state answers "where is execution and what is safe to do next?". LAB-006 evidence answers "what was actually observed about which artifact?". Run state may reference evidence IDs/receipts and should require an accepting verdict before `DONE`, but evidence should not be embedded as mutable worker narrative inside checkpoint state.

## What this verifier cannot prove

- that the requirements themselves are complete or correct;
- that a passing test has adequate semantic coverage;
- that an evidence producer is trustworthy if it can forge the observation channel;
- that nondeterministic/environment-dependent behavior will remain correct;
- human/product judgments that lack machine-checkable acceptance criteria.

These are trust/coverage boundaries, not reasons to let executor prose become proof.

## Integration implication

The next Evidence Ledger work should make observations append-only/content-addressed where practical, preserve producer/time/tool provenance, and let run-state terminal transitions reference a verifier verdict over immutable evidence IDs.
