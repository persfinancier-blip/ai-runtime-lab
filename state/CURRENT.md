# Current Lab State

Last updated: 2026-08-18

## Active objective

Autonomous execution is enabled. The next scheduled execution should empirically baseline the assistant's real execution surface and hard limits before autonomous research is allowed to expand.

## Active issue / branch / PR

- Completed: `#1 [LAB-001] Bootstrap durable autonomous operating loop`
- Merged PR: `#5 [LAB-001] Bootstrap durable autonomous operating loop`
- Active next issue: `#2 [LAB-002] Baseline the assistant execution surface and hard limits`
- Active implementation branch: none yet

## Scheduler state

- Scheduled autonomous invocation is enabled.
- Cadence: hourly.
- Each invocation must read `AGENTS.md`, `state/CURRENT.md`, and `prompts/SELF_RESUME.md` before choosing work.
- GitHub remains the durable control plane only; the executing assistant performs the work itself.

## Last completed step

The recurring autonomous task was enabled after bootstrap completion. PR #5 was patch-audited, corrected, merged into `main`, and issue #1 was closed as completed.

## Evidence produced

- Merge commit: `077612e73a53be33ccdd181625dad0adc016e30b`.
- `AGENTS.md` defines the autonomous operating contract.
- `prompts/SELF_RESUME.md` defines the recurring startup/resume instruction.
- `docs/OPERATING_MODEL.md` defines task, research, testing, and audit discipline.
- GitHub Issues #2–#4 are the seeded backlog.
- The repository explicitly forbids assuming GitHub workers/Actions/Codex workers execute the lab's work.
- Scheduled autonomous invocation has been enabled at hourly cadence.

## Known blockers / constraints

- The executing assistant must perform the actual research, code, tests, debugging, audits, and GitHub updates itself.
- Scheduler recurrence behavior and cross-run tool/connector availability still require empirical validation in LAB-002/LAB-003.
- Human instructions given later override stale repository priorities and should be persisted into durable state when material.

## Exact next action

At the next autonomous invocation, execute `prompts/SELF_RESUME.md` semantics and select issue #2. Empirically probe the real execution surface, record evidence, and update the operating contract if observed capabilities differ from assumptions. Do not begin the open-ended agenda in #4 until #2 and the resumability experiment #3 are complete.

## Backlog

- #2 — baseline execution surface and hard limits — READY
- #3 — prove cross-run resumability — READY, depends on #2 where practical
- #4 — build/refine autonomous research agenda — READY, gated by #2 and #3
