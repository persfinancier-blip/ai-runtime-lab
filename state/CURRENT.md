# Current Lab State

Last updated: 2026-09-03

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175, LAB-092 / #176 draft PR #177, LAB-088 / #167 draft PR #172, and LAB-091 / #170 draft PR #173 remain IN_PROGRESS.
- LAB-093/#178 through LAB-100/#185 remain READY follow-ups.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. PR #165 head remains unchanged and draft; no supported byte-preserving connector-response -> machine patch/hash path was observed, so security-critical LAB-086 source was not mutated and no fresh behavioral PASS is claimed.

Fallback source audit of PR #175 found another concrete LAB-100 provider-authority invariant gap: `ActivationState.next_fence` is not checked against fences retained in reconstructed `pending` / `committed` ticket state. A restart/reconstruction can therefore retain historical provider evidence at fence N while rewinding/defaulting `next_fence`, then issue a later activation with fence <= N. This breaks the monotonic fencing-token epoch that a real external fencing primitive must preserve. The finding strengthens existing LAB-100/#185; no duplicate issue was created.

## Evidence produced
- `research/2026-09-03-lab100-reconstructed-fence-counter-reuse.md` — main commit `03458a81d886785a5cbde61ac03230443fb2ce82`; #185 comment `5522730375`.
- Retained LAB-100 inherited-rotate evidence: `research/2026-09-03-lab100-inherited-provider-rotate-bypasses-activation-fence.md` — commit `40f226a3ee41a512f05d9f03a8e972b230fcc4f3`; #185 comment `5522087162`.
- Retained LAB-086 machine-handoff evidence: `research/2026-09-03-lab086-container-download-handoff-probe.md` commit `3cc6187748211c8800a6a39d387aa5043f59b96d`; full-blob connector reprobe commit `159ad6ed9edab9ab870e8cb9fc244df53bed43b8`.
- Retained LAB-090 evidence includes post-prepare status/connection leaks, unavailable abort/status semantics, activation-id collision recovery, duplicate-release race, and pre-SQL external-commit orphan fence.

## Known failures / blockers
- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and patch bytes are connector-readable, but no supported machine transform/handoff currently composes connector blob + unified diff into exact candidate bytes/blob SHA for a normal Contents write.
- Exact checkout/source execution remains unavailable; no fresh repository behavioral PASS is claimed.
- Keep PRs #165/#175/#177/#172/#173 draft until their retained exact gates execute.
- LAB-090 fixes must preserve one trusted ownership/recovery scope from successful prepare through status, SQL durability, provider commit, durable acknowledgement and release; outage semantics must not invent provider evidence while unavailable.
- LAB-100 provider authority must bind identity/key/position/request-results/activation state/synchronization and the monotonic fence allocator epoch into one coherent durable authority. Do not derive provider fencing authority solely from coordinator SQLite or repair epoch regression from unauthenticated mutable ticket collections.

## Exact next action
LAB-086 first: probe for a supported byte-preserving machine composition/materialization path for predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` + retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`. If available, apply only that patch, require candidate Git blob `b78e7c98e35138719f77c482c7f1aab36b702de7`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run retained LAB-090 REDs before PR #175 production changes and add both LAB-100 provider REDs: (1) inherited `rotate()` during live pending activation; (2) reconstructed activation state with historical fence N and allocator epoch `< N`, proving pre-fix a new fence can regress/reuse and requiring post-fix fail-closed reconstruction or a provably monotonic durable allocator.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen existing issues rather than creating duplicates.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178..#185 / LAB-093..LAB-100 — READY regression-first follow-ups; #185 now explicitly includes inherited provider identity/key rotation and reconstructed fencing-epoch monotonicity.
