# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Exact live `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs and resumed LAB-086 first.

Fresh GitHub connector inspection established a stronger byte-source fact: because `strict_fence.py` is still an addition relative to `main`, PR #165's per-file patch returns the complete current 949-line file as one `@@ -0,0 +1,949 @@` addition. This is the complete current source payload, not a partial diff. Inspection confirms the live source already has provider-receipt NULL rejection and alternate `(provider_id,generation)` collision protection, and still lacks hidden-rowid hardening.

A fresh direct clone probe in the execution container failed before transfer with `Could not resolve host: github.com`. Therefore exact source availability is no longer the blocker; the remaining runtime blocker is a supported byte-preserving connector-response -> executable-filesystem bridge. Manual transcription of 949 security-critical lines remains disallowed.

Durable note: `research/2026-08-28-lab086-pr-patch-byte-source.md`, main commit `827ffdb4444cace13fba9ef9b939ae9f1c8a9c7c`. Issue #163 comment `5453661676` records the same result.

No new unittest PASS is claimed in this run.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE focused RED→GREEN evidence remains valid; exact current source inspection proves the semantic guard is present in live `d4a6a40f...`.
- Provider-receipt NULL-identity guard is present in live `d4a6a40f...`.
- Hidden-rowid historical RED→GREEN evidence remains mechanism evidence only; durable patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch` blob `61841b58...`.
- PR #165's complete per-file patch is now an exact current source carrier for the 949-line runtime.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 evidence remains retained; PR #173 stays draft pending exact real-stack execution.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor; fresh `git clone` fails DNS resolution.
- The GitHub connector can return the complete current file but this run cannot byte-preservingly pipe that response into the execution filesystem.
- Publication through Contents API is allowed only after exact candidate bytes are materialized and actually tested; do not hand-rewrite the security-critical runtime.
- PR #165 must remain draft until rowid candidate exact testing/publication, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: materialize PR #165's complete `strict_fence.py` per-file patch payload into an execution filesystem through a supported byte-preserving bridge; strip only patch framing/prefix and require reconstructed Git blob == `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` before editing.
2. Apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`; compute and record the new candidate Git blob.
3. Execute unchanged focused regressions: `test_provider_receipt_null_identity_regression.py`, `test_thaw_alternate_unique_collision_regression.py`, `test_thaw_rowid_collision_regression.py`; require GREEN for all, then full strict/thaw conflict subgate + compileall.
4. Publish only exact tested bytes through a supported path; require GitHub returned blob == tested candidate, then re-fetch/hash-verify and repin executable snapshot.
5. Resume complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
6. If exact LAB-086 execution remains concretely tool-limited, resume LAB-091 real-stack regressions as fallback without claiming execution that did not occur.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; complete current source is available through PR patch; remaining blocker is byte-preserving connector→executor materialization, then rowid-only hardening + exact regression gate.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 exact execution is tool-limited.
