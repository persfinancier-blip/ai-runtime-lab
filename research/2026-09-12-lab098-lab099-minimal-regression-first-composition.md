# LAB-098 + LAB-099 minimal regression-first composition on LAB-090

Date: 2026-09-12
Status: SOURCE-PROVED PATCH SHAPE; exact RED/GREEN pending
Issues: #183 / LAB-098, #184 / LAB-099
Source inspected: draft PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`

## Objective

Pin the smallest coherent test/implementation seam that closes both:

- LAB-098: deleted/missing activation row while authenticated provider-generation transition remains;
- LAB-099: present activation row whose authority-relevant ticket fields were coherently rebound.

This note does not claim exact branch execution. Direct git materialization was re-probed in this run and failed before repository execution with `Could not resolve host: github.com`.

## Source facts

On PR #175:

1. `provider_generation_transitions(new_generation_id PRIMARY KEY, old_generation_id, provider_id, old_mac, new_mac)` is the authenticated non-bootstrap transition index.
2. `provider_generation_activations(..., new_generation_id UNIQUE, ..., status)` is the operational activation/recovery table.
3. `_verify_activation_records()` validates only activation rows that exist.
4. `_recover_pending_activation()` runs before `_verify_activation_records()` and may mutate provider/SQLite state.
5. transition evidence currently authenticates old/new generation identity only; it has no activation-ticket digest field.
6. `rotate_provider()` writes the activation row and provider-generation transition in the same SQLite transaction, so every LAB-090-governed non-bootstrap transition has exactly one legitimate activation row at creation time.

## Minimal regression-first seam

The combined constructor/restart gate should be expressed as one read-only provenance pass before `_recover_pending_activation()`.

Required order:

1. verify durable provider-generation history/transition authenticity;
2. verify activation schema provenance/classification (LAB-092 composition);
3. derive required activation row presence from authenticated `provider_generation_transitions`;
4. reject missing activation rows;
5. reject extra activation rows that have no authenticated transition;
6. canonicalize every required activation ticket under `ytim.lab099.activation-ticket.v1` and compare it with the digest authenticated by its transition;
7. verify runtime provider/head compatibility;
8. only now call `_recover_pending_activation()`;
9. after recovery, re-run structural/status checks as needed, but do not use the post-recovery state to prove pre-recovery provenance.

No failure in steps 1-7 may call provider `activation_status`, `commit_activation`, `release_activation`, `abort_activation`, or mutate SQLite.

## LAB-098 presence checks on the current relational shape

Given PR #175's one-row-per-transition model, the read-only completeness checks are two anti-joins.

Missing required activation:

```sql
SELECT t.new_generation_id
FROM provider_generation_transitions AS t
LEFT JOIN provider_generation_activations AS a
  ON a.new_generation_id = t.new_generation_id
WHERE a.new_generation_id IS NULL
LIMIT 1;
```

Unexpected activation without transition:

```sql
SELECT a.new_generation_id
FROM provider_generation_activations AS a
LEFT JOIN provider_generation_transitions AS t
  ON t.new_generation_id = a.new_generation_id
