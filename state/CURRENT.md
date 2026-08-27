# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Current PR #165 HEAD: `5887eb79da5a13d2beb03ee8b846d64efb9328bd`.
- Last fully executed runtime/test pin before the new blocker: `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`.
- Published runtime at that pin: `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- GitHub reports PR #165 draft/mergeable=true. Mergeability is not a test/security result.
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact work is concretely tool-limited.

## Last completed step

Fresh conflict-algorithm audit found a new LAB-086 merge blocker after the previously clean 31/31 strict/thaw subgate.

The permanent collision fences protect declared PK/UNIQUE identities, but the affected tables are ordinary SQLite rowid tables. During transaction-scoped thaw, `INSERT OR REPLACE` can target an existing hidden `rowid` while presenting a fresh declared key. With SQLite default `recursive_triggers=OFF`, the implicit REPLACE delete is not stopped by the ordinary DELETE trigger.

Focused executable counterexample:
- existing authenticated row: `rowid=1, history_id='old-id', marker='original'`;
- declared-key collision + UPDATE/DELETE immutability guards active;
- `INSERT OR REPLACE ... (rowid=1, history_id='attacker-id', marker='tampered')` succeeded;
- resulting row became `rowid=1, attacker-id, tampered`.

Exact pinned source inspection confirms the current runtime has no hidden-rowid predicate in:
- `_install_thaw_insert_history_collision_fences_locked()`;
- `_install_post_cutoff_evidence_freeze_locked()`;
- `_install_provider_receipt_freeze_locked()`.

Durable RED regression:
- `experiments/asymmetric_break_glass_history/tests/test_thaw_rowid_collision_regression.py`, blob `9773536e5c1627f2a01f13d45fcdcb7016aa7d08`, introduced by commit `beefe0cf8f8ed17a52f149d09284ecd513dbb865`.
- It covers public history during thaw, post-cutoff proof history during thaw, and append-only provider receipts.

Durable research/fix artifacts:
- `research/2026-08-28-lab086-hidden-rowid-replace.md`;
- `research/2026-08-28-lab086-hidden-rowid-replace.patch`, staged in current HEAD `5887eb79da5a13d2beb03ee8b846d64efb9328bd`.

Focused candidate mechanism was executed separately. A safe permanent guard needs both:
1. BEFORE INSERT: reject explicit rowid collision when `NEW.rowid != -1` and an existing row has that rowid;
2. AFTER INSERT: reject a stored `rowid == -1`, because SQLite exposes `NEW.rowid == -1` in BEFORE INSERT for ordinary auto-rowid inserts.

The focused candidate blocked hidden-rowid REPLACE, blocked declared-PK REPLACE, blocked explicit stored rowid `-1`, and still allowed an ordinary fresh insert with automatic rowid.

Runtime has not been changed yet; security-critical `strict_fence.py` must be patched only from byte-exact current source.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Previous repinned LAB-086 strict/thaw exact subgate: 31/31 PASS + compileall on pin `1fa85a0e...`.
- That 31/31 remains valid evidence for the preceding implementation but is no longer sufficient for merge because the hidden-rowid conflict class was not covered.
- Focused hidden-rowid RED counterexample executed and reproduced the replacement.
- Focused rowid-safe candidate mechanism executed and produced the desired block/allow behavior.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.

## Known blockers / constraints

- LAB-086 remains first priority. The hidden-rowid REPLACE bypass must be fixed before the full real-ledger gate can resume.
- Affected policy includes INSERT-thawed authenticated-history tables, post-cutoff proof creation surfaces and `asymmetric_provider_receipts` append-only history.
- Direct shell/raw GitHub transport remains unavailable. Connector reconstruction is byte-exact but file-by-file.
- A reconstructed file counts as evidence only if `git hash-object` equals the pinned Git blob.
- Do not manually transcribe/rewrite the large security-critical `strict_fence.py` without byte identity checks.
- PR #165 must remain draft until the rowid fix, repinned strict/thaw subgate, complete real-ledger gate, unsafe seed, compileall and final audit are all clean.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. Reconstruct/hash-verify current `strict_fence.py` and apply the staged rowid-safe patch from exact bytes to:
   - thawed authenticated-history collision fences;
   - post-cutoff proof no-replace fences;
   - provider-receipt append-only no-replace fence.
2. Publish only if the resulting Git blob matches the locally tested candidate bytes.
3. Execute/hash-verify `test_thaw_rowid_collision_regression.py` plus the complete strict/thaw conflict subgate and compileall; repin the executable snapshot only after green evidence.
4. Then resume the complete branch-local LAB-080→086 real-ledger modules, unsafe legacy-promotion expected-failure seed, full compileall and final security/reconciliation audit.
5. Use LAB-091 fallback only if exact LAB-086 reconstruction/execution is concretely tool-limited again.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; hidden-rowid REPLACE blocker RED and durable; exact runtime patch next.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; fallback only while LAB-086 is tool-limited.
