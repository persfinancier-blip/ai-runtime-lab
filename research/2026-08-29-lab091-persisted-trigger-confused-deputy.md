# LAB-091 — persisted trigger confused-deputy adoption gap

Date: 2026-08-29

## Finding

The final LAB-091 constructor replaced/reinstalled all known v2/v3/v4 authorization triggers, but it did not reject *additional* persisted triggers attached to the protected mutable tables.

That is a real alternate-write/reentrancy gap rather than a cosmetic schema difference. SQLite executes an attached trigger inside the same statement/transaction as an otherwise authorized write. An unknown durable trigger therefore inherits the trusted worker connection and can perform side-effect DML on a different table without possessing a LAB-091 one-shot permit for that side effect.

LAB-087's sole-writable-worker boundary does not remove this case: the durable trigger itself runs inside that trusted worker when a supported LAB-091 statement fires.

## RED mechanism reproduction

A focused local SQLite probe used:

- `shared_anchor_intents` as the authorized source table;
- `asymmetric_provider_head(singleton,generation)` initialized at generation `1`;
- an unknown persisted `AFTER INSERT ON shared_anchor_intents` trigger that executes `UPDATE asymmetric_provider_head SET generation=generation+100`.

After one insert, the observed provider-head generation was `101` and the unknown trigger remained durable. This proves the confused-deputy mechanism independently of any speculative threat model.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now contains `adoption_trigger_surface.py`.

`validate_protected_trigger_surface(q)` runs under the same adoption `BEGIN IMMEDIATE` transaction after all supported v2/v3/v4 LAB-091 triggers have been installed/replaced. It requires the durable trigger names attached to each protected table to match the exact supported set:

- `shared_anchor_meta`: v2 meta insert/update/delete guards + v3 matching-PREPARED meta guard;
- `shared_anchor_intents`: v2 insert/confirm/delete + v3 current-tail/provider + v4 deterministic-request + matching-receipt confirmation;
- `component_anchor_watermarks`: v2 insert/update/delete + both v4 confirmed-prefix guards;
- `asymmetric_provider_receipts`: v2 insert/update/delete + v3 matching-PREPARED receipt guard.

Any missing or additional durable trigger fails closed before adoption commits.

Published commits:

- helper: `f2cc3325ea69bc6ceab2fb6f9350c116060d318d`, blob `4f36f7eb12d4fd0839880292cbda9c1108a7c5ba`;
- final-class wiring: `150bbc6ba7d7f4dbcb2ab06bf9ebed738861d2a0`, `history_bound_operation_scoped.py` blob `e6be9f76f1ced6639e0ec4981911a08848e39e2f`;
- regression: `5c6038c87feaaae90a98ce6eac5fbeb3b08d85ad`, blob `64d3d2212688fc46c1955de061d1a57e6ddd4caa`.

## Executed evidence

The exact published helper and regression were reconstructed in the current Python runtime. `git hash-object` matched the fetched GitHub blobs exactly:

- helper `4f36f7eb12d4fd0839880292cbda9c1108a7c5ba`;
- test `64d3d2212688fc46c1955de061d1a57e6ddd4caa`.

Focused unittest result: **3/3 PASS**.

Cases:

1. exact known supported trigger-name surface is accepted;
2. unknown `legacy_confused_deputy` trigger is rejected;
3. missing expected LAB-091 trigger is rejected.

`python -m compileall -q experiments` over the reconstructed focused tree also passed.

## Scope / remaining evidence

This closes the demonstrated persisted-trigger confused-deputy adoption surface for the four LAB-091 protected source tables. It does not claim that arbitrary same-privilege DDL is sandboxed; that remains outside standalone LAB-091 and is owned by LAB-087's process/filesystem boundary.

The full final-ledger branch dependency closure is still not executable in the current shell because direct GitHub DNS resolution fails. Therefore the existing real-stack timeout/UNKNOWN and process concurrency/crash regressions remain pending full behavioral execution.

LAB-086 remains higher priority and still requires byte-preserving publication of exact candidate `b78e7c98e35138719f77c482c7f1aab36b702de7` from predecessor `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` before its full gate can run.
