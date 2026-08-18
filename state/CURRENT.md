# Current Lab State

Last updated: 2026-08-18

## Active objective

Complete bootstrap of the durable autonomous research/runtime loop so future executions can resume from repository state and perform the work themselves.

## Active issue / branch / PR

- Issue: `#1 [LAB-001] Bootstrap durable autonomous operating loop`
- Branch: `lab/bootstrap-autonomous-runtime`
- PR: pending creation

## Last completed step

Created the operating contract, self-resume prompt, operating model, research/decision conventions, issue template, README, and initial GitHub task queue.

## Evidence produced

- Repository was initially effectively empty except for a minimal README.
- Connected GitHub access can write repository files and issues.
- `AGENTS.md` explicitly forbids treating GitHub workers/Actions as execution workers.
- `prompts/SELF_RESUME.md` explicitly requires the executing assistant to perform research, implementation, tests, debugging, audits, and state updates itself.
- Initial queue exists:
  - `#1` bootstrap durable loop — IN_PROGRESS;
  - `#2` empirically baseline execution surface and hard limits — READY;
  - `#3` prove cross-run resumability — READY;
  - `#4` build/refine autonomous research agenda — READY.

## Known blockers / constraints

- GitHub workers/Actions must not be treated as execution workers.
- Repository state alone cannot cause continuous execution. A separate available scheduler/task trigger must invoke the assistant for each new run.
- Actual scheduler recurrence limits and cross-run connector availability must be treated as empirical questions and verified in LAB-002/LAB-003.

## Exact next action

Open and audit the bootstrap PR. Once bootstrap is integrated, make `#2` the active issue and configure the recurring self-resume trigger to invoke `prompts/SELF_RESUME.md` semantics.

## Backlog changes

Seeded issues #1–#4. Do not add open-ended research tasks until capability and resumability experiments establish what the autonomous loop can reliably execute.
