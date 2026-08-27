# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 executable pin: `05d8e75a636818afcb32e085d464c9fa9171dea5`; published `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`.
- PR #165 remains DRAFT; mergeability must not substitute for the execution gate.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact reconstruction/execution is concretely tool-limited.

## Last completed step

Attempted the repinned LAB-086 strict/thaw execution path again. Direct git/raw GitHub transport is still unavailable. Connector content is byte-exact, but there is still no supported machine stream/mount from connector response bytes into the local executor. A manually reconstructed `strict_fence.py` failed the mandatory Git blob gate (`e57f70530233912302851088a5bb6c44453b745d` != published `eb2198354d222ad0ad6b7d751bf5c649157b6b36`), so no LAB-086 test execution from that file was counted.

Because this was a concrete tool-limit, used the allowed LAB-091 fallback and found a real restart defect in the final supported candidate. LAB-080 `SharedAnchorLedger._init()` replays `INSERT OR IGNORE INTO shared_anchor_meta VALUES(1,0)` on every startup. Persistent LAB-091 `BEFORE INSERT` guard `lab091_v2_meta_no_insert` runs before SQLite uniqueness conflict resolution, so a normal reopen aborted before `verify_durable()` even when the singleton already existed. File-backed SQLite execution reproduced `sqlite3.IntegrityError: LAB-091 meta singleton already initialized`.

Fixed PR #173 without weakening the guard:
- added `restart_safe_schema.py`, which creates LAB-080 tables under `BEGIN IMMEDIATE`, reads the singleton first, and inserts `(1,0)` only on a genuinely fresh database;
- final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._init()` now uses this helper via dynamic dispatch from the LAB-080 base constructor;
- if a guarded database is missing the singleton, startup remains fail-closed because the persistent insert guard rejects reinitialization.

Exact published blobs:
- `restart_safe_schema.py` `975610219c710a42c4a8377bd38f9593a8bb23f5`;
- `test_restart_safe_schema.py` `3112877432a3f575e5624537d4c5180cf0b379d7`;
- `history_bound_operation_scoped.py` `8d2d511b2ea895c2f680ac495e26c4d694fd047d`.

The helper + regression were reconstructed from published bytes and matched `git hash-object`; executed result: **4/4 PASS + compileall PASS**. The final supported class was separately reconstructed and matched blob `8d2d511b...`, confirming the `_init()` override is wired into the actual candidate. Research note: `research/2026-08-28-lab091-persisted-trigger-restart-constructor.md`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Predecessor published LAB-086 thaw/fence exact subgate: 14/14 PASS + compileall.
- Corrected LAB-086 alternate-UNIQUE regression blob `a767e6bbb5e164a846c93d04b9c8c3f7980bba38`; published runtime blob `eb219835...` is byte-identical to the focused corrected candidate that passed 1/1 + `py_compile` before publication.
- Current run: failed LAB-086 reconstruction hash was rejected; zero new LAB-086 PASS claims were added.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 retained evidence includes one-shot 6/6, guard/persistence 12/12, v4 9/9, restart-trigger 3/3, single-PREPARED 2/2, process concurrency/crash 2/2, and unsafe raw-DML baseline failure as intended.
- New LAB-091 restart-safe constructor regression: exact published **4/4 PASS + compileall**.

## Known blockers / constraints

- LAB-086 remains first priority. Remaining work is the exact published execution gate, not protocol redesign unless a new executable/source blocker appears.
- The predecessor 14/14 thaw/fence result still must be rerun on repinned snapshot `05d8e75a...`.
- Direct shell/raw GitHub transport is unavailable. Connector reads are byte-exact but lack a supported stream/mount into the local executor; large manual reconstruction is non-evidence unless the local Git blob hash matches exactly.
- PR #165 must remain draft until the repinned strict/thaw subgate, complete branch-local LAB-080→086 real-ledger tests, unsafe seed, compileall and final security/reconciliation audit are all clean.
- PR #173 remains draft. The constructor/restart defect is fixed, but the final supported object still needs full exact LAB-080/LAB-082 two-worker/crash/UNKNOWN execution and retained LAB-087 composition.
- LAB-090/#169 provider handoff freshness remains separate. Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 first: obtain an exact local `strict_fence.py` whose `git hash-object` equals `eb2198354d222ad0ad6b7d751bf5c649157b6b36`; do not execute/count the subgate before that equality holds.
2. Reconstruct/hash-verify the strict/thaw regression modules and execute the repinned subgate: alternate-UNIQUE, primary/history/proof replacement, NULL identities, transaction-scoped thaw minimality, conflict/current-authority/root-head tests + compileall.
3. Reconstruct the complete branch-local LAB-080→086 dependency closure from the same executable pin, execute every normal LAB-086 real-schema module, unsafe legacy-promotion expected-failure seed and full compileall.
4. Perform final security/reconciliation audit and fresh branch/main compare. Only a completely clean gate may make PR #165 ready/integratable.
5. If LAB-086 exact transfer remains concretely tool-limited, LAB-091 fallback next target is the full exact `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` against real LAB-080/LAB-082 dependencies, specifically constructor reopen + two-worker/crash + timeout/UNKNOWN.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; alternate-UNIQUE fix published byte-exact; repinned execution gate next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; persisted-trigger constructor restart defect fixed exact-published 4/4; full real-stack gate remains.
