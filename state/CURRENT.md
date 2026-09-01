# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; source head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `16640c2d6ba8cd69d565982c47f7ff9f21fecfb8`; provenance blob `4c74336b9de27ae080411f1a8863862d3be63633`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs. LAB-086 remains first priority. The connector now proves PR #165 exposes the complete 949-line `strict_fence.py` as an added-file patch, but there is still no supported operation that can programmatically compose those fetched bytes with retained unified patch `61841b58...` and send the result to Contents API without manually/model-reserializing the security-critical file. Fresh direct `git clone` again failed before repository execution with `Could not resolve host: github.com`. No LAB-086 mutation was attempted.

Advanced the allowed LAB-092 fallback and found a reachable public-verification mutation-before-integrity-failure path. After a valid LAB-092 object is constructed, a caller can delete only the migration marker historical receipt, inject a malformed historical `COMMITTED` activation row referencing a missing provider generation, then call `verify_activation_schema_provenance()`. The old public method classified COMPLETE and immediately called inherited `execute()`. For a confirmed marker with a missing stored receipt, inherited `_reauthenticate()` can externally reconcile and persist a replacement receipt before any fresh `_verify_activation_records()` call.

Regression-first commit `5c0870ce25e461a31359843556e51efee60e708e` adds `test_public_verify_rechecks_activation_integrity_before_missing_marker_receipt_is_recreated` and requires `HistoricalVerificationError` with the marker receipt still absent.

Fix commit `16640c2d6ba8cd69d565982c47f7ff9f21fecfb8` changes public `verify_activation_schema_provenance()` to run `_verify_confirmation_authority(self, self.attested)` and `_verify_confirmation_activation_integrity(self)` before marker `execute()`. Re-fetch confirmed provenance blob `4c74336b9de27ae080411f1a8863862d3be63633` and the intended ordering.

Exact branch test execution remains unavailable because direct GitHub DNS resolution fails before code execution; no RED/GREEN or branch-level PASS is claimed.

Durable evidence: `research/2026-09-01-lab092-public-verify-preauth-integrity.md`, main commit `faa7941aba9e031b94ff4c0628f2ffefd42deb81`; #176 comment `5490353324`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility evidence retained. Atomic DDL+PREPARED, stale runtime/recovery checks, non-mutating confirmation, restart pre-authentication, full-history-before-receipt-recovery, activation-integrity-before-marker-reauth, and public post-construction pre-auth integrity hardening are published; exact PR #177 regression execution remains pending because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available. PR #165 exposes the full added-file patch, but no current supported bridge transfers that fetched payload into a byte-preserving local patch composition/write operation.
- Direct git transport failed again before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft; current head is `16640c2d...` and exact behavioral execution is still pending.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No marker receipt reauthentication may occur before full provider-history/runtime and activation-record integrity verification on startup, migration confirmation, or public provenance verification.
- Explicit branch/base conflict reconciliation is required before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #177 `test_activation_schema_pre_auth_history_verification.py` first on head `16640c2d...`, then restart precheck, migration confirmation bridge, stale runtime/PREPARED recovery, atomic boundary, unresolved activation, deletion/mismatch and legitimate legacy migration; execute PR #175 gates before any integration.

If execution remains unavailable, audit the second `self.execute(_completion_intent())` in LAB-092 `__init__` after `super().__init__()`. Determine whether this duplicate marker reauthentication is semantically redundant or creates a post-recovery mutation/revalidation ordering surface. Add regression first only for a reachable contract violation; otherwise document why the duplicate call is safe/necessary and move to the next LAB-092/LAB-090 integration risk.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; public post-construction pre-auth integrity fix published; exact regression gate pending.
