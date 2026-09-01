# Current Lab State

Last updated: 2026-09-02

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 remains draft PR #175; branch `lab-090-provider-activation-fencing`; head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head; head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`.
- LAB-093 / #178 READY with concrete delegation-capability violation now proved at source level; regression-first implementation pending exact execution.
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; exact one-generation attacker-history regression fixture specified.
- LAB-095 / #180 READY: canonical non-rebindable ledger/provider-history DB identity; source audit and concrete DB-A -> invalid DB-B regression plan complete.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 was probed first. The GitHub connector can now return the complete predecessor source byte-for-byte via blob lookup (`d4a6a40f...`) and can return the retained hidden-rowid patch byte-for-byte (`61841b58...`). However, the available Contents writer still accepts only complete replacement UTF-8 text; there is no supported operation in this run that composes a fetched blob plus unified patch into a byte-preserving write. Manual/model reserialization of the security-critical ~949-line `strict_fence.py` remains prohibited, so no LAB-086 source mutation was attempted.

Used the recorded fallback to complete LAB-093/#178 source-level capability-boundary audit. The earlier observation that the constructor caller already owns `AttestedCatchup` is insufficient once a supported ledger is delegated to another component. `SharedAnchorLedger` stores the exact mutable runtime object as public `self.attested`; the supported wrapper inherits that exposure unchanged. A ledger-only recipient can therefore recover `ledger.attested`, call `catch_up_one()` or raw provider methods directly, and advance the external anchor without the ledger's durable `reserve -> effect -> confirm` protocol. This produces a concrete availability/correctness violation: external position can advance while `shared_anchor_meta` / `shared_anchor_intents` contain no corresponding durable intent, after which supported verification fails closed on unexplained advance.

LAB-090 broadens the same escape because `ledger.attested.provider` may be a `FencedActivationProvider` exposing `prepare_activation`, `commit_activation`, `release_activation`, and `abort_activation`, allowing a ledger-only recipient to manipulate provider activation state outside coordinator ordering. This is a delegation/capability-amplification defect, not a LAB-092 provenance bypass and not an authority escalation for the original constructor owner.

Derived least-capability contract: keep exact mutable runtime privately as `_attested`; internal `execute`/reauthenticate/verify/rotation paths use the private handle; public introspection, if compatibility requires it, exposes immutable identity/status only and never `catch_up_one`, raw `.provider`, activation mutation, verifier/keyring mutation, or handle replacement. Regression must model a ledger-only delegate and inspect equivalent escape paths, not merely assert that an `attested` attribute disappeared.

## Evidence produced

- `research/2026-09-02-lab093-ledger-delegation-capability-boundary.md` — main commit `2892b115344ba0279c8f1a1e946480de3abc2f98`; #178 comment `5501214504`.
- `research/2026-09-02-lab095-canonical-db-identity-source-audit.md` — main commit `f74f14220729e98b5c44e28bbfba30a89cca1a48`; #180 comment `5500592779`.
- `research/2026-09-01-lab094-exact-attacker-history-fixture.md` — main commit `90735fdbe6941096437cd3daaf58b4e90a3a49b2`; #179 comment `5499844588`.
- `research/2026-09-01-lab094-bootstrap-compatibility-and-regression-plan.md` — main commit `195dbb1c8e6e3abdabc860b95778368333354fc1`; #179 comment `5499114749`.
- Existing LAB-092 evidence remains: four post-construction provenance-deletion mutation surfaces guarded; exact PR #177 regression/full execution pending.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- The complete predecessor and retained patch are now both retrievable byte-exact through the connector, but this run still lacks a supported blob+patch -> complete Contents payload composition bridge.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- Exact checkout/source execution remains unavailable in this run; no fresh behavioral PASS is claimed.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Do not stage LAB-093 production code until the delegated-ledger pre-fix capability escape executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-094 production code until the exact pre-fix reject-then-accept bootstrap-rebinding regression executes, or an equivalently strong auditable execution path becomes available.
- Do not stage LAB-095 production code until the exact DB-A -> invalid DB-B pre-fix redirect/mutation regression executes, or an equivalently strong auditable execution path becomes available.
- Do not add further LAB-092 wrappers/regressions without a concrete supported mutation-before-provenance-validation path.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for a supported byte-preserving transformation/write path that can consume the complete fetched predecessor blob and retained unified patch without model reserialization. If available, conflict-check predecessor `d4a6a40f...`, compose only patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`, then PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Also execute LAB-093's delegated-ledger capability-escape pre-fix RED, LAB-094's one-generation attacker-history RED, and LAB-095's DB-A -> invalid DB-B redirect/mutation RED before any production changes for those issues.

If execution and LAB-086 byte-preserving publication remain unavailable, LAB-093/094/095 source contracts are now sufficiently specified. Continue with a cross-issue retained-authority audit for other public mutable construction-bound fields/handles only when a concrete incremental capability or trust-root violation can be demonstrated; create a new issue rather than widening LAB-092/093/094/095 scope.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; ledger-owned public-surface audit exhausted; exact regression/full gate pending.
- #178 / LAB-093 — READY; concrete delegated-ledger capability amplification proved; executable RED/GREEN and implementation pending exact execution.
- #179 / LAB-094 — READY; source contract + compatibility map + exact one-generation regression fixture complete; executable RED/GREEN and implementation pending exact execution.
- #180 / LAB-095 — READY; canonical DB identity contract + exact DB-A -> invalid DB-B regression plan complete; executable RED/GREEN and implementation pending exact execution.
