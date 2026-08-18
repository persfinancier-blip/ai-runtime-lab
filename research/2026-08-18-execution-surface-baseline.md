# Execution Surface Baseline

Date: 2026-08-18
Issue: #2
Branch: `lab/002-execution-surface`

## Question

What can the executing assistant actually do in the current ChatGPT scheduled-task runtime, and what must the lab not assume?

## Method

Only capabilities that were directly probed in this run are marked **observed**. Product limits sourced from current official OpenAI documentation are marked **documented**. Everything else is explicitly left unproven.

## Capability matrix

| Surface | Status | Evidence observed in this run | Safe operating rule |
|---|---|---|---|
| GitHub repository read | OBSERVED | Read `AGENTS.md`, `state/CURRENT.md`, and `prompts/SELF_RESUME.md` from `main` via the connected GitHub app. | Use the GitHub connector as the primary durable read path. |
| GitHub issue/PR discovery | OBSERVED | Enumerated open Issues #2-#4 and confirmed no open PRs. | Reconstruct work state from issues/PRs every run. |
| GitHub branch creation | OBSERVED | Created `lab/002-execution-surface` from `main`. | Use task branches for material changes. |
| GitHub issue mutation | OBSERVED | Updated Issue #2 from READY to IN_PROGRESS and recorded the active branch. | Issue state can be treated as durable queue metadata after successful response. |
| GitHub repository write | OBSERVED | This research note is being created through the GitHub contents API connector. | Prefer connector writes over assuming local git credentials. Read back important writes when correctness matters. |
| Local code execution | OBSERVED | Container executed Python 3.13.5, created/read a temp file, and computed its SHA-256. `git version 2.47.3` is installed. | Local runtime is useful for computation, transforms, tests, and temporary artifacts. |
| Local GitHub CLI | OBSERVED ABSENT | `gh` command returned `command not found`. | Do not design the lab around `gh`; use the GitHub connector unless a later runtime proves otherwise. |
| Direct network from local container | OBSERVED UNAVAILABLE | Python `urllib.request` to `https://api.github.com` failed with DNS resolution error. | Do not assume shell/Python code has Internet access. Use the dedicated web/GitHub/app tools for networked work. |
| Web research | OBSERVED | Dedicated web search retrieved current official OpenAI Scheduled Tasks documentation and release notes. | Use web tooling for public Internet research, preferring primary sources. |
| Conversation/Library Files tooling | OBSERVED | `files.list` executed successfully; current conversation had zero attached files. | Files tooling is available when files exist; absence of a file is not a tooling failure. |
| Scheduler/task inspection | OBSERVED | Scheduler state was inspected; `AI Runtime Lab` is enabled with hourly recurrence. | Scheduler can trigger later runs, but repo state remains the handoff source. |
| Connected apps beyond GitHub/files | DISCOVERABLE, NOT VALIDATED | Runtime exposes app connectors, but no mailbox/calendar/private-data read was performed for this task. | Do not claim a connector works for autonomous runs until probed for the exact operation needed. Avoid irrelevant private-data access as a capability test. |
| Cross-run persistence of local container | UNPROVEN | No later-run experiment has yet tested `/tmp` or local filesystem persistence. | Treat local filesystem as ephemeral. Persist important state to GitHub. |
| Cross-run availability of every connector | UNPROVEN | This is the first controlled execution-surface run. | LAB-003 must validate actual cross-run reconstruction and required connector availability. |

## Scheduler facts from current official OpenAI documentation

Current OpenAI documentation states that Scheduled Tasks:

- can run while the user is offline;
- support one-off and recurring runs;
- cannot run more frequently than once per hour;
- may automatically pause after a period of unattended inactivity;
- have plan-dependent active-task limits;
- can use supported connected apps subject to account/workspace permissions;
- do not currently support webhooks;
- may lose access to project files when a task is created inside a project with files, so project-local files must not be assumed as scheduler state.

Primary sources retrieved 2026-08-18:

- OpenAI Help Center, `Scheduled Tasks in ChatGPT`: https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt
- OpenAI Help Center, ChatGPT Release Notes, 2026-06-17 Scheduled Tasks update: https://help.openai.com/en/articles/6825453-chatgpt-release-notes

## Hard limits and unsafe assumptions

1. **No continuous process.** The scheduler invokes discrete runs; it is not a continuously resident agent process.
2. **Hourly floor.** The lab cannot schedule runs more frequently than once per hour through ChatGPT Scheduled Tasks.
3. **Possible unattended pause.** A durable lab must tolerate the scheduler being paused after inactivity and must be recoverable by a later manual or scheduled invocation.
4. **No shell Internet assumption.** Local Python/shell execution in this run could not resolve external hosts. Network research must use dedicated tools.
5. **No `gh` assumption.** GitHub CLI is absent in this runtime. Repository workflows must remain connector-first.
6. **No local-disk memory assumption.** Container filesystem persistence across invocations is not established. GitHub is the durable memory boundary.
7. **No universal connector assumption.** Availability and permissions can differ across runs, plans, workspaces, or apps. Probe the exact operation before depending on it.
8. **No background execution claim.** A run must never say code/tests/research occurred unless the executing assistant directly observed the operation's result.
9. **No project-file dependency for scheduled execution.** Product documentation warns that scheduled tasks created in projects with files cannot access those project files. Repository state is therefore a stronger handoff mechanism for this lab.
10. **Run-duration ceiling is not empirically established here.** Do not invent a maximum. Work should be checkpointed in bounded slices so forced termination is survivable.

## Recommended execution pattern

Use a three-plane model:

1. **Durable control plane — GitHub**
   - issues = work queue;
   - branches/PRs = isolated changes;
   - `state/CURRENT.md` = exact handoff;
   - `research/` and `decisions/` = evidence and durable reasoning.

2. **Execution plane — current assistant runtime**
   - local container for computation/tests/temp artifacts;
   - dedicated web tool for Internet research;
   - connected GitHub/app/file tools for authenticated external operations.

3. **Trigger plane — Scheduled Tasks/manual invocation**
   - starts discrete runs;
   - is not trusted as memory;
   - failure/pause must be recoverable from GitHub alone.

## Fallback rules

- If local Internet fails: use dedicated web/app connectors.
- If `gh` is absent: use the GitHub connector.
- If a connector write is unavailable: preserve the intended patch/result locally in the run, record the blocker in any still-writable durable surface, and do not claim completion.
- If a task is too large for one invocation: stop only at a coherent checkpoint, persist exact next action, then resume next run.
- If scheduled execution pauses: a manual run using the same self-resume prompt must reconstruct the lab from GitHub.

## Audit of existing lab contract

The current `AGENTS.md` and `prompts/SELF_RESUME.md` already match the observed model in the most important respects: GitHub is the durable control plane; the executing assistant performs work directly; commands/tests must not be fabricated; and durable state must be written before a run ends.

One useful clarification is warranted: explicitly treat local filesystem and connector availability as per-run capabilities rather than stable guarantees. That change should be made before LAB-002 is closed.

## Confidence and remaining unknowns

High confidence:
- GitHub connector read/write branch/issue/file operations work in this run.
- local Python and git binary are available.
- `gh` is absent.
- direct container Internet is unavailable in this run.
- dedicated web research works.
- scheduler exists and is enabled hourly.

Still unproven:
- cross-run local filesystem persistence;
- cross-run availability of all tools/connectors;
- exact maximum execution duration per scheduled invocation;
- behavior when a scheduled run is forcibly interrupted mid-write;
- automatic recovery after unattended scheduler pause.

These unknowns are intentionally deferred to LAB-003 or later targeted probes rather than guessed.