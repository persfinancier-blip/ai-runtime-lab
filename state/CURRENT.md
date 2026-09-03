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
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and active PR/issue state. Re-probed direct machine access to the exact LAB-086 predecessor raw URL; filesystem-side Python networking failed before repository access with `Temporary failure in name resolution`, so the security-critical `strict_fence.py` was not reserialized or mutated and no fresh behavioral PASS is claimed.

Fallback source audit of PR #177 found a new distinct LAB-092 provenance gap: `_schema_object_state()` authenticates only the exact named LAB-090 activation table and required `block_intent_during_provider_activation` trigger, but does not authenticate the complete persistent trigger set on authority-relevant tables. An additional stable `AFTER INSERT ON shared_anchor_intents` trigger can therefore execute inside `_install_and_reserve_prepared()`'s own `BEGIN IMMEDIATE` transaction while the required trigger remains exact. An isolated file-backed SQLite probe reproduced this exact omission shape: the migration-shaped PREPARED insert committed and the extra trigger changed an existing component watermark from 0 to 777. This is neither carrier-schema substitution nor TOCTOU; the malicious extra trigger can pre-exist and remain unchanged throughout the operation.

## Evidence produced
- `research/2026-09-03-lab092-extra-trigger-authority-not-authenticated.md` — main commit `c06e8511acb262275b4e90a581454f50c4697b59`; #176 comment `5527945001`.
- `research/2026-09-03-lab092-explicit-migration-trusts-unverified-shared-ledger-tail.md` — main commit `15af8e1cfb8e15f712318ec890fd8e20e49f2adf`; #176 comment `5527186826`.
- `research/2026-09-03-lab092-preseedable-migration-marker-confused-deputy.md` — main commit `4a64f764bdf4859a9d1d9cfac440d36ebc43b329`; #176 comment `5526435082`.
- `research/2026-09-03-lab092-provenance-carrier-schema-not-authenticated.md` — main commit `71829f371ee250d0dc16d83e007f7a79e3d82cfb`; #176 comment `5525609997`.
- Retained LAB-092 evidence also includes explicit-migration, constructor/restart, and post-construction TOCTOU findings.
- Retained LAB-100 evidence: reconstructed fence-counter monotonicity, inherited provider rotate, caller-owned/reconstructed provider authority splits.
- Retained LAB-086 machine-handoff evidence: `research/2026-09-03-lab086-container-download-handoff-probe.md` commit `3cc6187748211c8800a6a39d387aa5043f59b96d`; full-blob connector reprobe commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`.
- Retained LAB-090 evidence includes post-prepare status/connection leaks, unavailable abort/status semantics, activation-id collision recovery, duplicate-release race, and pre-SQL external-commit orphan fence.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but no supported machine transform/handoff currently composes connector blob + unified diff into exact candidate bytes/blob SHA for a normal Contents write; direct filesystem network access again failed DNS in this run.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090 fixes must preserve one trusted ownership/recovery scope from successful prepare through status, SQL durability, provider commit, durable acknowledgement and release; outage semantics must not invent provider evidence while unavailable.
- LAB-092 completion evidence must be domain-separated from pre-LAB-092 generic ledger authority; authenticate the exact provenance-carrier schema, inherited LAB-080 durable ledger/tail/watermark invariants, and the complete authority-relevant persistent trigger set. These proofs must be bound to the consequential SQLite/external authority mutation boundary during explicit migration completion, startup confirmation, and post-construction operations. Required-object-only checks, row-content checks, magic-id renaming, selective duplicate LAB-080 checks, trigger-name blacklists, or another unsynchronized `_classify()` are insufficient.
- LAB-100 provider authority must bind identity/key/position/request-results/activation state/synchronization and the monotonic fence allocator epoch into one coherent durable authority.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition/materialization path for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run retained LAB-090 REDs before PR #175 production changes; then run LAB-092 regression groups for malformed inherited LAB-080 durable state, preseeded generic completion intent, exact-carrier substitution, untrusted additional persistent triggers, and the three deterministic TOCTOU schedules. For the extra-trigger group, keep the required LAB-090 trigger exact while adding an additional authority-relevant trigger and require failure before DDL/marker/meta/provider/receipt/activation/watermark mutation. Then run retained LAB-100 provider REDs.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen existing issues rather than creating duplicates.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; complete authority schema/trigger-set authentication, inherited LAB-080 durable-tail authentication, domain-separated non-preseedable completion provenance, and all retained TOCTOU regressions required.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups.
