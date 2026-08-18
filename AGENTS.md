# AI Runtime Lab — Operating Contract

## Mission

`ai-runtime-lab` is a durable laboratory for autonomous AI research, prototyping, implementation, testing, and technical synthesis.

The human owner defines direction and may intervene at any time. The executing assistant owns the work loop between interventions.

## Critical execution constraint

Do **not** depend on GitHub Actions, GitHub workers, Codex workers, or background repository agents to perform research or implementation.

GitHub is the durable control plane: source, issues, decisions, evidence, state, branches, commits, and pull requests.

The executing assistant itself performs the actual work using the tools available in its current runtime. If a required tool is unavailable, record the limitation and choose the best available fallback rather than pretending execution occurred.

## Autonomous loop

For every run:

1. Read this file.
2. Read `state/CURRENT.md`.
3. Inspect open GitHub issues and active branches/PRs.
4. Resume an in-progress task before starting a new one, unless it is blocked or superseded.
5. Select the highest-value unblocked task.
6. Research before implementation when uncertainty is material.
7. Implement directly when implementation is required.
8. Run relevant tests/checks and inspect failures.
9. Audit the result for correctness, regressions, duplication, security, and unsupported assumptions.
10. Persist evidence and decisions in the repository.
11. Update the task and `state/CURRENT.md` before ending the run.
12. Create follow-up issues for newly discovered work.

## Definition of done

A task is not done merely because code was written or a report was drafted. Done means, as applicable:

- the question or implementation objective is answered;
- sources/evidence are recorded;
- code is committed to a branch;
- tests or other validation were actually run;
- failures are either fixed or explicitly recorded;
- an audit pass found no unresolved blocker;
- decisions and tradeoffs are documented;
- follow-up work is converted into issues rather than left only in prose;
- `state/CURRENT.md` reflects reality.

## Research rules

- Prefer primary sources, standards, official documentation, papers, source code, tests, and production-grade repositories.
- Treat remembered facts about fast-moving technology as untrusted until verified.
- Record donor repositories and exact reusable mechanisms, not just names.
- Separate facts, inference, experiments, and decisions.
- Do not copy code blindly; preserve licenses and provenance.
- When competing approaches exist, compare them against explicit criteria.

## Engineering rules

- Inspect existing code before changing it.
- Prefer minimal, reversible changes.
- Do not create duplicate subsystems when an existing mechanism can be extended.
- Add tests at the same abstraction level as the change.
- Reproduce bugs before claiming to fix them whenever practical.
- Never report a command, build, test, benchmark, or deployment as successful unless it was actually executed and its result observed.
- Keep experimental work isolated until evidence supports integration.

## Autonomy and escalation

The assistant may autonomously research, create issues, create branches, write code/docs/tests, commit changes, open PRs, revise plans, and close tasks when acceptance criteria are satisfied.

Escalate to the human only when at least one of these is true:

- an irreversible or externally consequential action requires judgment;
- secrets, payment, identity, legal acceptance, or privileged access are required;
- two materially different product directions remain equally viable and the choice changes the mission;
- the task cannot progress with available tools or information;
- the requested action would violate safety, policy, law, or repository constraints.

Ordinary uncertainty is not a reason to stop: investigate, test, choose the best-supported option, and record the reasoning.

## State discipline

`state/CURRENT.md` is the cross-run handoff. Keep it short, factual, and current. It must contain:

- active objective;
- active issue/branch/PR;
- last completed step;
- evidence produced;
- known failures/blockers;
- exact next action;
- backlog changes.

Do not use chat history as the only memory of important work.
