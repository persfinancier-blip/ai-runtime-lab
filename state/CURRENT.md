# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor ordering and failed-prepare reservation defects remain pending exact RED/GREEN.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: outer + nested attested/provider/verifier/keyring capability rebinding.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust root.
- LAB-095 / #180 READY: construction-bound authenticated logical database/history identity.
- LAB-096 / #181 READY: provider-history strategy/capability rebinding.
- LAB-097 / #182 READY: provider-history deletion/rebootstrap + orphan-transition acceptance.
- LAB-098 / #183 READY: activation-record set completeness/bijection — missing/deleted required rows and surplus rows not backed by authenticated transitions.
- LAB-099 / #184 READY: historical `COMMITTED` activation ticket contents can be coherently rebound because current transition evidence does not authenticate `activation_id`, `expected_position`, or `fence`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. Re-probed direct git transport; it failed before repository execution with `Could not resolve host: github.com`.

Re-confirmed PR #165 remains draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, with `strict_fence.py` still exact predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. Retained patch `61841b58be42b01b97ca223567cbf9f428f7f0ce` is readable in full through the connector; required target blob `b78e7c98e35138719f77c482c7f1aab36b702de7` still returns 404 and therefore cannot be reused as an existing Git object.

Performed an isolated in-memory SQLite semantic probe of the retained patch's two-stage hidden-rowid sentinel mechanism. Ordinary implicit-rowid insertion succeeded; explicit `INSERT OR REPLACE` on an existing rowid was blocked before replacement; explicit `rowid=-1` was rolled back by the AFTER sentinel; same-rowid+same-key collision was blocked; a genuinely new explicit rowid remained insertable. No bypass was found in this specific mechanism. This is mechanism-level evidence only, not an exact PR behavioral PASS.

## Evidence produced

- `research/2026-09-02-lab086-rowid-sentinel-sqlite-semantics-probe.md` — commit `04bdef2f6e94f315e4215da51a839c4633a79ff6`; #163 comment `5510181024`.
- `research/2026-09-02-lab098-surplus-bootstrap-activation-row.md` — commit `6ac5525cd0a832d220066716e637a6500c48d2a6`; #183 comment `5509380250`.
- `research/2026-09-02-lab099-historical-activation-ticket-rebinding.md` — commit `3b6e311b835d07a347def9643be90294e49ac42b`; issue #184; #169 comment `5508684493`.
- `research/2026-09-02-lab098-deleted-activation-row-bypasses-recovery.md` — commit `f46e3759a5e3ad41846036d74625cb57f481a1ca`; issue #183.
- `research/2026-09-02-lab090-malformed-prepare-ticket-reservation-cleanup.md` — commit `2af77704a2f564cfd7b2cdd91fec68f50280f7ee`; #169 comment `5507313237`.
- `research/2026-09-02-lab097-orphan-transition-survives-rebootstrap.md` — commit `6cfe5407800ac14817956cb022b3297f53690d07`; #182 comment `5506608681`.
- Retained prior evidence: LAB-090 ordering `91f133b9...`, `3ca0f755...`; LAB-086 bridge `078b95c8...`; LAB-093 `fe484bae...`, `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 `cdb3bd98...`, `4ea3a667...`, `f74f1422...`; LAB-096 `ab541a60...`; LAB-097 bootstrap `8a765553...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Connector reads expose exact predecessor/patch bytes, but this run still lacks a supported machine transformation bridge that consumes those exact connector payloads, applies only the retained patch, verifies Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API.
- Publish LAB-086 only from `d4a6a40f... + 61841b58...`, require target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- The isolated rowid-sentinel probe supports the retained patch mechanism but does not replace hidden-rowid/receipt-NULL/alternate-UNIQUE real-schema regressions.
- Keep PRs #175/#177 draft until exact focused/integration/downstream gates execute.
- LAB-090 constructor: reject runtime-head mismatch before activation-schema mutation; verify complete activation history before any recovery mutation.
- LAB-090 fresh activation: prepare must not strand a newly-created provider reservation when ticket/status validation fails before SQL; cleanup must never abort unrelated prior activation state.
- LAB-098: derive the exact activation-record set from authenticated provider-generation transitions and require a bijection. Missing required current/historical records and surplus records (including bootstrap activation rows) must fail closed before mutation.
- LAB-099: completeness/bijection alone is insufficient. Exact ticket contents for each historical activation must also be authenticated by evidence independent of the mutable activation row; a self-hash in the same row is insufficient.
- Do not stage LAB-093/094/095/096/097/098/099 production code before their pre-fix REDs execute or an equivalently strong auditable execution path exists.

## Exact next action

LAB-086 first: probe for a supported byte-preserving machine composition operation for predecessor blob `d4a6a40f...` + retained patch `61841b58...`. If available, compose only that patch, require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit. Do not repeat the isolated rowid-sentinel semantic probe unless the retained patch changes.

If exact source execution becomes available first, run LAB-090 pre-fix REDs before PR #175 production changes: (1) runtime-head mismatch before schema installation; (2) invalid historical activation before recovery side effects; (3) malformed/failed prepare without stranded reservation. Then run LAB-098 REDs for missing current/historical activation records plus surplus bootstrap/non-transition activation records, requiring fail-closed behavior before provider/SQLite mutation. Then run LAB-099 REDs for historical `COMMITTED` ticket-field rebinding (`expected_position`, `activation_id`, `fence`, including coherent multi-field rewrite). Then run PR #175/#177 full gates, followed by LAB-093/094/095/096/097 REDs.

If neither becomes available, continue audit only for concrete distinct trust/capability/fail-closed violations not subsumed by existing issues.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY; executable RED/GREEN + implementation pending.
- #179 / LAB-094 — READY; executable RED/GREEN + implementation pending.
- #180 / LAB-095 — READY; executable RED/GREEN + implementation pending.
- #181 / LAB-096 — READY; provider-history strategy/capability rebinding RED/GREEN + implementation pending.
- #182 / LAB-097 — READY; deletion/orphan-transition RED/GREEN + authenticated initialization provenance pending.
- #183 / LAB-098 — READY; activation-record bijection RED/GREEN + transition-derived completeness design pending.
- #184 / LAB-099 — READY; historical activation ticket provenance RED/GREEN + authenticated ticket-binding design pending.
