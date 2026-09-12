# LAB-091 receipt collation exactness gap

Date: 2026-08-29
Branch: `lab/091-mutable-shared-anchor-writer`
Issue: #170
PR: #173

## Finding

LAB-091 adoption validation checked SQLite affinity/NOT NULL for `asymmetric_provider_receipts`, but SQLite declared collations can still change the semantics of trigger comparisons after adoption. A legacy-compatible schema such as `kind TEXT COLLATE NOCASE` preserves TEXT affinity and NOT NULL while making `kind='reconcile'` compare equal to the canonical state-machine literal `RECONCILE` in the previous v3 guard. The same mechanism applies to provider identity and receipt-binding comparisons.

This is reachable on the supported SQLite path: the collation is a durable table-schema property and is consulted by normal SQL comparison rules inside the trusted triggers.

## Reproduction

A focused sqlite3 harness reproduced all of the following against the pre-fix trigger semantics:

1. `kind TEXT COLLATE NOCASE` allowed a receipt with `kind='reconcile'` to satisfy the v3 `RECONCILE` predicate.
2. `provider_id TEXT COLLATE NOCASE` allowed receipt provider `anchor-a` to match prepared-intent provider `Anchor-A`.
3. NOCASE receipt fields allowed persisted `stable_binding='abcdef'` to satisfy confirmation with `receipt_binding='ABCDEF'` in the v4 matching predicate.

The canonical receipt form (`RECONCILE`, exact provider, exact binding) remained valid.

## Repair

Do not try to parse or reject every non-default `CREATE TABLE` collation. Instead, force the security/state-machine comparisons that must be byte-sensitive to use `COLLATE BINARY` explicitly.

Authoritative published files from the GitHub REST commit records:

- `experiments/mutable_shared_anchor_writer/cross_table_guards.py`
  - commit `078bdfe35b415b0a35dbcbf538cd0a6829c4704f`
  - blob `f76809e067d9d92aa0e7c96145c282757e1fbf0b`
- `experiments/mutable_shared_anchor_writer/history_binding_guards.py`
  - commit `89a7701437c1675e8107221b2610a95c0bd747ab`
  - blob `adb586f953816574a4f4f7380aace7305cf088b8`
- `experiments/mutable_shared_anchor_writer/tests/test_receipt_collation_exactness_regression.py`
  - commit `3078e64307b66687ff96b172a42dd136eb89d7a0`
  - blob `25f7eca3833c57b5246e82514a03e5a1ddf1b516`

The REST commit patches confirm that only the intended BINARY comparison changes were made in the two guard files and that the regression was added as a single new file. An earlier connector response surfaced inconsistent commit/blob identifiers; those values are intentionally not treated as evidence. The commit history and live branch contents above are the authoritative record.

## Focused gate executed in this run

A local sqlite3 harness using the same candidate v3/v4 trigger semantics exercised four regression cases:

- canonical receipt passes v3;
- lowercase `reconcile` under NOCASE is rejected;
- case-variant provider under NOCASE is rejected;
- v4 confirmation rejects case-variant binding and accepts the exact binding.

Result: **4/4 PASS**. `python -m compileall -q experiments/mutable_shared_anchor_writer` also passed in the focused harness.

Important evidence boundary: this run did **not** have a byte-preserving GitHub-branch-to-executable-filesystem bridge. The focused harness used minimal local stubs for the permit connection/state-machine UDF installation sufficient to install and execute the candidate v3/v4 trigger bodies. Therefore this is not claimed as a full branch pytest run or an exact published-byte execution. The repository regression remains queued for execution on the final supported class when executable branch transport is available.

## Follow-up audit

The same SQLite mechanism may affect remaining state/status comparisons in other LAB-091 guards. Next fallback audit should test whether a durable `COLLATE NOCASE` on `shared_anchor_intents.status` can weaken PREPARED/CONFIRMED transition guards, and force BINARY semantics only where a demonstrable reachable bypass exists.
