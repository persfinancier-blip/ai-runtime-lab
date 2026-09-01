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
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, open issues and active PRs. LAB-086 remains priority #1; its exact byte-preserving publication constraint is unchanged, so no manual/model reserialization of security-critical `strict_fence.py` was attempted.

Continued the allowed LAB-092 remaining-handle audit. `SharedAnchorLedger` stores the exact caller-supplied `AttestedCatchup` as public `self.attested`. `AttestedCatchup.catch_up_one()` can mutate the external monotonic anchor and `attested.provider` exposes provider mutation APIs; under LAB-090, `FencedActivationProvider` additionally exposes activation prepare/commit/release/abort state.

Decision: this is not a new LAB-092 provenance-deletion bypass. The caller already owns the exact mutable `attested`/provider object before constructing the ledger, so provenance deletion does not grant or amplify this capability. A LAB-092-only wrapper would silently redefine a lower-layer capability boundary and risks breaking LAB-080/LAB-090 exact-type/provider composition without first specifying whether `ledger.attested` is a supported public surface.

No LAB-092 production or regression change was made from this audit. Opened #178 / LAB-093 to define the capability-encapsulation boundary explicitly and its composition with LAB-087. Durable evidence: `research/2026-09-01-lab092-attested-provider-capability-boundary-audit.md`, main commit `682f0ace85ab83d8e7a6171e5be7726e0489676c`; #176 comment `5495390621`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility/order evidence retained; post-construction marker deletion is guarded on shared-anchor reservation/execute, provider rotation, component watermark mutation, and public provider-history receipt insertion. Exact PR #177 regression/full execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; exact checkout/source execution has not been observed in this run.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution and base/conflict reconciliation are available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Live LAB-092 `reserve()`/`execute()`, `rotate_provider()`, mutation-capable `verify_component()`, and public `provider_history.store_receipt()` must fail closed if post-construction provenance is no longer `COMPLETE`.
- Do not treat caller-owned direct `attested`/provider mutation as a LAB-092 provenance bypass until LAB-093 defines the capability ownership/public-surface contract.
- Do not add an exactly-once migration-marker execute or whole-call linearizable runtime-freshness requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 including all four post-construction provenance-deletion regressions on exact head `81673f8f...`. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, continue LAB-092 by auditing remaining **ledger-owned** publicly reachable objects/return values for concrete mutation-before-provenance-validation paths. Exclude caller-owned `attested`/provider capability exposure from LAB-092 unless new evidence shows privilege amplification; track that architecture question in #178. In particular inspect whether any activation/provider return object, entry/result object, bootstrap descriptor/key material, or non-underscore history/ledger method can mutate receipts, activation status, migration marker state, provider history, watermarks, or another ledger-owned durable authority surface without one of the four current guards. Add regressions only for concrete reachable violations; otherwise record negative audits.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; four post-construction provenance-deletion mutation surfaces guarded; exact regression/full gate pending.
- #178 / LAB-093 — READY; define `attested`/provider capability encapsulation and supported public-surface ownership boundary.
