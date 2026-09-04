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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected the live open issue/PR frontier. Fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed. #163 comment `5538327393` records the observation.

Completed the pre-recorded distinct fallback: froze a single authenticated provenance chain/link model connecting LAB-097 initialization, provider-generation/LAB-099 ticket transitions, LAB-092 migration certificates and LAB-100 authority transitions.

V1 adds domain-separated `ytim.provenance-chain-link.v1` links keyed by logical DB identity, strict U64 epoch, exact parent link digest, event kind/payload digest, and resulting provider-head/authority/schema-state digests. History is linear: initialization is epoch 0 from a domain-separated genesis digest; every successor must have `epoch == current + 1` and exact `parent_link_digest == current_head`. Different children of the same parent are corruption; verifier never chooses by rowid/time/order. Each event may change only its authorized post-state dimension: provider transition -> provider head; migration -> schema; authority transition -> authority.

Clarified LAB-097 construction to avoid self-referential hashing: initialization certificate binds the genesis digest; the epoch-0 initialization link then commits that certificate and becomes the first authenticated chain head. LAB-092 migration and LAB-100 authority-transition schemas gain `parent_chain_link_digest`. Added domain-separated schema-state digest and a 32-case RED-first chain matrix covering replay, fork, epoch gaps/rollback, cross-DB splice, wrong state deltas, UNKNOWN/idempotent recovery, LAB-099 rebinding, LAB-087 restart and LAB-093 confinement.

Durable evidence: `research/2026-09-04-authenticated-provenance-chain-link-schema-v1.md`, main commit `09b5d6a4e7af229df6dd8804ce0e1ae48c871685`; issue comments #176 `5538322000`, #182 `5538323499`, #184 `5538324418`, #185 `5538326520`. Verdict: `AUTHENTICATED_PROVENANCE_CHAIN_LINK_V1_FROZEN`.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport currently fails DNS before repository access; no fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared V1 canonical encoding plus the authenticated parent-linked chain; no independent locally-valid provenance islands.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement canonical encoder/chain tests first and execute frozen LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze the atomic durable append/recovery protocol that couples a domain-specific provenance event, its successor chain link, authenticated chain-head advancement, and the existing external/shared anchor under crash + timeout-after-commit/UNKNOWN semantics. It must specify PREPARED/COMMITTED states, exact idempotency key, restart classification, and when repair is forbidden. Do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical descriptors + chain binding frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + canonical V1 + parent-linked chain; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + 28-case RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated initialization/activation provenance + canonical V1 + global chain + regression matrices frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API + canonical V1 + global chain frozen.
