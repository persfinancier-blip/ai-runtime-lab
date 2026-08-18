# LAB-003 — Cross-Run Resumability Experiment, Stage A

Date: 2026-08-18
Issue: #3
Branch: `lab/003-resume-proof-stage-a`

## Purpose

Prove that a later assistant invocation can reconstruct unfinished work from repository state without relying on hidden chat continuity.

## Stage A checkpoint

Challenge token: `1a75552a-7c34-4b4c-8ec8-7fb78e8ee61e`

The next autonomous invocation must, using repository state as its authoritative source:

1. Read `AGENTS.md`, `state/CURRENT.md`, and `prompts/SELF_RESUME.md`.
2. Detect that Issue #3 is IN_PROGRESS.
3. Locate this Stage A experiment file and reproduce the challenge token exactly in the durable Stage B result.
4. Inspect whether the temporary local file `/tmp/ai_runtime_lab_probe.txt` from the prior run exists, but treat either outcome only as evidence about local-container persistence, never as required state.
5. Re-probe at least one required capability (GitHub read/write) rather than assuming it persists.
6. Create `experiments/LAB-003-stage-b.md` containing observed reconstruction evidence, including where each recovered fact came from.
7. Audit whether any step actually depended on chat-only context. If yes, mark the experiment failed and redesign the handoff.
8. Complete/merge the experiment only if the repository alone supplied all required task state.

## Success condition

Stage B must recover the exact token and the exact next action from durable repository state, continue the task, and leave evidence sufficient for an auditor to verify that no GitHub Action/worker performed the execution.

## Stop condition for this run

Do not execute Stage B in the same invocation. Stage A is intentionally a durable checkpoint. A later invocation must perform Stage B.
