# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current PR #173 HEAD `85bfbc0b806ba5d1c0c14d097db1543c9f679ee4`, mergeable=true, draft.

## Last completed step

Re-read AGENTS.md, this state and SELF_RESUME.md, re-inspected PR #165 and probed direct GitHub transport. Shell/`git` transport still fails before execution because `github.com` does not resolve/connect from this runtime; GitHub connector reads/writes remain healthy. The full exact LAB-086 dependency closure was therefore not reconstructed in this run and no new LAB-086 PASS/merge claim was made.

Per the recorded fallback, advanced LAB-091's transaction-wide writer-authority blocker. Published a complete one-shot SQL guard layer for all mutable shared-anchor row classes:
- `row_tokens.py` — canonical SHA-256 tokens over every field of intent and asymmetric-provider-receipt rows;
- `full_operation_guards.py` — exact one-shot guards for meta tail, intent INSERT, PREPARED→CONFIRMED, watermark INSERT/UPDATE and receipt INSERT, plus immutable/delete guards for history;
- `test_full_operation_guards.py` — exact focused regression suite.

Published blobs exactly matched the locally executed files:
- `row_tokens.py` `801eb0fbdb915bb31f40069d087bf3ce56d659a8`;
- `full_operation_guards.py` initially `6617f1cff072f0c8d61fb8e7658f9636006424b9`, then upgraded to blob `43f806b4182b7f02e20f803dd93609623a4108b7` so installation also drops the six legacy transaction-wide boolean trigger names;
- `test_full_operation_guards.py` `40ec2f20cca9c878199656ef2e9337c0764a9392`.

Focused exact guard suite ran **10/10 PASS** and compileall PASS. It proves full intent-row binding, exact confirmation old→new row binding, full receipt-row binding, receipt REPLACE/substitution rejection, one-shot consumption, exact watermark paths and meta tail +1 enforcement even if a caller attempts to issue a matching 0→999 permit.

Also published `operation_scoped_integration.py` as the new LAB-091 candidate supported surface, commit/current branch HEAD `85bfbc0b806ba5d1c0c14d097db1543c9f679ee4`, blob `95b5a810a4dbac634ff88bc783d7a787ee769430`; local hash matched and `py_compile` passed. It separates serialization from authority: `_write_txn()` only opens `BEGIN IMMEDIATE`, while reserve/receipt persistence/confirmation/watermark writes each receive a one-shot permit immediately around the exact DML statement; provider/network calls remain outside permits. This integration candidate has not yet passed real LAB-080/LAB-082 restart/concurrency/crash/UNKNOWN tests, so PR #173 remains draft.

## Evidence retained

- LAB-086 published own-proof cardinality commit remains `95fa5da3c457e3431cd596ec969d5939b0a1d925`; focused clean/orphan semantics remain recorded, but full real-ledger gate is outstanding.
- Exact lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 is merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot permit primitive exact 6/6 PASS + compileall; blobs `637784a5...` and `b410a511...`.
- LAB-091 meta/watermark guard layer exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guard layer exact 10/10 PASS + compileall; current guard blob `43f806b4...`.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is still exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. PR #165 reports mergeable=false; do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport remains unavailable in this runtime. Connector file-by-file reconstruction works but is expensive; this is not an owner blocker.
- LAB-091 `operation_scoped_integration.py` is now the candidate replacement for broad boolean authority, but real-stack exact execution is still required. The older `real_integration.py` remains a pre-fix reference/prototype and must not be treated as final authority.
- LAB-091 still needs exact restart, concurrency, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition tests, plus an audit of legacy/alternate supported write surfaces.
- LAB-090/#169 provider handoff freshness remains separate.
- LAB-086 SQL fences cover audited ordinary-DML/stale supported paths, not arbitrary same-privilege DDL/schema authority; LAB-087 owns that boundary. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and their real-schema tests on the already proven LAB-080→085 closure; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that exact closure is still tool-limited, continue LAB-091 from the newly published operation-scoped candidate: reconstruct exact LAB-080/LAB-082 dependencies and execute `operation_scoped_integration.py` against real reserve/confirm/reconcile/verify-component flows. Make the existing operation-scoped RED regression green on the real surface.
3. Add/process exact restart, concurrent workers, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition tests. Audit reentrancy and alternate legacy supported surfaces. Keep PR #173 draft until that complete gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; operation-scoped primitive 6/6, full guards 10/10 and integration candidate published, but real-stack restart/concurrency/crash/UNKNOWN gate remains; draft PR #173.
