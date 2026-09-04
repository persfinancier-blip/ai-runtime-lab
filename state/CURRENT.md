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
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and inspected the live open issue/PR frontier. Fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; LAB-086 exact machine composition/source execution remains unavailable. No `strict_fence.py` mutation and no new LAB-086 behavioral PASS are claimed.

Completed the pre-recorded distinct source-evidence task for LAB-092. Fresh PR #177 source confirms the current migration completion intent authenticates only `{schema: provider-generation-activation, version: 1}` while `_reservation_surface(path, attested, bootstrap)` reconstructs a partial authority surface by assigning caller-supplied `path`, `attested`, `provider_history.path`, and `provider_history.bootstrap`.

Frozen decision: LAB-092 migration is an authenticated transition of the same retained construction provenance used by normal restart, not a free-standing boolean marker. Its canonical certificate must bind canonical logical DB identity, bootstrap-root digest, provider-history descriptor/protocol, prior construction provenance digest, old/new LAB-100 activation-authority descriptor digests, exact activation table/trigger definition digests, current authenticated provider-generation head, and a migration epoch/nonce. A pure schema migration requires identical old/new activation-authority descriptors; implementation/version/protocol changes require a separate authenticated LAB-100 authority transition with explicit ordering.

Legacy migration startup order is now frozen: reconstruct canonical DB identity -> retained bootstrap/history strategy -> classify legacy without treating absence as pristine initialization -> verify provider-generation history -> verify runtime head -> reconstruct exact LAB-100 activation authority -> verify no incompatible pending handoff -> build exact certificate -> install DDL + PREPARED operational evidence -> externally authenticate exact certificate -> reverify exact DDL/certificate -> only then recovery/delegation.

A 24-case RED-first matrix is frozen covering DB/root/strategy/activation-authority rebinding, marker replay across DB/generation, exact DDL tamper, PREPARED recovery under wrong authority, confirmation-response loss, migration/authority-upgrade ordering, LAB-097..099 composition and LAB-093 confinement.

Durable evidence: `research/2026-09-04-lab092-migration-authority-graph-binding.md`, main commit `7639481a4549430f15bf57afc49e18a5e5254c67`; #176 comment `5537097320`. Verdict: `LAB092_MIGRATION_AUTHORITY_GRAPH_BINDING_FROZEN`.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Live predecessor/patch/target remain `d4a6a40f...` + `61841b58...` -> `b78e7c98...`; no supported connector-response-to-filesystem/Python machine transform has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Direct Git transport currently fails DNS before repository access; no fresh exact repository behavioral PASS is claimed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100 must use the frozen sealed/registered construction-bound `ActivationAuthority`.
- LAB-092 must use the retained domain-separated certificate + authority/schema/trigger serialization binding; do not patch only `_MIGRATION_PAYLOAD` while keeping caller-controlled `_reservation_surface` authority construction.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.

## Exact next action
LAB-086 first: continue probing only for a genuinely supported machine transform/materialization path that can consume exact GitHub predecessor + patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then the frozen LAB-090/LAB-100 and LAB-092 RED matrices, followed by LAB-094..096 and LAB-097..099 matrices before production refactors.

If neither capability appears: next distinct source-evidence task is to freeze one canonical byte-level serialization/domain scheme shared by LAB-092 migration certificates, LAB-097 initialization certificates, LAB-099 activation-ticket digests, and LAB-100 authority-transition descriptors so cross-contract digests cannot disagree through JSON/SQLite/type coercion. Do not write production code without executable RED/GREEN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority model frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration now bound to retained authority graph; exact RED/full gate pending.
- #178 / LAB-093 — READY; broker façade + endpoint lifecycle frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + 28-case RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated initialization/activation provenance + 38-case RED matrix frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade API frozen.
