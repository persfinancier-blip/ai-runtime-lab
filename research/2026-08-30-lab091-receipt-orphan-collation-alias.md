# LAB-091 receipt orphan ownership collation alias

Date: 2026-08-30
Issue: #170
Branch: `lab/091-mutable-shared-anchor-writer`
PR: #173

## Finding

LAB-091 adoption validation previously checked receipt ownership with:

```sql
SELECT r.request_id FROM asymmetric_provider_receipts r
WHERE NOT EXISTS(
  SELECT 1 FROM shared_anchor_intents i WHERE i.request_id=r.request_id
) LIMIT 1
```

This predicate inherits the declared collation of `shared_anchor_intents.request_id`. LAB-091 intentionally accepts legacy schemas whose identity columns can retain a non-BINARY declared collation when an independent full-table BINARY UNIQUE index proves canonical byte-distinct uniqueness. That makes the orphan predicate inconsistent with the accepted identity contract.

A legacy `request_id TEXT COLLATE NOCASE` plus `UNIQUE(request_id COLLATE BINARY)` admits both byte-distinct identity semantics at the index layer and NOCASE comparison at the plain predicate layer. In that schema, an intent request `abc` can make receipt request `ABC` appear owned even though the identifiers are byte-distinct.

## Reproduction

A local SQLite mechanism probe created both tables with `request_id COLLATE NOCASE` and separate BINARY UNIQUE indexes, inserted intent request `abc` and receipt request `ABC`, then compared the old and corrected orphan predicates.

Observed:

- old/default-collation orphan query: returned `None` (false ownership match);
- explicit BINARY orphan query: returned `('ABC',)` (correct orphan detection).

This is mechanism evidence, not byte-for-byte branch pytest execution.

## Fix

Published to `lab/091-mutable-shared-anchor-writer`:

- runtime/adoption fix commit `ec49b717f6fe4223485488ff92650fbe5168b736`;
- `experiments/mutable_shared_anchor_writer/adoption_validation.py` blob `8b676aadb5a5f88d7365e53740318d2788423ff5`;
- ownership predicate now compares `i.request_id COLLATE BINARY = r.request_id COLLATE BINARY`.

Regression published:

- commit `77c5ce6650cf282a18e9001dd9d5c63f386d0a6d`;
- `experiments/mutable_shared_anchor_writer/tests/test_adoption_collation_regression.py` blob `b177667fb2d565b5959a44cacaed3dd69545cb26`;
- the new regression constructs NOCASE request columns with separate BINARY UNIQUE overlays and requires the case-distinct receipt to be rejected as an orphan.

## Execution status

Current-run shell probe:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access ... Could not resolve host: github.com
```

Therefore the exact branch regression was not executed from a byte-preserving checkout in this run. Do not count the local SQLite mechanism probe as exact branch pytest evidence.

## Audit notes

- The fix is limited to an identity comparison already required to be byte-exact by LAB-091.
- It does not change the accepted BINARY UNIQUE overlay model.
- Canonical `generation_id` is SHA-256 lowercase and durable verification recomputes it, so the audited inherited generation-id rotation lookups did not yield an equivalent valid-state case-alias reproduction; no speculative change was made there.
- Continue auditing inherited LAB-082 provider/receipt identity predicates only when a supported path can reach them with a valid durable state.
