# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains draft PR #175; branch `lab-090-provider-activation-fencing`; head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head; head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY: raw capability exposure plus public `attested` authority-slot rebinding are source-proved; regression-first implementation pending exact execution.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; exact one-generation attacker-history regression fixture specified.
- LAB-095 / #180 READY: canonical non-rebindable ledger/provider-history DB identity; source audit and concrete DB-A -> invalid DB-B regression plan complete.
- LAB-096 / #181 READY: provider-history strategy/capability slot is publicly rebindable; source audit proves a delegated ledger holder can replace the trusted history implementation / create split authority.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 was probed first.

Detected that PR #165 head has advanced to `ee210a47221b6df53f3518aa3af74f76c5b0122b`, but direct inspection of `experiments/asymmetric_break_glass_history/strict_fence.py` at that exact head still reports Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`: the authoritative predecessor, not required hidden-rowid target `b78e7c98...`. The retained patch file remains exact blob `61841b58...`. Direct local Git clone was probed again and failed before repository execution with `Could not resolve host: github.com`; no LAB-086 source mutation or behavioral execution was claimed.

Used the recorded fallback to continue only a concrete retained-authority finding already within an existing issue rather than multiplying issues. Strengthened LAB-093: `ledger.attested` is not only a route to recover the caller-owned raw provider capability; it is itself a publicly replaceable authority slot. Supported `_provider()`, `_reauthenticate()`, `execute()`, and `verify_component()` dispatch through it, and `HistoricalSharedAnchorLedger._require_runtime_matches_durable_head()` compares generation identity, not external anchor-instance identity. A ledger-only delegate can therefore replace `ledger.attested` with another exact `AttestedCatchup` carrying the same provider generation/key but independent provider state and redirect supported authenticated operations to that other anchor instance without reconstructing the ledger.

Recorded this as part of LAB-093, not a new issue. The implementation contract now explicitly requires a private active attested handle with changes only through validated transition paths such as successful provider rotation. Added a regression-first same-generation/key split-anchor substitution case.

## Evidence produced

- `research/2026-09-02-lab093-attested-slot-rebinding-audit.md` — commit `5e81524da3fc9419c624036af32ce5c7e37fccbd`; #178 comment `5502417697`.
- `research/2026-09-02-lab096-provider-history-strategy-rebinding-audit.md` — commit `ab541a6017e33703c5077551520556137c587db1`; issue #181.
- `research/2026-09-02-lab093-ledger-delegation-capability-boundary.md` — main commit `2892b115344ba0279c8f1a1e946480de3abc2f98`; #178 comment `5501214504`.
- `research/2026-09-02-lab095-canonical-db-identity-source-audit.md` — main commit `f74f14220729e98b5c44e28bbfba30a89cca1a48`; #180 comment `5500592779`.
- `research/2026-09-01-lab094-exact-attacker-history-fixture.md` — main commit `90735fdbe6941096437cd3daaf58b4e90a3a49b2`; #179 comment `5499844588`.
- Existing LAB-092 evidence remains: four post-construction provenance-deletion mutation surfaces guarded; exact PR #177 regression/full execution pending.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- The complete predecessor and retained patch are retrievable byte-exact through the connector, but this run still lacks a supported blob+patch -> complete Contents payload composition bridge.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Do not stage LAB-093 production code until the delegated-ledger raw-capability and attested-slot-rebinding pre-fix REDs execute, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-094 production code until the exact pre-fix reject-then-accept bootstrap-rebinding regression executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-095 production code until the exact DB-A -> invalid DB-B pre-fix redirect/mutation regression executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-096 production code until at least one concrete pre-fix strategy-rebinding RED executes; prefer both the permissive replacement and legitimate DB-A/DB-B split-authority cases.
- Do not add further LAB-092 wrappers/regressions without a concrete supported mutation-before-provenance-validation path.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for a supported byte-preserving transformation/write path that can consume exact `strict_fence.py` predecessor blob `d4a6a40f...` and retained unified patch `61841b58...` without model reserialization. Re-check PR #165 head first because branch state may advance between runs. If available, conflict-check exact predecessor, compose only the retained patch, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`, then PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Also execute LAB-093's two pre-fix REDs (raw capability escape and same-generation/key `attested` slot substitution), LAB-094's one-generation attacker-history RED, LAB-095's DB-A -> invalid DB-B redirect/mutation RED, and LAB-096's provider-history strategy-rebinding RED before any production changes for those issues.

If execution and LAB-086 byte-preserving publication remain unavailable, continue the retained-authority audit only where it strengthens an existing construction-bound authority issue or demonstrates a genuinely distinct capability/trust-root/strategy violation. Do not create new issues for findings already subsumed by LAB-093/094/095/096.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; ledger-owned public-surface audit exhausted; exact regression/full gate pending.
- #178 / LAB-093 — READY; raw capability amplification plus replaceable attested authority slot proved; executable RED/GREEN and implementation pending exact execution.
- #179 / LAB-094 — READY; source contract + compatibility map + exact one-generation regression fixture complete; executable RED/GREEN and implementation pending exact execution.
- #180 / LAB-095 — READY; canonical DB identity contract + exact DB-A -> invalid DB-B regression plan complete; executable RED/GREEN and implementation pending exact execution.
- #181 / LAB-096 — READY; provider-history strategy/capability rebinding and legitimate split-authority case proved at source level; executable RED/GREEN and implementation pending exact execution.
