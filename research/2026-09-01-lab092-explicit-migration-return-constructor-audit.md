# LAB-092 — explicit migration return-constructor audit

Date: 2026-09-01

## Question

After `migrate_activation_schema_v1()` has atomically installed DDL + PREPARED provenance and then explicitly confirmed the deterministic migration marker, it returns `cls(path, attested, bootstrap)`. Does that immediate constructor restart create a reachable security/correctness violation by redundantly re-authenticating the same marker?

## Observed control flow

Current PR #177 source at `d05f7c7d7cf9a79182f03274042b25ec652bfa78` performs:

1. `_install_and_reserve_prepared(...)`;
2. non-mutating `_reservation_surface(...)`;
3. full provider-history/runtime verification;
4. activation-record integrity verification;
5. `confirmation.execute(_completion_intent())` and exact `CONFIRMED` check;
6. `return cls(path, attested, bootstrap)`.

The constructor then classifies the local schema as `COMPLETE`, creates a fresh non-mutating confirmation surface, repeats full provider-history/runtime verification and activation-record verification, and only then calls `execute(_completion_intent())` before entering the LAB-090 parent constructor.

## Audit result

The second marker `execute()` is redundant in the ordinary successful migration path, but the current code does **not** lose the confirmation authority result or permit an unverified mutation window:

- the constructor does not trust the earlier result blindly;
- provider history/runtime is freshly verified before the second external marker path;
- activation history is freshly verified before the second external marker path;
- LAB-090 parent recovery begins only after this second pre-auth sequence succeeds;
- concurrent provider-generation change therefore fails the fresh runtime-vs-durable-head check before marker receipt recovery/reconciliation;
- concurrent activation-record corruption fails the fresh activation-integrity check before marker receipt recovery/reconciliation.

If the historical receipt disappears between explicit confirmation and constructor restart, the second `execute()` may perform a redundant authenticated receipt recovery/reconcile. That is extra work, but it remains behind the same full authority/integrity checks and is not a demonstrated security or correctness contract violation.

## Regression experiment discipline

A temporary regression was published as commit `1662a99f9aa61eb2153c82125c8872e2ac4952b4` to assert that explicit migration executes the marker only once. On audit, that assertion was judged to encode an optimization/non-duplication preference rather than an established security contract. The test change was therefore removed in commit `cc50513cfd867d8711fb29db8f33490200390d0d`; the test file blob returned exactly to `6058efd814855120f741019c77b2eaeb34f329cb`.

No production source change was made for this boundary.

## Integration risk observation

PR #177 remains directly based on LAB-090 head `d9a381dd4607a928cd1315adef6431e239995bc1`, so its parent dependency is exact.

PR #175 is 96 main commits behind because main has accumulated durable research/state commits while LAB-090 stayed isolated. GitHub REST currently reports PR #175 `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`. A compare from the LAB-090 merge base `6cc7a044...` to current main shows only research/state files on main; the LAB-090 code file set is disjoint from those main-side changes. Thus current evidence does not show a textual main↔LAB-090 conflict, despite one connector snapshot briefly returning `mergeable=false`; the direct REST state is the higher-confidence observation.

## Decision

Do not add a new LAB-092 regression or source mutation for the migration-return constructor at this time. Keep PR #177 draft until exact behavioral execution is possible. Before integration, re-check PR #175 against current main and PR #177 against the exact LAB-090 head, then run LAB-090 gates before LAB-092 gates.
