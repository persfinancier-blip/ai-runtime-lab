# Rebootstrap relying-party convergence, ecosystem split-brain, legacy-client quarantine — v1

Status: `REBOOTSTRAP_RELYING_PARTY_CONVERGENCE_ECOSYSTEM_SPLIT_BRAIN_LEGACY_CLIENT_QUARANTINE_V1_FROZEN`

Date: 2026-09-08

## Context

The preceding total-loss contract established a hard boundary: if every current recovery signer and every previously authenticated continuity root is lost or compromised, a replacement root cannot honestly be described as a cryptographic continuation of the old lineage. Recovery becomes an explicit external rebootstrap into a new trust lineage.

The remaining problem is distribution and convergence. A heterogeneous verifier population will not migrate atomically. During rollout, some verifiers will accept the new lineage, some will still accept the old lineage, some will know that a rebootstrap occurred but lack sufficient evidence to accept the new root, and long-offline clients may reappear with arbitrarily stale trust state. Treating local acceptance as universal convergence creates a split-brain authority window.

## Primary source findings

### Initial trust is external to the relying protocol

RFC 9718 states that a trust anchor is authoritative because trust is assumed rather than derived, and the decision to trust it is made outside the system that relies on it. It also distinguishes initial trust-anchor establishment from RFC 5011 secure in-band succession after trust has already been established. This supports treating total-loss rebootstrap as a new explicit relying-party acceptance event, not as ordinary rotation.

Source: RFC 9718, January 2025, sections 1 and 1.1: https://www.rfc-editor.org/rfc/rfc9718.html

### Distribution assurance is distinct from acceptance policy

RFC 9718 further says validator operators may choose whether to accept published trust anchors according to their own policy. Signatures/TLS can authenticate origin, but they do not force acceptance. This means ecosystem convergence cannot be inferred merely from publishing a correctly signed new root.

### Trust bundles must remain domain-bound and freshness-aware

SPIFFE Federation requires clients to bind a retrieved trust bundle to a specific trust domain, periodically refresh bundle data, and distribute changes to validators. It recommends publishing newly added keys sufficiently ahead of use (3–5 refresh hints), and warns not to merge bundles from different trust domains because that permits impersonation. This is a useful production donor for maintaining explicit `<lineage/domain, bundle>` identity and for rollout telemetry rather than pooling old/new roots into one undifferentiated trust set.

Source: SPIFFE Federation specification: https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/

### Bootstrap and ongoing refresh are separate states

SPIFFE's `https_spiffe` profile requires an initial configured bundle for a self-serving endpoint; after successful bootstrap, subsequent connections use the most recently fetched bundle. This supports distinguishing `BOOTSTRAP_ACCEPTED` from `REFRESHED_CURRENT`, and retaining evidence of which bootstrap artifact a verifier accepted.

## Threat model

Assume the old lineage `L0` suffered total continuity loss and a new externally rebootstrap-authorized lineage `L1` exists. During migration:

- some verifiers know only `L0`;
- some know both but have not accepted the rebootstrap package;
- some have accepted `L1`;
- some are offline or partitioned;
- an attacker may replay old `L0` configuration, suppress `L1` distribution, or present different migration packages to different populations;
- a service may be reachable simultaneously through old and new verifier populations.

The security objective is not perfect instantaneous convergence. It is to prevent stale populations from silently exercising authority that the migrated ecosystem believes has moved to `L1`.

## Core boundary

`NEW_LINEAGE_PUBLISHED != NEW_LINEAGE_ACCEPTED != ECOSYSTEM_CONVERGED`

A second invariant follows:

`DUAL_TRUST_FOR_COMPATIBILITY != CONTINUITY_PROOF`

Temporarily accepting both lineages can be an operational bridge, but it must never be represented as evidence that `L1` cryptographically continues `L0`.

## Frozen data model

### `RebootstrapPackageV1`

Must bind at least:

