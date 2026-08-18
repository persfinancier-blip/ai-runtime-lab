# Operating Model

## Purpose

This repository is a durable workspace for long-running AI research and engineering where individual chat sessions may end, reset, or lose context.

The design goal is resumability, evidence, and autonomous continuation — not unattended GitHub-side execution.

## Control plane

### GitHub Issues — task queue

Each meaningful unit of work is an issue. An issue should contain:

- objective;
- context;
- acceptance criteria;
- dependencies;
- expected evidence/tests;
- links to produced artifacts/PRs.

Issue state is authoritative for backlog status.

### Branches and pull requests — change isolation

Implementation and material documentation changes should normally happen on a task branch and be reviewed through a pull request before integration.

### `state/CURRENT.md` — execution handoff

This file is intentionally small. It answers: "What exactly should the next run do first?"

It is not a full project log and should not become one.

### `research/` — durable findings

Research outputs should preserve:

- question;
- date;
- sources;
- observed mechanisms;
- experiments;
- conclusions;
- confidence/unknowns;
- implications for implementation.

### `decisions/` — architecture/product decisions

Material decisions should be written as short ADR-style records with status, context, decision, alternatives, consequences, and reversal conditions.

## Suggested issue lifecycle

Use normal GitHub issue state plus an explicit status line in the issue body when useful:

- `READY` — actionable and unblocked;
- `IN_PROGRESS` — selected by the current execution;
- `BLOCKED` — cannot progress, with exact blocker recorded;
- `VERIFY` — implementation exists but independent validation/audit remains;
- `DONE` — acceptance criteria and validation satisfied.

Do not create a complex workflow engine unless real usage proves it necessary.

## Priority rule

Default ordering:

1. broken invariant, security issue, data-loss/corruption risk;
2. blocker of currently active work;
3. incomplete verification/audit of recently implemented work;
4. highest-leverage research uncertainty;
5. smallest implementation slice that unlocks downstream work;
6. cleanup/documentation.

## Research-to-code pipeline

For material technical uncertainty:

`question -> source scan -> donor/mechanism extraction -> experiment -> decision -> implementation -> test -> audit -> integration`

A donor is valuable only when the exact transferable mechanism is identified. A repository name alone is not a finding.

## Testing policy

Tests should be proportional to risk and should include, where relevant:

- parser/static validation;
- unit tests;
- integration tests;
- regression tests for reproduced bugs;
- cold-start/runtime smoke tests;
- failure-path tests;
- platform-specific checks;
- manual behavioral verification when automation is insufficient.

A test that was not run is not evidence.

## Audit policy

After implementation and tests, perform a distinct audit pass. Check at minimum:

- objective/acceptance coverage;
- hidden assumptions;
- duplicate mechanisms;
- state/concurrency hazards;
- failure recovery;
- security boundaries;
- platform compatibility;
- evidence quality;
- stale docs/state.

If defects are found, return to implementation and test again. Audit is a loop, not a report-only phase.

## Human intervention

The owner can interrupt or redirect the laboratory at any time. The next execution must treat the latest explicit human instruction as higher authority than old issue/state text and update durable state accordingly.
