# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; source head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 remains IN_PROGRESS; branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `7b14fc29217bdf987704d61bfcbc80fba43db1a4`; provenance blob `35e1adef996640578bf7ade76972680189211bd4`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs and the exact LAB-092/LAB-090/LAB-080 authority paths. LAB-086 remains first priority, but the current GitHub surface still exposes no supported byte-preserving patch-composition bridge and the 949-line security-critical `strict_fence.py` must not be manually/model reserialized.

Advanced the allowed LAB-092 fallback. The COMPLETE-startup pre-auth bridge was audited for local `receipt_binding` tamper, provider-history corruption and repeated reauthentication side effects.

Direct `receipt_binding` substitution is already fail-closed because confirmed execution compares the durable binding to a cryptographically verified historical receipt. With a stored receipt, restart reauthentication is local verification rather than another external reconcile call.

A separate reachable ordering gap was found when the marker receipt is missing: `confirmation.execute()` could reconcile externally and persist a replacement historical receipt before the later LAB-090 constructor performed full provider-history verification. Receipt-only verification can miss corruption elsewhere in provider history, such as a valid-looking orphan successor descriptor.

Regression-first commit `e243511fb4001d049f3948227d727d486a3691f4` adds `test_activation_schema_pre_auth_history_verification.py`, requiring corrupt provider history to fail before a missing migration-marker receipt is recreated.

Fix commit `7b14fc29217bdf987704d61bfcbc80fba43db1a4` adds read-only `_verify_confirmation_authority()`: full `_verify_durable_locked()` provider-history verification plus exact runtime/current-generation comparison now runs before external marker reauthentication on COMPLETE startup and on the post-DDL migration confirmation handoff. Re-fetched commit diff confirms only this ordering hardening. Current provenance blob `35e1adef996640578bf7ade76972680189211bd4`.

Fresh exact checkout/test execution was attempted with `git clone --depth 1 --branch lab-092-activation-schema-provenance ...`; transport again failed before repository code execution with `Could not resolve host: github.com`. No branch-level RED/GREEN is claimed.

Durable evidence: `research/2026-09-01-lab092-preauth-full-history-before-receipt-recovery.md`, main commit `1bd28430cb0ea14b5ec20cae0a6ce041704bc859`; #176 comment `5488824164`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 classifier/atomic-visibility evidence retained. Atomic DDL+PREPARED, stale runtime/recovery checks, non-mutating confirmation, restart pre-authentication, legacy startup read-only precheck and full-history-before-receipt-recovery hardening are published; exact PR #177 regression execution remains pending because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport failed again before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft; current head is `7b14fc29...` and exact behavioral execution is still pending.
- Ordinary LAB-092 startup must never reserve/mutate migration provenance on legacy/unmarked/PREPARED state.
- No provider activation recovery may run before a locally COMPLETE marker is fully authority-verified and externally re-authenticated.
- Explicit branch/base conflict reconciliation is required before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute the new PR #177 regression `test_activation_schema_pre_auth_history_verification.py` first on head `7b14fc29...`, then `test_activation_schema_restart_precheck.py` and `test_activation_schema_migration_confirmation_bridge.py`, followed by stale runtime/PREPARED recovery, atomic boundary, unresolved activation, deletion/mismatch and legitimate legacy migration; execute PR #175 gates before any integration.

If execution remains unavailable, audit the remaining LAB-092 handoff between successful external marker reauthentication and LAB-090 constructor recovery for concurrent provider-history/activation changes. Add regression first for any reachable mutation-before-revalidation gap; otherwise document closure and move to the next highest-value LAB-092/LAB-090 integration risk.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; full-history-before-marker-receipt-recovery hardening published; exact regression gate pending.
