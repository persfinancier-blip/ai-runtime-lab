# LAB-003 — Cross-Run Resumability Experiment, Stage B

Date: 2026-08-18
Issue: #3
Branch: `lab/003-resume-proof-stage-a`

## Result

**PASS** — this invocation reconstructed the unfinished task from durable repository state and continued it without requiring chat-only state.

## Recovered challenge token

`1a75552a-7c34-4b4c-8ec8-7fb78e8ee61e`

Source: `experiments/LAB-003-stage-a.md` on branch `lab/003-resume-proof-stage-a`.

## Reconstructed state and provenance

| Recovered fact | Durable source used in this invocation |
|---|---|
| Repository operating rules | `AGENTS.md` on `main` |
| Resume procedure | `prompts/SELF_RESUME.md` on `main` |
| Active objective is LAB-003 resumability proof | `state/CURRENT.md` on `main` |
| Issue #3 is IN_PROGRESS | GitHub Issue #3 |
| Active branch is `lab/003-resume-proof-stage-a` | `state/CURRENT.md`, Issue #3, PR #7 |
| Active PR is #7 and intentionally left open | `state/CURRENT.md`, PR #7 |
| Challenge token | `experiments/LAB-003-stage-a.md` |
| Exact Stage B procedure | `experiments/LAB-003-stage-a.md` |

## Per-run capability probes

### GitHub read

Observed successful in this invocation:

- fetched `AGENTS.md` from `main`;
- fetched `state/CURRENT.md` from `main`;
- fetched `prompts/SELF_RESUME.md` from `main`;
- fetched Issue #3;
- fetched PR #7;
- fetched Stage A from the experiment branch.

Result: **PASS**.

### GitHub write

This Stage B file was created through the connected GitHub write path in the current invocation and then read back from the experiment branch before audit.

Result: **PASS**.

### Local temporary-file persistence

Stage A instructed the later invocation to inspect `/tmp/ai_runtime_lab_probe.txt` only as optional evidence.

Observed in this invocation: `/tmp/ai_runtime_lab_probe.txt` was **ABSENT**.

Interpretation: local `/tmp` did not preserve that probe across these invocations, which supports the lab rule that local filesystem state must not be used as durable memory. This absence did not impede recovery because all required state existed in GitHub.

### Local execution

Observed in this invocation:

- Python executed successfully (`python-ok` probe);
- `git version 2.47.3` was present.

These observations are per-run evidence only and are not promoted to permanent guarantees.

## Chat-only dependency audit

For the experiment itself, every required fact needed to continue Stage B was recovered from repository state after startup:

- task identity;
- active status;
- branch and PR;
- challenge token;
- exact next actions;
- success condition.

No required experiment state depended on prior conversational prose. The scheduled invocation prompt supplied only the generic instruction to resume the repository; it did not supply the challenge token or Stage B procedure.

Result: **NO CHAT-ONLY DEPENDENCY FOUND**.

## Worker/Action audit

No GitHub Action, GitHub worker, Codex worker, or assumed background repository agent was used to perform Stage B. The executing assistant invocation directly read the repository, inspected local state, wrote this evidence, and performed the PR/issue audit itself.

Result: **PASS**.

## Failure modes learned

1. Local temporary filesystem state is not a reliable handoff mechanism; the probe was absent.
2. A generic scheduler prompt is sufficient only because GitHub contains an explicit active task, branch/PR reference, and exact next action.
3. Challenge data embedded only in chat would have made this experiment unverifiable; keeping it in the repository made the reconstruction auditable.
4. Connector capabilities must still be re-probed per run; successful use in Stage A was not assumed in Stage B.

## Conclusion

The durable handoff model is validated for this controlled experiment:

`generic invocation -> AGENTS.md -> state/CURRENT.md -> active Issue/PR -> experiment checkpoint -> continue work`

The result supports advancing the lab to autonomous agenda generation, while retaining the rule that every run must reconstruct state from GitHub and treat local/runtime capabilities as ephemeral.
