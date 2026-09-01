# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage; issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090 head. Current branch head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`; production provenance source blob `396b67a46686f6df23584b1b366824c1b7ac1886`; post-construction tamper regression blob `8f177a88cc861d4790b859b739c80070e2c6c232`.
- LAB-093 / #178 is READY: define encapsulation boundary for caller-owned `AttestedCatchup` / provider mutation capabilities exposed through ledger objects.
- LAB-094 / #179 is READY: make the provider-history construction-time bootstrap trust root immutable/non-rebindable for later `verify_durable()` authority decisions.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PR metadata. LAB-086 was probed first. Fresh local `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository code execution with `Could not resolve host: github.com`; no manual/model reserialization or LAB-086 branch mutation was attempted.

Continued the allowed LAB-092 ledger-owned reference/rebinding audit. Found a concrete lower-layer trust-root issue: `DurableProviderHistory.__init__()` retains the validated bootstrap as public mutable `self.bootstrap`, while `DurableProviderHistory.verify_durable()` and `IntegratedProviderHistory._verify_durable_locked()` later consume `self.bootstrap.generation_id` as the authenticated first-generation root. Because supported ledger composition exposes the live `ledger.provider_history` object, rebinding this slot changes authority used by a supported verification method. This is security-relevant authority interpretation, not merely arbitrary attribute reassignment.

Scope decision: do not patch LAB-092. The issue originates in the provider-history layer and affects LAB-081/LAB-090/LAB-092 composition. Opened #179 / LAB-094 for an immutable construction-time bootstrap trust-root contract. This is distinct from #178/LAB-093, which concerns caller-owned `attested`/provider capabilities.

No LAB-092 production/regression change was made. Durable evidence: `research/2026-09-01-lab092-ledger-owned-bootstrap-trust-root-audit.md`, main commit `f468dcc6a17957ce484523353e7f8efd5038f772`; #176 comment `5496946820`. PR #177 remains draft; current metadata reports `mergeable=true`, exact base `d9a381dd...`, head `81673f8f...`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility/order evidence retained; post-construction marker deletion is guarded on shared-anchor reservation/execute, provider rotation, component watermark mutation, and public provider-history receipt insertion. Public return-value/descriptor audit found no additional mutable ledger-owned authority handle. Exact PR #177 regression/full execution remains pending.
- LAB-094 finding: public mutable provider-history `bootstrap` is later consumed as the durable-history trust root; no fix attempted in LAB-092.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; exact checkout/source execution has not been observed in this run because direct git transport failed DNS resolution.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Live LAB-092 `reserve()`/`execute()`, `rotate_provider()`, mutation-capable `verify_component()`, and public `provider_history.store_receipt()` must fail closed if post-construction provenance is no longer `COMPLETE`.
- Do not treat caller-owned direct `attested`/provider mutation as a LAB-092 provenance bypass until LAB-093 defines the capability ownership/public-surface contract.
- Do not patch mutable provider-history bootstrap only in LAB-092; LAB-094 must define the lower-layer trust-root lifetime contract first.
- Do not add an exactly-once migration-marker execute or whole-call linearizable runtime-freshness requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, continue the ledger-owned reference audit with `path` and related retained DB/reference fields. Require a concrete supported-API authority amplification before creating a regression. Keep LAB-094 bootstrap trust-root work separate unless it becomes the highest-value unblocked task after LAB-092 remaining surfaces are exhausted.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; four post-construction provenance-deletion mutation surfaces guarded; public return-value/descriptor audit negative; bootstrap trust-root issue split to LAB-094; exact regression/full gate pending.
- #178 / LAB-093 — READY; define `attested`/provider capability encapsulation and supported public-surface ownership boundary.
- #179 / LAB-094 — READY; immutable provider-history bootstrap trust-root lifetime contract and regression.
