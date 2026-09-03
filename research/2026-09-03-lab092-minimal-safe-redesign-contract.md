# LAB-092 — minimal safe redesign contract

Date: 2026-09-03
Issue: #176
PR under audit: #177 (`lab-092-activation-schema-provenance`, observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`)

## Purpose

Consolidate the retained LAB-092 findings into one implementation contract so the next production change does not patch symptoms independently and recreate the same trust gap at another check/use boundary.

This note does **not** claim an exact branch RED/GREEN run. Direct repository execution remains unavailable in this runtime; this is a source-derived redesign contract over the already retained findings and current PR source.

## Why the current shape is not safely patchable one check at a time

The current candidate establishes `COMPLETE` by combining:

- exact-name checks for the LAB-090 activation table and required activation trigger;
- a `shared_anchor_intents` row shaped like a deterministic migration intent;
- inherited shared-anchor confirmation/re-authentication.

Retained audits have shown four independent classes of failure in that composition:

1. **The completion proof is not domain-separated.** A pre-LAB-092 generic ledger caller can pre-seed the same migration-shaped intent and obtain a real CONFIRMED row before LAB-092 installs the activation schema.
2. **The carrier/authority schema is only partially authenticated.** Exact activation DDL alone does not authenticate the schema/constraints of the provenance carrier, inherited ledger authority tables, or the complete persistent trigger set that can execute inside the migration transaction.
3. **Inherited durable state is incompletely authenticated before consequential work.** Shared-ledger tail/watermark/history invariants cannot be treated as trusted merely because provider history and the migration row look valid.
4. **Checks are separated from the mutation/confirmation boundary.** Explicit migration, constructor/startup, and post-construction operations all admit deterministic check/use schedules where provenance/schema can change after an earlier `_classify()` but before external or durable authority mutation.

Therefore adding another `_classify()`, another exact-name check, a trigger-name blacklist, or a different magic migration intent id is not a coherent fix.

## Minimal safe redesign boundary

### 1. Introduce a LAB-092-specific installation certificate, not a generic ledger intent

The durable proof of installation must be domain-separated so pre-LAB-092 code cannot manufacture it through the ordinary `Intent` API.

The certificate must bind at least:

- a protocol/domain tag that generic LAB-080 writers cannot issue;
- schema version;
- canonical digest of the exact authority-relevant schema set defined below;
- the durable provider-generation identity/head used for migration;
- the exact shared-anchor predecessor/position used for installation completion;
- a unique installation epoch/identity sufficient to reject replay from another logical history/database once LAB-095 identity semantics are available.

A self-hash stored only beside mutable SQLite rows is not sufficient authentication.

### 2. Define one canonical authority-schema manifest

The installation proof must authenticate the complete schema surface whose behavior can affect the operation, not only two required object names.

At minimum the canonical manifest must cover:

- `provider_generation_activations` exact table definition;
- required LAB-090 activation fence trigger exact definition;
- exact provenance-certificate carrier schema;
- inherited `shared_anchor_intents`, `shared_anchor_meta`, and `component_anchor_watermarks` authority-relevant definitions/constraints;
- the complete set of persistent triggers whose target/action can mutate or gate those authority-relevant tables during the operation.

Unexpected persistent triggers on those surfaces must be fail-closed unless explicitly part of the canonical manifest. Name blacklists are insufficient.

The manifest must use deterministic SQLite metadata normalization/fingerprinting and must be covered by regressions for same-name substitution, weakened constraints, and additional persistent triggers.

### 3. Bind proof validation to the SQLite serialization boundary

For any operation that can create/advance migration authority, the trusted predicate must be re-established **inside the same `BEGIN IMMEDIATE` transaction immediately before the durable mutation it authorizes**.

The transaction must establish in one coherent read-set:

- canonical schema manifest matches;
- certificate/provenance state is the expected predecessor state;
- inherited shared-ledger history/tail is valid for the intended next position;
- provider-generation durable head matches the migration authority;
- no unresolved activation/intent state violates the migration precondition.

The mutation must then either commit against that exact state or fail without partial durable authority changes.

An earlier constructor/preflight `_classify()` is advisory only and cannot be the authorization proof for a later mutation.

