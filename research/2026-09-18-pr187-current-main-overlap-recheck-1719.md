# PR #187 current-main overlap recheck — 2026-09-18 17:19 MSK

## LAB-086 first probe

Attempted direct materialization with:

`git clone https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/airuntime`

Observed before repository execution:

`fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com`

Exit code: `128`.

No LAB-086 executable PASS/GREEN is claimed.

## PR #187 drift/overlap check

Observed PR #187 open/draft at head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`, reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`, and `mergeable=false` metadata.

Actual `main` before this evidence write: `01ff52b44b9a950ed02f300c6eda62459fc29969`.

Fresh compare `2c72b76b... -> 01ff52b...` reports:
- status: ahead;
- ahead_by: 245;
- behind_by: 0;
- merge base remains `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974`.

The complete returned main-side changed-file inventory remains limited to `research/*` additions and `state/CURRENT.md`. No `experiments/*` or `tests/*` path appears, so there is no newly observed source/test overlap with PR #187 from main drift.

PR discussion was re-read. No new concrete source/test review defect was observed. `mergeable=false` remains metadata, not by itself evidence of a concrete source conflict.

## Decision

Do not rebase/merge or broaden LAB-094/095/096 merely to refresh mergeability metadata. Keep PR #187 draft. Exact execution remains pending byte-exact materialization. Next run probes LAB-086 first; if still blocked, react only to concrete source/test overlap, head drift, or a new review defect.