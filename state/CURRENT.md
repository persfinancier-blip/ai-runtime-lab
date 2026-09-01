# Current Lab State

Last updated: 2026-09-01

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`.
- Exact LAB-086 predecessor `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required target `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- LAB-090 / #169 fallback remains draft PR #175; branch `lab-090-provider-activation-fencing`; atomic source fix head `d9a381dd4607a928cd1315adef6431e239995bc1`, `supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.
- LAB-092 / #176 is IN_PROGRESS on branch `lab-092-activation-schema-provenance`, draft PR #177 based on LAB-090. Current head `aaf13678b0d9d84f42e709a2d9cd051c83e06787`; current provenance blob `b529e93879659dfe857795e632985b9d06938f71`.
- LAB-091 / #170 draft PR #173 and LAB-088 / #167 draft PR #172 remain IN_PROGRESS.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #177. LAB-086 remains first priority. Current GitHub operations still expose normal Contents reads/writes but no supported byte-preserving patch-composition operation; do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.

Advanced the allowed LAB-092 fallback. Audit confirmed `_install_and_reserve_prepared()` read activation DDL/marker under `BEGIN IMMEDIATE` but returned existing PREPARED/CONFIRMED markers before full inherited provider-history verification and runtime-current validation. This made recovery authorization weaker than first installation.

Published regression-first commit `978613365271090cb18a624fbcfc9ae3e61f70e2`: `test_stale_runtime_cannot_recover_existing_prepared_marker` creates a valid generation-2 durable head plus exact DDL+PREPARED marker, retries explicit migration from generation-1 runtime, requires `CurrentGenerationRequired`, and requires the marker to remain PREPARED.

Published implementation/current PR #177 head `aaf13678b0d9d84f42e709a2d9cd051c83e06787`: inside the same migration `BEGIN IMMEDIATE`, full `_verify_durable_locked(q)` and exact runtime-generation comparison now occur immediately after schema/marker classification and before both PREPARED and CONFIRMED early returns. Existing fail-closed behavior for missing/mismatched DDL with provenance is unchanged. GitHub patch re-fetch confirmed this ordering; provenance blob is `b529e93879659dfe857795e632985b9d06938f71`.

Fresh exact checkout/test execution was attempted again with `git clone --depth 1 --branch lab-092-activation-schema-provenance ...`; transport failed before repository execution with `Could not resolve host: github.com`. No branch-level RED/GREEN is claimed.

Durable evidence: `research/2026-09-01-lab092-marker-recovery-runtime-verification.md`, main commit `7ab908bc43821bcfedf2078f5dbcece1d365ba9d`; #176 comment `5487116946`.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; unsafe lower baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; hidden-rowid RED→GREEN evidence and exact predecessor/target derivation retained; publication/full gate pending.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-088 exact focused/core evidence 22/22 PASS + compileall; supported/downstream gate pending.
- LAB-090 provider primitive/concurrency exact-byte slice 10/10 PASS + compileall; atomic installation fix published, exact branch behavioral/full-suite execution pending.
- LAB-092 earlier classifier `py_compile`/standalone state-machine and atomic-visibility evidence retained. Atomic DDL+PREPARED, non-mutating history view, stale-first-install regression, and stale-PREPARED-recovery hardening are published; exact PR #177 regressions remain unexecuted because checkout transport still fails before code execution.

## Known blockers / constraints

- LAB-086 remains first priority. Do not manually/model-reserialize the 949-line security-critical `strict_fence.py`.
- Publish LAB-086 only from exact predecessor `d4a6a40f...` + retained patch `61841b58...`, requiring exact target `b78e7c98...`, then re-fetch/hash-verify and run the complete security gate.
- GitHub connector read/write is available, but no supported byte-preserving server-side patch-composition write is exposed.
- Direct git transport failed again before repository execution with `Could not resolve host: github.com`.
- Keep PR #175 draft until exact focused/integration/downstream behavioral gates execute.
- Keep PR #177 draft. Source hardening is published, but exact behavioral execution is still pending.
- Do not solve LAB-092 with unauthenticated local markers, marker confirmation before exact DDL, post-confirmation auto-repair, durable PREPARED-before-DDL state, provider-history bootstrap as a migration side effect, or marker recovery that bypasses full durable-history/runtime-current verification.
- Explicit branch/base conflict reconciliation is required before integration of #175/#177.

## Exact next action

LAB-086 first: probe for a supported byte-preserving composition/transfer bridge. If available, conflict-check predecessor `d4a6a40f...`, apply only retained patch `61841b58...`, require target `b78e7c98...`, publish/re-fetch/hash-verify, then run the full LAB-086 security gate.

If still unavailable and exact source execution becomes available, execute PR #175 `test_activation_schema_installation_race.py` first on source blob `8140d6e1...`, then remaining LAB-090 gates; then execute all PR #177 provenance tests on head `aaf13678...`, including stale first-install, stale PREPARED recovery, atomic boundary, unresolved activation, PREPARED recovery, deletion/mismatch, and legitimate legacy migration.

If execution remains unavailable, audit the LAB-092 handoff after `_install_and_reserve_prepared()`: it constructs `SupportedHistoricalSharedAnchorLedger` before external completion-marker confirmation. Determine whether that constructor can perform provider-activation recovery/mutation that should be forbidden during schema migration, especially with exact DDL+PREPARED provenance and unresolved LAB-090 activation records. Add a regression first if a side effect is reachable; then replace the confirmation bridge with the narrowest existing non-mutating/authenticated mechanism that preserves LAB-080 confirmation semantics.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; atomic installation source fix published; exact behavioral/full gate pending.
- #170 / LAB-091 — IN_PROGRESS fallback; full behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; atomic DDL+PREPARED candidate and marker-recovery authority hardening published; confirmation-bridge audit plus exact regression gate pending.
