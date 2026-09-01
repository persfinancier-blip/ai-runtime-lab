# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains draft PR #175; branch `lab-090-provider-activation-fencing`; head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head; head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: caller-owned `AttestedCatchup` / provider capability encapsulation.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; exact one-generation attacker-history regression fixture specified.
- LAB-095 / #180 READY: canonical non-rebindable ledger/provider-history DB identity; source audit and concrete DB-A -> invalid DB-B regression plan now complete.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues, active PRs and LAB-09x branches. Probed LAB-086 first: fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository code execution with `Could not resolve host: github.com`; no LAB-086 branch/source mutation was attempted.

Used the allowed fallback to complete LAB-095/#180 source-level lifetime DB-identity audit. Confirmed supported composition retains two independently rebindable durable authority references: base shared-anchor `ledger.path` and `provider_history.path`. Ledger `_con()` selects the former; standalone history APIs select the latter; integrated `_current_locked(q)` follows the already-open ledger connection rather than re-running full history verification. LAB-092 adds separate `_classify(self.path)` checks on ledger/history surfaces, so path divergence can make provenance checks target different DBs rather than removing the split.

Specified the strongest minimal reproduction: valid DB A with bootstrap g1/current g2; DB B with shared-anchor schema and superficially matching current g2 head but no valid g1->g2 continuity. Fresh supported construction against B must reject under full `verify_durable()`. Pre-fix, a live ledger constructed against A can rebind `ledger.path = DB_B`; `reserve()` then opens B, calls `_current_locked(q)` (head-only, no bootstrap-chain verification), and can mutate B. This proves post-construction rebinding can redirect the durable authority target to a DB that fresh construction would reject.

Minimal contract derived: one construction-bound canonical immutable DB identity, private storage, getter-only `path` if compatibility requires introspection, all `_con()`/schema/provenance classifiers consume that identity, and composed ledger/history identities cannot diverge. Do not use a generic object freeze and do not mix LAB-094 bootstrap immutability or LAB-093 caller-owned provider capability into this patch.

## Evidence produced

- `research/2026-09-02-lab095-canonical-db-identity-source-audit.md` — main commit `f74f14220729e98b5c44e28bbfba30a89cca1a48`; #180 comment `5500592779`.
- `research/2026-09-01-lab094-exact-attacker-history-fixture.md` — main commit `90735fdbe6941096437cd3daaf58b4e90a3a49b2`; #179 comment `5499844588`.
- `research/2026-09-01-lab094-bootstrap-compatibility-and-regression-plan.md` — main commit `195dbb1c8e6e3abdabc860b95778368333354fc1`; #179 comment `5499114749`.
- `research/2026-09-01-lab094-bootstrap-trust-root-contract.md` — main commit `c3e5a5d7dee036df33135f0aec5159871594b40d`.
- Existing LAB-092 evidence remains: four post-construction provenance-deletion mutation surfaces guarded; exact PR #177 regression/full execution pending.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; exact checkout/source execution is unavailable in this run because direct git transport fails DNS.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Do not stage LAB-094 production code until the exact pre-fix reject-then-accept bootstrap-rebinding regression executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-095 production code until the exact DB-A -> invalid DB-B pre-fix redirect/mutation regression executes, or an equivalently strong auditable execution path becomes available.
- Do not add further LAB-092 wrappers/regressions without a concrete supported mutation-before-provenance-validation path.
- Do not patch caller-owned `attested`/provider exposure inside LAB-092; #178/LAB-093 owns it.
- Do not patch bootstrap trust-root lifetime only in LAB-092; #179/LAB-094 owns it.
- Do not patch mutable DB identity only in LAB-092; #180/LAB-095 owns it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`, then PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Also execute LAB-094's one-generation attacker-history pre-fix RED and LAB-095's DB-A -> invalid DB-B pre-fix redirect/mutation RED before any production changes for those issues.

If execution and LAB-086 byte-preserving publication remain unavailable, LAB-094 and LAB-095 source plans are now complete enough. Move next to LAB-093/#178 source-level capability-boundary audit: determine whether `ledger.attested` exposure creates any property violation beyond capabilities the caller already owns, map exact internal uses needed by LAB-080/LAB-090, and derive a least-capability contract only if a concrete incremental violation exists. Do not stage production code without a proof/reproduction.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; ledger-owned public-surface audit exhausted; exact regression/full gate pending.
- #178 / LAB-093 — READY; next source-level fallback if execution remains unavailable.
- #179 / LAB-094 — READY; source contract + compatibility map + exact one-generation regression fixture complete; executable RED/GREEN and implementation pending exact execution.
- #180 / LAB-095 — READY; canonical DB identity contract + exact DB-A -> invalid DB-B regression plan complete; executable RED/GREEN and implementation pending exact execution.
