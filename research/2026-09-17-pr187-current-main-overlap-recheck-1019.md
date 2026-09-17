# PR #187 current-main overlap recheck — 2026-09-17 10:19 Europe/Moscow

## LAB-086 first probe

The required direct executable transport probe was attempted first in this run:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

Observed result: exit 128 before repository code execution, `Could not resolve host: github.com`.

Therefore the authoritative LAB-086 executable pin cannot be byte-exact materialized through shell Git transport in this runtime and no LAB-086 executable PASS/GREEN is claimed.

## Control-plane observations

- Actual main tip before this evidence write: `db2f55ad9ab59c551e738a2ef74fb244d1424ccc`.
- PR #187 remains open and draft.
- PR #187 head remains `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.
- GitHub currently reports `mergeable=false`; this metadata is not treated as source-conflict proof.
- Inline review-thread query returned no threads.
- Open issues still retain LAB-086/#163 as IN_PROGRESS priority work; LAB-094/#179, LAB-095/#180, LAB-096/#181 and LAB-101/#188 remain the composed closure set around PR #187.

## Fresh overlap check

Compare from PR #187 reported base snapshot `2c72b76b2f1ffbee520e3871d4f1e0e878fe7974` to actual main `db2f55ad9ab59c551e738a2ef74fb244d1424ccc` reports:

- status: ahead;
- main ahead by 183 commits;
- main behind by 0;
- returned changed paths are research records plus `state/CURRENT.md` only.

No `experiments/*` or `tests/*` path appears in the returned main drift, so there is no newly observed source/test overlap requiring mutation, rebase, or merge of PR #187. No new review defect was observed either.

## Decision

Keep PR #187 draft and unchanged. Do not rebase/merge merely to refresh GitHub mergeability metadata. Preserve LAB-086 as the first executable probe next run. If byte-exact materialization becomes available, verify retained blob/hash identity first, execute the closure inventory in `research/2026-09-16-lab094-096-closure-inventory.md`, then full pytest and compileall. Do not infer executable GREEN from this source/control-plane audit.