- `old_lineage_id`;
- `new_lineage_id`;
- `new_root_digest`;
- `rebootstrap_generation`;
- external governance/acceptance evidence digest;
- `not_before`;
- optional `old_lineage_quarantine_at`;
- optional `old_lineage_reject_at`;
- operation-class policy during transition;
- distribution channels / transparency checkpoint references;
- package canonical digest.

### `RelyingPartyMigrationStateV1`

Per verifier / verifier cohort:

- verifier identity or cohort identity;
- last trusted old-lineage frontier;
- rebootstrap package digest observed;
- new lineage/root digest accepted;
- acceptance source/channel;
- accepted-at trusted-time/frontier;
- latest refreshed migration generation;
- allowed operation classes;
- state enum.

State enum:

- `LEGACY_UNAWARE`;
- `REBOOTSTRAP_OBSERVED_NOT_ACCEPTED`;
- `DUAL_TRUST_QUARANTINED`;
- `NEW_LINEAGE_CURRENT`;
- `STALE_OFFLINE_UNKNOWN`;
- `MIGRATION_CONFLICT_NO_AUTHORITY`.

### `EcosystemConvergenceProofV1`

A migration-complete claim must include independently auditable evidence over the required verifier population/cohorts, not merely a server-side flag. At minimum:

- migration generation/package digest;
- required verifier/cohort inventory or bounded population definition;
- accepted-current counts/weights by independent administrative domain;
- explicit excluded/offline population;
- last-seen frontier and freshness for each required cohort;
- telemetry/probe provenance;
- legacy rejection evidence;
- contradiction/fork observations;
- policy threshold for declaring completion.

## Migration semantics

### 1. Publication is discovery, not authority

Publishing `L1` is not sufficient. Each relying party must authenticate the rebootstrap package through its configured external acceptance policy and persist the exact package/root digest it accepted.

### 2. Never silently mutate lineage identity

A verifier configured for `L0` must not reinterpret `L1` as a newer generation of `L0`. `L1` is a distinct lineage. Any alias, endpoint or product name that remains the same must still carry an authenticated lineage identifier internally.

### 3. Dual trust is scoped and temporary

If compatibility requires accepting both `L0` and `L1`, dual trust must be explicitly bounded by:

- operation class;
- object/resource namespace;
- start/end frontier or trusted-time bound;
- verifier cohort;
- migration package digest.

Consequential writes, root/recovery governance, authority rotation, and irreversible state transitions SHOULD move to `L1` earlier than low-risk historical/read-only verification.

### 4. Legacy authority must enter quarantine before ecosystem-complete

Once a verifier accepts `L1`, it must not continue treating `L0` as unconstrained current authority. At minimum, old-lineage authority moves to `DUAL_TRUST_QUARANTINED` with explicit allowed surfaces. Rollback from `L1` acceptance to ordinary `L0` current authority is forbidden.

### 5. Long-offline clients fail closed on current authority

A verifier returning after its migration/freshness evidence expired cannot simply resume consequential operations under `L0`. It may perform historical verification if policy allows, but current-authority operations return `CURRENT_LINEAGE_UNKNOWN_OFFLINE` until it obtains a fresh authenticated migration frontier.

### 6. Partition asymmetry is intentional

A partition that has accepted `L1` never downgrades to `L0`. A partition still on `L0` may continue only within a pre-authorized bounded legacy allowance. After that bound expires, consequential mutation fails closed as `CURRENT_LINEAGE_UNKNOWN_PARTITIONED`.

### 7. Endpoint identity cannot substitute for lineage identity

Serving `L1` from the same hostname/API endpoint previously used for `L0` does not make it continuous. Conversely, moving endpoints does not create a new lineage by itself. Endpoint migration and trust-lineage migration are independent dimensions.

## Quarantine model

Define operation classes:

- `HISTORICAL_VERIFY` — verify artifacts whose claimed time/frontier is safely before the incident boundary;
- `READ_CURRENT_NON_AUTHORITATIVE` — diagnostics/status only;
- `AUTHORITATIVE_READ` — decisions used to authorize downstream action;
- `MUTATE_REVERSIBLE`;
- `MUTATE_CONSEQUENTIAL`;
- `GOVERNANCE_ROOT_RECOVERY`.

