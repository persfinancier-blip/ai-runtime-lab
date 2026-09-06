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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and open PRs. PR #165 remains open/draft on `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

LAB-086 capability status remains blocked at the same safety boundary:
- connector can read repository/history and normal Contents writes are available;
- no supported byte-preserving machine transform/materialization path was observed that consumes exact connector-returned predecessor bytes plus retained patch bytes and writes the mechanically composed result;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `EQUIVALENCE_CERTIFICATE_TRUST_ROOT_ROTATION_CROSS_GENERATION_VERIFIER_HANDOFF_RECURSIVE_PROOF_AGILITY_V1_FROZEN` in `research/2026-09-06-equivalence-certificate-trust-root-rotation-cross-generation-verifier-handoff-recursive-proof-agility-v1.md`, main commit `6c4718fcc8768d7bd21341b453d4d5dfcdb24119`; #178 comment `5561220638` records the result.

Key decisions:
- rotate the cryptographic/verifier carrier, never silently redefine the immutable historical certificate statement/root obligation set;
- ordinary root rotation uses TUF-like predecessor-threshold + successor-threshold authentication of the same handoff statement, monotonic generations and rollback rejection;
- retirement is separate from historical verification: historical-only evidence cannot authorize new destructive substitution/GC;
- compromised-old-root recovery cannot self-bootstrap and requires a pre-authorized independent recovery path;
- algorithm/proof/verifier migrations are checked per logical ancestor; a strong terminal signature or recursive proof cannot launder a rejected/revoked ancestor;
- verifier V1->V2 handoff requires direct replay, independently justified observation subsumption, or bounded dual-verifier comparison over retained originals;
- recursive compression preserves parent statement/public inputs, ROS and revocation dependencies; historical-verifier permission is not new-proof authority after retirement;
- offline late verifiers walk authenticated handoff generations or an explicitly anchored checkpoint; newest-root-only self-bootstrap fails closed;
- explicit 80-case RED-first matrix is frozen across root rollover, compromise, algorithm retirement, verifier/proof migration, offline catch-up, downgrade resistance, GC races and recovery.

Primary donor mechanisms: TUF root continuity/key migration; Sigstore TUF trust-root rotation, revocation/freshness and offline-root handling; NIST CSWP 39 crypto agility; SLSA VSA verifier/version + policy/input-attestation binding.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor + retained patch are readable via connector history, but no supported byte-preserving machine composition bridge has been observed in this run.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility contracts instead of creating locally valid authority islands.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **historical re-attestation scheduling / cryptographic sunset horizon / evidence refresh completeness semantics**. Define how every still-live certificate depending on a soon-to-be-rejected carrier is discovered before its sunset deadline; require authenticated inventory/coverage checkpoints, priority for irreplaceable E2/E3/E4 evidence, refresh/replay/subsumption outcomes, offline/archive handling, GC interlocks, completeness proof, and RED cases for missed certificates, late revocation, unavailable originals, campaign races, mixed algorithms and deadline expiry.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; trust-root rotation/cross-generation verifier/proof agility contract now frozen in addition to prior evidence/GC/substitution contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
