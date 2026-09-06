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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and open PRs. PR #165 remains the highest-priority unfinished task and is still draft/open at the recorded head.

Re-probed the exact LAB-086 capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read/write remains available but no supported byte-preserving machine transform from exact predecessor+patch bytes to the exact candidate has been observed;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `MANIFEST_SCHEMA_AUTHORITY_DECLARATION_SLOT_COMPILER_SCHEMA_COMPLETENESS_PROOF_V1_FROZEN` in `research/2026-09-07-manifest-schema-authority-declaration-slot-compiler-schema-completeness-proof-v1.md`, main commit `b3e6de4ebfe71af0be4f68b955814b4049a5fdd8`; #178 comment `5562916751` records the result.

Key decisions:
- closed-world manifest schemas are consequential authority metadata; producer-only schema publication is insufficient;
- schema generations are threshold-authorized, immutable, monotonic and predecessor-linked, with explicit activation/rollout frontiers;
- canonical operation dispatch is total and unambiguous; aliases are authenticated/acyclic and no consequential unknown operation may silently fall into a permissive default;
- material declaration slots use stable non-reusable semantic IDs; removal reserves an ID, while semantic change gets a new slot identity;
- generated artifacts bind exact schema/compiler/mapping roots, but consequential assurance requires an independent interpreter/checker rather than producer+verifier sharing the same generated helper;
- `SchemaCompletenessProofV1` proves declared-universe completeness only when a separately derived `OperationSemanticInventoryV1` discharges every material capability through a slot or reviewed NOT_APPLICABLE witness;
- late discovery of a missing schema slot yields `SCHEMA_OMITTED_MATERIAL_SLOT_PROVEN`, stales affected finalization/GC authority, re-roots a bounded historical closure and requires additive N+1 + repair rather than rewriting old schema bytes;
- explicit 80-case RED-first matrix frozen across authority, dispatch, slot lifecycle, compiler drift, completeness, rotation/downgrade, fraud proof, concurrency and GC/recovery.

Primary donors: TUF versioned threshold-authorized trust metadata and predecessor/new-root handoff; Protocol Buffers stable/non-reusable field-number discipline; JSON Schema explicit closed-world property validation; OpenAPI explicit polymorphic alternatives and ambiguity constraints.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch remain readable through connector history, but no supported byte-preserving composition bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier/producer-manifest/schema-authority contracts instead of creating locally valid authority islands.
- New audit risk: `OperationSemanticInventoryV1` can itself become the next common-mode blind spot. If the inventory omits a real effect capability, the schema-completeness checker can honestly discharge an incomplete semantic universe.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **semantic-inventory authority / effect-capability registration / latent-side-effect detection semantics**. Define how the supposedly independent `OperationSemanticInventoryV1` is built without merely restating the manifest schema; how runtime/plugin/provider capabilities that can mutate storage, emit network/broker effects, schedule delayed work, alter authority/recovery state or create GC dependencies are registered and independently observed; how dynamic/reflection/FFI/plugin paths are represented; how inventory generations roll forward/revoke; and how a late-observed effect not covered by the inventory yields an `INVENTORY_OMITTED_CAPABILITY_PROVEN` fraud proof, bounded historical repair and stale schema-completeness proofs. Freeze RED cases for hidden plugin effects, dynamic dispatch, generated wrapper drift, FFI/native escape hatches, capability aliasing, partial registration, runtime upgrades and concurrent inventory rotation.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; producer-bound manifest completeness plus manifest-schema authority/slot-compiler/completeness-proof contracts now frozen in addition to prior evidence/GC/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
