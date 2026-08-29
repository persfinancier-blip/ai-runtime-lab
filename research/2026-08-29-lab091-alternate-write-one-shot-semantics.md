# LAB-091 alternate-write / one-shot permit semantics probe

Date: 2026-08-29

## Question

Could SQLite conflict algorithms or statement fan-out turn one legitimate LAB-091 one-shot permit into broader write authority on `shared_anchor_intents`?

This probe was run only because LAB-086 exact publication remains concretely tool-limited in the current runtime. It is part of the saved LAB-091 alternate-write/reentrancy fallback audit, not a replacement for the still-pending full real-stack tests.

## Exact source anchors inspected

Branch: `lab/091-mutable-shared-anchor-writer`

- `full_operation_guards.py` blob `529ee8094d04b0cc9bb208f3fce8f85b2bc6db0f`
- `operation_permit.py` blob `637784a5cb61a024a1df3e0e983887b6d0a838be`
- `row_tokens.py` blob `801eb0fbdb915bb31f40069d087bf3ce56d659a8`
- canonical LAB-080 shared-intent schema from `experiments/shared_anchor_intent_ledger/protocol.py` blob `68834409363c93eee4e9a9a7b9ec076098af0acf`

The focused executable probe reproduced the exact v2 intent INSERT/UPDATE/DELETE guard predicates and the exact Python-side one-shot permit consumption rule on an in-memory canonical `shared_anchor_intents` table.

## Cases executed

1. **`INSERT OR REPLACE` with a fresh `intent_id`/`request_id` but an existing alternate UNIQUE `position`.**
   - A permit exactly matching the candidate new row was installed.
   - Result: `IntegrityError: LAB-091 exact intent creation permit required`.
   - Reason: the v2 INSERT trigger's preexisting `position` check fires before SQLite can use REPLACE to remove the conflicting row.

2. **UPSERT (`INSERT ... ON CONFLICT(intent_id) DO UPDATE`) against an existing intent.**
   - A permit exactly matching the candidate INSERT row was installed.
   - Result: `IntegrityError: LAB-091 exact intent creation permit required`.
   - Reason: the BEFORE INSERT guard sees the existing `intent_id`; the statement never converts insert authority into update authority.

3. **One `UPDATE` statement matching two PREPARED rows while only one exact confirmation permit is present.**
   - The permit matched the first row's exact old/new token only.
   - Result: `IntegrityError: LAB-091 exact intent confirmation permit required`.
   - SQLite rolled the whole statement back; both rows remained PREPARED with NULL receipt binding.
   - Therefore statement fan-out cannot reuse one consumed permit across multiple row mutations.

Observed final rows after all failed probes:

```text
[('i1', 1, 'PREPARED', None), ('i2', 2, 'PREPARED', None)]
```

## Verdict

No reachable LAB-091 bypass was established through these three alternate-write mechanisms. The current v2 exact-row guard plus one-shot Python permit semantics fail closed for:

- alternate-UNIQUE `REPLACE` on intents;
- UPSERT conflict conversion;
- multi-row UPDATE fan-out.

No code change is justified from this probe. Do not add speculative guards for these mechanisms unless one of the pinned source blobs changes or a new reachable schedule is reproduced.

## Remaining work

The high-value LAB-091 gap remains behavioral execution of the published full supported-surface regressions:

- timeout-after-commit/UNKNOWN convergence blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e`;
- process concurrency/crash blob `938877479d4c4b997ea52e8b5857bf89e5c3e246`.

LAB-086 remains priority #1 and should preempt this fallback immediately when a supported byte-preserving source-composition/transfer path is available.
