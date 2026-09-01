# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage (`05d8e75a...` / `eb219835...`); issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current branch head `cc50513cfd867d8711fb29db8f33490200390d0d`; production provenance source remains blob `fe9322800c41e5cbb641b4d86810e8f2cf0e8b0a`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected active PRs. LAB-086 remains priority #1 and retains the exact hidden-rowid publication constraint; no supported byte-preserving composition bridge was observed in this run, so no LAB-086 mutation was attempted.

Advanced the allowed LAB-092 fallback. Audited `migrate_activation_schema_v1() -> return cls(...)` after explicit marker confirmation. The immediate constructor does redundantly call the migration marker `execute()` again, but only after a fresh full provider-history/runtime verification and activation-record integrity verification. LAB-090 recovery begins only after that sequence. Concurrent provider-generation change therefore fails before marker receipt recovery/reconcile; concurrent activation-record corruption likewise fails before marker receipt recovery/reconcile. Receipt disappearance in the gap can cause redundant authenticated reconcile, but no unverified authority/mutation window was demonstrated.

A temporary exactly-once regression was published as `1662a99f9aa61eb2153c82125c8872e2ac4952b4`, then removed after audit because it encoded an optimization rather than an established security/correctness contract. Removal commit `cc50513cfd867d8711fb29db8f33490200390d0d` restores `test_activation_schema_migration_confirmation_bridge.py` exactly to blob `6058efd814855120f741019c77b2eaeb34f329cb`; production source was not changed.

Integration/rebase audit: PR #177 remains based exactly on LAB-090 head `d9a381dd...`. PR #175 is 96 main commits behind from merge base `6cc7a044...`, but current-main changes across that divergence are research/state-only and disjoint from the 21 LAB-090 changed files. Direct GitHub REST reports PR #175 `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`; one normalized connector snapshot briefly reported `mergeable=false`, so direct REST is treated as the higher-confidence current observation. No integration attempted because both PRs remain draft and exact behavioral gates are still pending.

Durable evidence: `research/2026-09-01-lab092-explicit-migration-return-constructor-audit.md`, main commit `9cc2ce443947213fb48e669ee67e252a81bc04cb`; #176 comment `5491789666`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility and ordering evidence retained. Atomic DDL+PREPARED, stale runtime/recovery checks, non-mutating confirmation, restart pre-authentication, full-history-before-receipt-recovery, activation-integrity-before-marker-reauth, public post-construction pre-auth integrity, removal of duplicate post-recovery marker reauth, and migration-return constructor audit are persisted; exact PR #177 regression execution remains pending.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct source execution/checkout has not been observed available in the recent runs.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution is available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Do not add an exactly-once migration-marker execute requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is still required immediately before integration even though current REST reports PR #175 clean.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If exact source execution becomes available before that bridge, execute PR #175 focused/integration/downstream gates first on exact head `d9a381dd...`; then execute PR #177 restart-precheck, pre-auth history verification, migration confirmation bridge, stale runtime/PREPARED recovery, atomic boundary, unresolved activation, deletion/mismatch, public verification, and legitimate legacy migration gates on current branch head/source. Do not integrate either draft before those gates.

If execution remains unavailable, continue integration audit rather than inventing more LAB-092 contracts: inspect PR #175 vs current main at the exact file/hunk level for any semantic dependency on main-side state/research assumptions, then inspect PR #177 cumulative dependency on PR #175 for any changed inherited method/signature that would require a rebase adjustment. Record only reachable semantic conflicts; otherwise leave both drafts unchanged and advance to the next highest-value mutation boundary.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration-return constructor audited with no proven contract violation; exact regression gate pending.
