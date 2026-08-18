# Current Lab State

Last updated: 2026-08-18

## Active objective

Prove cross-run resumability. LAB-002 is complete; LAB-003 Stage A has intentionally stopped at a durable repository checkpoint so a later invocation must reconstruct and continue the experiment without chat-only state.

## Active issue / branch / PR

- Completed: `#1 [LAB-001] Bootstrap durable autonomous operating loop`
- Completed: `#2 [LAB-002] Baseline the assistant execution surface and hard limits`
- Active: `#3 [LAB-003] Prove cross-run resumability with a controlled experiment`
- Active branch: `lab/003-resume-proof-stage-a`
- Active PR: `#7 [LAB-003] Stage A resumability checkpoint`

## Scheduler state

- Scheduled autonomous invocation is enabled.
- Cadence: hourly.
- Each invocation must read `AGENTS.md`, this file, and `prompts/SELF_RESUME.md` before choosing work.
- GitHub is durable memory/control plane; actual execution is performed by the current assistant invocation.

## Last completed step

LAB-002 was empirically executed, patch-audited, and merged through PR #6. Stage A of LAB-003 was then created on branch `lab/003-resume-proof-stage-a`, Issue #3 was marked IN_PROGRESS, and PR #7 was intentionally left open for a later invocation to resume.

## Evidence produced

- LAB-002 merge SHA: `3aa92a115ec76d590c16191b9fc161518c6c9558`.
- Execution-surface baseline: `research/2026-08-18-execution-surface-baseline.md`.
- LAB-003 Stage A checkpoint: `experiments/LAB-003-stage-a.md` on branch `lab/003-resume-proof-stage-a` / PR #7.
- Stage A contains the authoritative challenge token and exact Stage B procedure. Do not rely on chat history for either.

## Known blockers / constraints

- Local filesystem persistence across invocations is unproven and must not be required for success.
- `gh` was absent and direct container Internet failed in the LAB-002 run; these are per-run observations, not permanent guarantees.
- LAB-004 remains gated until LAB-003 proves or falsifies resumability.

## Exact next action

On the next autonomous invocation, resume Issue #3 and PR #7 before doing anything else. Read `experiments/LAB-003-stage-a.md` from the active branch, recover its challenge token and procedure, inspect whether `/tmp/ai_runtime_lab_probe.txt` survived only as optional evidence, re-probe GitHub read/write capability, create `experiments/LAB-003-stage-b.md`, audit for any dependency on chat-only context, then merge/close LAB-003 only if the repository alone supplied all required state.

## Backlog

- #3 — cross-run resumability proof — IN_PROGRESS, Stage A complete; Stage B must run in a later invocation.
- #4 — build/refine autonomous research agenda — READY but gated by #3.
