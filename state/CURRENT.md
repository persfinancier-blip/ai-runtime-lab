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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, open PRs and branch inventory. PR #165 remains open/draft on `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Re-probed direct source execution in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128).
- No safe byte-preserving connector-resource -> machine patch-transform -> normal Contents-write bridge was observed.
- Therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `SUBSTITUTION_CHAIN_COMPOSABILITY_EQUIVALENCE_CERTIFICATE_TRANSITIVITY_PROOF_COMPRESSION_V1_FROZEN` in `research/2026-09-06-substitution-chain-composability-equivalence-certificate-transitivity-proof-compression-v1.md`, main commit `3dc4724bfc2f17830808fd0854151e39e24e8ffd`; #178 comment `5560869209` records the result.

Key decisions:
- semantic equivalence is non-transitive by default; local `O->S1` and `S1->S2` PASS do not imply deletion-authoritative `O->S2`;
- first destructive substitution freezes an immutable root obligation set (ROS) containing every material observation/authority dependency descendants must preserve;
- chain composition requires observation-set monotonicity plus exact/authorized context and verifier/recovery support-set compatibility;
- inherited destructive authority is allowed only through direct root replay, an explicitly proven transitive relation over the complete observation algebra, or a recursive proof that binds the complete parent statement/public inputs + ROS;
- proof compression may discard representation redundancy, never observation obligations, revocation dependencies, dependency class, context, support sets or authority frontiers;
- revocation blast radius follows every material ancestor in the logical proof DAG even after compression; cycles/self-support have zero authority;
- E3 recovery evidence cannot be laundered into E2 verification-only evidence;
- explicit 80-case RED-first matrix is frozen across transitivity, observation monotonicity, context/support-set drift, proof compression, revocation, cycles and GC/recovery.

Primary donor mechanisms: SLSA VSA subject/policy/input-attestation binding and transitive-dependency summaries; SLSA provenance completeness semantics; in-toto step/material/product chain verification; recursive-proof statement-binding as a mechanism donor only. No recursive proof system is selected or implemented.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor + retained patch are readable via connector history, but no supported byte-preserving machine composition bridge has been observed in this run.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution-chain contracts instead of creating locally valid authority islands.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **equivalence-certificate trust-root rotation / cross-generation verifier handoff / recursive-proof verifier agility**. Define how long-lived compressed substitution chains survive signer/verifier-key rotation, cryptographic algorithm retirement and proof-system upgrades without trusting obsolete cryptography forever or invalidating all historical substitutions at once; require authenticated handoff/subsumption, downgrade resistance, algorithm-agility policy, offline late-verifier semantics and RED cases for compromised old roots, dual-sign periods, mixed-algorithm chains and verifier migration.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; substitution-chain transitivity/proof-compression contract now frozen in addition to prior evidence/GC/substitution contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
