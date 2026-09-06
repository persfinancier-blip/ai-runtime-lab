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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues/PRs and PR #165 directly. PR #165 remains open/draft on `ee210a47221b6df53f3518aa3af74f76c5b0122b`; its own remaining gate still requires exact strict/thaw plus full LAB-080→086 execution before ready/merge.

Re-probed the exact source path with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it failed before repository execution with `Could not resolve host: github.com` (exit 128). The available GitHub connector exposes exact repository reads, PR patches/comparisons and normal Contents API full-file replacement, but no supported machine transform/materialization bridge that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit a byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `COMPATIBILITY_PROOF_ORACLE_INDEPENDENCE_MUTANT_SOUNDNESS_METAMORPHIC_RELATIONS_V1_FROZEN` in `research/2026-09-06-compatibility-proof-oracle-independence-mutant-soundness-metamorphic-relations-v1.md`, main commit `cd0f7e56bc47731f940d4a63a9ecef138fcd3d8a`; #178 comment `5556862743` records the result.

Key decisions:
- distinguishing fixtures are insufficient unless the oracle is independent and the mutant faithfully represents the prohibited semantic interpretation;
- oracles are classified as `SPEC_DERIVED`, `DUAL_IMPLEMENTATION`, `AUTHENTICATED_HISTORICAL`, `ALGEBRAIC_METAMORPHIC`, `PROVIDER_OBSERVED`, or insufficient-alone `SAME_PIPELINE`;
- candidate and oracle may share neutral low-level primitives but may not share the disputed semantic transformation/codegen/canonicalizer/classifier as sole proof;
- every mutant binds exact semantic dimension, intended prohibited interpretation, modified artifact/path, expected divergence, reachability, equivalence status and provenance;
- accepted mutants are first-order semantic, minimal proven interactions, historical reinterpretations, or exact boundary mutants; syntax-error, always-fail, unrelated, unreachable-by-construction and broad unproven mutants do not count;
- only `KILLED` and `EQUIVALENT_PROVEN` discharge mutant obligations; `LIKELY_EQUIVALENT`, `UNREACHED`, `MASKED`, `ORACLE_WEAK`, `NONDETERMINISTIC` and `INVALID_MUTANT` block affected admission;
- explicit independent metamorphic relations are frozen for presence/default, enum/union openness, signing/canonical scope, idempotency/retry, error classification and historical replay;
- provider nondeterminism is constrained by independently justified invariants; a consequential one-shot observation with no deterministic oracle is `INCONCLUSIVE`, not silently retried/widened;
- proof bundles bind source/target model, semantic diff, impact cone, fixtures, mutant catalog, oracle, metamorphic catalog, historical frontier and harness generations;
- newly discovered obligations, invalid mutants or common-mode oracle defects move affected historical edges to `REVALIDATION_REQUIRED`, never silent reinterpretation.

An explicit 80-case RED-first matrix is frozen across oracle independence, mutant fidelity/equivalence, presence/default, enum/open-world behavior, signing/effect/retry, errors/reconciliation and historical replay/provenance. No production prover, mutant engine, oracle engine or behavioral compatibility PASS is claimed.

Primary donors: mutation-testing coupling/equivalent-mutant literature and metamorphic-testing oracle-problem literature. These are donor mechanisms only; LAB's consequential compatibility admission remains stricter and provenance-bound.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed in this run.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler/evidence-schema-registry/model-normalization/model-semantic-diff/fixture-proof/oracle-independence contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade or provider evidence-schema widening may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **compatibility proof reproducibility / deterministic proof-bundle / independent adjudication contract**. Define canonical proof-bundle encoding and replay so a second verifier can reproduce obligations/verdicts without invoking candidate codegen; require deterministic seed/domain capture for generated fixtures and mutants; define trusted/non-trusted toolchain boundaries and dual-verifier disagreement handling; require evidence for nondeterministic/provider-observed relations; prevent proof-bundle self-signing or same-toolchain provenance from being mistaken for independent attestation; bind adjudication to authenticated registry frontier; freeze RED cases for environment drift, random-seed drift, toolchain downgrade, non-reproducible mutant generation, oracle package substitution, verifier disagreement, stale proof replay and partial bundle omission.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model-normalization/model-semantic-diff/fixture-proof/oracle-independence contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
