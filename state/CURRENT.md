# Current Lab State

Last updated: 2026-08-29

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: #163 / LAB-086 — IN_PROGRESS; draft PR #165, branch `lab/086-asymmetric-break-glass-history`.
- Exact live `strict_fence.py` blob: `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.
- Exact retained hidden-rowid candidate: `b78e7c98e35138719f77c482c7f1aab36b702de7` (tested previously, not published).
- LAB-088 / #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / #170 remains IN_PROGRESS on draft PR #173; fallback only while LAB-086 exact publication/execution is concretely tool-limited.

## Last completed step

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected all open issues and PRs. LAB-086 remains first priority. A fresh executable-shell probe of the exact raw GitHub URL again failed before byte transfer with DNS resolution failure, so no safe byte-preserving response->filesystem/Contents-API bridge was observed in this run. The security-critical ~40 KB runtime was not hand-reserialized and candidate `b78e7c98...` was not published.

Under the allowed LAB-091 fallback, reconstructed the exact published adoption validator and three focused regression files from branch `lab/091-mutable-shared-anchor-writer`, verified their Git blob identities before execution, then ran them together.

Exact reconstructed blobs:
- `adoption_validation.py` `2281d8e5ae21817b8eab0f52dc44abe61104c745`;
- `operation_permit.py` `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `state_machine_udfs.py` `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`;
- expression-UNIQUE regression `cec968e15f2cc4cfb0f38030ff44ae4c24bb89f0`;
- partial-UNIQUE regression `e77521d839510490a2bea4d92d68d9071241ff35`;
- schema-contract regression `e87c550282ac455e4ca5bedeb9de4f6626d563a4`.

Combined focused execution: **4/4 PASS**. `python -m compileall -q experiments/mutable_shared_anchor_writer` also PASS. The lower `shared_anchor_intent_ledger.protocol` import was represented only by its branch-verified `ALLOWED_INTENT_TYPES` constant because these zero-history schemas do not execute lower-ledger behavior; this is exact validator/test-source evidence, not a full dependency-closure claim.

Durable note: `research/2026-08-29-lab091-exact-adoption-index-gate.md`, main commit `437cf6a52fa1a9fba487a6c3b614a24d0dc76922`. Issue #170 comment `5458354413` and PR #173 comment `5458355110` record the evidence.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED->GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision and explicit `rowid=-1` sentinel regressions are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 focused evidence covers adoption lock/WAL behavior, existing-row identity ambiguity, missing canonical identity constraints, partial-UNIQUE false guarantees, expression-UNIQUE false guarantees, and published expression-index rejection at exact validator blob `2281d8e5...`.
- LAB-091 exact published expression/partial/missing-constraint suites now execute together **4/4 PASS + compileall** against the exact target/test blobs listed above.

## Known blockers / constraints

- LAB-086 remains first priority.
- Current LAB-086 live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Full exact LAB-086 source bytes are connector-readable, but no byte-preserving response->filesystem/Contents-API replacement bridge has been observed in the executable runtime. Fresh raw-GitHub shell access still fails at DNS. Do not hand-rewrite the security-critical runtime.
- PR #165 remains draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080->086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft pending complete real-stack gate. The narrow adoption-index suite is now exact-target-source GREEN, so do not repeat it unless a pinned blob changes.
- Do not broaden legacy schema rejection merely for structural similarity. Require a reproduced ambiguity or unsupported transition that survives current row validation.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: probe for any newly available supported byte-preserving response->write path. If available, publish exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; require returned/re-fetched Git blob equality, then run the four focused regressions + strict/thaw subgate + compileall and resume the LAB-080->086 real-ledger gate.
2. If LAB-086 remains concretely transport-limited, LAB-091: stop repeating the now-GREEN adoption-index gate and reconstruct/execute the complete `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` real LAB-080/LAB-082 dependency closure. Run two-worker/concurrency/crash semantics, timeout-after-commit/UNKNOWN reconciliation, LAB-087 composition, and reentrancy/legacy/alternate write-surface audit.
3. Keep PR #173 draft until that complete real-stack gate is clean; fix any reproduced defect before expanding scope.
4. Do not expand to NOT NULL/CHECK/collation/order rejection without a reproduced future-ambiguity gap.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; full exact source is connector-readable but byte-preserving publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; adoption-index exact target/test gate 4/4 PASS + compileall; full supported real-stack gate remains open.
