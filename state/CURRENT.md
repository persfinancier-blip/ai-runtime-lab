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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and PR #165. LAB-086 remains first priority and is not superseded. The available GitHub connector exposes fetch/read and normal Contents replacement writes, but no supported machine transform/materialization operation was observed that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `PROVIDER_MODEL_SEMANTIC_DIFF_COMPATIBILITY_EDGE_CODEGEN_IMPACT_CONE_V1_FROZEN` in `research/2026-09-06-provider-model-semantic-diff-compatibility-edge-codegen-impact-cone-v1.md`, main commit `2943aa7d8a00b09384aaa7165ec471d5c62d356e`; #178 comment `5556314862` records the result.

Key decisions:
- compatibility is directional and dimension-specific, not a blanket property of a schema/package/version;
- every admitted edge separately proves request-effect, historical replay, evidence, reconciliation and disclosure behavior;
- machine diff operates on the admitted normalized transitive semantic graph, including wire location/name, defaults/presence/nullability, auth/signing, idempotency/retry, errors, open-world extensions and transitive source changes;
- remove+add is never automatically promoted to rename by similarity heuristics; an explicit provider-specific migration proof is required;
- adding/changing defaults is consequential until parser/serializer/provider/SDK-default semantics are distinguished and proved;
- protobuf/Smithy/OpenAPI wire or source compatibility alone never proves LAB replay/evidence/reconciliation compatibility;
- generated request/response/error DTOs, serializers, final-request extractors, replay adapters, evidence projections, reconciliation parsers, retry/idempotency classifiers and disclosure/observability policy bundles are linked by explicit dependency edges;
- any changed dependency invalidates the exact artifact impact cone unless a no-impact proof exists; partial regeneration fails closed;
- compatibility-edge attestations bind both source generations, semantic-diff engine/normalizer/policy/codegen generations, diff + impact-cone digests, regenerated artifact digests, fixture-set digests and authenticated registry frontier;
- historical evidence remains bound to its original source/artifact generations; reverse compatibility is never inferred from forward compatibility.

An explicit 80-case RED-first matrix is frozen across identity/equivalent raw drift, false rename inference, defaults/presence, enum/union/open-world deltas, wire/auth/effect changes, errors/reconciliation, impact-cone/partial regeneration, directionality and historical rollback. No production compatibility engine or behavioral PASS is claimed.

Primary donors: Smithy evolving-model rules, Smithy `breakingChanges`/Diff semantics and mixin flattening; Protocol Buffers documented binary wire-safe/unsafe evolution; JSON Schema compatibility/dialect evolution. These are donor mechanisms only; LAB's consequential compatibility claim remains stricter and multi-dimensional.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler/evidence-schema-registry/model-normalization/model-semantic-diff contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade or provider evidence-schema widening may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **compatibility proof fixture synthesizer / minimal distinguishing corpus / historical edge coverage contract**. Define how each typed semantic delta deterministically generates positive and negative witness fixtures; prove that every compatibility edge has a fixture capable of distinguishing the prohibited change; minimize fixtures without losing semantic coverage; bind fixture provenance to source generations and impact-cone nodes; define historical corpus retention/selection so rare enum/error/default/presence states are not lost; reject compatibility attestations whose fixture set cannot distinguish a claimed no-impact rule; freeze RED cases for vacuous equality fixtures, unreachable branches, correlated mutations, fixture minimization dropping the sole distinguisher, historical corpus bias and generator/toolchain drift.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model-normalization/model-semantic-diff contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
