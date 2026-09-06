# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending hidden-rowid lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues, PRs and branches. PR #165 remains the highest-priority unfinished task.

Re-probed the exact LAB-086 execution capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read/write remains available, but no observed supported byte-preserving machine transform consumes the exact predecessor blob + retained patch and emits the exact composed file without model reserialization;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `REFRESH_CAMPAIGN_INVENTORY_ATTESTATION_DELTA_CAPTURE_CONCURRENT_MUTATION_V1_FROZEN` in `research/2026-09-06-refresh-campaign-inventory-attestation-delta-capture-concurrent-mutation-v1.md`, main commit `a4391fbfba4bb8b94ba95fecbc3eab026e58a6f3`; #178 comment `5561898982` records the result.

Key decisions:
- a refresh campaign universe is authenticated `BaselineSnapshot(F0) ⊕ CanonicalDeltas(F0,F1]`, not the rows observed by a scanner;
- delta retention/capture starts at the same opening cut as the baseline snapshot; scan-then-subscribe is invalid because it creates an omission gap;
- finalization requires authenticated `RESOLVED_THROUGH(F1)` evidence from every material source; idle workers, an empty queue or a current high-water read are not completeness proof;
- snapshot/delta overlap is expected and deterministically deduplicated by immutable obligation identity plus predecessor/generation semantics;
- federated domains use authenticated vector frontiers, but per-domain resolved positions are not enough unless cross-domain transaction/causal closure is proven;
- liveness, revocation, appeal, dependency-repair, archive-location/availability, verifier/policy/trust and substitution mutations through F1 can create or reopen obligations;
- archive relocation is add+retrieve/content-verify before retire; location is not evidence identity;
- active campaign inputs, delta-retention leases, unresolved closures and originals needed for renewal interlock with GC as temporary roots;
- crash recovery resumes from durable authenticated source frontiers and idempotent dispositions; missing retained source history yields `GAP_UNRECOVERABLE` rather than guessed completion;
- independent replay must reproduce the final obligation-set root and exact-one terminal-disposition root;
- explicit 80-case RED-first matrix is frozen across opening-cut gaps, overlap/dedup, concurrent liveness/repair/revocation, archive relocation, resolved-through finalization, exact-one dispositions, crash/rollback/gaps, GC races and independent verification.

Primary donors: PostgreSQL exported logical-replication snapshot + consistent point; Debezium incremental snapshot watermark/window dedup; CockroachDB resolved timestamps; Kafka transactional offset/fencing semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch are readable via connector history, but no supported byte-preserving machine composition bridge has been observed in this run.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh/concurrent-inventory contracts instead of creating locally valid authority islands.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **federated finalization barrier / causal-closure attestation / cross-domain partial-transaction detection semantics**. Define the minimum authenticated protocol that lets independent evidence, revocation, repair, liveness and archive domains publish a common F1 without a globally serializable database; determine how barrier epochs, causal transaction manifests and timeout/UNKNOWN states compose with source equivocation, offline domains and GC authority; freeze executable RED cases for split transactions, delayed consequences, domain membership changes and stale barrier acknowledgements.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; concurrent refresh snapshot+delta completeness contract now frozen in addition to prior evidence/GC/substitution/verifier-agility/sunset-refresh contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
