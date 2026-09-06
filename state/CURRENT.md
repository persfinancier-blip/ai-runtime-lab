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
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected current open PRs. PR #165 remains open/draft on `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Re-probed the exact LAB-086 execution capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector can read repository/history and normal Contents writes remain available;
- no supported byte-preserving machine transform/materialization bridge was observed that consumes exact connector-returned predecessor bytes plus retained patch bytes and writes the mechanically composed result;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `HISTORICAL_REATTESTATION_SCHEDULING_CRYPTOGRAPHIC_SUNSET_EVIDENCE_REFRESH_COMPLETENESS_V1_FROZEN` in `research/2026-09-06-historical-reattestation-scheduling-cryptographic-sunset-evidence-refresh-completeness-v1.md`, main commit `8272e6c36cab0f16176b1fd41b42cb8f318ad70f`; #178 comment `5561546213` records the result.

Key decisions:
- cryptographic retirement has separate acceptance, historical-verification, and destructive-retention sunsets; a deadline alone never makes old evidence safe to forget;
- destructive sunset requires a proof-carrying refresh campaign with authenticated inventory coverage, exact-one disposition for every still-live obligation, and successor coverage preserving the full dependency-class/root-obligation semantics;
- carrier-only renewal is allowed only when the underlying commitment remains secure; weak content/Merkle/hash/public-input commitments require underlying-object access and recommitment, following RFC 4998/RFC 6283-style hash-tree renewal semantics;
- verifier-generation changes require direct replay or independently justified observation subsumption; old PASS cannot merely be resigned;
- E2/E3/E4 refresh completion requires independent validation rather than trusting only the same extractor/verifier lineage that could have omitted the dependency;
- archive manifests are not availability proof: when underlying bytes are required, retrieval + content/provenance verification precede refresh; otherwise the obligation becomes `QUARANTINED_UNREFRESHABLE` and is retained;
- active/unresolved refresh obligations and scan gaps interlock with GC as roots; campaign completion does not itself authorize deletion;
- late revocation, dependency-repair, appeal, fork recovery, or new liveness creates delta obligations and invalidates stale completion/GC proofs until reprocessed;
- explicit 80-case RED-first matrix is frozen across inventory completeness, materiality, carrier renewal, hash renewal, verifier migration, deadlines, archives, GC races, crash/recovery, and independent completion replay.

Primary donors: NIST CSWP 39upd1 crypto agility; NIST NCCoE cryptographic discovery/inventory for PQC migration; RFC 4998 ERS and RFC 6283 XMLERS evidence renewal; ETSI long-term preservation semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch are readable via connector history, but no supported byte-preserving machine composition bridge has been observed in this run.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh contracts instead of creating locally valid authority islands.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **refresh-campaign inventory attestation / delta-capture / completeness-under-concurrent-mutation semantics**. Define an authenticated snapshot+delta protocol proving the refresh universe remains complete while evidence, revocations, appeals, repair edges, liveness roots and archive locations mutate concurrently; determine a compact source-log/checkpoint cut without globally stopping writers; freeze RED cases for phantom obligations, double-counted moves, archive relocation, snapshot/delta gaps, rollback and finalization races.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; historical re-attestation / cryptographic sunset / refresh-completeness contract now frozen in addition to prior evidence/GC/substitution/verifier-agility contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
