# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Authoritative pending LAB-086 lineage: predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- PR #165 body still describes the older alternate-UNIQUE executable lineage (`05d8e75a...` / `eb219835...`); issue #163 is authoritative for the pending hidden-rowid publication.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; head/base for LAB-092 is `d9a381dd4607a928cd1315adef6431e239995bc1`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based exactly on LAB-090 head. Current branch head `cc50513cfd867d8711fb29db8f33490200390d0d`; production provenance source blob `fe9322800c41e5cbb641b4d86810e8f2cf0e8b0a`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected active PRs and issues. LAB-086 remains priority #1. A fresh local `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` again failed before repository execution with `Could not resolve host: github.com`. No exact branch tests executed and no behavioral PASS is claimed.

Re-probed the LAB-086 publication path. The connector can fetch source and perform normal Contents writes, but no observed supported operation composes the exact fetched predecessor blob plus the retained unified patch into a byte-preserving replacement payload automatically. Low-level ref/tree manipulation and manual/model reserialization remain prohibited. No LAB-086 branch mutation was attempted.

Completed the allowed semantic integration fallback for LAB-090/LAB-092. Exact GitHub compare from PR #175 base `6cc7a04496187075db1c02f3e27c1d394da53026` to current `main` reports current main 98 commits ahead / 0 behind, with the complete changed-file set limited to `research/**` and `state/CURRENT.md`. None of PR #175's 21 production/test files overlap the main-side divergence. No reachable production semantic conflict with current main was found.

PR #177 remains based exactly on PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`; its 9 changed files are additive LAB-092 files. Inspection of the exact LAB-090 head confirms the inherited classes/constants and `_verify_activation_records(self)` surface consumed by `activation_schema_provenance.py` are present with matching signatures. No reachable inherited-method/signature conflict was found. Remaining integration risk is behavioral execution, so both PRs remain draft.

Durable evidence: `research/2026-09-01-lab090-lab092-semantic-integration-audit.md`, main commit `a88de2e944a28c73bc647ff96160ba81eefa8e38`; #176 comment `5492479662`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; exact published-head behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility and ordering evidence retained. Atomic DDL+PREPARED, stale runtime/recovery checks, non-mutating confirmation, restart pre-authentication, full-history-before-receipt-recovery, activation-integrity-before-marker-reauth, public post-construction pre-auth integrity, removal of duplicate post-recovery marker reauth, and migration-return constructor audit are persisted; exact PR #177 regression execution remains pending.
- Integration audit: PR #175 current-main divergence is control-plane/evidence-only with no overlap across its 21 changed files; PR #177 is based exactly on PR #175 head and no inherited API/signature conflict was found.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available; direct source execution/checkout is not available in this run because local GitHub DNS resolution fails.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft until exact regression/full behavioral execution is available.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Constructor migration-marker authentication occurs only on the pre-recovery non-mutating confirmation bridge; do not reintroduce post-recovery duplicate `execute()`.
- Do not add an exactly-once migration-marker execute requirement unless a concrete correctness/security contract requires it.
- Explicit branch/base reconciliation is still required immediately before integration even though the current semantic audit found no production overlap.

## Exact next action

LAB-086 first: probe again for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If exact source execution becomes available first, execute PR #175 focused/integration/downstream gates on exact head `d9a381dd...`; then execute PR #177 restart-precheck, pre-auth history verification, migration confirmation bridge, stale runtime/PREPARED recovery, atomic boundary, unresolved activation, deletion/mismatch, public verification, and legitimate legacy migration gates on current head/source. Do not integrate either draft before those gates.

If execution and LAB-086 byte-preserving publication remain unavailable, advance to the next reachable LAB-092 mutation boundary audit. Prefer a concrete post-construction or public-method mutation/revalidation window; add no regression or production change unless a reachable correctness/security violation is demonstrated. Record negative audits as evidence rather than inventing new contracts.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; semantic integration audit found no source/API conflict; exact regression gate pending.
