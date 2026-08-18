# Autonomous software-engineering loop — composition experiment

Date: 2026-08-18  
Issue: #18 / LAB-010  
Branch: `lab/010-software-engineering-loop`

## Question

Can the correctness primitives proven in LAB-005–009 compose into a reliable full-cycle software-engineering lifecycle that rejects superficially plausible success?

## Current primary-source donors

### 1. SWE-bench evaluation harness

Primary sources:
- https://github.com/SWE-bench/SWE-bench
- https://github.com/SWE-bench/SWE-bench/blob/main/docs/reference/harness.md

Transferable mechanisms:
- evaluate generated patches against actual repository tests rather than narrative claims;
- isolate evaluation in reproducible execution environments;
- separate patch generation from the evaluation harness;
- derive completion from observed test outcomes for a concrete task instance.

Implication: test execution is evidence produced by a separate validation stage, not a property the patch author may assert.

### 2. SWE-agent / mini-SWE-agent

Primary source:
- https://github.com/SWE-agent/SWE-agent

Transferable mechanisms:
- software-engineering agents operate across a complete issue/repository/edit/execute interaction loop;
- the Agent-Computer Interface makes repository inspection, editing and execution explicit operations;
- current SWE-agent documentation recommends the smaller mini-SWE-agent implementation, reinforcing that lifecycle correctness does not require a huge orchestration layer.

Implication: the lab should keep the lifecycle coordinator thin and leave execution/evidence responsibilities at explicit boundaries.

### 3. SWE-bench Verified / OpenAI Preparedness evaluation work

Primary source:
- https://openai.com/index/introducing-swe-bench-verified/

Transferable mechanisms:
- benchmark tasks and tests themselves can be underspecified or invalid;
- OpenAI and SWE-bench authors created a human-validated subset and improved evaluation harness because evaluation quality materially affects capability conclusions;
- a plausible patch score is unsafe when the evaluation specification is defective.

Implication: reproduction and requirement coverage are first-class gates before terminal success; a passing narrow test alone cannot prove full task completion.

## Lifecycle state machine

```text
NEW
  -> REPRODUCED       [observed bug reproduction]
  -> PATCHED          [artifact version increments]
  -> VALIDATED        [safe route + passing current-version evidence + all requirements]
  -> AUDITED          [separate clean regression audit]
  -> COMPLETE         [completion decision gate]
```

Failure transitions:

```text
unreproduced -> HOLD
validation failure -> HOLD
partial fix -> HOLD
stale evidence -> HOLD
audit regression -> PATCHED
no safe validation route -> BLOCKED
missing required evidence -> HOLD
```

## Reuse map to LAB-005–009

LAB-010 intentionally does not build replacement subsystems.

- **LAB-005 durable run state:** production lifecycle transitions belong in durable versioned run state; this experiment only models them in memory.
- **LAB-006 verification harness:** the final decision is a verifier gate over observations, not an agent self-report.
- **LAB-007 evidence ledger:** reproduction/test/audit evidence should be durable append-only records with artifact identity and provenance; the local `Evidence` dataclass is a stand-in.
- **LAB-008 capability negotiation:** validation chooses only available + safe routes, then prefers the best eligible route. A high-priority unsafe route remains ineligible.
- **LAB-009 memory:** memory may surface relevant repository/task context, but superseded/stale memories cannot substitute for authoritative current-version evidence.

## Experiment

Prototype:
- `experiments/software_engineering_loop/loop.py`
- `experiments/software_engineering_loop/tests/test_loop.py`

Observed commands in the executing runtime:

```text
python -m unittest discover -s experiments/software_engineering_loop/tests -p 'test_*.py' -v
Ran 9 tests ... OK

python -m compileall -q experiments
completed with exit code 0
```

## Seeded trajectories and outcomes

| Scenario | Expected | Observed classification |
|---|---|---|
| reproduced bug -> complete patch -> passing validation -> clean audit | ACCEPT | accepted |
| patch attempted without successful reproduction | REJECT | `unreproduced_bug` |
| primary behavior fixed but secondary requirement omitted while headline test passes | REJECT | `partial_fix` |
| passing validation evidence belongs to prior artifact version | REJECT | `stale_evidence` |
| tests pass but audit discovers regression | REJECT + return to patch | `audit_regression`, phase `PATCHED` |
| preferred validation capability absent, safe fallback available | CONTINUE | `safe-fallback` selected, accepted after clean audit |
| preferred route absent and only unsafe route available | BLOCK | `no_safe_validation_route` |
| observed validation actually fails | REJECT | `validation_failed` |

The deliberately plausible false-success case is the partial fix: the supplied validation result is `passed=True`, but the lifecycle rejects completion because not all declared requirements were satisfied.

## Measured failure taxonomy

The deterministic taxonomy has seven stable classes:

1. `unreproduced_bug`
2. `validation_failed`
3. `partial_fix`
4. `stale_evidence`
5. `audit_regression`
6. `no_safe_validation_route`
7. `missing_evidence`

The seeded taxonomy test verifies stable names/counting for the principal injected failures. The taxonomy is intended as an observation vocabulary, not a claim that these are all real-world coding-agent failures.

## Audit findings

### What composed cleanly

- artifact-version binding from LAB-006/007 prevents stale successful tests from authorizing a newer patch;
- LAB-008 safety-first routing cleanly handles tool loss without lowering correctness requirements;
- a separate audit gate catches regressions that headline tests miss;
- explicit requirement coverage catches partial fixes even when supplied validation says success;
- `BLOCKED` is a valid terminal-for-now state when no safe validation path exists.

### What must remain separate

- durable execution state is not evidence;
- evidence/provenance is not conversational memory;
- memory relevance is not verification;
- capability availability is not permission to weaken a required gate;
- an audit is not the same observation as the test suite it audits.

### Gaps versus real repository engineering

This deterministic simulator does not prove:
- real repository checkout/edit/build/test isolation;
- correctness of automatically generated patches;
- coverage adequacy of a real test suite;
- flaky-test handling;
- dependency/environment drift;
- merge-conflict/rebase behavior;
- security review quality;
- model reasoning quality;
- calibration of hidden requirements inferred from natural-language issues.

Those need real repository tasks and execution sandboxes. The current result only proves the lifecycle gate semantics under controlled failure injection.

## Protocol decision

A software-engineering agent should not transition directly from PATCHED to DONE. The minimum reliable completion path is:

`observed reproduction -> versioned patch -> safe current-version validation -> requirement coverage -> independent audit -> evidence-backed completion decision`.

If a required gate cannot be performed safely, the correct outcome is HOLD/BLOCKED, not optimistic success.

## Stop-condition assessment

Three current primary-source donor families were compared. The deterministic prototype covers every required LAB-010 scenario, rejects all injected false-success cases, accepts the valid case and safe-fallback case, and exposes a stable failure taxonomy. Broader real-repository benchmarking is intentionally deferred rather than turning this issue into a general coding-agent platform.
