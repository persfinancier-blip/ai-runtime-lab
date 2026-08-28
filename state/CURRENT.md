# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- PR #165 remains draft; live `strict_fence.py` blob is `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, published by executable commit `05d8e75a636818afcb32e085d464c9fa9171dea5` for the alternate-UNIQUE thaw hardening. Branch HEAD is newer because of research/state commits.
- Historical hidden-rowid candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` is **not** the current publication target anymore: it was built and tested on older predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` before `eb219835...` was published.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; use only as fallback while LAB-086 exact work is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs/issues and resumed LAB-086 first.

Reconciled a stale durable handoff against live PR #165. The PR/Issue state shows the independent alternate-UNIQUE thaw fix has already been published byte-exact, with live runtime blob `eb219835...`. Fresh source inspection of live `strict_fence.py` confirms the hidden-rowid mechanism is still absent: provider-receipt trigger enumeration has no rowid sentinel, thaw collision trigger enumeration has no rowid sentinel, and thaw insert collision guards do not contain the hidden-rowid checks from the durable patch.

The exact hidden-rowid RED→GREEN note proves historical candidate `b78e7c98...` was constructed from older predecessor `d4a6a40f...`. It must therefore not be published over the newer `eb219835...` runtime, because that could discard the already-published alternate-UNIQUE hardening.

Recorded the reconciliation and rebase requirement in `research/2026-08-28-lab086-hidden-rowid-candidate-rebase-required.md`, commit `365c5de5c521ae47ad9dd378a2160f8ce7cde291`, and Issue #163 comment `5451854392`.

A fresh direct-network probe from the local executor still failed DNS resolution for `raw.githubusercontent.com`, so no claim is made that exact local execution is available in this run.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous strict/thaw exact subgate evidence retained from earlier executable pins.
- Alternate-UNIQUE fix: predecessor RED, candidate `eb219835...` GREEN 1/1 + `py_compile`; published byte-exact at executable commit `05d8e75a...`.
- Hidden-rowid historical RED→GREEN: predecessor `d4a6a40f...` RED 3/3, historical candidate `b78e7c98...` GREEN 3/3 + compileall. This remains mechanism evidence only, not a publishable current candidate.
- Durable hidden-rowid patch remains `research/2026-08-28-lab086-hidden-rowid-replace.patch` blob `61841b58...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain gate and previously recorded focused evidence remain retained; PR #173 stays draft pending exact real-stack execution.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current task is no longer “publish `b78e7c98...`”. The hidden-rowid patch must first be **rebased onto exact live predecessor `eb219835...`**, producing a new candidate blob and new execution evidence.
- Direct shell/raw GitHub transport is unavailable in this executor in the current run (DNS failure observed for `raw.githubusercontent.com`).
- The GitHub Contents writer accepts complete replacement UTF-8 text; publication is allowed only after exact tested candidate bytes are known and can be transferred without weakening byte-identity discipline.
- PR #165 must remain draft until rebased hidden-rowid GREEN evidence, complete strict/thaw gate, full LAB-080→086 real-ledger gate, unsafe seed, compileall and final audit are clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: reconstruct exact live `strict_fence.py` predecessor `eb2198354d222ad0ad6b7d751bf5c649157b6b36` in an execution-capable path, apply the durable hidden-rowid patch semantics, and compute the **new** candidate Git blob.
2. Execute unchanged `test_thaw_rowid_collision_regression.py`: require live predecessor RED and rebased candidate GREEN. Execute unchanged alternate-UNIQUE regression on the rebased candidate and require it stays GREEN. Run the complete strict/thaw conflict subgate plus compileall.
3. Publish only the exact tested rebased bytes through a supported byte-preserving path, require GitHub to return the newly recorded candidate blob, re-fetch/hash-verify it, then repin the executable snapshot.
4. Resume the complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
5. If exact LAB-086 reconstruction/execution remains concretely tool-limited, resume LAB-091 real-stack regressions as fallback without claiming LAB-086 progress that was not executed.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE fix is published; hidden-rowid mechanism must be rebased and re-executed on live predecessor `eb219835...` before publication.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 exact execution is tool-limited.
