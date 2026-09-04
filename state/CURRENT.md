# Current Lab State

Last updated: 2026-09-04

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. Fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed. #163 comment `5539719608` records the observation.

Completed the pre-recorded distinct fallback: froze `PROVENANCE_DURABLE_SQL_STORAGE_SCHEMA_V1_FROZEN` in `research/2026-09-04-provenance-durable-sql-storage-schema-v1.md`, main commit `7a8805cbd428479b23363be48e7fb236c4851a6d`.

The storage contract reuses LAB-080 as the sole outer monotonic-anchor/idempotency authority and defines four V1 tables: immutable canonical `provenance_events_v1`, immutable parent-linked `provenance_chain_links_v1`, one `PREPARED|COMMITTED` `provenance_transitions_v1` row tied 1:1 to `shared_anchor_intents.intent_id`, and singleton `provenance_chain_head_v1` as a non-authoritative cache. Security digests are BLOB32; SQLite storage class is checked; V1 append epoch stops at signed SQLite `2^63-1` before PREPARE.

Transaction A freezes exact event/link/transition bytes and reserves the existing LAB-080 intent but does not advance the provenance head. Transaction B runs only after exact external LAB-080 receipt re-authentication and atomically performs PREPARED->COMMITTED plus compare-and-swap head advancement and only the event-authorized post-state mutation. Sibling/fork UNIQUE constraints are defense-in-depth; complete authenticated chain + retained authority graph + exact LAB-080 evidence remain the authority.

Startup classification is frozen before any provider release/repair/rebootstrap/worker delegation: exact schema, one authenticated genesis, one contiguous COMMITTED prefix ending at cached head, at most one PREPARED immediate child, exact referenced LAB-080 intent, and deterministic UNKNOWN-after-commit recovery only for the already frozen bytes. A 46-case RED-first storage matrix covers row deletion/rebinding, sibling forks, type confusion, head rollback, crash windows, LAB-092/099/100 state-delta constraints and LAB-087/093 composition.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport currently fails DNS before repository access; no fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol and durable SQL storage schema; no independent locally-valid provenance islands.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement canonical encoder/chain/atomic-append/storage tests first and execute frozen LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the exact side-effect-free provenance startup verifier and recovery-planner API over the new storage schema: ordered queries, canonical decode/digest checks, full-chain traversal, LAB-080 receipt re-authentication inputs, explicit corruption/error taxonomy, and a pure `VerifyResult/RecoveryPlan` boundary such that verification itself performs no SQLite/provider writes and only an exact eligible PREPARED transition can yield a narrowly scoped recovery action. Do not implement production verifier code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery/storage frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery/storage; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + 28-case RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery/storage + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery/storage frozen.
