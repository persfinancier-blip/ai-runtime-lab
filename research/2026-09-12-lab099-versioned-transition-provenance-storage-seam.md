# LAB-099 — versioned transition-provenance storage seam

Date: 2026-09-12
Status: SOURCE/SCHEMA DECISION FROZEN; exact RED/GREEN pending
Related: LAB-092/#176 PR #177, LAB-097/#182, LAB-098/#183, LAB-099/#184, LAB-100/#185

## Objective

Determine the smallest sound storage/versioning seam for the frozen LAB-099 `activation_ticket_digest` contract without inventing provenance from mutable activation rows and without destabilizing the already-published LAB-090/LAB-092 draft stack.

## Current source facts

On LAB-090 draft PR #175, `provider_generation_transitions` is a five-column legacy relation:

- `new_generation_id` primary key;
- `old_generation_id`;
- `provider_id`;
- `old_mac`;
- `new_mac`.

The MAC body authenticates only provider id + old generation id + new generation id. It does not authenticate the LAB-090 activation reservation (`expected_position`, `activation_id`, provider-assigned `fence`) or any activation protocol version.

LAB-090 stores those ticket fields only in `provider_generation_activations`. `_verify_activation_records()` can therefore validate row shape but cannot recover the original ticket after a coherent rewrite.

PR #177 / LAB-092 already treats migration provenance as an authenticated completion event and intentionally keeps schema installation/restart classification outside ordinary auto-repair. The frozen global provenance-chain contract also requires domain-specific event payloads and chain links to remain separate rather than making one mutable SQL row family prove every layer of authority.

## Decision

Use a **separate versioned authenticated provider-transition provenance relation** keyed one-to-one by `new_generation_id`. Do **not** ALTER the legacy `provider_generation_transitions` row into a mixed V1/V2 proof format.

The legacy transition row remains the compatibility/structural projection used by current LAB-081/LAB-090 code. The new relation is the authoritative LAB-099 event payload for transitions governed after the authenticated cutover.

Minimum V2 relation semantics:

```text
provider_generation_transition_provenance
    new_generation_id            PRIMARY KEY / exact transition identity
    transition_protocol_version  INTEGER (exact supported version)
    parent_chain_link_digest     DIGEST32
    activation_protocol_version  INTEGER
    activation_ticket_digest     DIGEST32
    old_authenticator            canonical old-authority authenticator
    new_authenticator            canonical successor authenticator
```

Exact SQL names/types stay implementation-gated until executable REDs are available, but these semantics are mandatory. The V2 authenticator body must cover the complete canonical transition event, including the frozen LAB-099 activation-ticket digest and protocol version; the existing V1 MAC over only `(provider_id, old_generation_id, new_generation_id)` is not sufficient authentication for the sidecar fields.

The relation must be one-to-one with `provider_generation_transitions` for every post-cutover LAB-090-governed transition. An unauthenticated digest column or self-hash in `provider_generation_activations` is explicitly insufficient.

## Why a separate relation is the smallest safe seam

### 1. It preserves the published legacy proof format

Directly adding nullable/version-dependent columns to `provider_generation_transitions` would create one row whose interpretation changes by protocol generation. Existing V1 `old_mac/new_mac` values would still authenticate only the old three-field body, so merely adding `activation_ticket_digest` beside them would look versioned while remaining unauthenticated.

A true in-place V2 row would therefore require replacing the meaning of the existing MAC columns, migration of every historical transition, and dual parser rules inside the same table. That is a larger and more ambiguous change than a keyed V2 event relation.

### 2. It matches the frozen chain architecture

`AUTHENTICATED_PROVENANCE_CHAIN_LINK_V1_FROZEN` requires domain-specific event payloads and global chain links to be persisted separately. A provider-generation transition event is one such payload. A dedicated relation gives LAB-099 a natural event boundary while the chain link provides ordering, epoch, parent and post-state commitments.

### 3. It composes cleanly with LAB-098

For each governed non-bootstrap transition, startup can perform two read-only cardinality checks before recovery:

- authenticated transition/event -> exactly one activation row;
- activation row -> exactly one authenticated governed transition/event.

Then canonicalize the activation ticket and require its digest to equal the authenticated provenance row. Presence and content are thus derived from the same authenticated transition event.

### 4. It avoids retroactive self-authentication

The mutable activation table cannot be used to mint its own historical truth during migration. A separate authenticated event makes that boundary explicit.

## Migration / cutover classification

