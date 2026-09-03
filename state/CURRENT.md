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
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, and current open issue/PR state. Re-probed LAB-086 execution/materialization paths: direct `git ls-remote` again failed before repository execution with `Could not resolve host: github.com`; raw web fetch of the exact PR-head `strict_fence.py` URL was unavailable; GitHub connector base64 fetch still truncates the whole-file payload at the presentation boundary. The security-critical file was not manually/model-reserialized, no branch mutation was attempted, and no fresh behavioral PASS is claimed.

Because LAB-086 exact composition remains concretely tool-limited, the fallback strengthened existing LAB-092/#176 rather than creating another narrow finding. Current PR #177 source and all retained LAB-092 findings were consolidated into one minimal safe redesign contract: a domain-separated LAB-092 installation certificate, canonical authority-schema/trigger manifest, serialization-bound validation, explicit recoverable external-confirmation state machine, and a unified regression matrix covering preseeded generic markers, carrier/constraint substitution, extra persistent triggers, malformed inherited ledger state, deterministic TOCTOU schedules, and crash/restart/UNKNOWN outcomes.

## Evidence produced
- `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` — main commit `c215b3ab0ac5bb1c78dcd373077bac8174e3282f`; #176 comment `5528679972`.
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
- Exact predecessor and patch bytes are connector-readable, but no supported machine transform/handoff currently composes connector blob + unified diff into exact candidate bytes/blob SHA for a normal Contents write; direct filesystem network access again failed DNS and raw web fetch was unavailable in this run.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090 fixes must preserve one trusted ownership/recovery scope from successful prepare through status, SQL durability, provider commit, durable acknowledgement and release; outage semantics must not invent provider evidence while unavailable.
- LAB-092 should no longer be patched as independent `_classify()`/marker checks. The retained redesign contract requires a non-preseedable domain-separated installation certificate, canonical authority-schema + complete relevant trigger manifest, inherited durable-state authentication, serialization-bound authorization, and a recoverable external-confirmation state machine. Constructor/preflight checks, magic-id renaming, selective duplicate LAB-080 checks, trigger-name blacklists, or another unsynchronized `_classify()` are insufficient.
- LAB-100 provider authority must bind identity/key/position/request-results/activation state/synchronization and the monotonic fence allocator epoch into one coherent durable authority.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition/materialization path for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run retained LAB-090 REDs before PR #175 production changes; then implement the LAB-092 regression matrix from `research/2026-09-03-lab092-minimal-safe-redesign-contract.md` against current PR #177 before changing production code. Obtain exact REDs for domain separation, carrier/schema/extra-trigger authenticity, malformed inherited durable state, all three TOCTOU schedules, and crash/restart/UNKNOWN recovery. Only then replace the current marker/check composition with one coherent certificate/manifest/state-machine boundary and run LAB-080/081/090/092 downstream gates. Then run retained LAB-100 provider REDs.

If neither exact composition nor exact source execution becomes available, continue only with concrete distinct trust/capability/fail-closed evidence or consolidation that materially strengthens an existing issue; do not create duplicate narrow findings.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending; consolidated redesign contract now recorded; complete authority schema/trigger-set authentication, inherited LAB-080 durable-tail authentication, domain-separated non-preseedable completion provenance, recoverable external-confirmation state machine, and all retained TOCTOU/crash regressions required.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups.
