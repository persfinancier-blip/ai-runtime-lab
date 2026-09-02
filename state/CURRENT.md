# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor ordering, post-prepare cleanup, activation-record integrity, and activation-provider authority defects remain pending exact RED/GREEN.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY; LAB-094 / #179 READY; LAB-095 / #180 READY; LAB-096 / #181 READY; LAB-097 / #182 READY; LAB-098 / #183 READY; LAB-099 / #184 READY; LAB-100 / #185 READY.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues/PRs, PR #175 source, and the exact LAB-086 predecessor/patch blobs. Re-probed direct Git transport: it still fails before repository execution with `Could not resolve host: github.com`. The GitHub connector now returned the complete predecessor blob and retained patch in this run, but there is still no supported byte-preserving machine bridge that can consume those exact connector payloads, apply the patch, verify target blob `b78e7c98...`, and publish the complete result through Contents API. No LAB-086 source mutation was attempted.

Fallback-audited PR #175's `COMMITTED -> provider release` interval. `_mark_activation_committed()` stops the SQL trigger from blocking new intents before `_release_committed_activation()` removes the provider fence. After checking supported surfaces, this is not a new standalone bypass: the rotating object still has the old runtime and `reserve()` rejects runtime/durable-generation mismatch; a new current-generation ledger must complete activation recovery before construction succeeds; stale runtime construction fails; raw SQLite writers remain LAB-087 scope. Recorded this as a composition boundary rather than opening a duplicate issue. It must be included in LAB-093/LAB-100 regressions because capability/runtime rebinding could invalidate those assumptions.

No production code was staged and no exact repository behavioral PASS is claimed.

## Evidence produced

- `research/2026-09-02-lab090-committed-before-release-window-audit.md` — commit `6e1e69b051ea35c928cff6b5d58908e7b04fcdbf`; #169 comment `5515032277`.
- `research/2026-09-02-lab090-cleanup-secondary-sqlite-dependency.md` — commit `7c2dc24f9d42bdef1a487350afb063f6a9733b0a`; #169 comment `5514259088`.
- `research/2026-09-02-lab090-post-prepare-connection-open-reservation-leak.md` — commit `4c488991a6150e00355d471fb1ec003623ad5574`; #169 comment `5513466831`.
- `research/2026-09-02-lab100-caller-owned-activation-state-authority.md` — commit `ee7b6ae09ecbd63617fded48e210f9292cdcec1b`; #185 comment `5512698359`.
- `research/2026-09-02-lab100-inherited-provider-rotate-breaks-activation-state.md` — commit `25297f0bb6812114e34b94673134d18c27f3c494`; #185 comment `5511876977`.
- `research/2026-09-02-lab100-activation-provider-subclass-authority.md` — commit `8b1abf6f9297a80f67a9e0111f19f78fc630bb9d`; issue #185.
- `research/2026-09-02-lab086-rowid-sentinel-sqlite-semantics-probe.md` — commit `04bdef2f6e94f315e4215da51a839c4633a79ff6`; #163 comment `5510181024`.
- `research/2026-09-02-lab098-surplus-bootstrap-activation-row.md` — commit `6ac5525cd0a832d220066716e637a6500c48d2a6`; #183 comment `5509380250`.
- `research/2026-09-02-lab099-historical-activation-ticket-rebinding.md` — commit `3b6e311b835d07a347def9643be90294e49ac42b`; issue #184.
- Retained prior evidence: LAB-098 deleted row `f46e3759...`; LAB-090 failed prepare `2af77704...`; LAB-097 orphan transition `6cfe5407...`; LAB-090 ordering `91f133b9...`, `3ca0f755...`; LAB-086 bridge `078b95c8...`; LAB-093 `fe484bae...`, `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 `cdb3bd98...`, `4ea3a667...`, `f74f1422...`; LAB-096 `ab541a60...`; LAB-097 bootstrap `8a765553...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Connector reads can expose exact predecessor/patch bytes, but this run still lacks a supported machine transformation bridge from connector payload -> patch application -> Git blob verification -> Contents write.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- Keep PRs #175/#177 draft until exact focused/integration/downstream gates execute.
- LAB-090 constructor: reject runtime-head mismatch before activation-schema mutation; verify complete activation history before any recovery mutation.
- LAB-090 fresh activation: once this attempt owns a newly-created valid PREPARED reservation, every subsequent fallible coordinator step must be inside exact-ticket cleanup scope. Cleanup must not depend on a secondary fallible DB read before abort and must never abort unrelated prior/idempotently returned activation state; if ownership cannot be inferred, add explicit provider attempt/provenance identity.
- LAB-090 `COMMITTED -> release` interval is not a standalone supported-surface bypass under current runtime-generation/construction checks, but integration tests must prove that LAB-093/LAB-100 capability rebinding cannot turn it into one.
- LAB-098: derive required activation records from authenticated transitions and require a bijection.
- LAB-099: bind exact historical activation ticket contents into independent authenticated evidence.
- LAB-100: exact-type acceptance alone is insufficient. Bind provider implementation, identity/key/state-machine authority, and activation-state ownership for the lifetime of pending/committed activation; reject generic inherited identity rotation while state is non-quiescent or define a proven activation-aware transition.
- Do not stage LAB-093/094/095/096/097/098/099/100 production code before their pre-fix REDs execute or an equivalently strong auditable execution path exists.

## Exact next action

LAB-086 first: probe for a supported byte-preserving machine composition operation for predecessor blob `d4a6a40f...` + retained patch `61841b58...`. If available, compose only that patch, require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090 pre-fix REDs before PR #175 production changes: constructor ordering, malformed/failed prepare cleanup, first post-prepare `_con()` failure, exception-handler `_activation_row()` failure, LAB-100 fake subclass/inherited rotation/caller-owned ActivationState cases, and `COMMITTED` durable acknowledgement with provider still `COMMITTED_FENCED` proving no supported writer path can create/execute a new intent before exact-ticket release. Then run LAB-098/099 REDs and PR #175/#177 full gates, followed by LAB-093/094/095/096/097 REDs.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen an existing issue rather than creating a duplicate when the finding shares the same authority boundary.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending; cleanup and composition regressions expanded.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY.
- #179 / LAB-094 — READY.
- #180 / LAB-095 — READY.
- #181 / LAB-096 — READY.
- #182 / LAB-097 — READY.
- #183 / LAB-098 — READY.
- #184 / LAB-099 — READY.
- #185 / LAB-100 — READY; provider implementation/capability/state authority RED/GREEN pending.
