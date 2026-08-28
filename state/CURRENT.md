# Current Lab State

Last updated: 2026-08-28

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Exact live `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact retained hidden-rowid candidate: `b78e7c98e35138719f77c482c7f1aab36b702de7` (tested previously, not published).
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs and resumed LAB-086 first.

Re-probed current-run transport. Direct `git clone` still fails before transfer with `Could not resolve host: github.com`; web raw-file open remains disabled. GitHub `fetch_file` can return base64 line ranges, but larger ranges are truncated by the connector response budget. This did not yet produce a practical full byte-preserving local materialization/publication path for the ~40 KB security-critical `strict_fence.py`, so no manual reserialization or runtime rewrite was attempted and no new LAB-086 PASS is claimed.

Per the allowed fallback policy, advanced LAB-091 with a focused concurrency check of the current first-adoption TOCTOU lock envelope under SQLite WAL mode. Fresh file-backed three-connection execution proved: `BEGIN IMMEDIATE` permits a sibling reader to see committed state while a competing writer is blocked with `database is locked`; after the reserving transaction installs a `BEFORE UPDATE` guard and commits, the competing writer reaches the new guard and is rejected; original state remains unchanged.

Durable note: `research/2026-08-28-lab091-adoption-lock-wal-probe.md`, main commit `15d69e2b759f19bca025a70a5c01a0803271b1b3`. Issue #170 comment `5454921277` records the same result. This is mechanism evidence only, not a full LAB-080/LAB-082/LAB-091 exact-stack PASS.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED→GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision regression and explicit `rowid=-1` sentinel regression are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 one-shot/state-machine/restart/concurrency focused evidence remains retained; new WAL-mode adoption-lock probe supports the current `BEGIN IMMEDIATE -> verify_durable -> install guards -> validate -> commit` envelope.

## Known blockers / constraints

- LAB-086 remains first priority.
- The current live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Direct shell/raw GitHub transport remains unavailable in this executor.
- Connector reads are exact but do not mount the complete candidate into the execution filesystem; large base64 ranges are truncated. Publication through Contents API is allowed only after exact candidate bytes are materialized and tested; do not hand-rewrite the security-critical runtime.
- PR #165 must remain draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- LAB-091 WAL probe is supportive mechanism evidence only; PR #173 remains draft pending its complete real-stack gate.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: obtain a supported byte-preserving publication path for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; do not manually reserialize the file.
2. Require GitHub returned blob == `b78e7c98...`, then re-fetch/hash-verify.
3. Execute unchanged focused regressions: provider-receipt NULL identity, alternate UNIQUE, hidden-rowid collision, and explicit `rowid=-1` sentinel; then full strict/thaw conflict subgate + compileall and repin.
4. Resume complete LAB-080→086 real-ledger gate, unsafe legacy-promotion expected-failure seed, full compileall, security/reconciliation audit and branch/main conflict check.
5. If LAB-086 remains concretely transport-limited, continue LAB-091 exact real-stack integration/audit work without overstating mechanism probes as candidate PASS.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; WAL adoption-lock mechanism verified, full real-stack gate still open.