The migration must distinguish three classes.

### A. Pre-LAB-090 history

A database whose historical provider transitions predate activation fencing and has no prior LAB-090 activation evidence may be explicitly migrated by the authenticated LAB-092/provenance-chain path.

The authenticated migration/cutover event defines the first provider-generation transition that is required to carry V2 activation provenance. Earlier transitions remain explicitly `LEGACY_UNGATED`; they do not receive fabricated activation tickets and are not silently reinterpreted as LAB-090 transitions.

### B. Fresh post-cutover history

Every provider rotation after the cutover must:

1. bind/verify the exact successor provider authority;
2. reserve the exact activation ticket (`prepare_activation()`);
3. canonicalize and digest that exact ticket;
4. construct/authenticate the V2 provider-transition event containing that digest and the current provenance-chain parent;
5. durably persist the transition, V2 provenance event and activation row as one recoverable logical transition;
6. advance the authenticated provenance chain;
7. only after durable verification perform provider commit/release according to LAB-090 recovery semantics.

### C. Existing LAB-090 rows without authenticated ticket provenance

This is the critical case: a database may already contain LAB-090 activation rows created by PR #175 semantics, but those rows were never committed by authenticated transition evidence.

Such history **must not be silently upgraded** by hashing the current activation rows and calling the result authenticated. A coherent attacker-controlled rewrite would be blessed as history.

Classify this state as `LEGACY_LAB090_UNATTESTED` (name illustrative). Ordinary V2 startup fails closed before provider/SQLite recovery mutation.

A future explicit re-attestation/import protocol may upgrade such a database only if it has independently authenticated evidence sufficient to establish the original ticket bytes. If no such evidence exists, the historical ticket cannot be made LAB-099-authenticated retrospectively. This is a provenance limitation, not a migration inconvenience.

## Constructor verification order

For an initialized V2 database, startup order is:

1. bind LAB-094..096 retained authority/database identity;
2. authenticate initialization + LAB-092 migration/cutover provenance;
3. verify provider-generation V1 structural history from the retained root;
4. verify every required V2 transition-provenance event and provenance-chain link;
5. derive the exact governed activation-row set from those authenticated events;
6. verify LAB-098 one-to-one presence and LAB-099 canonical ticket digests;
7. verify runtime provider/head compatibility;
8. only then call `_recover_pending_activation()` or any provider commit/release/SQLite repair path.

This preserves the LAB-100 verify-before-recover finding.

## Regression-first additions

When exact execution is available, add these REDs before production provenance code:

1. V1 transition row + injected unauthenticated digest column/side data cannot satisfy V2 startup.
2. V2 provenance row whose ticket digest is changed while legacy transition MACs remain valid fails.
3. V2 provenance row whose old/new authenticator still covers only the V1 body fails protocol-version verification.
4. transition has V2 provenance but activation row missing -> fail before recovery.
5. activation row exists but no V2 provenance for a post-cutover transition -> fail before recovery.
6. pre-cutover legacy transition has no activation/V2 provenance -> PASS only when authenticated cutover proves it predates LAB-090 governance.
7. existing LAB-090 activation history with no authenticated ticket provenance -> explicit `LEGACY_LAB090_UNATTESTED`, fail closed; migration must not hash-and-bless current rows.
8. valid post-cutover rotation persists exact ticket digest and restarts successfully.
9. one-byte change to `expected_position`, `activation_id`, `fence`, provider/generation identity or protocol version fails before recovery side effects.
10. current recoverable `SQL_COMMITTED` activation plus separately tampered historical V2 ticket fails before current provider commit/release or SQLite mutation.

## Implementation boundary

Do not implement this production refactor until exact branch materialization allows RED/GREEN execution. The current result is the storage/versioning decision needed to avoid a wrong partial patch.

The first executable implementation should introduce the V2 event relation/parser and tests in isolation, then compose it with PR #177 migration classification and LAB-098 anti-joins before changing rotation ordering.

## Verdict

`LAB099_SEPARATE_VERSIONED_TRANSITION_PROVENANCE_RELATION_FROZEN`

A separate one-to-one authenticated provider-transition provenance event is the smallest sound seam. Directly versioning the existing transition row would either leave the new digest unauthenticated or force a larger ambiguous reinterpretation of legacy MAC fields. Pre-LAB-090 history may cross an authenticated cutover without fabricated tickets; already-existing LAB-090 ticket rows without authenticated commitments cannot be silently upgraded.