# Current Lab State

Last updated: 2026-08-27

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `e6bf48d81129914b8dbe3e23a2b1a416fab11e24`; current executable pin: `05d8e75a636818afcb32e085d464c9fa9171dea5`.
- Fresh GitHub status: PR #165 is draft + mergeable=true. Mergeability is not a substitute for the execution gate.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; current HEAD `5b3aebea574f9e8d6c4d7883625ef37b91a487cf`, draft + mergeable=true. Fallback only while LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Resumed the repinned LAB-086 execution gate. Per-run capability probe reconfirmed that direct `git` and raw GitHub HTTP are unavailable in this runtime (`Could not resolve host` for both `github.com` and `raw.githubusercontent.com`). Connector reads remain exact but file-by-file, so the 30-module LAB-080→086 gate was not replaced by a manual/partial reconstruction.

Fresh source audit of pinned `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36` found no new thaw/semantic-identity bypass beyond the already fixed `UNIQUE(provider_id,generation)` case. The exact full gate remains required.

Because the documented fallback condition was met, advanced LAB-091 adversarial coverage. `shared_anchor_intents` has PK `intent_id` plus secondary UNIQUE identities `position` and `request_id`; the existing v2 insert guard checks all three, but the published suite did not explicitly attack REPLACE through the two secondary identities. Added `test_intent_alternate_unique_replace_regression.py` on PR #173, commit `5b3aebea574f9e8d6c4d7883625ef37b91a487cf`.

Exact published-source evidence for that regression:
- `operation_permit.py` blob `637784a5cb61a024a1df3e0e983887b6d0a838be` — local `git hash-object` MATCH;
- `row_tokens.py` blob `801eb0fbdb915bb31f40069d087bf3ce56d659a8` — MATCH;
- `full_operation_guards.py` blob `8e409d61d3d813dbf3a564ea8ea5f4d3015106fb` — MATCH;
- new published regression blob `cb034b5b62e59ecf52038c69c652a74a9c9783d8` — MATCH;
- post-publication execution: 2/2 PASS; focused compileall PASS.

The two attacks use fresh `intent_id` values with a colliding existing `request_id` or `position` under a matching one-shot insert permit. Both `INSERT OR REPLACE` attempts fail and the authenticated original row remains unchanged. No LAB-091 runtime change was required; this closes an adversarial-coverage gap rather than a discovered bypass.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Corrected LAB-086 alternate-UNIQUE regression blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`.
- Published LAB-086 `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36` is byte-identical to the corrected candidate that passed the focused alternate-UNIQUE regression 1/1 + `py_compile` before publication.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 exact published secondary-UNIQUE intent regression: 2/2 PASS + compileall, blob `cb034b5b62e59ecf52038c69c652a74a9c9783d8`.

## Known blockers / constraints

- LAB-086 remains first priority. Remaining work is the exact published execution gate, not more protocol redesign unless a new executable/source audit blocker appears.
- The retained predecessor 14/14 thaw/fence result must be rerun on repinned snapshot `05d8e75a...`.
- Direct shell/raw GitHub transport is unavailable in this run. Connector reconstruction is byte-exact but file-by-file.
- PR #165 must remain draft until the repinned strict/thaw subgate, complete branch-local LAB-080→086 real-ledger tests, unsafe seed, compileall and final security/reconciliation audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct exact `strict_fence.py` and strict/thaw test modules from executable pin `05d8e75a...`, hash-verify every file, and execute the repinned subgate: alternate-UNIQUE, primary/history/proof replacement, NULL identities, transaction-scoped thaw minimality, conflict/current-authority/root-head tests + compileall.
2. Reconstruct the complete branch-local LAB-080→086 dependency closure from the same executable pin, hash-verify every file, execute every normal LAB-086 real-schema module, unsafe legacy-promotion expected-failure seed and full compileall.
3. Perform final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
4. Use LAB-091 fallback only when exact LAB-086 reconstruction/execution is concretely tool-limited; next fallback target is the full real LAB-080/LAB-082 supported-surface two-worker/crash/UNKNOWN gate, not more focused guard tests unless a new specific threat is identified.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE fix published byte-exact; repinned execution gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; new exact secondary-UNIQUE intent regression 2/2 PASS; full real-stack gate remains.
