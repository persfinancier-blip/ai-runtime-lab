# Current Lab State

Last updated: 2026-08-18

## Active objective

Bootstrap is complete. The next execution should empirically baseline the assistant's real execution surface and hard limits before autonomous research is allowed to expand.

## Active issue / branch / PR

- Completed: `#1 [LAB-001] Bootstrap durable autonomous operating loop`
- Merged PR: `#5 [LAB-001] Bootstrap durable autonomous operating loop`
- Next issue: `#2 [LAB-002] Baseline the assistant execution surface and hard limits`
- Active implementation branch: none yet

## Last completed step

PR #5 was patch-audited, corrected, squash-merged into `main`, and issue #1 was closed as completed.

## Evidence produced

- Merge commit: `077612e73a53be33ccdd181625dad0adc016e30b`.
- `AGENTS.md` defines the autonomous operating contract.
- `prompts/SELF_RESUME.md` defines the recurring startup/resume instruction.
- `docs/OPERATING_MODEL.md` defines task, research, testing, and audit discipline.
- GitHub Issues #2–#4 are the seeded backlog.
- The repository explicitly forbids assuming GitHub workers/Actions/Codex workers execute the lab's work.

## Known blockers / constraints

- The executing assistant must perform the actual research, code, tests, debugging, audits, and GitHub updates itself.
- Repository state does not self-execute. A separate scheduled ChatGPT task/invocation must trigger each run.
- Scheduler recurrence behavior and cross-run tool/connector availability still require empirical validation in LAB-002/LAB-003.

## Exact next action

When autonomous execution is enabled, invoke the semantics of `prompts/SELF_RESUME.md`. The first selected task should be issue #2. Do not begin the open-ended agenda in #4 until #2 and the resumability experiment #3 are complete.

## Backlog

- #2 — baseline execution surface and hard limits — READY
- #3 — prove cross-run resumability — READY, depends on #2 where practical
- #4 — build/refine autonomous research agenda — READY, gated by #2 and #3
