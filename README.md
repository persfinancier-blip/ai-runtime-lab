# ai-runtime-lab

A durable autonomous research and engineering laboratory.

## What this repository is

GitHub is the lab's **control plane and memory**, not its execution worker. The executing assistant performs research, coding, testing, debugging, audits, documentation, and GitHub updates itself using the tools available in each run.

The lab is designed to survive chat/session boundaries.

## Start here

1. Read [`AGENTS.md`](AGENTS.md) — operating contract and autonomy rules.
2. Read [`state/CURRENT.md`](state/CURRENT.md) — exact cross-run handoff.
3. Inspect open Issues and active PRs.
4. Use [`prompts/SELF_RESUME.md`](prompts/SELF_RESUME.md) as the recurring startup instruction.
5. Execute work now; do not delegate it to GitHub Actions/workers.

## Durable structure

- `AGENTS.md` — constitution of the lab.
- `state/CURRENT.md` — current objective and exact next action.
- `prompts/SELF_RESUME.md` — startup/resume prompt for each invocation.
- `docs/OPERATING_MODEL.md` — control-plane, task, testing, and audit conventions.
- `research/` — source-grounded research evidence and experiments.
- `decisions/` — ADR-style durable decisions.
- GitHub Issues — authoritative backlog/task queue.
- Branches/PRs — isolated, reviewable changes.

## Execution constraint

Do not assume GitHub workers, Actions, Codex workers, or other repository-side agents will execute tasks. If code or research is required, the assistant running the current invocation must perform it directly and record what actually happened.
