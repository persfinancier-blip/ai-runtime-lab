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

Re-probed exact source transfer. The repository is public, but direct shell/Python raw-GitHub access still fails DNS. `container.download` was also tested as a possible byte-preserving path; it requires a successful prior web-open, while the raw/blob GitHub URLs were disabled by the web fetcher in this run. Therefore the full 949-line security-critical runtime was not manually reconstructed or rewritten.

Found a focused coverage gap in the rowid-only hardening candidate: the saved patch intentionally uses `NEW.rowid == -1` as SQLite's pre-insert auto-rowid sentinel and adds an AFTER INSERT rejection for a genuinely stored `rowid=-1`, but the existing rowid regression covered only collisions with an already-existing positive hidden rowid.

Added `experiments/asymmetric_break_glass_history/tests/test_thaw_rowid_sentinel_regression.py` on the LAB-086 branch, commit `ee210a47221b6df53f3518aa3af74f76c5b0122b`, Git blob `4c3c41426e4ff26ba53ba3ba088d6eb7bd75be33`. The exact authored bytes passed `python -m py_compile`, and local `git hash-object` matched the GitHub blob exactly.

A standalone in-memory SQLite probe using the proposed trigger shape confirmed: omitted rowid receives an ordinary auto-assigned rowid; explicit `rowid=-1` raises `IntegrityError` and does not persist; `_rowid_` and `oid` collision aliases are rejected; original history remains unchanged. This is mechanism evidence only, not a PASS against the unpublished branch candidate.

Durable note: `research/2026-08-28-lab086-rowid-sentinel-regression.md`, main commit `9abe31fa2415c25e151a1360c7332d1311fbc852`. Issue #163 comment `5454326978` records the same result.

No new branch-runtime unittest PASS is claimed in this run.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE focused RED→GREEN evidence remains valid; exact current source inspection proves the semantic guard is present in live `d4a6a40f...`.
- Provider-receipt NULL-identity guard is present in live `d4a6a40f...`.
- Hidden-rowid historical RED→GREEN evidence remains mechanism evidence only; durable patch is `research/2026-08-28-lab086-hidden-rowid-replace.patch` blob `61841b58...`.
- New explicit `rowid=-1` sentinel regression is published as blob `4c3c4142...`; syntax/blob identity verified. Standalone SQLite sentinel/alias probe passed as mechanism evidence.
- PR #165's complete per-file patch remains an exact current source carrier for the 949-line runtime.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 evidence remains retained; PR #173 stays draft pending exact real-stack execution.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor; fresh raw access fails DNS resolution.
- The GitHub connector can return the complete current file, but this run still has no supported byte-preserving connector-response -> executable-filesystem bridge. `container.download` did not remove this because its web-view precondition could not be satisfied for the raw/blob URL.
- Publication through Contents API is allowed only after exact candidate bytes are materialized and actually tested; do not hand-rewrite the security-critical runtime.
- PR #165 must remain draft until rowid candidate exact testing/publication, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a supported byte-preserving transfer of PR #165's complete `strict_fence.py` payload into an execution filesystem; require reconstructed Git blob == `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` before editing.
2. Apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`; compute and record the new candidate Git blob.
3. Execute unchanged focused regressions: `test_provider_receipt_null_identity_regression.py`, `test_thaw_alternate_unique_collision_regression.py`, `test_thaw_rowid_collision_regression.py`, and new `test_thaw_rowid_sentinel_regression.py`; require GREEN for all, then full strict/thaw conflict subgate + compileall.
4. Publish only exact tested bytes through a supported path; require GitHub returned blob == tested candidate, then re-fetch/hash-verify and repin executable snapshot.
5. Resume complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
6. If exact LAB-086 execution remains concretely tool-limited, resume LAB-091 real-stack regressions as fallback without claiming execution that did not occur.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; rowid sentinel coverage improved; complete current source is available through PR patch, remaining blocker is byte-preserving connector→executor materialization, then rowid-only hardening + exact regression gate.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 exact execution is tool-limited.
