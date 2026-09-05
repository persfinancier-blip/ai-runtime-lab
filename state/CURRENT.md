# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and PRs. LAB-086 remains first priority and the authoritative hidden-rowid lineage is unchanged.

Probed LAB-086 first in this runtime with a real `git clone --no-checkout`. Git transport again failed before repository access with `Could not resolve host: github.com` (exit 128). The GitHub connector remains readable/writable, but no supported machine bridge was observed that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `OBSERVER_EVIDENCE_DURABILITY_BOUNDED_QUEUE_RECOVERY_JOURNAL_V1_FROZEN` in `research/2026-09-05-observer-evidence-durability-bounded-queue-recovery-journal-v1.md`, main commit `6ed41b4744847ceeeb183549d657c86f73b4144f`; #178 comment `5554534236` records the result.

Key durability decision: pre-I/O `SINK_ENTERED` is a synchronous durable barrier and may **not** be deferred to an in-memory/bounded queue. Provider I/O is forbidden until the exact attempt record has crossed the admitted durability boundary and all evidence-store transactions/locks are released. If the barrier cannot commit within a finite budget because of `SQLITE_BUSY`, ENOSPC, IOERR, failed sync, corruption/profile drift or writer failure, the attempt fails closed before sink entry.

Post-I/O observations may be decoupled through a bounded queue, but evidence loss is monotone toward ambiguity: after durable `SINK_ENTERED`, queue overflow, disk-full, consumer crash, missing callback or torn later journal tail can never yield `FAILED_BEFORE_IO`; the attempt remains at least `UNKNOWN` absent a previously durable authenticated protocol-certified non-processing proof.

The frozen admission profile covers same-host SQLite WAL, `synchronous=FULL` when power-loss durability is claimed, finite busy handling, explicit capacity reserve/high-water quarantine, no SQL/provider/pool lock across network I/O, append-only framed recovery journal with torn-tail handling, idempotent journal-to-SQL replay, multi-process writer/ACK semantics and startup profile/recovery verification. WAL/SQLite is still single-writer and network-filesystem WAL is not admitted.

A 64-case RED-first matrix is frozen across barrier ordering, lock discipline, SQLite contention, disk/fsync/corruption, queue overflow, multi-process writer service behavior, recovery-journal replay, restart classification and capacity/topology admission. No production observer implementation or behavioral PASS is claimed.

Primary donors recorded: SQLite WAL, `PRAGMA synchronous`, bounded `sqlite3_busy_timeout`, and SQLite atomic-commit/recovery semantics.

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
- LAB-093 must implement the frozen least-capability façade and all retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **durable evidence-store capacity reservation / compaction / archival continuity contract**. Specify segment/checkpoint/compaction rules, retention versus replay needs, authenticated archival/restore, disk-reserve accounting, safe deletion proofs, WAL/journal truncation, evidence pinning for unresolved `UNKNOWN`/manual-resolution cases and a RED-first crash/space-amplification matrix. Production observer code remains read-only/offline until executable RED/GREEN exists.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; transport observer durability/recovery-journal contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
