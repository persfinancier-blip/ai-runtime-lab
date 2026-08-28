# LAB-091 — expression UNIQUE adoption fix published

Date: 2026-08-29

## Context

LAB-086 remains the first-priority task. In this run the GitHub connector newly returned the complete exact `strict_fence.py` blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`, proving read access to the whole ~40 KB security-critical source. However, no supported byte-preserving bridge from that connector response into the executable filesystem / Contents-API replacement payload was available. The raw-download fallback was also unavailable. Therefore the retained LAB-086 hidden-rowid candidate was not manually reserialized or published.

Per `state/CURRENT.md`, work continued on the allowed LAB-091 fallback.

## Change

The staged expression-index patch was applied through the normal GitHub Contents API to exact predecessor:

- path: `experiments/mutable_shared_anchor_writer/adoption_validation.py`
- predecessor blob: `bab8366438f266342ab461307c9191c9328653bd`
- branch: `lab/091-mutable-shared-anchor-writer`
- commit: `8243a85b8c92cbffc6ea335ff11dd394d99db20d`
- resulting blob: `2281d8e5ae21817b8eab0f52dc44abe61104c745`

The implementation now reads all `PRAGMA index_info()` terms and rejects the index as a canonical identity guarantee if any term has `name=NULL`. SQLite reports expression terms this way (`cid=-2/name=NULL`). This prevents `UNIQUE(id, expression)` from being collapsed into a false table-wide `UNIQUE(id)` guarantee.

A post-write re-fetch returned the same resulting blob and the intended block, so the Contents API write is conflict-checked against the exact predecessor and publication identity is known.

## Validation actually executed

A local in-memory SQLite focused mechanism gate was executed using the exact updated `_unique_key_sets()` algorithm and the same schema shapes as the durable regressions:

1. expression `UNIQUE(id, lower(scope))` is **not** reported as `UNIQUE(id)`; two rows with the same `id` and different `scope` remain insertable, proving the weaker index semantics;
2. all five partial-UNIQUE target shapes remain rejected as canonical identity guarantees: `intent_id`, `position`, `request_id`, watermark component, receipt request;
3. a canonical schema with global PK/UNIQUE identity constraints remains accepted.

Result: **focused schema-admission mechanism checks PASS**.

This is not represented as the full branch unittest gate or complete LAB-080/LAB-082 real-stack acceptance. The durable test files remain the source regression specifications, and PR #173 remains draft.

## Audit

The change is minimal and preserves the previous partial-index rejection. It does not broaden rejection to ASC/DESC, collation, NOT NULL or CHECK semantics because no future-ambiguity counterexample for those has been established. Expression indexes are rejected only because their omitted expression term can demonstrably weaken the apparent named-column identity guarantee.

## Next action

LAB-086 remains first priority. If no byte-preserving write bridge is available for exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7`, resume LAB-091 by executing/reconstructing the exact published expression + partial + missing-constraint regression suites against blob `2281d8e5...`, then continue the full supported LAB-080/LAB-082 concurrency/restart/crash/UNKNOWN gate and reentrancy audit.