Recommended transition:

- `LEGACY_UNAWARE`: no post-incident consequential authority should be accepted once server-side incident policy is active;
- `REBOOTSTRAP_OBSERVED_NOT_ACCEPTED`: historical verify only; no cross-lineage bridge;
- `DUAL_TRUST_QUARANTINED`: allow explicitly enumerated low-risk reads/historical compatibility; deny governance and consequential mutations through `L0`;
- `NEW_LINEAGE_CURRENT`: all current authority uses `L1`; `L0` only for bounded historical verification;
- conflict/unknown states: fail closed for current authority.

## Server-side protection against stale clients

Client-side migration is insufficient because stale clients may continue presenting old credentials/proofs. Services that enforce authority must therefore know the migration generation and apply lineage-aware admission:

- request carries/verifiably implies lineage id and verifier migration generation;
- service rejects `L0` for operation classes already cut over;
- service does not accept a stale client's local statement that `L0` is current;
- compatibility gateways must terminate old-lineage authority and re-authorize into `L1` under an explicit bridge policy rather than transparently forwarding old authority.

This is the critical anti-split-brain property: stale verifiers may remain stale, but they cannot silently cause post-cutover consequential effects.

## Bridge semantics

A bridge from `L0` to `L1` is allowed only as a new authority decision under `L1`, not as continuity evidence.

`LineageBridgeAuthorizationV1` must bind:

- source lineage and source evidence class;
- destination lineage;
- allowed operation/resource scope;
- replay identity;
- expiry/frontier;
- migration generation;
- destination-authority signature/quorum.

The bridge must never permit `GOVERNANCE_ROOT_RECOVERY` or mint unrestricted destination authority from an old-lineage credential after quarantine.

## Ecosystem convergence declaration

Do not declare migration complete merely because:

- the new root is published;
- a majority of recent clients fetched it;
- the control plane reports healthy;
- the old endpoint is removed;
- a telemetry window contains no observed old clients.

`ECOSYSTEM_MIGRATION_COMPLETE` requires all policy-designated critical verifier cohorts to have fresh `NEW_LINEAGE_CURRENT` evidence **and** enforcement points to reject old-lineage consequential authority.

If the population is open/unbounded, universal convergence is unprovable. In that case the only defensible completion claim is operational: `ENFORCEMENT_CUTOVER_COMPLETE_WITH_RESIDUAL_LEGACY_CLIENTS`, with stale clients denied consequential authority until rebootstrap.

## Rollback and fork handling

- Seen/accepted migration generation is monotonic per verifier.
- A smaller migration generation is `REBOOTSTRAP_MIGRATION_ROLLBACK_PROVEN`.
- Different package/root digests for the same `(old_lineage_id, rebootstrap_generation)` are `REBOOTSTRAP_PACKAGE_EQUIVOCATION_PROVEN`.
- Different independently credible new lineages for the same old lineage/incidence create `REBOOTSTRAP_GOVERNANCE_DISPUTE_NO_AUTOMATIC_ACCEPT`.
- No LWW/newest-timestamp/majority-endpoint heuristic resolves a governance fork.

## Fraud / contradiction proofs

1. `SILENT_LINEAGE_REBIND_PROVEN` — same configured logical identity silently changes from `L0` to `L1` without explicit rebootstrap acceptance.
2. `MIGRATION_ROLLBACK_PROVEN` — verifier accepts generation g then later current-authorizes g-1.
3. `REBOOTSTRAP_PACKAGE_EQUIVOCATION_PROVEN` — conflicting roots/packages for same generation.
4. `LEGACY_POST_CUTOVER_AUTHORITY_PROVEN` — old lineage authorizes a prohibited operation after cutover frontier.
5. `DUAL_TRUST_SCOPE_ESCAPE_PROVEN` — dual-trust bridge is used outside its scope/expiry.
6. `STALE_CLIENT_SERVER_ACCEPTANCE_PROVEN` — enforcement point accepts old-lineage consequential authority after configured cutover.
7. `FALSE_CONVERGENCE_CLAIM_PROVEN` — completion asserted without required cohort freshness/rejection evidence.
8. `ENDPOINT_CONTINUITY_LAUNDERING_PROVEN` — same endpoint is used as evidence of lineage continuity.
9. `OFFLINE_LEGACY_REVIVAL_PROVEN` — long-offline client resumes current authority under old lineage without fresh migration proof.
10. `BRIDGE_GOVERNANCE_ESCALATION_PROVEN` — compatibility bridge mints root/recovery/governance authority in destination lineage.

