# LAB-097 — orphan transition evidence can survive silent re-bootstrap

Date: 2026-09-02

## Scope

Follow-up evidence for #182 / LAB-097. This is not a separate issue: it strengthens the existing partial-deletion contract.

## Source observation

`DurableProviderHistory.__init__()` calls `_init()` before `verify_durable()`. `_init()` treats an empty `provider_generation_head` as fresh state and installs the caller-supplied bootstrap generation/head.

`verify_durable()` verifies transition rows only while iterating adjacent descriptors in the currently visible `provider_generations` chain. It does not enumerate `provider_generation_transitions` independently and reject transition rows that are not part of that chain.

Therefore a partial-history-loss state can retain durable evidence that the DB was previously beyond bootstrap while current initialization still rewrites the active chain to bootstrap and subsequent verification ignores the retained orphan evidence.

## Executed SQLite semantics probe

A file-backed SQLite probe reproduced the exact relevant table semantics:

1. create valid g1 -> g2 provider history and head g2;
2. delete `provider_generation_head` and all `provider_generations` rows, while intentionally leaving the authenticated g1 -> g2 row in `provider_generation_transitions`;
3. execute the current `_init()` empty-head rule: insert bootstrap g1 into `provider_generations` and set head to g1;
4. evaluate the current one-generation terminal verification conditions.

Observed result:

```text
rows = [g1]
head = g1
orphan_transitions = 1
current_terminal_conditions_accept = True
```

No repository behavioral PASS is claimed; this was an isolated file-backed SQLite semantics probe derived from the current source ordering and queries.

## Security/correctness consequence

This is stronger than the complete-row-deletion case already recorded for LAB-097. The database can retain positive evidence of a later historical generation while startup normalizes the active generation chain back to bootstrap and `verify_durable()` still accepts because that orphan transition is never examined.

A verifier that claims durable provider-history integrity must reject unexplained extra transition evidence, not only missing transition evidence for visible adjacent generations.

## Regression-first addition

Extend LAB-097 pre-fix RED with:

- initialize g1;
- rotate durably to g2;
- delete head + generation rows but retain the g1 -> g2 transition row;
- restart with original g1 bootstrap;
- pre-fix: demonstrate `_init()` reconstructs g1 and verification accepts despite the surviving orphan transition;
- post-fix: fail closed before any bootstrap/head write and leave the tampered state unchanged.

Also include the symmetric orphan checks after the initialization-provenance fix: every transition row must belong exactly to the authenticated contiguous chain, with no extra transition rows outside that chain.

## Design implication

LAB-097 cannot be fixed only by checking whether the active generation/head tables are empty. Existing durable transition/receipt evidence is itself proof that the database is not a genuinely fresh bootstrap target. More generally, the authenticated logical-history identity being designed with LAB-095 must cover the complete provider-history relation, including rejection of orphan transition evidence.
