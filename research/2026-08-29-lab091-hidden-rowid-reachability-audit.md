# LAB-091 hidden-rowid reachability audit

Date: 2026-08-29

## Question

After LAB-086 exposed authenticated-history replacement through an implicit SQLite `rowid`, determine whether the same mechanism is reachable through the supported LAB-091 final writer and therefore needs another guard.

## Exact surface inspected

Branch: `lab/091-mutable-shared-anchor-writer`

- final class `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` (`history_bound_operation_scoped.py` blob `e6be9f76f1ced6639e0ec4981911a08848e39e2f`);
- operation-scoped implementation (`operation_scoped_integration.py` blob `95b5a810a4dbac634ff88bc783d7a787ee769430`);
- convergent confirmation implementation (`convergent_operation_scoped.py` blob `7fe0d682c0be4c6388799dd6b8a6ba87f65dda3b`);
- restart-safe schema (`restart_safe_schema.py` blob `5b1ff616d9ddefbf82742e79d3b547eb02b8754b`);
- first-adoption validator (`adoption_validation.py` blob `1731648b4e65b1c5984d4f93b78c45d5a066dd95`).

## Findings

1. The final `_con()` path reaches `SupportedOperationScopedAsymmetricSharedAnchorLedger._con()`, which creates an exact `PermitConnection`, installs the operation-permit UDF and row-token UDFs, and does not enable foreign keys or any alternative mutation mechanism.
2. Supported writes are fixed SQL statements. Intent creation uses `INSERT INTO shared_anchor_intents VALUES(...)`; receipt persistence is delegated through the provider-history writer under an exact one-shot receipt permit; watermark creation uses `INSERT INTO component_anchor_watermarks VALUES(?,?)`. None exposes or supplies an explicit SQLite `rowid`.
3. Every consequential mutable-row DML in the supported path is immediately wrapped in a one-shot permit bound to exact operation identity and old/new logical row state. `BEGIN IMMEDIATE` is explicitly not authority.
4. A raw caller could attempt `INSERT OR REPLACE ... (rowid, ...)`, or could call the public Python permit helper directly, only if it already executes arbitrary same-privilege code inside the writable worker. LAB-091 explicitly does not claim to sandbox such an actor; LAB-087 owns the single-writable-process/filesystem boundary.
5. Repository code search found no `recursive_triggers` or `foreign_keys` enablement that would make an indirect cascade/trigger write newly reachable from the supported final connection.

## Decision

Do **not** add a hidden-rowid sentinel guard to LAB-091 on this evidence. The LAB-086 rowid mechanism is security-relevant there because a legitimate thawed INSERT surface can be redirected through SQLite conflict semantics. In LAB-091, no supported final writer exposes rowid selection and no exact-permit-bearing statement can be steered to an alternate rowid without arbitrary same-privilege code, which is outside the standalone LAB-091 claim.

Adding a speculative rowid guard would expand persistent trigger complexity without a reproduced reachable mutation path and would violate the current audit rule in `state/CURRENT.md`.

## Runtime capability observations

- `git clone --depth 1 --branch lab/091-mutable-shared-anchor-writer https://github.com/persfinancier-blip/ai-runtime-lab.git` failed in this run with `Could not resolve host: github.com`; therefore the two full real-stack regressions were not executable from a branch checkout.
- LAB-086 `strict_fence.py` was successfully fetched through the GitHub connector in four non-overlapping line ranges covering lines 1-949; all ranges reported the exact expected predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. This proves complete readable coverage but not a byte-preserving machine-to-machine composition path into `update_file`; no LAB-086 branch mutation was attempted.

## Next action

Keep LAB-086 first. Publish only exact target `b78e7c98e35138719f77c482c7f1aab36b702de7` when a supported byte-preserving composition path exists. Otherwise obtain a supported branch-to-executable-filesystem transfer and execute LAB-091 real-stack timeout/UNKNOWN blob `92133cdc54fd8b95eb9e3270b5e69d4b85a4b05e` and process concurrency/crash blob `938877479d4c4b997ea52e8b5857bf89e5c3e246` before adding further speculative SQL guards.