### 4. Separate local installation from external confirmation, but make the handoff recoverable

SQLite cannot make the external provider atomic with its transaction. The design therefore needs an explicit recoverable state machine rather than pretending the external confirmation is part of the local transaction.

Required durable phases should distinguish at least:

- local exact-schema installation reserved/committed;
- external confirmation pending;
- externally confirmed but not yet durably acknowledged, if that outcome can occur;
- final COMPLETE.

Every externally consequential step must have a durable recovery handle before the external call can leave an ambiguous or committed effect. Restart must be able to reconcile from durable evidence without reconstructing authority from caller-supplied runtime state.

This follows the same ownership principle exposed by LAB-090: successful preparation must establish one trusted recovery scope that survives all later fallible operations.

### 5. COMPLETE must be non-preseedable and non-self-authenticating

`COMPLETE` is valid only when all of the following are authenticated together:

- LAB-092-specific domain-separated certificate;
- canonical authority-schema manifest digest;
- exact installation position/history binding;
- external confirmation evidence for that certificate/position;
- durable provider-generation continuity required to verify that evidence.

A row being syntactically `CONFIRMED` is not itself provenance. A marker cannot authenticate the table/trigger/schema that gives the marker meaning.

### 6. Post-construction operations require boundary checks, not constructor trust

`reserve`, provider rotation, component verification/watermark advancement, receipt persistence, and any future authority mutation must not rely on constructor-time COMPLETE as a lifetime invariant.

If post-construction deletion/substitution is in scope, each consequential mutation needs either:

- a serialization-bound revalidation of the canonical LAB-092 authority predicate; or
- a lower-level capability/ownership mechanism that makes the authenticated objects impossible to mutate through supported writers between construction and use.

Repeated unsynchronized preflight checks do not close the retained TOCTOU schedules.

## Regression matrix required before PR #177 can become ready

### Domain separation
- pre-seed the current generic migration intent through ordinary pre-LAB-092 ledger APIs;
- prove it cannot satisfy the new LAB-092 installation certificate.

### Carrier/schema authenticity
- replace provenance carrier with column-compatible but constraint-weakened schema;
- keep the required LAB-090 trigger exact and add an extra persistent authority-relevant trigger;
- alter inherited ledger/meta/watermark schema while keeping row contents superficially valid;
- all must fail before consequential durable/external mutation.

### Inherited durable-state authenticity
- malformed/gapped shared-anchor tail;
- invalid watermark relative to confirmed history;
- inconsistent provider-history/ledger binding;
- fail closed before installation confirmation or repair.

### Deterministic TOCTOU schedules
- explicit migration: pause after local install/reservation and alter authority schema from a second connection before external confirmation;
- constructor/startup: alter authority state between initial classification and confirmation/recovery;
- post-construction: alter provenance/schema after object construction but before reserve/rotate/verify mutation;
- require no DDL/marker/certificate/provider/receipt/activation/watermark mutation after the predicate is invalidated.

### Crash/restart recovery
- crash after local installation reservation;
- timeout/unknown after external confirmation;
- crash after external confirmation but before durable COMPLETE acknowledgement;
- restart must either reconcile exact evidence or fail closed without inventing completion.

## Integration order

1. Keep PR #177 draft.
2. Write the retained regression groups first against the current candidate and obtain exact RED evidence.
3. Implement one coherent certificate/schema-manifest/state-machine boundary rather than incremental `_classify()` patches.
4. Run LAB-080/LAB-081/LAB-090/LAB-092 focused gates plus compileall.
5. Re-run LAB-090/LAB-100 retained provider-authority regressions because the external-confirmation/recovery boundary composes with provider activation.
6. Audit the final patch specifically for new self-authenticating SQLite markers and new check/use gaps.

## Current runtime observation

LAB-086 remains higher priority. In this run direct `git ls-remote` failed with `Could not resolve host: github.com`; raw web fetch of the exact `strict_fence.py` URL was also unavailable. The GitHub connector still exposes the authoritative LAB-086 source but truncates the whole-file payload at the presentation boundary, so manual/model reserialization remains prohibited. No LAB-086 branch mutation or fresh behavioral PASS is claimed.
