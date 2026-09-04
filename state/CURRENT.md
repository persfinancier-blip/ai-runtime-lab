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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. Fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed. #163 comment `5540290488` records the observation.

Completed the pre-recorded distinct fallback: froze `PROVENANCE_STARTUP_VERIFIER_RECOVERY_PLANNER_V1_FROZEN` in `research/2026-09-04-provenance-startup-verifier-recovery-planner-v1.md`, main commit `5319a313875a50d48d0829d661451b6d4d1e2a5a`.

The verifier contract separates three authorities: side-effect-free `verify_startup`, pure `plan_recovery`, and later write-capable `execute_recovery` through LAB-080/LAB-091/LAB-087. Startup reads exact schema/initialization identity/head/genesis/full chain/transitions/events/LAB-080 intents/event-specific durable state before requesting any narrow external evidence. Full canonical traversal from genesis, not cached-head/MAX(rowid/epoch), establishes authority.

At most one PREPARED provenance transition is recoverable and only when it is the exact immediate child of the authenticated head with byte-identical event/link/transition and LAB-080 bindings. Local LAB-080 PREPARED may yield exact retry or exact reconciled-confirm-then-commit; local CONFIRMED requires exact receipt re-authentication. Every actionable plan carries a preconditions digest and must be rechecked inside the final authorized transaction; stale plans fail closed. A 48-case RED-first matrix covers structural corruption, canonical/type confusion, fork/gap/head rollback, PREPARED classifications, UNKNOWN/reconcile paths, illegal state deltas, historical activation deletion/rebinding, retained-authority drift and LAB-093 confinement.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport currently fails DNS before repository access; no fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage schema and startup verifier/planner; no independent locally-valid provenance islands.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement canonical encoder/chain/atomic-append/storage/verifier tests first and execute frozen LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the exact external-evidence collector + terminal-anchor continuity protocol consumed by the new verifier/planner: authenticated-read vs reconcile semantics, exact request/position/receipt inputs and outputs, side-effect classification of provider APIs, snapshot freshness/version binding, handling of provider-ahead/behind/UNKNOWN, and proof that evidence collection cannot itself release activation fences or mutate SQLite/provider generation state. Do not implement production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery/storage/verifier frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery/storage/verifier; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + 28-case RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery/storage/verifier + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery/storage/verifier frozen.
