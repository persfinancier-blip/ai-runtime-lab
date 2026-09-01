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
- LAB-094 / #179 READY: immutable provider-history bootstrap trust-root lifetime contract; architecture/source contract now documented.
- LAB-095 / #180 READY: canonical non-rebindable ledger/provider-history DB identity.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. Probed LAB-086 first: fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository code execution with `Could not resolve host: github.com`; no LAB-086 branch/source mutation was attempted.

Completed the remaining LAB-092 ledger-owned public-surface/return-object audit. No additional supported mutation-before-provenance-validation path was found beyond the four already guarded surfaces (`reserve`/`execute`, `rotate_provider`, mutation-capable `verify_component`, public `provider_history.store_receipt`). `entry()` and `watermark()` are read-only; returned `LedgerEntry`, `GenerationDescriptor`, and `HistoricalReceipt` are frozen/value-like; remaining live provider-history public methods are read-only/value-construction or coordinator-blocked. Treat this LAB-092 audit surface as exhausted unless a new concrete bypass is demonstrated.

Promoted LAB-094 source/architecture work without staging unexecuted code. Confirmed `DurableProviderHistory.__init__()` stores caller-validated `bootstrap` in a public rebindable slot and both `DurableProviderHistory.verify_durable()` and `IntegratedProviderHistory._verify_durable_locked()` later consume that slot as the authenticated root of durable history. Defined the minimum lifetime contract: original bootstrap identity is immutable for the object's lifetime; a different bootstrap requires fresh construction/full verification. Preferred implementation is private retained `_bootstrap` plus read-only `bootstrap` introspection, with every trust decision consuming the private source. No code was staged because the acceptance regression and downstream gates cannot execute in this run.

## Evidence produced

- `research/2026-09-01-lab092-ledger-owned-public-surface-closure-audit.md` — main commit `ed39c1467db1ef3d9a80aaed0a05bbfb13bccfc8`; #176 comment `5498381599`.
- `research/2026-09-01-lab094-bootstrap-trust-root-contract.md` — main commit `c3e5a5d7dee036df33135f0aec5159871594b40d`; #179 comment `5498382948`.
- Existing LAB-092 evidence remains: four post-construction provenance-deletion mutation surfaces guarded; exact PR #177 regression/full execution pending.
- Existing LAB-095 evidence remains: public mutable ledger/provider-history DB paths independently select durable authority targets.

## Known failures / blockers

- LAB-086 remains first priority. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, require exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; exact checkout/source execution is unavailable in this run because direct git transport fails DNS.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Do not add further LAB-092 wrappers/regressions without a concrete supported mutation-before-provenance-validation path.
- Do not patch caller-owned `attested`/provider exposure inside LAB-092; #178/LAB-093 owns it.
- Do not patch bootstrap trust-root lifetime only in LAB-092; #179/LAB-094 owns it.
- Do not patch mutable DB identity only in LAB-092; #180/LAB-095 owns it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`, then PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, continue LAB-094/#179 at source level only: inspect all bootstrap read/write/introspection compatibility surfaces and test layout, then prepare the exact regression-first patch plan. Stage code only when the pre-fix substituted-history authority failure can be executed or an equivalently strong auditable execution path becomes available. LAB-095/#180 follows after LAB-094.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; ledger-owned public-surface audit exhausted; exact regression/full gate pending.
- #178 / LAB-093 — READY.
- #179 / LAB-094 — READY; contract defined, regression-first implementation pending exact execution.
- #180 / LAB-095 — READY.
