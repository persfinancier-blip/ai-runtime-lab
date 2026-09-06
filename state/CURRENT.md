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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs. LAB-086 remains first priority and is not superseded.

Probed LAB-086 first with a real `git clone --no-checkout`. Git transport again failed before repository access with `Could not resolve host: github.com` (exit 128). The GitHub connector remains readable/writable, but no supported machine bridge was observed that can consume exact connector-returned predecessor bytes plus retained patch bytes and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `PROVIDER_EVIDENCE_SCHEMA_REGISTRY_GENERATED_CLOSED_DTO_SDK_DRIFT_ADMISSION_V1_FROZEN` in `research/2026-09-06-provider-evidence-schema-registry-generated-closed-dto-sdk-drift-admission-v1.md`, main commit `477d903c9ec7206ff27d72f5a6bebc391e49ad1f`; #178 comment `5555742148` records the result.

Key decisions:
- consequential provider capability binds an authenticated content-addressed `evidence_schema_generation_id`, never only an SDK/package version label;
- schema generation covers exact provider-model snapshot + transitive references, canonical evidence mappings, policy generation, generator/config identity and generated sink artifact hashes;
- generated request/response/error DTO serializers are closed and may not reflect/traverse arbitrary SDK object graphs or persist arbitrary `metadata/extra/context/extensions`, raw exception dictionaries, `Any`/`Struct` or free-form JSON without explicit classification;
- unknown/new provider fields are admission blockers, not implicit OMIT; open-world surfaces such as OpenAPI `additionalProperties=true/default` and protobuf unknown fields require explicit constraint/classification;
- field presence and generated-client defaults are schema material when they can change provider-visible semantics;
- SDK/model upgrades use directional compatibility edges (`new accepts old evidence`, `new can replay old capsule`, `old accepts new evidence`) rather than symmetric version compatibility;
- historical evidence remains interpreted under its original evidence-schema generation and is never rewritten merely to adopt the latest schema ID;
- provider errors/exceptions are first-class model material with separately generated closed DTOs;
- runtime capability admission verifies generated artifact hash/generation, preventing same-name module/package substitution or manual generated-code edits from inheriting authority;
- downgrade/rollback is fail-closed unless authenticated directional compatibility proves no newer authority-relevant material is forgotten.

An explicit 80-case RED-first matrix is frozen across registry snapshot identity, generated DTO closure, SDK/model drift, generation binding, request/default/wire semantics, responses/errors, sensitive-data handling, unknown/open fields, rollback/history and codegen supply-chain integrity. No production registry/codegen implementation or behavioral PASS is claimed. Primary donors: Smithy model/sensitive semantics, AWS public Smithy API models + Botocore versioned service models, OpenAPI object openness semantics, and Protobuf unknown-field behavior.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Direct git transport in this run failed before repository access with DNS resolution failure.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler/evidence-schema-registry contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade or provider evidence-schema widening may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **provider model normalization / transitive-reference closure / registry frontier admission contract**. Define deterministic, versioned normalization for Smithy/OpenAPI/protobuf/provider-native schemas; prove `$ref`/import/descriptor closure cannot omit authority-relevant transitive material; distinguish raw-source digest from normalized semantic digest; authenticate source provenance without treating URLs/version labels as authority; define model-snapshot append/frontier/rollback rules; and freeze RED cases for reference cycles, remote-ref drift, duplicate IDs, normalization collisions, unknown extensions, schema-source replacement, archive/restore and downgrade.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; privacy-minimization/cryptographic-erasure + evidence policy compiler/taint/selective-disclosure + provider evidence-schema registry/generated closed DTO/SDK drift contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
