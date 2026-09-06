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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PR state. LAB-086 remains first priority and PR #165 remains open/draft at `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Re-probed direct source execution with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-probe`

It failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `LOG_TO_SUBJECT_INDEX_DERIVATION_COMPLETENESS_SKIPPED_LEAF_FRAUD_PROOF_MAPPER_CHECKPOINT_V1_FROZEN` in `research/2026-09-06-log-to-subject-index-derivation-completeness-skipped-leaf-fraud-proof-mapper-checkpoint-v1.md`, main commit `60c96c782ad0a37c6ce62d11156aff03b8665c90`; #178 comment `5558867592` records the result.

Key decisions:
- a signed `(source_log_root, derived_map_root)` pair does not prove derivation completeness;
- every authenticated source position in a claimed contiguous mapper interval must have exactly one canonical committed disposition; there is no implicit ignored state;
- exact-once completeness is position-based even when semantic event IDs/retries are deduplicated;
- batch/parallel mapping requires a disjoint exhaustive positional cover plus deterministic merge semantics; gaps, overlaps, missing shards and guessed progress fail closed;
- the derivation transcript commits source position + source leaf digest + disposition + derived operation digest;
- compact fraud evidence is defined for skipped positions, duplicated positions, wrong source binding, deterministic misclassification, wrong derived effect, interval gaps/overlaps and generation reinterpretation;
- coverage and correct state execution are separate proof obligations; complete dispositions alone do not prove `M_prev -> M_next`;
- independent full replay from authenticated source leaves is the reference safe verifier/fallback and must reproduce both disposition commitment and target map root;
- mapper checkpoints form a monotonic lineage binding previous mapper checkpoint, contiguous source frontier and previous/next map roots;
- source-schema/canonicalizer/policy evolution creates explicit generations and cannot reinterpret historical intervals;
- proven mapper fraud monotonically removes checkpoint authority and triggers descendant revalidation; recovery creates a new corrected lineage while preserving the bad checkpoint/fraud evidence;
- explicit 80-case RED-first matrix is frozen across source frontier, exact-one disposition, batch coverage, compact fraud proofs, deterministic classification, derived execution, crash/restart/checkpoint lineage and auditor/omission composition.

Primary donors: July 2026 IETF Key Transparency combined prefix/log tree and auditor transition checks; Google Key Transparency sparse-map roots committed into append-only log history; Trillian log/map/personality and independent log-auditing patterns. Donor mechanisms only; no production mapper/prover/index or behavioral PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-completeness contracts rather than creating independent locally-valid authority islands.
- No production omission verdict may treat silence, lookup failure, a missing dense-log inclusion proof, or a signed but derivation-unverified subject-map root alone as cryptographic non-membership/completeness evidence.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **mapper checkpoint bootstrap / late-joining auditor / snapshot provenance and compaction semantics**. Define how a new independent verifier can begin at a later trusted mapper checkpoint without replaying genesis, what authenticated snapshot/state commitments are required, how it proves the checkpoint is an admissible descendant of previously witnessed trust-frontier state, how source/derived history pruning preserves skipped-leaf fraud detectability and historical omission proof reproducibility, and which minimum retained receipts/proofs prevent a compacted snapshot from laundering an earlier incomplete or fraudulent mapper interval.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitor-completeness/challenge-response/non-inclusion/mapper-derivation contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
