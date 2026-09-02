# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; constructor audit requires runtime-head verification before schema mutation and complete activation-history verification before recovery side effects.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: outer + nested attested/provider/verifier/keyring capability rebinding; executable RED/GREEN pending.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust root; executable RED/GREEN pending.
- LAB-095 / #180 READY: construction-bound authenticated logical database/history identity; executable RED/GREEN pending.
- LAB-096 / #181 READY: provider-history strategy/capability rebinding; executable RED/GREEN pending.
- LAB-097 / #182 READY: provider-history deletion/rebootstrap plus orphan-transition acceptance; executable repository RED/GREEN pending.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 was probed first. Direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository execution with `Could not resolve host: github.com`; no LAB-086 source mutation or new behavioral PASS was claimed.

Fallback work strengthened existing LAB-097/#182 rather than opening another issue. Source inspection showed `verify_durable()` verifies only transition rows required by adjacent descriptors in the currently visible generation chain; it does not enumerate and reject orphan rows in `provider_generation_transitions`.

Executed file-backed SQLite semantics probe: valid g1->g2 -> delete provider head + all generation rows while retaining the authenticated g1->g2 transition row -> current empty-head initialization reconstructs bootstrap g1 -> one-generation terminal verification conditions accept with one surviving orphan transition. This proves partial history loss can retain positive evidence of prior g2 while startup silently normalizes active history back to g1.

## Evidence produced

- `research/2026-09-02-lab097-orphan-transition-survives-rebootstrap.md` — main commit `6cfe5407800ac14817956cb022b3297f53690d07`; #182 comment `5506608681`.
- Prior LAB-097 evidence: `research/2026-09-02-lab097-provider-history-empty-state-rebootstrap.md` — commit `8a765553fa0219d240868a0e18fef20626c1fd8f`.
- Retained prior evidence: LAB-090 ordering notes `91f133b9...`, `3ca0f755...`; LAB-086 bridge note `078b95c8...`; LAB-093 notes `fe484bae...`, `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 `cdb3bd98...`, `4ea3a667...`, `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Connector reads expose exact predecessor/patch bytes, but this run still lacks a supported machine transformation bridge that consumes those exact bytes, applies only the retained patch, verifies Git blob `b78e7c98...`, and supplies the complete result to the normal Contents API.
- Publish LAB-086 only from `d4a6a40f... + 61841b58...`, require target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh repository behavioral PASS is claimed.
- Keep PRs #175/#177 draft until exact focused/integration/downstream gates execute.
- LAB-090: reject runtime-head mismatch before activation-schema mutation; verify complete activation history before any recovery mutation.
- Do not stage LAB-093/094/095/096/097 production code before their pre-fix REDs execute or an equivalently strong auditable execution path exists.
- LAB-093: an outer read-only property returning raw mutable `AttestedCatchup` is insufficient; nested provider/verifier/expected/keyring aliases must not leak.
- LAB-095: path-only, `Path.resolve()`, inode/device identity, or a self-asserted database UUID alone are insufficient; newly opened target must prove authenticated logical history rooted at construction-bound authority.
- LAB-097: distinguish genuine first bootstrap from prior-history loss before any bootstrap/history/head write. `COUNT(*) == 0` is insufficient. Verification must also reject orphan transition/history evidence outside the authenticated contiguous chain; surviving transition rows are proof the DB is not a fresh bootstrap target.

## Exact next action

LAB-086 first: probe for a supported byte-preserving machine composition operation for predecessor blob `d4a6a40f...` + retained patch `61841b58...`. If available, compose only that patch, require candidate Git blob `b78e7c98...`, conflict-check PR #165 still contains the predecessor, publish through normal Contents API, re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080->086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, run LAB-090 constructor pre-fix regressions before PR #175 production changes, then PR #175/#177 full gates. Next run LAB-093/094/095/096/097 REDs. LAB-097 RED set must include: (1) complete history deletion -> silent g1 rebootstrap; (2) head+generation deletion while leaving g1->g2 transition -> silent g1 rebootstrap despite orphan evidence; post-fix both must fail before mutation and leave tampered state unchanged.

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
- #181 / LAB-096 — READY; executable RED/GREEN + implementation pending.
- #182 / LAB-097 — READY; complete-deletion and orphan-transition rebootstrap RED/GREEN + authenticated initialization provenance design pending.
