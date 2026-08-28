# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Fresh PR #165 HEAD before the latest research-note commit: `abafb3aabe0276b4a73def343a311b459c818dc8`; research-note commit added after inspection: `e46e4ec2226310201cb4114bdbe024428235b65f`.
- Exact live `strict_fence.py` inspected this run is blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs and resumed LAB-086 first.

Fresh exact source inspection corrected another lineage inference. Although current `strict_fence.py` blob `d4a6a40f...` differs from historical alternate-UNIQUE GREEN blob `eb219835...`, the live source **already contains** the alternate `(provider_id,generation)` semantic collision guard in `_install_thaw_insert_history_collision_fences_locked`. It also contains provider-receipt NULL identity rejection (`NEW.request_id IS NULL`). Direct search of the exact live source finds no `rowid` guard.

Therefore the previous handoff statement that live `d4a6a40f...` had lost alternate-UNIQUE protection is retracted. Blob inequality did not imply semantic regression. A compare from historical executable commit `05d8e75a...` to current HEAD shows only 7 additions / 3 deletions in `strict_fence.py` among later work.

Durable correction note: `research/2026-08-28-lab086-live-guard-presence-correction.md`, commit `e46e4ec2226310201cb4114bdbe024428235b65f`. Issue #163 comment `5453013883` records the same correction.

No new unittest PASS is claimed: this runtime can read exact GitHub source/PR patches but still lacks an execution-capable byte-preserving checkout of the complete dependency closure.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE focused RED→GREEN evidence remains valid for historical executable candidate `eb219835...`; exact current source inspection proves the semantic collision guard is also present in live `d4a6a40f...`.
- Provider-receipt NULL-identity guard is present in live `d4a6a40f...`.
- Hidden-rowid historical RED→GREEN evidence remains mechanism evidence only; durable patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch` blob `61841b58...`.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 evidence remains retained; PR #173 stays draft pending exact real-stack execution.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is now narrowed to hidden-rowid hardening. Do **not** reapply a separate alternate-UNIQUE patch or reconstruct from historical `eb219835...`; preserve the already-live alternate semantic guard and provider-receipt NULL guard.
- Direct shell/raw GitHub transport remains unavailable in this executor; GitHub connector reads are available.
- Publication through Contents API is allowed only after exact candidate bytes are reconstructed and actually tested; do not hand-rewrite the ~949-line security-critical runtime without byte identity.
- PR #165 must remain draft until the rowid candidate is exact-tested/published, the complete strict/thaw gate and LAB-080→086 real-ledger gate are clean, unsafe seed and compileall pass, and final security/reconciliation audit is clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain an execution-capable byte-preserving reconstruction of exact current `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` plus the focused test dependency closure.
2. Apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`; verify the candidate preserves all three protections: provider-receipt NULL rejection, alternate `(provider_id,generation)` collision rejection, and new hidden-rowid collision/sentinel guards. Compute and record the new Git blob.
3. Execute unchanged focused regressions: `test_provider_receipt_null_identity_regression.py`, `test_thaw_alternate_unique_collision_regression.py`, `test_thaw_rowid_collision_regression.py`; require candidate GREEN for all. Then run the full strict/thaw conflict subgate + compileall.
4. Publish only exact tested bytes through a supported byte-preserving path; require GitHub returned blob == recorded candidate blob, re-fetch/hash-verify, and repin the executable snapshot.
5. Resume the complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
6. If exact LAB-086 execution remains concretely tool-limited, resume LAB-091 real-stack regressions as fallback without claiming execution that did not occur.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current source guard presence corrected; next delta is rowid-only hardening + exact regression gate.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 exact execution is tool-limited.
