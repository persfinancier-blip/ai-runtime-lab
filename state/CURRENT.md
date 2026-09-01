# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage; issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head. Current branch head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; PR metadata currently reports `mergeable=true`, `draft=true`.
- LAB-093 / #178 is READY: define encapsulation boundary for caller-owned `AttestedCatchup` / provider mutation capabilities exposed through ledger objects.
- LAB-094 / #179 is READY: make the provider-history construction-time bootstrap trust root immutable/non-rebindable for later `verify_durable()` authority decisions.
- LAB-095 / #180 is READY: bind supported ledger/provider-history database identity immutably after construction and prevent cross-DB path rebinding/divergence.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR metadata. LAB-086 was probed first. Fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository code execution with `Could not resolve host: github.com`; no manual/model reserialization or LAB-086 branch mutation was attempted.

Continued the allowed LAB-092 ledger-owned retained-reference audit. Found a concrete lower-layer DB identity issue. `SharedAnchorLedger.__init__()` stores public mutable `self.path`; `DurableProviderHistory.__init__()` independently stores its own public mutable `self.path`. In supported LAB-081/LAB-090/LAB-092 composition, `HistoricalSharedAnchorLedger.reserve()` opens `q = self._con()` from the ledger's current path and then calls `provider_history._current_locked(q)` using that already-selected connection before mutation. Therefore post-construction `ledger.path` rebinding can redirect supported authority decisions and durable intent writes to another SQLite file without running the constructor's full `verify_durable()` against that target. LAB-092 `_classify(self.path)` proves activation schema/provenance shape only and is not provider-history trust verification.

Scope decision: do not patch LAB-092 only. Opened #180 / LAB-095 for lifetime-stable canonical DB identity, prevention of ledger/provider-history path divergence, and a cross-DB rebinding regression. This is distinct from #179/LAB-094 bootstrap trust-root rebinding and #178/LAB-093 caller-owned external-provider capabilities.

No LAB-092 production/regression change was made. Durable evidence: `research/2026-09-01-lab092-ledger-path-rebinding-audit.md`, main commit `a037f49ab17bcf0fbc07e559cd6c91fdcbd00284`; #176 comment `5497699998`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility/order evidence retained; post-construction marker deletion is guarded on shared-anchor reservation/execute, provider rotation, component watermark mutation, and public provider-history receipt insertion. Public return-value/descriptor audit found no additional mutable ledger-owned authority handle. Exact PR #177 regression/full execution remains pending.
- LAB-094 finding: public mutable provider-history `bootstrap` is later consumed as the durable-history trust root; no fix attempted in LAB-092.
- LAB-095 finding: public mutable ledger/provider-history DB paths are independently retained; ledger path rebinding changes the SQLite connection consumed by supported operations, and reserve-time `_current_locked(q)` does not replace a fresh full durable verification of the newly selected DB.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; exact checkout/source execution has not been observed in this run because direct git transport failed DNS resolution.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Live LAB-092 `reserve()`/`execute()`, `rotate_provider()`, mutation-capable `verify_component()`, and public `provider_history.store_receipt()` must fail closed if post-construction provenance is no longer `COMPLETE`.
- Do not patch caller-owned `attested`/provider exposure only in LAB-092; #178/LAB-093 owns that capability-boundary question.
- Do not patch mutable provider-history bootstrap only in LAB-092; #179/LAB-094 owns the lower-layer trust-root lifetime contract.
- Do not patch mutable DB path only in LAB-092; #180/LAB-095 owns canonical DB identity/path lifetime and cross-object path divergence.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, finish the LAB-092 retained-reference audit for remaining ledger-owned non-underscore references/return objects. Require a concrete supported-API authority amplification before adding regression. If those surfaces are exhausted, promote the highest-value lower-layer READY follow-up among LAB-094 (bootstrap trust root) and LAB-095 (canonical DB identity), with regression-first implementation only when exact execution becomes available or a safe auditable source-only slice is possible.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; four post-construction provenance-deletion mutation surfaces guarded; bootstrap issue split to LAB-094; DB identity/path issue split to LAB-095; exact regression/full gate pending.
- #178 / LAB-093 — READY; define `attested`/provider capability encapsulation and supported public-surface ownership boundary.
- #179 / LAB-094 — READY; immutable provider-history bootstrap trust-root lifetime contract and regression.
- #180 / LAB-095 — READY; canonical non-rebindable ledger/provider-history DB identity and cross-DB rebinding regression.