WHERE t.new_generation_id IS NULL
LIMIT 1;
```

Because `provider_generation_transitions.new_generation_id` is a primary key and `provider_generation_activations.new_generation_id` is unique, an empty result for both anti-joins establishes one-to-one presence for the existing LAB-090 model. Bootstrap remains intentionally activation-free because it has no transition row.

These checks must run after transition-history authenticity is verified. The activation table is not allowed to prove its own required row set.

## Why LAB-099 cannot be a local PR #175 verifier patch

The current transition table has no authenticated activation commitment. Therefore a local `_verify_activation_records()` change can validate structure and cross-table identity but cannot recover the original historical `expected_position`, `activation_id`, or `fence` after a coherent row rewrite.

Adding a self-hash to `provider_generation_activations` would not help: an attacker who can coherently rewrite that mutable row can rewrite its self-hash too.

Therefore the smallest sound GREEN for LAB-099 necessarily changes authenticated transition provenance.

## Minimal authenticated transition delta

Each LAB-090-governed non-bootstrap transition must authenticate one additional fixed 32-byte value:

```text
activation_ticket_digest = SHA-256(
    canonical record domain ytim.lab099.activation-ticket.v1:
      provider_id,
      provider_generation,
      new_generation_id,
      expected_position,
      activation_id,
      fence,
      activation_protocol_version
)
```

The digest must participate in the bytes authenticated by predecessor/successor transition authority. Merely adding an unauthenticated SQL column does not close LAB-099.

This implies a versioned transition schema/protocol change (or a new authenticated provenance transition relation) and therefore composes with LAB-092/LAB-097 provenance migration. Do not silently alter legacy `TransitionProof` semantics under the same version.

## Rotation ordering implication

PR #175 currently receives a transition proof before provider activation preparation, while the LAB-099 digest contains `expected_position` and provider-assigned `fence`, which do not exist until `prepare_activation()` returns.

Therefore a sound implementation cannot keep the exact current call contract unchanged and still authenticate the exact ticket. One of these must become explicit in the new protocol version:

- create/obtain the activation reservation first, canonicalize the exact ticket, then construct/sign the activation-aware provider-generation transition; or
- authenticate an equivalent externally produced activation-handoff record that already commits the exact ticket and is itself cryptographically bound into the provider-generation transition.

The first shape is the smaller prototype change because the current test model already retains generation verification keys in `GenerationDescriptor`, but production semantics must preserve the intended authority boundary rather than treating key availability in the prototype as permission to mint transitions arbitrarily.

## Smallest RED-first test set

Add tests at supported constructor/restart abstraction level before production provenance changes:

1. valid g1 -> g2; delete only g2 activation row; restart -> current code accepts/returns past absence path (RED); fixed code fails before provider calls or SQLite mutation.
2. valid g1 -> g2 -> g3; delete historical g2 activation row -> RED then fail closed.
3. add extra structurally valid activation row with no transition (where test fixture/schema permits) -> fail closed.
4. valid g1 -> g2 -> g3; rewrite historical g2 `expected_position`, recompute deterministic `activation_id`, choose another positive fence -> current structural verifier accepts (RED); digest-bound verifier fails.
5. mutate only authenticated transition ticket digest -> transition/provenance verification fails before recovery.
6. intact current `SQL_COMMITTED` exact ticket -> provenance pass succeeds, then existing recovery behavior proceeds.
7. intact `COMMITTED_FENCED` exact ticket -> provenance pass succeeds, then release may occur.
8. tampered historical row plus recoverable current pending activation -> constructor fails before current provider is committed/released; this composes directly with LAB-100's verify-before-recover finding.

For tests 1, 2, 4, 5, and 8, snapshot provider activation state and relevant SQLite rows before restart and assert byte/value equality after the expected constructor failure.

## Implementation target

Do not patch PR #175 alone with a fake historical ticket checker. The smallest coherent implementation target is the provenance-composed branch/stack that can version transition evidence and activation schema together.

Suggested production decomposition once exact execution returns:

- shared canonical provenance encoder from the already frozen V1 contract;
- transition/provenance schema version carrying authenticated `activation_ticket_digest`;
- `_verify_activation_provenance_before_recovery()` performing transition authenticity, both anti-joins, strict SQLite type checks, and digest comparisons;
- constructor ordering changed so this verifier completes before `_recover_pending_activation()`;
- existing post-recovery structural/status verifier retained only as a secondary invariant check.

## Verdict

`LAB098_LAB099_MINIMAL_REGRESSION_FIRST_COMPOSITION_PINNED`

LAB-098 has a minimal current-schema read-only completeness seam. LAB-099 necessarily crosses the authenticated transition protocol/schema boundary because the original ticket is otherwise unrecoverable after coherent historical rewrite. The combined GREEN must therefore be provenance-versioned and verify-before-recover; no exact behavioral PASS is claimed until byte-exact repository execution is available.