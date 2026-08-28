# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Exact PR #165 HEAD observed this run before the new research-note commit: `365c5de5c521ae47ad9dd378a2160f8ce7cde291`.
- **Live `strict_fence.py` at that exact HEAD is blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, not `eb219835...`.**
- Exact commit `05d8e75a636818afcb32e085d464c9fa9171dea5` does contain prior alternate-UNIQUE GREEN blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, but later branch work changed the runtime back to `d4a6a40f...`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs/issues and resumed LAB-086 first.

Fresh exact GitHub reads found a material lineage error in the durable handoff and Issue wording. `strict_fence.py` at PR #165 HEAD is `d4a6a40f...`; at historical executable commit `05d8e75a...` it is `eb219835...`. A direct compare confirms `05d8e75a...` is an ancestor of HEAD. Earlier state commit `c180fc2b...` explicitly recorded a later provider-receipt NULL-identity publication whose runtime blob was again `d4a6a40f...`, so the live branch really regressed away from the alternate-UNIQUE candidate; this is not a stale connector view.

Also corrected the previous rebase conclusion: durable `research/2026-08-28-lab086-hidden-rowid-replace.patch` already contains the alternate-UNIQUE semantic collision guard for `asymmetric_provider_generations` (`provider_id IS NEW.provider_id AND generation IS NEW.generation`) in addition to hidden-rowid collision/sentinel logic. Therefore a combined candidate constructed from exact current `d4a6a40f...` can preserve/restore alternate-UNIQUE protection; applying two independent patches blindly is unnecessary and risks composition mistakes.

Durable correction note was committed on PR #165 branch as `research/2026-08-28-lab086-live-blob-lineage-correction.md`, commit `abafb3aabe0276b4a73def343a311b459c818dc8`; Issue #163 comment `5452447274` records the same correction.

A fresh local `git clone` probe still failed DNS resolution for `github.com`, so no new exact combined-candidate unittest PASS is claimed in this run.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Prior strict/thaw exact subgate evidence retained from earlier executable pins.
- Alternate-UNIQUE focused RED→GREEN evidence remains valid for historical candidate `eb219835...`; **it is no longer live on current PR HEAD**.
- Provider-receipt NULL-identity hardening is present in current `d4a6a40f...` according to the later publication record/source lineage.
- Hidden-rowid historical RED→GREEN evidence remains mechanism evidence only; durable combined patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch` blob `61841b58...`, and that patch already includes alternate-UNIQUE semantic-collision logic.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 adoption-state/domain evidence remains retained; PR #173 stays draft pending exact real-stack execution.

## Known blockers / constraints

- LAB-086 remains first priority.
- Current PR HEAD has a **live alternate-UNIQUE regression** relative to historical executable `eb219835...`; do not describe that fix as currently published/live until a new combined candidate is published and re-fetched.
- The next candidate must start from exact current `d4a6a40f...` and compose provider-receipt NULL identity + alternate-UNIQUE + hidden-rowid protections together.
- Direct shell/raw GitHub transport remains unavailable in this executor (fresh `git clone` failed DNS resolution).
- The GitHub Contents writer accepts complete replacement UTF-8 text; publication is allowed only after exact tested candidate bytes are known and can be transferred without weakening byte-identity discipline.
- PR #165 must remain draft until the combined candidate is exact-tested/published, the complete strict/thaw gate and LAB-080→086 real-ledger gate are clean, unsafe seed and compileall pass, and final security/reconciliation audit is clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: reconstruct/hash-verify exact current `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` in an execution-capable path.
2. Apply the durable **combined** hidden-rowid patch semantics once; verify the resulting source contains all three required protections: provider-receipt NULL rejection, alternate `(provider_id,generation)` collision rejection, and hidden-rowid collision/sentinel guards. Compute the new Git blob.
3. Execute unchanged focused regressions against exact predecessor/candidate as applicable: `test_provider_receipt_null_identity_regression.py`, `test_thaw_alternate_unique_collision_regression.py`, `test_thaw_rowid_collision_regression.py`; require candidate GREEN for all. Then run the full strict/thaw conflict subgate + compileall.
4. Publish only exact tested combined bytes through a supported byte-preserving path; require GitHub returned blob == recorded candidate blob, re-fetch/hash-verify, and repin the executable snapshot.
5. Resume the complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
6. If exact LAB-086 reconstruction/execution remains concretely tool-limited, resume LAB-091 real-stack regressions as fallback without claiming LAB-086 execution that did not occur.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; live lineage corrected; current HEAD is `d4a6a40f...` and has lost historical alternate-UNIQUE guard; next step is one exact combined candidate + regression gate.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 exact execution is tool-limited.
