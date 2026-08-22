# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-082 — make LAB-081's historical verification-only provider state cryptographic by retaining Ed25519 public verification material in durable history while keeping private signing capability outside the database.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-081.
- LAB-081 Issue #153 closed DONE; PR #154 squash-merged as `d9a692877c7ad6d3ce5fa2a17c5efe78f1513f82`.
- Active: Issue #155 / LAB-082 — IN_PROGRESS.
- Active branch: `lab/082-asymmetric-provider-history`.
- Draft PR: none yet. Normal PR creation was attempted and blocked by an external safety-status gate before execution; do not treat that as a research blocker or bypass it with low-level refs/trees.
- Branch is ahead of `main` by 5 commits, behind by 0, with five new LAB-082 files only.

## Last completed step

LAB-081 final exact-source gate completed: 50/50 normal tests across LAB-081/LAB-080/LAB-036 passed, compileall passed, unsafe LAB-080 and LAB-036 baselines failed as expected, final remote audit was clean, and PR #154 merged normally.

LAB-082 was then started. `cryptography 46.0.4` was observed available. An Ed25519 reference protocol was built and published: durable SQL stores public keys, transition signatures and signed receipts only; runtime `GenerationSigner` objects hold private signing capability outside durable history. Exact N→N+1 transition requires signatures from both old and new generation keys. Only the signer matching the durable current public generation can create a new receipt; historical receipts verify from public material after rotation/restart.

A schema/security audit fixed two early defects: an incorrect exact concrete-type check for cryptography's Ed25519 backend objects, and insufficient canonical/type checking that could permit Python bool/integer or alternate-hex identity aliases.

## Evidence produced

- Issue #155 / LAB-082 — IN_PROGRESS.
- Branch `lab/082-asymmetric-provider-history`, ahead 5 / behind 0 from merge base `d9a692877c7ad6d3ce5fa2a17c5efe78f1513f82`.
- `experiments/asymmetric_provider_history/protocol.py` branch blob `a2fc3456233930d94aaaca5fe57b1debd50cbdab`; local pre-publication source hash matched this blob exactly.
- Branch test blobs currently reported by GitHub: corrected test `f737f71559e90e9a748fc3bd3d3e0cf90872a898`, unsafe seed `f8d4cb7a30eee2373fa0c1ecdeef4d2edfdbe0ce`.
- Local pre-publication corrected suite after schema audit: 16/16 passed.
- Unsafe symmetric baseline: failed as expected because durable HMAC verification material could sign a new effect.
- Compileall: passed.
- Primary mechanisms recorded from RFC 8032 and TUF root-update continuity.

## Known blockers / constraints

- No owner/product blocker.
- Normal draft PR creation is currently blocked by an external safety-status gate before execution; continue on the durable branch and retry normal PR creation later.
- The published protocol blob is exact-source matched, but published test blobs do not match the local pre-publication file hashes, so the branch test bytes must be reconstructed/executed before claiming exact-source validation.
- The current LAB-082 slice is isolated. It has not yet replaced/adapted LAB-081's historical HMAC verification behind the supported LAB-080 shared-anchor serialization surface.
- Ed25519 removes signing capability from durable historical material, but this reference does not provide HSM/KMS custody, provider consensus, cross-provider failover, PKI certificate issuance, or compromise recovery.
- Direct shell GitHub checkout has repeatedly failed DNS in this runtime family; connector reconstruction is the supported fallback.

## Exact next action

Resume Issue #155 on `lab/082-asymmetric-provider-history`. Reconstruct exact published `test_protocol.py` and `unsafe_symmetric_expected_failure.py` through the GitHub connector, verify their Git blob identities, and execute the exact branch LAB-082 corrected/unsafe suites plus compileall. Fix any publication-byte or test discrepancy.

Then build the integration behind the merged LAB-081/LAB-080 supported shared-anchor boundary: current LAB-036 observation may be authenticated at execution time, but durable historical verification must be represented by Ed25519 public material/signatures so no historical HMAC/private signing key is required after rotation. Preserve the same SQLite PREPARED-vs-rotation serialization and restart semantics. Add mixed generation, restart, race, private-material-absence, receipt/capability rebinding and corruption regressions. Run LAB-082 plus LAB-081/LAB-080/LAB-036 regressions, perform a fresh remote audit, retry normal draft PR creation, and only integrate when the exact-source gate is clean.

## Backlog

- #155 / LAB-082 — asymmetric provider receipts and cryptographic verification-only history — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
