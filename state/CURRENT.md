# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage; issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based exactly on LAB-090 head. Current branch head `cc50513cfd867d8711fb29db8f33490200390d0d`; production provenance source blob `fe9322800c41e5cbb641b4d86810e8f2cf0e8b0a`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and active PR state. LAB-086 remains priority #1.

Fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository execution with `Could not resolve host: github.com`. The live branch `strict_fence.py` was conflict-checked through the connector and still reports exact predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. The retained semantic patch was re-fetched from the LAB-086 branch and is still exact blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`.

The connector can return exact line-ranged predecessor source and the full semantic patch, but the observed Contents write action still requires a complete UTF-8 replacement body and exposes no automatic connector-bytes/local-file reference transfer. Manual/model reserialization of security-critical `strict_fence.py` remains prohibited. No LAB-086 branch mutation was attempted.

Completed the next allowed LAB-092 mutation/revalidation audit: `verify_activation_schema_provenance()` racing with provider rotation. No new mutation-before-revalidation defect was demonstrated. On the missing-marker-receipt path, inherited LAB-090 `_reauthenticate()` re-reads durable current generation and rejects a historical migration entry after concurrent rotation before external reconcile / receipt storage. On the stored-receipt path, marker verification is non-mutating. Requiring linearizable runtime freshness across the entire unsynchronized public verification call would be a new contract, not a reproduced security/correctness violation, so no regression or production change was added.

Durable evidence: `research/2026-09-01-lab092-public-verify-concurrent-rotation-negative-audit.md`, main commit `de2aac8d774b5f8adf7e1e8d92b6cbd89f2790c9`; #176 comment `5493111469`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility and ordering evidence retained. Atomic DDL+PREPARED, stale runtime/recovery checks, non-mutating confirmation, restart pre-authentication, full-history-before-receipt-recovery, activation-integrity-before-marker-reauth, public post-construction pre-auth integrity, removal of duplicate post-recovery marker reauth, migration-return constructor audit, semantic integration audit, and concurrent-rotation negative audit are persisted; exact PR #177 regression execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct source execution/checkout is not available in this run because local GitHub DNS resolution fails.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution is available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Do not add an exactly-once migration-marker execute or whole-call linearizable runtime-freshness requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is required immediately before integration.

## Exact next action

LAB-086 first: probe for any newly supported byte-preserving connector/local-file -> Contents replacement bridge. If available, conflict-check predecessor `d4a6a40f...`, compose only retained patch `61841b58...`, require candidate Git blob `b78e7c98...`, publish/re-fetch/hash-verify, then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, complete strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall, and final security/reconciliation audit.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 restart-precheck, pre-auth history verification, migration confirmation bridge, stale runtime/PREPARED recovery, atomic boundary, unresolved activation, deletion/mismatch, public verification, and legitimate legacy migration gates on current head/source. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, continue LAB-092 only at a concrete durable mutation-before-validation boundary. Prefer methods that can write provider receipts, activation status, migration marker state, or provider history after post-construction tamper; record negative audits rather than inventing new contracts.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; concurrent-rotation public verify audit found no new mutation defect; exact regression gate pending.