## RED-first matrix

At least the following cases must be executable before production integration:

### Bootstrap / acceptance
1. publish L1, client does not accept -> no current authority;
2. authenticated external package -> client accepts exact L1 digest;
3. package root digest mismatch -> reject;
4. same product/endpoint, different lineage without acceptance -> reject;
5. L1 accepted, attempt to relabel as continuation of L0 -> reject.

### Dual trust / quarantine
6. historical L0 verification during bridge -> allowed if scoped;
7. L0 consequential mutation after quarantine -> blocked;
8. L1 consequential mutation after acceptance -> allowed;
9. dual-trust scope escape -> blocked;
10. bridge expiry -> L0 path blocked.

### Rollback / partition / offline
11. accepted g2 then replay g1 -> rollback detected;
12. partitioned L1 side receives L0 -> no downgrade;
13. partitioned legacy side within bounded allowance -> only allowed classes;
14. allowance expired -> fail closed;
15. long-offline L0 client returns -> current authority unknown until refresh;
16. snapshot restores pre-L1 migration state -> external fresh frontier required.

### Server enforcement
17. stale L0 client attempts cutover-prohibited mutation -> server rejects;
18. stale L0 client attempts historical read -> policy-dependent allowed;
19. missing lineage id on consequential request -> reject;
20. compatibility gateway transparently forwards old authority -> reject;
21. explicit L1 bridge authorization -> scoped success;
22. bridge attempts governance-root operation -> reject.

### Convergence evidence
23. 99% clients migrated but critical signing cohort stale -> not complete;
24. all critical cohorts fresh + enforcement cutover proven -> complete;
25. open population with residual offline clients -> only operational cutover claim;
26. telemetry absence without rejection evidence -> not complete;
27. two independent probes disagree on cohort state -> unknown/dispute;
28. stale convergence report replay -> reject by freshness/frontier.

### Forks / equivocation
29. two roots for same generation -> no automatic acceptance;
30. majority endpoints serve A, minority serves B -> no majority heuristic;
31. governance package A/B each independently credible -> dispute/no mutation;
32. endpoint redirect changes lineage unexpectedly -> reject.

## Implementation implications for LAB-093 family

When exact executable source becomes available, the authority graph should gain explicit lineage and migration-generation identity. Do not hide rebootstrap inside generic key rotation or bundle refresh.

Likely implementation surfaces:

- immutable `trust_lineage_id` on authority-bearing records and capability views;
- monotonic accepted `rebootstrap_generation` in verifier durable state;
- operation-class admission that rejects legacy lineage after configured cutover;
- historical verifier path distinct from current-authority path;
- explicit bridge authorization object if compatibility is required;
- convergence audit/reporting that cannot itself grant authority.

These are design requirements only; no executable PASS is claimed in this run.

## Decision

Freeze `REBOOTSTRAP_RELYING_PARTY_CONVERGENCE_ECOSYSTEM_SPLIT_BRAIN_LEGACY_CLIENT_QUARANTINE_V1_FROZEN`.

A non-continuous rebootstrap is complete only when current-authority enforcement has converged sufficiently to prevent stale old-lineage verifiers from causing prohibited effects. Client population convergence and server enforcement are separate evidence dimensions. Universal convergence is not claimable for an unbounded/offline population; the safe operational endpoint is enforcement cutover plus explicit residual-legacy quarantine.
