# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor ordering, failed-prepare reservation, and activation-provider implementation/state-authority defects remain pending exact RED/GREEN.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: outer + nested attested/provider/verifier/keyring capability rebinding.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust root.
- LAB-095 / #180 READY: construction-bound authenticated logical database/history identity.
- LAB-096 / #181 READY: provider-history strategy/capability rebinding.
- LAB-097 / #182 READY: provider-history deletion/rebootstrap + orphan-transition acceptance.
- LAB-098 / #183 READY: activation-record set completeness/bijection.
- LAB-099 / #184 READY: historical activation ticket contents require independent authenticated binding.
- LAB-100 / #185 READY: activation-provider implementation/capability/state authority; exact provider class inherits identity/key mutation that can strand pending activation state and also accepts/re-exposes caller-owned mutable `ActivationState`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. Re-probed direct Git transport in the current runtime; it failed before repository execution with `Could not resolve host: github.com`.

LAB-086 therefore remains blocked specifically on the safe byte-preserving composition/publication bridge; no security-critical source was manually/model-reserialized and no fresh behavioral PASS was claimed.

Fallback-audited PR #175 / LAB-100 rather than opening a duplicate issue. Found that exact provider type enforcement is still insufficient when `FencedActivationProvider` accepts a caller-supplied mutable `ActivationState` and stores that same authority object publicly as `self.activation_state`. The activation lifecycle and `increment()` directly trust public mutable `pending`, `committed`, and `next_fence`. An external holder of the same state reference can clear `pending` without `release_activation()` / `abort_activation()`, making the exact provider stop observing the activation fence; committed/fence state is similarly externally mutable. An isolated reference-semantics probe reproduced pending-present -> external clear -> pending-absent.

Recorded this as a strengthening of LAB-100, not a new issue. No production code was staged because exact repository RED/GREEN execution remains unavailable.

## Evidence produced

- `research/2026-09-02-lab100-caller-owned-activation-state-authority.md` — commit `ee7b6ae09ecbd63617fded48e210f9292cdcec1b`; #185 comment `5512698359`.
- `research/2026-09-02-lab100-inherited-provider-rotate-breaks-activation-state.md` — commit `25297f0bb6812114e34b94673134d18c27f3c494`; #185 comment `5511876977`.
- `research/2026-09-02-lab100-activation-provider-subclass-authority.md` — commit `8b1abf6f9297a80f67a9e0111f19f78fc630bb9d`; issue #185.
- `research/2026-09-02-lab086-rowid-sentinel-sqlite-semantics-probe.md` — commit `04bdef2f6e94f315e4215da51a839c4633a79ff6`; #163 comment `5510181024`.
- `research/2026-09-02-lab098-surplus-bootstrap-activation-row.md` — commit `6ac5525cd0a832d220066716e637a6500c48d2a6`; #183 comment `5509380250`.
- `research/2026-09-02-lab099-historical-activation-ticket-rebinding.md` — commit `3b6e311b835d07a347def9643be90294e49ac42b`; issue #184.
- Retained prior evidence: LAB-098 deleted row `f46e3759...`; LAB-090 failed prepare `2af77704...`; LAB-097 orphan transition `6cfe5407...`; LAB-090 ordering `91f133b9...`, `3ca0f755...`; LAB-086 bridge `078b95c8...`; LAB-093 `fe484bae...`, `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 `cdb3bd98...`, `4ea3a667...`, `f74f1422...`; LAB-096 `ab541a60...`; LAB-097 bootstrap `8a765553...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Connector reads expose exact predecessor/patch bytes, but this run still lacks a supported machine transformation bridge that consumes those exact connector payloads, applies only the retained patch, verifies Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- Keep PRs #175/#177 draft until exact focused/integration/downstream gates execute.
- LAB-090 constructor: reject runtime-head mismatch before activation-schema mutation; verify complete activation history before any recovery mutation.
- LAB-090 fresh activation: prepare must not strand a newly-created provider reservation when ticket/status validation fails before SQL; cleanup must never abort unrelated prior activation state.
- LAB-098: derive required activation records from authenticated transitions and require a bijection.
- LAB-099: bind exact historical activation ticket contents into independent authenticated evidence.
- LAB-100: exact-type acceptance is not sufficient by itself. Bind provider implementation, identity/key/state-machine authority, and ownership of activation state for the lifetime of pending/committed activation. Reject generic inherited identity rotation while activation state is non-quiescent (or define/prove an activation-aware transition), and do not permit caller-owned/raw mutable `ActivationState` to serve as the trusted fence-state authority through the supported capability surface.
- Do not stage LAB-093/094/095/096/097/098/099/100 production code before their pre-fix REDs execute or an equivalently strong auditable execution path exists.

## Exact next action

LAB-086 first: probe for a supported byte-preserving machine composition operation for predecessor blob `d4a6a40f...` + retained patch `61841b58...`. If available, compose only that patch, require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090 pre-fix REDs before PR #175 production changes: (1) runtime-head mismatch before schema installation; (2) invalid historical activation before recovery side effects; (3) malformed/failed prepare without stranded reservation; (4) LAB-100 fake `FencedActivationProvider` subclass returning valid-looking lifecycle values without a real provider-side fence; (5) LAB-100 exact `FencedActivationProvider` with a valid pending ticket followed by inherited identity/generation rotation; (6) LAB-100 exact provider with caller-retained `ActivationState`, valid PREPARED ticket, then out-of-band raw state mutation proving the fence/state authority is externally mutable. Then run LAB-098/099 REDs and PR #175/#177 full gates, followed by LAB-093/094/095/096/097 REDs.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues; strengthen an existing issue rather than creating a duplicate when the finding shares the same authority boundary.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY.
- #179 / LAB-094 — READY.
- #180 / LAB-095 — READY.
- #181 / LAB-096 — READY.
- #182 / LAB-097 — READY.
- #183 / LAB-098 — READY.
- #184 / LAB-099 — READY.
- #185 / LAB-100 — READY; provider implementation/capability authority now includes exact-class inherited identity rotation and caller-owned mutable activation-state authority; RED/GREEN pending.
