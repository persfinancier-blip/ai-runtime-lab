# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`.
- PR remains draft; exact real-ledger current-head gate is incomplete.
- LAB-087 / Issue #166 is DONE; PR #171 squash-merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.

## Last completed step

Re-audited the current LAB-086 migration/cardinality path while the bulk exact dependency export remains unavailable in this runtime.

The new `_verify_lower_evidence_cardinality_locked()` rule was compared with the exact merged LAB-083 enablement semantics. LAB-083 controls provider transitions strictly where `new_generation > start_provider_generation`; LAB-086 uses the same strict `>` boundary. A focused SQLite semantic execution using the exact current cardinality logic observed:
- valid history PASS;
- orphan provider transition rejected;
- orphan threshold proof rejected;
- orphan root transition rejected;
- a successor represented by both normal-root and recovery-root evidence rejected;
- enablement at provider generation 2 correctly permits the generation-2 legacy transition without a threshold proof while requiring the generation-3 proof.

A separate source audit checked migration ceremony ordering against the current DML fence. The legacy freeze triggers intentionally permit only the one-way HMAC scrub transforms (`signatures_json -> []`, `keys_json -> {}`) while freezing semantic columns, so `projection/boundary/root-proof -> scrub -> verify -> commit` is compatible with the installed fence. LAB-085 public-custody `verify_durable()` uses a read transaction, so calling it while the outer LAB-086 verifier owns `BEGIN IMMEDIATE` does not attempt a second writer lock. No new blocker was established in this pass.

Issue #163 comment `5421940902` records this continuation evidence.

## Evidence produced / reconfirmed

LAB-086 focused evidence this run:
- exact LAB-083 `SupportedThresholdAuthorizedAsymmetricProviderLedger.verify_durable()` uses `WHERE g.generation > enablement.start_provider_generation`, matching the LAB-086 cardinality rule;
- focused cardinality semantic harness: valid PASS; orphan provider/proof/root and double root-proof-type cases rejected; later enablement boundary PASS;
- migration scrub ordering is compatible with current legacy semantic-freeze triggers;
- nested public-custody verifier uses `BEGIN` read transaction, not a competing `BEGIN IMMEDIATE`.

Cumulative exact lower-stack evidence remains:
- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS, asymmetric-custody 8/8 PASS, public/final 11/11 PASS.
- Exact standalone LAB-086 corrected suite previously passed 12/12; focused migration/fence evidence remains recorded in Issue #163 / PR #165.
- Current migration guard blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current least-privilege fence blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Current suffix blob: `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.

LAB-087 final exact evidence remains 14/14 PASS + compileall PASS and is merged/DONE.

## Known blockers / constraints

- LAB-086 remaining merge gate: execute current `test_pre_cutoff_lower_evidence_cardinality.py`, then the full current-head real-schema migration/suffix/final-supported/security suite from one exact LAB-080→086 dependency closure; run unsafe seed, compileall and final audit.
- Direct shell/raw GitHub transport remains unavailable. GitHub connector reads work; its archive endpoint is not supported. File-by-file exact reconstruction remains the safe execution path.
- The focused cardinality execution above validates the formula but is not the exact real-ledger test module and is not counted as the merge gate.
- PR #165 is currently reported non-mergeable by GitHub and is substantially diverged from current `main`; do not reconcile/integrate until the complete test/security gate is clean.
- LAB-086 fences cover audited supported/DML paths. LAB-087 supplies the separate process/filesystem/write-handle boundary; root, broker UID, `CAP_DAC_OVERRIDE`, ACL/capability policy outside mode bits and privileged namespace replacement remain outside that claim.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Continue file-by-file connector reconstruction of the exact LAB-080→086 dependency closure required by `test_pre_cutoff_lower_evidence_cardinality.py`; verify every reconstructed executable file with `git hash-object` and execute the real test module against migration guard blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
2. On the same closure execute current `test_suffix.py` and every remaining LAB-086 real-schema migration/final-supported/security module, followed by unsafe legacy-promotion seed and full compileall.
3. Perform a fresh final security audit focused on reverse evidence cardinality, cutoff/root/public proof binding, alternate supported mutation paths, transaction-scoped thaw/restoration, restart snapshots and rotation races.
4. Re-check branch/main divergence and PR mergeability. Keep PR #165 draft until the complete current-head gate is clean; only then reconcile and integrate using supported auditable operations.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head real-ledger gate remains.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
