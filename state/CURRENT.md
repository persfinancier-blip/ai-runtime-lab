# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending hidden-rowid lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. PR #165 remains the highest-priority unfinished task.

Re-probed the exact LAB-086 execution capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read/write remains available, but no observed supported byte-preserving machine transform consumes the exact predecessor blob + retained patch and emits the exact composed file without model reserialization;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `FEDERATED_FINALIZATION_BARRIER_CAUSAL_CLOSURE_PARTIAL_TRANSACTION_V1_FROZEN` in `research/2026-09-07-federated-finalization-barrier-causal-closure-partial-transaction-v1.md`, main commit `538d578bfb10e6e1c8e2a038fb63d36e0151cfe9`; #178 comment `5562255088` records the result.

Key decisions:
- a federated campaign finalizes at vector `F1` only after every policy-required material domain supplies a current authenticated `RESOLVED_THROUGH(F1_i)` ack and the combined cut is causally/transactionally closed;
- local high-water marks alone are insufficient; a recorded material effect must have its authenticated cause represented, while a cause whose consequence crosses the cut becomes an explicit in-flight obligation;
- cross-domain transactions use authenticated expected participant sets; partial participant completion is `RECORDED_INFLIGHT` or `UNKNOWN`, never global success;
- delayed deterministic consequences caused at/before F1 stay inside the campaign universe even if execution occurs after candidate F1;
- closure is computed to a fixed point: discovering a consequence beyond a domain's current ack advances that domain's F1 and requires a fresh ack;
- frozen membership epochs prevent silent join/remove semantics; an offline material domain blocks destructive finalization unless authenticated drain/decommission proves complete closure;
- source equivocation, stale ack generations, trust/schema/membership rotation and missing evidence yield `UNKNOWN`/`REVALIDATION_REQUIRED`, never latest-wins;
- archive relocation is a cross-domain transaction: write + content verification + independent retrieval + manifest must close before old-copy retirement can become eligible;
- open campaign inputs, source-retention leases and in-flight obligations remain GC roots until a current finalization certificate and all other retention contracts permit deletion;
- final certificate commits membership, F0/F1 vectors, domain acks, resolved proofs, transaction/causal roots, exact-one dispositions, empty unresolved root, obligation root and policy/trust/schema/verifier frontiers;
- explicit 80-case RED-first matrix is frozen across frontier semantics, causal cuts, split transactions, revocation/repair/appeal, archive moves, membership/offline domains, equivocation and crash/GC/fixed-point behavior.

Primary donors: Chandy-Lamport distributed consistent cut/in-flight channel state; PostgreSQL exported logical-replication snapshot + consistent point; Kafka transaction identity/epochs; CockroachDB resolved timestamp completeness promises.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch are readable via connector history, but no supported byte-preserving machine composition bridge has been observed in this run.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier contracts instead of creating locally valid authority islands.
- New federated-barrier audit risk: completeness depends on consequential producers emitting authenticated transaction/causal manifests on the same authority path as the effect. An optional observer can miss undeclared edges and make an otherwise valid barrier graph incomplete.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **causal/transaction manifest emission completeness / undeclared-edge fraud proof / producer-path binding semantics**. Define how every consequential cross-domain mutation proves that all material outgoing edges/participants were declared on the same authenticated authority path; design completeness commitments and compact fraud proofs for an omitted participant/causal edge; prevent a buggy or malicious producer from emitting an effect while hiding the edge that would have kept the federated barrier or GC root open; freeze executable RED cases for undeclared effects, producer/reporter common-mode failure, schema evolution, delayed edge discovery and independent replay.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; federated finalization barrier/causal-closure contract now frozen in addition to prior evidence/GC/substitution/verifier-agility/sunset-refresh/concurrent-inventory contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
