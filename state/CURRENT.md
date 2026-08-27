# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD after non-executable manifest update: `e6bf48d81129914b8dbe3e23a2b1a416fab11e24`; PR is draft and currently mergeable=true.
- Current executable pin for the exact gate: `05d8e75a636818afcb32e085d464c9fa9171dea5`.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only if LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Removed the LAB-086 byte-safe publication blocker and published the already-proven alternate-UNIQUE thaw fix to the real runtime.

`strict_fence.py` is an addition relative to `main`, so `fetch_pr_file_patch` returns the entire 935-line current file. The full per-file patch was read as a single connector response resource, eliminating the previous risk from manually reconstructing truncated `fetch_file` ranges. The saved minimal semantic-collision patch was applied to that complete payload and written through the normal Contents API.

GitHub returned exactly the expected candidate blob:
- executable commit: `05d8e75a636818afcb32e085d464c9fa9171dea5`;
- published `strict_fence.py`: `eb2198354d222ad0ad6b7d751bf5c649157b6b36`.

This is byte-identical to the candidate that had already passed the corrected exact alternate-UNIQUE regression 1/1 and `py_compile`. A post-publication focused SQLite semantic check reconfirmed that same-PK and alternate `(provider_id,generation)` replacement are blocked, the original generation remains unchanged, and a genuinely new successor remains insertable.

Repinned `research/2026-08-27-lab086-exact-gate-manifest.md` to executable snapshot `05d8e75a...` and updated the expected strict-fence blob to `eb219835...`. Issue #163 and PR #165 now reflect publication success rather than the obsolete "candidate not yet published" state.

Fresh branch/main compare: ahead 180 / behind 128; all 75 PR paths remain additions relative to `main`, so the observed divergence is historical rather than a current path-level overlap. Do not use mergeability as a substitute for the execution gate.

## Evidence retained

- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS.
- LAB-085 asymmetric custody 8/8 PASS.
- LAB-085 public/final 11/11 PASS.
- Lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Corrected alternate-UNIQUE regression blob: `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.
- Pre-publication exact candidate `eb219835...`: corrected regression 1/1 PASS + `py_compile`.
- Published runtime now has the identical blob `eb219835...`; focused post-publication semantic check reconfirmed the intended block/allow behavior.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained evidence remains recorded in #170/#173; do not substitute it for LAB-086 work while the primary gate is unblocked.

## Known blockers / constraints

- LAB-086 remains first priority. The protocol/design blocker and byte-safe publication blocker are both removed. Remaining work is now the exact published execution gate.
- The predecessor 14/14 thaw/fence result is useful retained evidence but is not a substitute for rerunning the repinned subgate after the semantic-identity change.
- Direct shell/raw GitHub transport remains unavailable; exact connector reconstruction is still file-by-file. The per-file PR-patch technique is a valid byte-safe path for PR-added files.
- PR #165 must remain draft until the repinned strict/thaw subgate, complete branch-local LAB-080→086 real-ledger tests, unsafe seed, compileall and final security/reconciliation audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the published `strict_fence.py` from executable pin `05d8e75a...` and exact current thaw/strict tests; verify every local file with `git hash-object`.
2. Execute the repinned strict/thaw subgate: corrected alternate-UNIQUE regression plus `test_strict_fence.py`, thaw history-key, NULL proof-key, proof-replace, transaction-scoped thaw minimality and relevant conflict/current-authority fence regressions; run compileall.
3. Reconstruct the complete branch-local LAB-080→086 dependency closure from the same executable pin, hash-verify every file, execute every normal LAB-086 real-schema test module, unsafe legacy-promotion expected-failure seed and full compileall.
4. Perform a fresh final security/reconciliation audit and branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
5. Use LAB-091 fallback only if the exact LAB-086 reconstruction/execution becomes concretely tool-limited again.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE thaw blocker published byte-exact; repinned execution gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
