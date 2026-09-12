# LAB-098 source audit — transition-derived activation presence before recovery

Date: 2026-09-12

## Scope

Source-level audit of draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) for the smallest non-reconstructive fix shape for LAB-098/#183.

This is not an executable RED/GREEN result. Direct exact repository materialization is unavailable in this run, so no behavioral PASS is claimed.

## Current source facts

`IntegratedProviderHistory._verify_durable_locked()` already treats `provider_generations` plus `provider_generation_transitions` as the durable authenticated generation chain:

- the bootstrap descriptor must remain first;
- every later descriptor must have a transition row keyed by its `new_generation_id`;
- each transition proof must equal `make_transition(old, new)`;
- the head must equal the final descriptor.

LAB-090 adds `provider_generation_activations`, where `new_generation_id` is `UNIQUE`, but current startup verification iterates only activation rows that are still present. `_recover_pending_activation()` also returns immediately when the current generation has no activation row.

Therefore deletion is an omission attack: validating only extant activation rows cannot prove that every authenticated post-bootstrap generation still has its required activation evidence.

## Minimal source-level repair seam

Presence should be derived from the authenticated generation-transition side, not from the activation table.

Before any provider recovery mutation, run a read-only verification that conceptually checks:

```sql
SELECT t.new_generation_id
FROM provider_generation_transitions AS t
LEFT JOIN provider_generation_activations AS a
  ON a.new_generation_id = t.new_generation_id
WHERE a.new_generation_id IS NULL;
```

Any row is fail-closed: an authenticated provider transition exists but its required LAB-090 activation evidence is missing.

The inverse orphan check should also remain explicit:

```sql
SELECT a.new_generation_id
FROM provider_generation_activations AS a
LEFT JOIN provider_generation_transitions AS t
  ON t.new_generation_id = a.new_generation_id
WHERE t.new_generation_id IS NULL;
```

Any row is fail-closed as activation evidence with no authenticated transition provenance.

Because both `provider_generation_transitions.new_generation_id` and `provider_generation_activations.new_generation_id` are unique keys in the current model, the two anti-joins establish one-to-one **presence** for every governed non-bootstrap generation without synthesizing missing rows.

## Ordering requirement

The check must occur after durable generation-history verification but before `_recover_pending_activation()` or any provider `commit_activation()` / `release_activation()` call.

Required startup ordering is therefore:

1. verify activation schema provenance / expected schema surface;
2. verify durable provider-generation chain/head;
3. verify transition-derived activation presence and no activation orphans;
4. verify retained activation-row structural/content provenance (LAB-099 composes here);
5. only then reconcile current recoverable activation state;
6. re-verify relevant invariants after recovery mutation before startup succeeds.

This composes with the LAB-100 finding that current PR #175 recovery precedes historical activation verification. Moving only the existing row verifier earlier is insufficient for LAB-098 because an empty/missing rowset still vacuously passes; transition-derived completeness is required.

## Regression consequences

LAB-098 RED/GREEN should distinguish at least:

- delete current `SQL_COMMITTED` activation row while its authenticated transition/head remains;
- delete current `COMMITTED` activation row;
- delete historical `COMMITTED` activation row while a later generation is head;
- insert orphan activation row with no corresponding transition;
- untouched bootstrap-only database: zero transitions implies zero required activation rows;
- valid g1 -> g2 -> g3: exactly one activation row for each transition-derived non-bootstrap generation.

All tamper cases must fail before provider or SQLite mutation and leave the tampered state unchanged.

## Boundary with LAB-099

This closes omission/presence only. It does not authenticate `activation_id`, `expected_position`, `fence`, or other ticket fields. A present but coherently rebound row is LAB-099 and requires the already-frozen authenticated ticket digest/transition binding.

The implementation should therefore not treat the anti-join completeness check as sufficient provenance for activation contents.

## Decision

For LAB-098 implementation, use the authenticated transition chain as the required-record index. Never reconstruct a missing activation row from the current provider, current head, or deterministic activation-id formula. Verify completeness before recovery side effects.
