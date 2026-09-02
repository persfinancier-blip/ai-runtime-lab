# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage remains: live predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 draft PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: raw capability exposure + public `attested` authority-slot rebinding source-proved; executable RED/GREEN pending.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; executable RED/GREEN pending.
- LAB-095 / #180 READY: database identity must be construction-bound; public path rebinding plus unchanged-path filesystem substitution now both covered at source/contract level.
- LAB-096 / #181 READY: provider-history strategy/capability slot publicly rebindable; executable RED/GREEN pending.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open PRs and #163. LAB-086 was probed first. Direct local clone again failed before repository execution with `Could not resolve host: github.com`, so no behavioral execution or security-critical source mutation was claimed.

Reconciled a stale-looking PR-body statement against durable LAB-086 evidence: PR #165 body still describes an older `eb219835...` publication, but the later durable lineage correction on the current branch explicitly records that subsequent work moved live `strict_fence.py` back to `d4a6a40f...`; #163 and this state remain authoritative for the pending hidden-rowid publication. Compare from historical executable commit `05d8e75a...` to current head shows later modifications to `strict_fence.py`, consistent with that correction.

With LAB-086 publication and exact execution still blocked, strengthened existing LAB-095 rather than creating a new issue. Source audit shows that a private/read-only pathname alone would not bind database authority: `_con()` reopens SQLite by pathname each operation, so an unchanged path can resolve to a replacement DB after construction. LAB-095 therefore needs database-instance/history identity, not merely immutable path spelling. Added a same-path DB-A -> DB-B substitution regression requirement and recommended evaluating one authenticated durable database-instance identifier verified on every fresh connection before authority decisions/mutations.

## Evidence produced

- `research/2026-09-02-lab095-pathname-is-not-database-identity.md` — main commit `4ea3a667251dc071b1d803d5ae733c0621e0fd19`; #180 comment `5502895398`.
- Prior retained evidence: LAB-093 notes/commits `2892b115...`, `5e81524d...`; LAB-094 `90735fdb...`; LAB-095 original `f74f1422...`; LAB-096 `ab541a60...`.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- This run still lacks a supported byte-preserving predecessor+patch -> complete Contents payload composition bridge.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution is unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PRs #175/#177 draft until their exact focused/integration/downstream gates execute.
- Do not stage LAB-093/094/095/096 production code before their specified pre-fix REDs execute, or an equivalently strong auditable execution path exists.
- For LAB-095, do not accept `_path`/read-only property or `Path.resolve()` alone as sufficient; same-path file substitution must fail closed on database-instance identity.

## Exact next action

LAB-086 first: re-check PR #165 head and probe for a supported byte-preserving transformation/write path that can consume exact `strict_fence.py` predecessor blob `d4a6a40f...` plus retained unified patch `61841b58...`. If available, conflict-check exact predecessor, compose only that patch, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 and #177 full gates, then LAB-093/094/095/096 pre-fix REDs before production changes. LAB-095 must include both explicit path rebinding and unchanged-path DB substitution.

If both remain unavailable, continue retained-authority audit only where it strengthens an existing LAB-093/094/095/096 issue with a concrete distinct trust/capability violation; do not multiply issues for subsumed findings.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact regression/full gate pending.
- #178 / LAB-093 — READY; executable RED/GREEN + implementation pending.
- #179 / LAB-094 — READY; executable RED/GREEN + implementation pending.
- #180 / LAB-095 — READY; database-instance identity contract now includes same-path substitution; executable RED/GREEN + implementation pending.
- #181 / LAB-096 — READY; executable RED/GREEN + implementation pending.
