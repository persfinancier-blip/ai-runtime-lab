# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage (`05d8e75a...` / `eb219835...`); issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `d05f7c7d7cf9a79182f03274042b25ec652bfa78`; provenance blob `fe9322800c41e5cbb641b4d86810e8f2cf0e8b0a`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected active PRs and LAB-086 issue #163. Fresh direct `git clone` again failed before repository execution with `Could not resolve host: github.com`. No supported byte-preserving bridge was observed for composing exact LAB-086 predecessor `d4a6a40f...` with retained patch `61841b58...`; no LAB-086 mutation was attempted.

Advanced the allowed LAB-092 fallback. Audited the second `self.execute(_completion_intent())` in `ProvenancedHistoricalSharedAnchorLedger.__init__()` after `super().__init__()`. The deterministic migration marker is already authenticated on the non-mutating confirmation surface after full provider-history/runtime and activation-record verification, before LAB-090 recovery. The second call did not strengthen that boundary and reopened inherited historical reauthentication after recovery; if the marker historical receipt disappeared in the intervening window, receipt recovery/reconcile could occur post-recovery without a new LAB-092 pre-auth sequence.

Regression-first commit `aca95c2c7a86fa139109d7aed3bb24b49024f406` adds `test_complete_restart_does_not_reauthenticate_marker_after_lab090_recovery`.

Fix commit `d05f7c7d7cf9a79182f03274042b25ec652bfa78` removes only the duplicate three-line post-recovery marker execution/check. Re-fetched GitHub commit diff confirms exact source scope. PR #177 remains draft and mergeable; current head is `d05f7c7d...`.

Exact branch execution remains unavailable because direct GitHub DNS resolution fails before code execution; no RED/GREEN or branch-suite PASS is claimed. Regression source was syntax-compiled locally before publication.

Durable evidence: `research/2026-09-01-lab092-remove-post-recovery-marker-reauth.md`, main commit `51551fc9218c4fdc01f718ba7745a6cf2c667559`; #176 comment `5491045026`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility and ordering evidence retained. Atomic DDL+PREPARED, stale runtime/recovery checks, non-mutating confirmation, restart pre-authentication, full-history-before-receipt-recovery, activation-integrity-before-marker-reauth, public post-construction pre-auth integrity, and removal of duplicate post-recovery marker reauth are published; exact PR #177 regression execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct git transport currently fails DNS resolution.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution is available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Explicit branch/base conflict reconciliation is required before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If exact source execution becomes available before that bridge, execute PR #177 `test_activation_schema_restart_precheck.py` first on head `d05f7c7d...`, including the new no-post-recovery-reauth regression; then execute pre-auth history verification, migration confirmation bridge, stale runtime/PREPARED recovery, atomic boundary, unresolved activation, deletion/mismatch, public verification, and legitimate legacy migration; execute PR #175 gates before any integration.

If execution remains unavailable, continue LAB-092/LAB-090 integration audit at the next mutation boundary: inspect `migrate_activation_schema_v1()` returning `cls(...)` after explicit confirmation and verify that the immediate constructor restart cannot perform any redundant external marker/authentication mutation or lose the exact confirmation result under concurrent receipt/history changes. Add a regression first only for a reachable contract violation; otherwise document the proof and advance to PR #175/#177 conflict/rebase risk analysis.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; duplicate post-recovery marker reauth removed; exact regression gate pending.
