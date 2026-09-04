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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. Fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed. #163 comment `5539069536` records the observation.

Completed the pre-recorded distinct fallback: froze `ATOMIC_PROVENANCE_APPEND_RECOVERY_V1_FROZEN` in `research/2026-09-04-atomic-provenance-append-recovery-protocol-v1.md`, main commit `7ff93363dc3f4d51c99e72a2d54c81b3eeea6838`.

The protocol explicitly reuses LAB-080's existing deterministic PREPARED shared-anchor intent, contiguous position allocation, request-id binding, external `reconcile_increment()` and CONFIRMED receipt semantics instead of inventing another anchor/commit subsystem. One canonical transition identity commits logical DB identity, exact parent chain head/epoch, domain event digest, exact successor-link digest and resulting provider/authority/schema post-state.

Transition lifecycle is `ABSENT -> PREPARED -> externally anchored -> COMMITTED`: Transaction A freezes exact event/link/transition bytes before any external mutation but does not advance the chain head; timeout/UNKNOWN retries reconcile only the exact LAB-080 request; Transaction B re-reads parent/head/event/link/receipt/authority predicates and atomically commits event+link+head only after exact external re-authentication. Restart may complete only the exact previously PREPARED bytes; generic recomputation from mutable current rows is forbidden. Forks, unexplained external advance, missing/mismatched event/link bytes, authority rebinding and old-chain restoration under a newer external anchor all fail closed. A 36-case RED-first matrix covers crash windows, UNKNOWN, idempotency, sibling forks, event-specific state-delta rules, LAB-092/099/100 one-byte changes, LAB-087 restart and LAB-093 confinement.

Cross-contract comments: #176 `5539070566`, #184 `5539071822`.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport currently fails DNS before repository access; no fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain and atomic append/recovery protocol; no independent locally-valid provenance islands.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement canonical encoder/chain/atomic-append tests first and execute frozen LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the exact durable SQL/storage schema for provenance events, chain links, transition records and authenticated head cache under the atomic V1 protocol. Specify primary/unique keys, PREPARED/COMMITTED representation, immutable-column rules, sibling/fork prevention, how LAB-080 intent/receipt identity is referenced, startup queries/classification, and which constraints are defense-in-depth versus authenticated authority. Do not add production tables/triggers without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding + atomic recovery frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain + atomic recovery; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + 28-case RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance + canonical V1 + global chain + atomic recovery + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain + atomic recovery frozen.
