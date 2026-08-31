# LAB-090 PR #175 mergeability reconciliation — 2026-08-31

## Question

`state/CURRENT.md` recorded PR #175 as `mergeable=false`. Determine whether this is a real source conflict that blocks LAB-090 integration or a transient/stale GitHub mergeability observation.

## Observations

- PR #175 head: `ae3a3cf089f7436ea74548ef9fa6cc5242e276e8` on `lab-090-provider-activation-fencing`.
- Merge base with `main`: `6cc7a04496187075db1c02f3e27c1d394da53026`.
- Comparing PR head -> main: main is 51 commits ahead / 39 behind and the files changed on the main side after the merge base are research notes plus `state/CURRENT.md`; no LAB-090 source/test path appears on that side.
- Comparing main -> PR head: the branch changes are the LAB-090 source/test paths (`experiments/provider_generation_history/*`, one shared-anchor protocol change) and do not include `state/CURRENT.md` or the research files added on main after the merge base.
- A direct GitHub REST pull-request fetch currently reports `mergeable=true`, `rebaseable=true`, `mergeable_state="clean"`.
- The higher-level PR metadata call observed `mergeable=false` immediately before that REST fetch. Treat that result as a stale/transient mergeability computation, not as evidence of a source conflict.

## Execution capability probe

A fresh direct transport probe was executed:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
```

Therefore exact published-head repository execution remains unavailable in this runtime. No whole-branch behavioral PASS is claimed.

## Decision

- Remove `mergeable=false` as an active LAB-090 blocker.
- Keep PR #175 draft because its exact published-head behavioral/integration/downstream gates still have not executed.
- Do not merge or apply its large multi-file delta through Contents API as a fallback: the change is not a small already-audited file-scoped integration and behavioral evidence is incomplete.
- LAB-086 remains priority #1 and remains constrained by its byte-preserving exact-composition contract.

## Next gate

When exact source execution becomes available, execute the published PR #175 head focused restart/tamper regressions, activation integration/restart suite, then downstream LAB-080/082/083/084/085/086 compatibility gates. If execution remains unavailable, continue only narrow byte-verifiable LAB-090 audits/fixes and keep the PR draft.
