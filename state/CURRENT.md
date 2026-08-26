# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current observed PR #165 HEAD remains `95fa5da3c457e3431cd596ec969d5939b0a1d925`; mergeable=false; full current-head LAB-080→086 real-ledger execution gate remains outstanding.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current PR #173 HEAD `f65b7e51965631eca4fd0b724d49871a1c4b1734`, mergeable=true, draft.

## Last completed step

Re-read AGENTS.md, this state and SELF_RESUME.md, re-inspected PR #165/#173 and Issues #163/#170. LAB-086 remains first priority, but the exact full LAB-080→086 dependency closure was not reconstructed in this runtime; no new LAB-086 PASS or merge claim was made.

Per the recorded fallback, audited LAB-091's remaining alternate/legacy supported surfaces and found a real downgrade path. The first operation-scoped guards reused trigger names that the older transaction-wide `SupportedMutableAsymmetricSharedAnchorLedger` installer knows and drops. A focused executable counterexample proved the downgrade: exact guard blocked `shared_anchor_meta.reserved_position 0 -> 999`; legacy trigger reinstall plus broad `lab091_writer_authorized()==1` accepted and persisted `999`.

Fixed the downgrade without changing the outer LAB-087 trust claim. Operation-scoped guards now use persistent `lab091_v2_*` trigger names outside the legacy installer's drop namespace. Legacy reinstall may add broad triggers but can no longer remove the one-shot guards. A real legacy connection lacks `lab091_consume_permit`, so consequential writes fail closed; the final operation-scoped connection continues to consume exact permits normally.

Published/exact evidence:
- `full_operation_guards.py` commit `2975b733b046bd9657e4ee51c2ea9151416f8bf1`, blob `8e409d61d3d813dbf3a564ea8ea5f4d3015106fb`;
- new regression `test_legacy_surface_persistence.py` blob `e47e2ed29e3652b2c70ec7eec1a86d8975219a1a`;
- exact dependencies matched published blobs: `operation_permit.py 637784a5...`, `row_tokens.py 801eb0fb...`, existing `test_full_operation_guards.py 40ec2f20...`;
- existing exact full-guard suite + new legacy-surface regression: **12/12 PASS**; compileall PASS;
- research note `research/2026-08-26-lab091-legacy-surface-trigger-persistence.md` committed as `f65b7e51965631eca4fd0b724d49871a1c4b1734`.

Issue #170 and PR #173 were updated to reflect the operation-scoped candidate and the new alternate-surface fix.

## Evidence retained

- LAB-086 lower-stack exact evidence remains LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric custody 8/8, public/final 11/11; lower unsafe baselines failed as expected.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- LAB-087 is merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 reference layer exact 11/11 PASS + compileall; unsafe raw-DML seed failed as intended.
- LAB-091 one-shot permit primitive exact 6/6 PASS + compileall.
- LAB-091 full mutable-row guards now have exact **12/12 PASS** including the legacy-surface persistence regression.

## Known blockers / constraints

- LAB-086 remains first priority. Merge gate is still exact current-head execution on one LAB-080→086 closure: own/lower cardinality + migration + suffix + final-supported/security suites, unsafe seed, compileall and final audit. PR #165 reports mergeable=false; do not reconcile/integrate before that gate is clean.
- Direct shell GitHub transport is not assumed; connector reconstruction works but full closure assembly remains expensive.
- LAB-091 `operation_scoped_integration.py` still needs exact real LAB-080/LAB-082 execution: restart, concurrency, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.
- The v2 trigger persistence fix protects against the specific legacy installer namespace. Arbitrary same-privilege DDL that explicitly drops v2 triggers remains outside LAB-091 and is owned by LAB-087.
- LAB-090/#169 provider handoff freshness remains separate.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. LAB-086 first: connector-reconstruct exact current PR #165 `migration_guard.py`, `suffix.py`, `final_supported.py` and their real-schema tests on the proven LAB-080→085 closure; execute own/lower cardinality, migration, suffix, final-supported, cross-binding/history, inherited/direct-surface, strict-fence/thaw, restart/concurrency tests; then unsafe seed + full compileall + final audit.
2. If that exact closure remains tool-limited, continue LAB-091 from PR #173: reconstruct exact LAB-080/LAB-082 dependencies and execute `operation_scoped_integration.py` against real reserve/confirm/reconcile/verify-component flows, including reopening the DB through the legacy surface to prove v2 guards survive the actual installer rather than only the focused trigger model.
3. Add exact restart, concurrent workers, crash rollback, timeout-after-commit/UNKNOWN reconciliation and LAB-087 restricted-worker composition tests. Keep PR #173 draft until that complete gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger execution gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; operation-scoped primitive/guards exact-tested, legacy-surface downgrade fixed, but real-stack restart/concurrency/crash/UNKNOWN/LAB-087 gate remains.
