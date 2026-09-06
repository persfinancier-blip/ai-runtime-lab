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

Re-probed direct source execution with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-probe`

It failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `PUBLICATION_PROMISE_FULFILLMENT_VERIFIABLE_NON_INCLUSION_SUBJECT_INDEX_COMPLETENESS_V1_FROZEN` in `research/2026-09-06-publication-promise-fulfillment-verifiable-non-inclusion-subject-index-completeness-v1.md`, main commit `fd6d15a26502b1374a11cbd3bb2abc7e0ff0f9bb`; #178 comment `5558585915` records the result.

Key decisions:
- a conventional dense append-only Merkle log gives inclusion and consistency proofs, but a failed lookup/404/timeout/missing inclusion proof is not generic non-membership evidence;
- consequential promises bind canonical subject-key, leaf-encoding, duplicate/retry, hash/domain-separation, destination-proof-class and policy generations;
- sparse-map non-membership requires an authenticated path proving the canonical empty leaf/subtree for the deterministic subject key at the exact committed map root;
- ordered/range completeness requires authenticated comparator/order and predecessor/successor/range boundaries; an unordered hash map cannot prove ordered interval completeness by assertion;
- append-only event log and subject index are separate commitments and must be cryptographically bound at the same authenticated frontier; a signed map root without log→map derivation completeness is insufficient;
- log-derived map authority requires deterministic complete mapping of every eligible source leaf, collision/duplicate/tombstone semantics, generation pinning, and replayable mapper-completeness evidence;
- full-log reconstruction matching the authenticated dense-log root is allowed as an expensive exact-leaf absence proof, but does not prove semantic-subject absence if alternate encodings are possible;
- migration/rehash/canonicalizer changes create new generations with explicit dual-frontier linkage; historical proofs are not reinterpreted under current rules;
- `OMISSION_PROVEN` requires a signed promise + eligible post-deadline authenticated frontier + policy-approved verifiable non-membership/completeness proof + log/index binding; otherwise verdict remains `OMISSION_SUSPECTED` or `UNKNOWN_UNPROVABLE`;
- explicit 80-case RED-first matrix is frozen across dense-log absence, subject binding, sparse maps, collisions/retries, range completeness, log-derived mapper completeness, deadline/tombstone history and migration/reproducibility.

Primary donors: RFC 9162 CT inclusion/consistency and SCT/MMD promise semantics; Trillian verifiable-map/sparse-Merkle deterministic key paths and committed empty subtree hashes. Donor mechanisms only; no production subject index/prover or behavioral compatibility PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion contracts rather than creating independent locally-valid authority islands.
- No production omission verdict may treat silence, lookup failure, or a missing dense-log inclusion proof alone as cryptographic non-membership.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **log-to-subject-index derivation completeness / skipped-leaf fraud-proof / mapper checkpoint semantics**. Define how a verifier proves that a subject-index revision incorporated every eligible append-only source leaf exactly once through frontier N, how skipped/duplicated/misclassified leaves yield compact fraud evidence, how mapper revisions and source-schema evolution are bound, and how independent replay/checkpointing avoids trusting a signed but incomplete derived map.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitor-completeness/challenge-response/non-inclusion contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
