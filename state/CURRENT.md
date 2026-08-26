# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD: `95fa5da3c457e3431cd596ec969d5939b0a1d925`.
- Current published `migration_guard.py` blob: `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current observed HEAD after this run: `1dc1b65ea7c1dcb38e990092c0819530d540053a`.

## Last completed step

Reconciled a stale LAB-086 handoff with the actual PR history. Commit `95fa5da3c457e3431cd596ec969d5939b0a1d925` already published the pre-cutoff LAB-086 own-proof cardinality fix. GitHub reports that commit as exactly +20/−0 lines in `migration_guard.py`, and the commit patch matches `research/2026-08-26-lab086-pre-cutoff-own-proof-cardinality.patch` exactly. The old handoff claim that runtime still used blob `2ae3df...` and that candidate `7db4b53...` was unpublished is superseded.

Focused executable SQLite semantics for the published cardinality method: clean pre-cutoff state accepted; orphan `provider_asymmetric_break_glass_proofs` rejected; orphan `provider_asymmetric_recovery_public_root_proofs` rejected. This is focused evidence only, not the complete real-ledger gate.

Direct shell GitHub transport is still unavailable in this runtime, so the exact LAB-080→086 closure was not bulk-checked out. Per fallback policy, LAB-091 was audited instead.

Fresh LAB-091 audit found a new merge blocker: `lab091_writer_authorized()` is a transaction-wide boolean, not an exact operation capability. Focused execution using the published trigger predicates showed unauthorized mutable DML is blocked, but once authorization is true the transaction can set `shared_anchor_meta.reserved_position` directly `0 -> 999` and a component watermark `1 -> 999`. The fixed production methods do not intentionally issue those jumps; the flaw is overly broad authority scope for any bug/alternate SQL executed during the authorized window.

Durable LAB-091 artifacts added to PR #173:
- `research/2026-08-26-lab091-operation-scoped-writer-permits.md` (commit `e090c519a127bd9bf8ddad8572f0453afe7bb9a9`);
- RED regression `test_operation_scoped_permit_regression.py` (commit/current HEAD `1dc1b65ea7c1dcb38e990092c0819530d540053a`).

Required LAB-091 correction: replace boolean transaction authority with a connection-local one-shot operation permit binding operation kind + exact identity + expected old/new row transition (or canonical digest), installed immediately around one DML statement and consumed/cleared afterward. Provider/network calls remain outside permit scope.

## Evidence retained

- LAB-086 published own-proof cardinality commit: `95fa5da3c457e3431cd596ec969d5939b0a1d925`; current blob `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`.
- Focused LAB-086 cardinality semantics: clean PASS; orphan break-glass proof BLOCKED; orphan public-root proof BLOCKED.
- Fresh LAB-086 compare: ahead 154 / behind 98; all 59 PR paths remain additions relative to current main.
- Exact lower-stack evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 remains merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer remains exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 new focused counterexample: unauthorized meta update BLOCKED; transaction-authorized meta jump to 999 SUCCEEDED; transaction-authorized watermark jump to 999 SUCCEEDED.

## Known blockers / constraints

- LAB-086 publication blocker is resolved. Do not republish the obsolete staged hash `7db4b53...` over current runtime.
- Remaining LAB-086 merge gate is exact execution: reconstruct current HEAD with LAB-080→085 dependencies and run real-ledger cardinality + migration + suffix + final-supported/security suites, unsafe seed and compileall.
- LAB-091 boolean writer authority is now a known merge blocker; PR #173 must remain draft until operation-scoped one-shot permits replace it and the new RED regression is green.
- LAB-091 exact published integration execution and restart/concurrency/crash/UNKNOWN/LAB-087 composition gates remain outstanding.
- Direct shell GitHub may remain unavailable; connector exact reads/writes are the control-plane fallback.
- LAB-086 SQLite fences cover audited ordinary-DML/stale supported paths, not arbitrary same-privilege DDL/schema authority; LAB-087 owns that boundary.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 remains first priority: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and tests on the proven LAB-080→085 closure; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If exact closure reconstruction remains tool-limited, fix LAB-091 by replacing transaction-wide boolean authorization with one-shot operation-scoped permits. Make `test_operation_scoped_permit_regression.py` green, then run exact published integration + restart/concurrency/crash/UNKNOWN and LAB-087 composition tests.
3. Keep PR #165 and PR #173 draft until their complete current-head gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; own-proof cardinality fix published; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; transaction-wide boolean writer authority is now a RED merge blocker; draft PR #173.
