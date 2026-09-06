# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. LAB-086 remains first priority and PR #165 remains open/draft.

Re-probed the exact LAB-086 publication path with the GitHub connector:
- `fetch_blob(d4a6a40f...)` now returns the complete predecessor source payload;
- `fetch_blob(61841b58...)` returns the complete retained hidden-rowid unified patch;
- however, no supported connector operation observed in this run can mechanically pipe those exact returned bytes through a patch transform into a normal Contents-API write while preserving byte identity. The available write requires model-supplied whole-file text; manually/model-reserializing this security-critical ~949-line file remains prohibited.

Therefore no `strict_fence.py` mutation was attempted and no new LAB-086 behavioral PASS is claimed. The blocker is now precisely **machine composition/materialization**, not source/patch readability.

Completed the recorded distinct fallback: froze `SEMANTIC_EQUIVALENCE_SUBSTITUTION_MINIMAL_RETENTION_WITNESS_DEPENDENCY_CLASS_PORTABILITY_V1_FROZEN` in `research/2026-09-06-semantic-equivalence-substitution-minimal-retention-witness-dependency-class-portability-v1.md`, main commit `7493b2dc1024b19410265abbccc8a1f5be0681f1`; #178 comment `5560531617` records the result.

Key decisions:
- distinguish byte identity, lossless re-encoding, semantic equivalence and lossy projection; lossy projections never authorize destructive substitution for `E1/E2/E3`;
- semantic equivalence is scoped to dependency class, guarantee namespace, context, observation-schema generation and supported verifier/recovery generation set — there is no universal GC-authoritative `equivalent(O,S)`;
- `E1`, `E2` and `E3` have distinct portability requirements; verifier-only equivalence cannot silently replace recovery evidence; ordinary `E4` authority continuity remains exact/lossless by default;
- every destructive semantic substitution requires a content-addressed minimal-retention witness binding original/substitute, context, support sets, independent verifier diversity, challenge/revocation state, GC frontier and exact deletion epoch;
- consequential `E2/E3` requires independent transform-side and verifier-side evidence; common parser/canonicalizer/oracle/toolchain lineage collapses verifier diversity;
- version drift, materiality upgrades, revocation, context changes or new observations enter `REVALIDATION_REQUIRED`; if the original is already gone and the substitute lacks the newly required information, quarantine/degrade the affected guarantee rather than invent data;
- accepted substitutes retain the original through an authenticated challenge horizon and require independent replay/archive plus a fresh complete mark before deletion;
- explicit 80-case RED-first matrix is frozen across identity/lossless boundaries, E1/E2/E3 portability, context reuse, revocation/version drift, GC/archive races and malicious smaller-projection laundering.

Primary donor mechanisms: Reproducible Builds bit identity/checksums, Nix content-addressed object/reference semantics + reachability GC, SLSA provenance/subject verification, and in-toto materials/products + signed-policy inspection. Donor mechanisms only; no production substitution/GC implementation or behavioral PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are readable through `fetch_blob`, but no supported byte-preserving connector-resource -> machine patch-transform -> normal Contents-write bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-completeness/bootstrap-compaction/GC/schema-repair/materiality/substitution contracts rather than creating independent locally-valid authority islands.
- No semantic/canonical smaller substitute may become destructive-GC authority merely because current output/verdict matches, it is content-addressed, or its producer signed it.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **substitution-chain composability / equivalence-certificate transitivity / downgrade-safe proof compression semantics**. Define when `O -> S1 -> S2` can inherit equivalence without replaying `O`, require observation-set monotonicity and context/support-set compatibility, prevent a chain from laundering information discarded by an earlier substitute, define revocation blast radius across transitive certificates, and freeze RED cases for non-transitive semantic relations, mixed verifier generations, partial context overlap, cyclic certificates and compressed witness omission.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-derivation/bootstrap-compaction/proof-carrying-GC/schema-repair/materiality/substitution contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
