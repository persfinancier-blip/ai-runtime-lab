# LAB-096 construction-bound provider-history strategy slice

Date: 2026-09-14

## Context

LAB-095/#180 had already made the supported ledger/database path construction-bound, but the supported historical ledger still retained its trusted provider-history strategy in a replaceable public `provider_history` slot. Replacing that slot with another legitimate `CoordinatorOnlyProviderHistory` bound to DB B creates split authority: ordinary history calls can open DB B while transaction-internal locked helpers consume the ledger's DB-A connection.

LAB-096/#181 therefore became a composed prerequisite for LAB-095 closure.

## Current-run capability observation

LAB-086 was probed first as required. A direct clone attempt failed before repository code execution:

```
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
```

Exit status: 128. No LAB-086 behavioral PASS is claimed and its complete byte-exact gate was not weakened.

## Implemented slice on PR #187

PR #187 branch `lab-095-database-identity-red-intent` now construction-binds the supported provider-history strategy in `experiments/provider_generation_history/supported.py`.

Mechanism:

- `_provider_history` is the private source-of-truth slot;
- the first `provider_history = CoordinatorOnlyProviderHistory(...)` assignment performed during supported construction initializes that slot;
- later assignment to either `provider_history` or `_provider_history` raises `AttributeError("provider history strategy is construction-bound")`;
- first assignment requires the exact audited `CoordinatorOnlyProviderHistory` type;
- the public `provider_history` name remains a read-only compatibility/introspection alias so existing LAB-081 call sites do not require a broad API rewrite in this slice.

This is deliberately narrower than redesigning every inherited history call. Existing inherited methods still dereference the read-only property, but the property can no longer select a different strategy object after construction.

Production commit sequence on the PR branch:

- `2d2794f3a9703324f3bb7e91f94767ee467d19f5` — construction-bind strategy;
- `af0ed4cfafc830628ee80905ca2809158f546965` — legitimate DB-B strategy replacement regression.

Current PR head after this slice: `af0ed4cfafc830628ee80905ca2809158f546965`.

## Regression added

`experiments/provider_generation_history/tests/test_database_path_binding.py` now includes a legitimate-object replacement case:

1. construct supported ledger/history on DB A;
2. independently construct a legitimate `CoordinatorOnlyProviderHistory` on DB B;
3. attempt public `ledger.provider_history = replacement`;
4. attempt private `ledger._provider_history = replacement`;
5. require both to fail construction-bound;
6. prove the ledger still retains the exact original strategy bound to DB A;
7. execute a supported intent through the ledger;
8. require DB B tail to remain zero and contain no resulting intent row.

This avoids relying only on a fake/permissive monkeypatched strategy and directly targets the split-authority form identified in #181.

## Validation actually executed

The full repository closure is still unavailable in the executable filesystem, so the new repository test has **not** been counted GREEN.

Executed locally in this run:

- authored `supported.py` text: Python compile check PASS before publication;
- isolated construction-bound strategy micro-regression: first bind PASS; public replacement rejected; private-slot replacement rejected; original object retained.

This micro-regression validates the object-binding primitive only. It does not replace the exact repository DB-A/DB-B behavioral gate.

## Audit

The slice closes the specific whole-object replacement path without modifying provider-history cryptographic semantics, DB identity derivation, rotation rules, receipt verification, or caller-owned external provider authority.

Remaining concerns:

- the read-only public alias still exposes the underlying history object and therefore does not by itself solve LAB-093/094 least-capability/trust-root concerns;
- inherited LAB-081 methods continue to dispatch through the property rather than a direct private-slot helper, although the property is now non-rebindable;
- LAB-090 conflict resolution must preserve both activation fencing semantics and this construction-bound strategy invariant;
- exact repository execution remains mandatory before #181/#180 can close.

## Next exact gate

When a supported byte-preserving connector-to-filesystem path is available, execute the PR #187 head exactly and run:

1. `test_database_path_binding.py`, including the legitimate DB-B strategy replacement regression;
2. retained LAB-095 no-stub recovery/confirmed-finalize/locked-custody suite;
3. LAB-081 focused tests;
4. conflict-resolved LAB-090/LAB-092 downstream gates while preserving both `CanonicalDatabaseBinding` and construction-bound provider-history strategy semantics.

Keep PR #187 draft until those gates are observed cleanly.
