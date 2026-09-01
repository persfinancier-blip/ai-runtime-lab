# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains draft PR #175; branch `lab-090-provider-activation-fencing`; head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head; head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: caller-owned `AttestedCatchup` / provider capability encapsulation.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; exact one-generation attacker-history regression fixture is now specified against the current schema.
- LAB-095 / #180 READY: canonical non-rebindable ledger/provider-history DB identity.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. Probed LAB-086 first: fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository code execution with `Could not resolve host: github.com`; no LAB-086 branch/source mutation was attempted.

Continued LAB-094/#179 only to the allowed source-level boundary. Re-read exact current `experiments/provider_generation_history/protocol.py` and `tests/test_protocol.py` and reduced the planned security reproduction to a minimal one-generation substituted-history fixture. No transition row or historical receipt is required: construct with legitimate `g1`, directly replace `provider_generations` plus `provider_generation_head` with an internally self-consistent `attacker_g1`, prove `verify_durable()` rejects under the construction bootstrap, then rebind public `h.bootstrap = attacker_g1` and prove current pre-fix verification accepts. This isolates trust-root rebinding as the only variable.

The intended post-RED production contract remains minimal: private `_bootstrap`, getter-only `bootstrap` if introspection is needed, and all bootstrap-sensitive init/verification paths consume `_bootstrap`. Do not mix in DB-path identity (#180) or caller-owned provider capability (#178).

## Evidence produced

- `research/2026-09-01-lab094-exact-attacker-history-fixture.md` — main commit `90735fdbe6941096437cd3daaf58b4e90a3a49b2`; #179 comment `5499844588`.
- `research/2026-09-01-lab094-bootstrap-compatibility-and-regression-plan.md` — main commit `195dbb1c8e6e3abdabc860b95778368333354fc1`; #179 comment `5499114749`.
- `research/2026-09-01-lab094-bootstrap-trust-root-contract.md` — main commit `c3e5a5d7dee036df33135f0aec5159871594b40d`.
- Existing LAB-092 evidence remains: four post-construction provenance-deletion mutation surfaces guarded; exact PR #177 regression/full execution pending.
- Existing LAB-095 evidence remains: public mutable ledger/provider-history DB paths independently select durable authority targets.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; exact checkout/source execution is unavailable in this run because direct git transport fails DNS.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Do not stage LAB-094 production code until the exact pre-fix reject-then-accept bootstrap-rebinding regression executes, or an equivalently strong auditable execution path becomes available.
- Do not add further LAB-092 wrappers/regressions without a concrete supported mutation-before-provenance-validation path.
- Do not patch caller-owned `attested`/provider exposure inside LAB-092; #178/LAB-093 owns it.
- Do not patch bootstrap trust-root lifetime only in LAB-092; #179/LAB-094 owns it.
- Do not patch mutable DB identity only in LAB-092; #180/LAB-095 owns it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`, then PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Also execute the LAB-094 standalone one-generation attacker-history regression against pre-fix source before any LAB-094 production change. Do not integrate either draft before their gates.

If execution and LAB-086 byte-preserving publication remain unavailable, LAB-094 source planning is now complete enough. Move next to LAB-095/#180 source-level lifetime DB-identity audit: enumerate every path consumer and composed ledger/history divergence route, derive the smallest non-rebindable canonical-identity contract, and prepare a concrete DB-A -> DB-B regression plan without staging production code.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; ledger-owned public-surface audit exhausted; exact regression/full gate pending.
- #178 / LAB-093 — READY.
- #179 / LAB-094 — READY; source contract + compatibility map + exact one-generation regression fixture complete; executable RED/GREEN and implementation pending exact execution.
- #180 / LAB-095 — READY; next source-level fallback if execution remains unavailable.
