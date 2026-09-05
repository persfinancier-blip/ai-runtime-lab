# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and open PRs. LAB-086 remains first priority and is not superseded.

Probed LAB-086 first in this runtime with a real `git clone --no-checkout`. Git transport again failed before repository access with `Could not resolve host: github.com` (exit 128). The GitHub connector remains readable/writable, but no supported machine bridge was observed that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `EVIDENCE_STORE_CAPACITY_COMPACTION_ARCHIVAL_CONTINUITY_V1_FROZEN` in `research/2026-09-06-evidence-store-capacity-compaction-archival-continuity-v1.md`, main commit `26fd617b439cee4845412a3aa86d27d2d9df867e`; #178 comment `5554838046` records the result.

Key storage-authority decision: physical/logical reclamation requires two independent proofs before source evidence can be deleted: (1) semantic deletion eligibility — no unresolved/pinned UNKNOWN/manual-resolution/challenge/quarantine/replay/audit dependency; and (2) authenticated continuity — a verified archive/compaction descendant commits to the exact source range/digests and trusted global evidence frontier. TTL/age, upload success, checkpoint, VACUUM or `max_page_count` are not deletion authority.

Capacity is now explicit authority state. Admission reserve accounts conservatively for live DB + WAL + open recovery-journal segment + archive/compaction staging amplification + filesystem/quota margin + emergency safety bytes. High-water/quarantine removes new consequential SEND/MUTATE/RESUME/TOKEN_MINT before ENOSPC. WAL checkpoint starvation or maintenance backlog therefore reduces admission rather than assuming future truncation will succeed.

`UNKNOWN`, evidence-gap, manual-resolution, active challenge/quarantine and related replay/authority evidence remain pinned until exact authorized terminal resolution. Archive objects are content-addressed/read-after-write verified and bound by authenticated manifest chains; restore checks global/external monotonic provenance so an internally valid but older snapshot is rejected as rollback. A 72-case RED-first matrix is frozen across capacity accounting, WAL/checkpointing, pinning/retention, archive verification, compaction/deletion proof, journal segment rotation, backup/restore and physical reclamation. No production compactor/archiver implementation or behavioral PASS is claimed.

Primary donors recorded: SQLite WAL/checkpoint semantics, `sqlite3_wal_checkpoint_v2`, SQLite Online Backup API, SQLite page/max-page/vacuum limits, and RFC 9162 Merkle append-only frontier/consistency concepts.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Direct git transport in this run failed before repository access with DNS resolution failure.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and all retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction-archive contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze an **evidence retention / cryptographic-erasure / privacy minimization versus auditability contract**. Define which provider payload/body/header fields must never enter durable evidence; redaction/tokenization before the pre-I/O barrier; digest/commitment forms sufficient for retry/UNKNOWN/manual resolution; secret/key separation and destruction semantics; archive/backup copies; retention/legal/privacy holds versus unresolved-security pinning; and a RED-first matrix proving minimization cannot destroy authority-critical evidence or make erased secrets recoverable from derived stores.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence-store capacity/compaction/archive continuity contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
