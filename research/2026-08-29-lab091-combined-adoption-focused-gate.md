# LAB-091 combined adoption focused gate — 2026-08-29

## Context

LAB-086 remained first priority. The live `lab/086-asymmetric-break-glass-history` `strict_fence.py` was re-fetched at blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; shell GitHub transport again failed before byte transfer with DNS resolution failure. The exact unpublished LAB-086 candidate was therefore not approximated or manually reserialized.

Per `state/CURRENT.md`, this run used the permitted LAB-091 fallback and exercised the combined adoption hardening surface against the current branch logic after head `210d51dd15ebfcaf4858bb927e2b729765c176b3`.

## Exact source observations

Fetched from `lab/091-mutable-shared-anchor-writer`:

- `adoption_validation.py` blob `1731648b4e65b1c5984d4f93b78c45d5a066dd95`;
- `adoption_schema_domains.py` blob `1abef5360fc57f5a863e8665556cbdb9dee6f012`;
- `full_operation_guards.py` blob `529ee8094d04b0cc9bb208f3fce8f85b2bc6db0f`;
- expression-UNIQUE regression blob `cec968e15f2cc4cfb0f38030ff44ae4c24bb89f0`;
- collation regression blob `ad2b3b80bf848f874e300acf6304cb57997f5bca`;
- weakened-watermark-CHECK regression blob `5d2ffd4a299e68c4807b5feb7bc5fa0e1e9f800f`.

## Executed focused gate

A local SQLite harness reproduced the exact fetched branch logic for `_unique_key_sets`, identity-constraint admission, required-NOT-NULL admission, deterministic request-id encoding, and the published v2 watermark insert trigger predicate. It exercised all hardening classes together rather than as isolated historical snapshots.

Observed results: **17/17 PASS**.

1. canonical identity contract accepted;
2. canonical required-NOT-NULL contract accepted;
3. missing meta singleton uniqueness rejected;
4. missing intent-id uniqueness rejected;
5. missing position uniqueness rejected;
6. missing request-id uniqueness rejected;
7. missing watermark component uniqueness rejected;
8. missing receipt request-id uniqueness rejected;
9. NOCASE intent-id identity rejected;
10. NOCASE request-id identity rejected;
11. NOCASE watermark component identity rejected;
12. NOCASE receipt request identity rejected;
13. expression UNIQUE does not collapse into false single-column identity, and duplicate exact ids remained insertable in the counterexample;
14. partial UNIQUE does not establish table-wide identity, and duplicate PREPARED ids remained insertable in the counterexample;
15. weakened `component_id` NOT NULL contract rejected;
16. legacy watermark table missing only `CHECK(position>=0)` still rejects `position=-1` through the current exact-permit trigger path;
17. `position=0` remains accepted through the same exact-permit path.

This is a combined **focused SQLite mechanism gate over exact fetched branch logic**. It is not claimed as execution of every published unittest file or as the full real LAB-080/LAB-082 supported-class acceptance gate.

## Decision

The previously independent adoption-index/collation, NOT NULL, and weakened-watermark-CHECK fixes compose cleanly in this focused combined execution. No regression was found in the currently hardened admission/trigger logic.

Do not spend another run repeating this focused gate unless one of the pinned source blobs changes. The highest-value LAB-091 work, while LAB-086 publication remains tool-limited, is now the explicit remaining proof gap from PR #173: exercise `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` with exact real LAB-080/LAB-082 dependencies, starting with timeout-after-commit/UNKNOWN retry convergence, then two-worker/crash behavior.
