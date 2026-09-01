# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains draft PR #175; branch `lab-090-provider-activation-fencing`; head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head; head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY with concrete delegation-capability violation proved at source level; regression-first implementation pending exact execution.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; exact one-generation attacker-history regression fixture specified.
- LAB-095 / #180 READY: canonical non-rebindable ledger/provider-history DB identity; source audit and concrete DB-A -> invalid DB-B regression plan complete.
- LAB-096 / #181 READY: provider-history strategy/capability slot is publicly rebindable; source audit proves a delegated ledger holder can replace the trusted history implementation / create split authority.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 was probed first. Direct Git transport again failed before repository execution with `Could not resolve host: github.com`; no source mutation or behavioral execution was claimed.

Used the recorded fallback to continue the retained-authority audit only where a concrete incremental violation could be demonstrated. Found that `HistoricalSharedAnchorLedger` stores its live provider-history helper as public mutable `self.provider_history`, then repeatedly trusts methods reached through that slot in supported operations: `reserve()` -> `_current_locked(q)`, `rotate_provider()` -> `_rotate_locked(q, ...)`, runtime checks -> `current()`, reauthentication -> `current()/load_receipt()/store_receipt()`, and durable verification -> `_verify_durable_locked(q)` / `_load_receipt_locked(q)`.

This is distinct from the existing mutable-data findings. A ledger-only delegate can replace the strategy/capability object itself, thereby replacing the implementation trusted for provider-generation identity, history verification, receipt verification/storage, and rotation. A permissive replacement can alter authority decisions while the ledger continues using supported DB mutation paths. A second, non-synthetic case exists with another legitimate `IntegratedProviderHistory`: locked helpers receive the ledger's already-open DB-A connection, while ordinary methods on the replacement object open that object's own DB, creating method-dependent split authority.

Opened #181 / LAB-096 with a construction-bound private-history contract and two regression-first requirements: a permissive delegated-strategy replacement and a legitimate DB-A ledger + DB-B history replacement. No production code was staged because exact execution is still unavailable.

## Evidence produced

- `research/2026-09-02-lab096-provider-history-strategy-rebinding-audit.md` — commit `ab541a6017e33703c5077551520556137c587db1`; issue #181.
- `research/2026-09-02-lab093-ledger-delegation-capability-boundary.md` — main commit `2892b115344ba0279c8f1a1e946480de3abc2f98`; #178 comment `5501214504`.
- `research/2026-09-02-lab095-canonical-db-identity-source-audit.md` — main commit `f74f14220729e98b5c44e28bbfba30a89cca1a48`; #180 comment `5500592779`.
- `research/2026-09-01-lab094-exact-attacker-history-fixture.md` — main commit `90735fdbe6941096437cd3daaf58b4e90a3a49b2`; #179 comment `5499844588`.
- `research/2026-09-01-lab094-bootstrap-compatibility-and-regression-plan.md` — main commit `195dbb1c8e6e3abdabc860b95778368333354fc1`; #179 comment `5499114749`.
- Existing LAB-092 evidence remains: four post-construction provenance-deletion mutation surfaces guarded; exact PR #177 regression/full execution pending.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- The complete predecessor and retained patch are retrievable byte-exact through the connector, but this run still lacks a supported blob+patch -> complete Contents payload composition bridge.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Do not stage LAB-093 production code until the delegated-ledger pre-fix capability escape executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-094 production code until the exact pre-fix reject-then-accept bootstrap-rebinding regression executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-095 production code until the exact DB-A -> invalid DB-B pre-fix redirect/mutation regression executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-096 production code until at least one concrete pre-fix strategy-rebinding RED executes; prefer both the permissive replacement and legitimate DB-A/DB-B split-authority cases.
- Do not add further LAB-092 wrappers/regressions without a concrete supported mutation-before-provenance-validation path.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for a supported byte-preserving transformation/write path that can consume the complete fetched predecessor blob and retained unified patch without model reserialization. If available, conflict-check predecessor `d4a6a40f...`, compose only patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`, then PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Also execute LAB-093's delegated-ledger capability-escape pre-fix RED, LAB-094's one-generation attacker-history RED, LAB-095's DB-A -> invalid DB-B redirect/mutation RED, and LAB-096's provider-history strategy-rebinding RED before any production changes for those issues.

If execution and LAB-086 byte-preserving publication remain unavailable, continue the retained-authority audit only for construction-bound public mutable fields/handles where a new capability/trust-root/strategy violation can be demonstrated. Do not multiply issues for cosmetic mutability or findings already subsumed by LAB-093/094/095/096.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; ledger-owned public-surface audit exhausted; exact regression/full gate pending.
- #178 / LAB-093 — READY; concrete delegated-ledger capability amplification proved; executable RED/GREEN and implementation pending exact execution.
- #179 / LAB-094 — READY; source contract + compatibility map + exact one-generation regression fixture complete; executable RED/GREEN and implementation pending exact execution.
- #180 / LAB-095 — READY; canonical DB identity contract + exact DB-A -> invalid DB-B regression plan complete; executable RED/GREEN and implementation pending exact execution.
- #181 / LAB-096 — READY; provider-history strategy/capability rebinding and legitimate split-authority case proved at source level; executable RED/GREEN and implementation pending exact execution.
