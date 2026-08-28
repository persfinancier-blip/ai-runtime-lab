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

Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs. A new connector capability observation materially narrowed the LAB-086 blocker: `fetch_blob` returned the complete exact ~40 KB `strict_fence.py` content for blob `d4a6a40f...`. However, there is still no supported byte-preserving bridge from that connector response into the executable filesystem / Contents-API whole-file replacement payload, and the raw-download fallback remains unavailable. Therefore the security-critical runtime was still not manually reserialized and candidate `b78e7c98...` was not published.

Under the allowed LAB-091 fallback, applied the already staged expression-UNIQUE hardening through the normal Contents API against exact predecessor blob `bab8366438f266342ab461307c9191c9328653bd`.

Published LAB-091 branch result:
- commit `8243a85b8c92cbffc6ea335ff11dd394d99db20d`;
- resulting `experiments/mutable_shared_anchor_writer/adoption_validation.py` blob `2281d8e5ae21817b8eab0f52dc44abe61104c745`;
- post-write re-fetch matched the returned blob and the intended block.

The validator now rejects a UNIQUE index as a canonical named-column identity guarantee when `PRAGMA index_info()` reports any term with `name=NULL` (SQLite expression term). This closes the reproduced false collapse `UNIQUE(id, lower(scope)) -> UNIQUE(id)` while preserving the earlier partial-UNIQUE rejection.

Executed a focused in-memory SQLite mechanism gate using the updated collector semantics and the same schema shapes as the durable regressions: expression-UNIQUE counterexample PASS, all five prior partial-UNIQUE targets remain rejected, and canonical global PK/UNIQUE schema remains accepted. This is not represented as the full PR unittest or LAB-080/LAB-082 real-stack gate.

Research note: `research/2026-08-29-lab091-expression-unique-fix-published.md`, main commit `e6e3fd02cf4c8d330baf78e7a5c72d7d30672e85`. Issue #170 comment `5457859259` and PR #173 comment `5457861059` record the publication/evidence.

## Evidence retained

- LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS; asymmetric custody 8/8 PASS; public/final 11/11 PASS; lower unsafe baselines failed as intended.
- Standalone LAB-086 previously 12/12 PASS; unsafe legacy auto-promotion failed as intended.
- Alternate-UNIQUE and provider-receipt NULL protections are present in live `d4a6a40f...`.
- Hidden-rowid RED→GREEN evidence retained: exact predecessor `d4a6a40f...` -> candidate `b78e7c98...`; candidate remains unpublished. Rowid collision and explicit `rowid=-1` sentinel regressions are durable on PR #165.
- LAB-087 merged/DONE with exact 14/14 PASS + compileall.
- LAB-091 focused evidence covers adoption lock/WAL behavior, existing-row identity ambiguity, missing canonical identity constraints, partial-UNIQUE false guarantees, expression-UNIQUE false guarantees, and published expression-index rejection at exact blob `2281d8e5...`.

## Known blockers / constraints

- LAB-086 remains first priority.
- Current LAB-086 live security delta is rowid-only hardening. Do not reapply alternate-UNIQUE or provider-receipt NULL patches.
- Full exact LAB-086 source bytes are now readable through the GitHub connector, but no byte-preserving response→filesystem/Contents-API replacement bridge has been observed in this run. Raw GitHub download remains unavailable. Do not hand-rewrite the security-critical runtime.
- PR #165 remains draft until candidate publication/hash verification, complete strict/thaw gate, LAB-080→086 real-ledger gate, unsafe seed, compileall and final security/reconciliation audit are clean.
- PR #173 remains draft pending complete real-stack gate. Expression-UNIQUE fix is published, but exact branch regression execution and the full supported surface remain open.
- Do not broaden legacy schema rejection merely for structural similarity. Require a reproduced ambiguity or unsupported transition that survives current row validation.
- LAB-090/#169 provider handoff freshness remains separate.

## Exact next action

1. LAB-086 first: if a supported byte-preserving response→write path exists, publish exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` over predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; require returned/re-fetched Git blob equality, then run the four focused regressions + strict/thaw subgate + compileall and resume the LAB-080→086 real-ledger gate.
2. If LAB-086 remains concretely transport-limited, LAB-091: reconstruct/execute the exact published expression-UNIQUE, partial-UNIQUE and missing-constraint regression suites against validator blob `2281d8e5ae21817b8eab0f52dc44abe61104c745`; do not promote the focused mechanism check to exact branch-test evidence without that reconstruction.
3. Then resume the complete LAB-080/LAB-082 supported-surface concurrency/restart/crash/UNKNOWN gate and reentrancy audit.
4. Do not expand to NOT NULL/CHECK/collation/order rejection without a reproduced future-ambiguity gap.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid candidate tested but unpublished; full exact source is connector-readable but byte-preserving publication/execution transport remains blocker.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173; expression-UNIQUE false identity guarantee fixed/published at blob `2281d8e5...`; exact branch regression reconstruction + full real-stack gate still open.
