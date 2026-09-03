# Current Lab State

Last updated: 2026-09-03

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177 (observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`), LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remains blocked from safe publication because no supported byte-preserving connector-response -> machine patch/hash path was observed; security-critical `strict_fence.py` was not mutated and no fresh behavioral PASS is claimed.

Fallback source audit of PR #177 found an additional LAB-092 trust-boundary gap: the migration provenance carrier `shared_anchor_intents` is accepted when it merely exists as a SQLite table. `_classify()` and `_install_and_reserve_prepared()` do not verify the exact LAB-080 table definition/constraints before storing or accepting PREPARED/CONFIRMED provenance. A query-compatible but constraint-weakened replacement carrier can therefore host apparently valid migration provenance while activation DDL itself remains exact. This is distinct from the three retained LAB-092 TOCTOU classes: those concern drift between check/use; this finding shows the carrier semantics are not authenticated in the first place. No duplicate issue was created; #176 was strengthened.

## Evidence produced
- `research/2026-09-03-lab092-provenance-carrier-schema-not-authenticated.md` — main commit `71829f371ee250d0dc16d83e007f7a79e3d82cfb`; #176 comment `5525609997`.
- `research/2026-09-03-lab092-explicit-migration-completion-toctou.md` — main commit `858d6522218f4e5ff16b74f70c94b58798f0426e`; #176 comment `5524875372`.
- `research/2026-09-03-lab092-startup-provenance-check-use-side-effect-race.md` — main commit `27049c89699241d212b493e914a522df6a8abbb3`; #176 comment `5524229508`.
- `research/2026-09-03-lab092-postconstruction-provenance-check-toctou.md` — main commit `a4430559efe919bf1942194d17164c7856872d1e`; #176 comment `5523513078`.
- Retained LAB-100 evidence: reconstructed fence-counter monotonicity, inherited provider rotate, caller-owned/reconstructed provider authority splits.
- Retained LAB-086 machine-handoff evidence: `research/2026-09-03-lab086-container-download-handoff-probe.md` commit `3cc6187748211c8800a6a39d387aa5043f59b96d`; full-blob connector reprobe commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`.
- Retained LAB-090 evidence includes post-prepare status/connection leaks, unavailable abort/status semantics, activation-id collision recovery, duplicate-release race, and pre-SQL external-commit orphan fence.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but no supported machine transform/handoff currently composes connector blob + unified diff into exact candidate bytes/blob SHA for a normal Contents write.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090 fixes must preserve one trusted ownership/recovery scope from successful prepare through status, SQL durability, provider commit, durable acknowledgement and release; outage semantics must not invent provider evidence while unavailable.
- LAB-092 must authenticate the exact authority-relevant provenance-carrier schema and bind that proof to the consequential mutation/serialization boundary during explicit migration completion, startup confirmation, and post-construction operations; row-content checks or another unsynchronized `_classify()` merely leave a carrier-substitution or TOCTOU gap.
- LAB-100 provider authority must bind identity/key/position/request-results/activation state/synchronization and the monotonic fence allocator epoch into one coherent durable authority.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition/materialization path for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run retained LAB-090 REDs before PR #175 production changes; then run LAB-092 regressions including (1) provenance-carrier schema substitution before migration and after COMPLETE, requiring fail-closed before DDL/marker/tail/provider/receipt/watermark mutation, and (2) the three deterministic TOCTOU groups already retained for explicit migration, constructor/restart, and post-construction operations. The schema proof must be bound to the same serialization/authority boundary rather than checked earlier without synchronization. Then run retained LAB-100 provider REDs.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen existing issues rather than creating duplicates.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; provenance-carrier schema authentication plus explicit-migration, constructor/restart, and post-construction TOCTOU regressions are required.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups.
