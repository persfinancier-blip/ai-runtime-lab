# Authenticated provenance chain/link schema V1

Date: 2026-09-04
Status: design contract frozen; exact RED/GREEN pending
Related: LAB-092/#176, LAB-097/#182, LAB-099/#184, LAB-100/#185, LAB-094..096/#179..181

## Objective

Freeze one authenticated link model connecting the already selected provenance objects for:

- trusted initialization (LAB-097);
- provider-generation transitions and their LAB-099 activation-ticket commitments;
- LAB-092 schema migrations;
- LAB-100 activation-authority upgrades/replacements.

The prior canonical-byte contract defines how each object is serialized and digested. This note defines **how those objects form one history**, which parent digest each transition consumes, and the monotonic epoch/replay rules required to prevent a valid certificate from being transplanted into another point in the same logical database history.

This note does not change production code. In this run direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; no exact repository behavioral PASS is claimed.

## Problem

Individually authenticated records are insufficient if each subsystem can accept its own locally valid certificate without proving where that certificate belongs in the global authority history.

Without an explicit parent-link rule, an attacker who can rewrite mutable SQLite rows could attempt to:

- replay an old but valid migration certificate after later provider-generation changes;
- replay a valid activation-authority transition at the wrong point in history;
- splice a provider-generation transition from another branch of the same logical DB;
- restore an earlier provenance record together with matching local rows while leaving later durable state partially intact;
- create two apparently valid descendants of one parent and rely on verifier ambiguity about which branch is canonical.

The remedy is a single append-only authenticated provenance chain whose head is a first-class construction invariant.

## Frozen chain model

Every security-relevant provenance event after initialization consumes the digest of the exact previous chain link and produces a new chain-link digest.

The chain is linear in V1. Forks are invalid.

Conceptually:

```text
InitializationCertificate
        |
        v
ChainLink(epoch=0, event=INITIALIZATION, parent=GENESIS)
        |
        +--> ChainLink(epoch=1, event=PROVIDER_GENERATION_TRANSITION, parent=link0)
        |
        +--> ChainLink(epoch=2, event=SCHEMA_MIGRATION, parent=link1)
        |
        +--> ChainLink(epoch=3, event=ACTIVATION_AUTHORITY_TRANSITION, parent=link2)
        |
        +--> ...
```

A provider-generation transition, migration certificate, or activation-authority transition is never accepted merely because its own authenticated payload is valid. It must also be the exact event payload committed by the next valid chain link whose `parent_link_digest` equals the currently authenticated head.

## Canonical domain

Add one domain to the frozen `YTIMPRV1` canonical family:

```text
ytim.provenance-chain-link.v1
```

Required fields:

```text
1  logical_database_identity_digest  DIGEST32
2  epoch                             U64
3  parent_link_digest                DIGEST32
4  event_kind                        U64
5  event_payload_digest              DIGEST32
6  resulting_provider_head_digest    DIGEST32
7  resulting_authority_digest        DIGEST32
8  resulting_schema_state_digest     DIGEST32
9  chain_protocol_version            U64
```

`event_payload_digest` is the digest of the domain-specific object (initialization certificate, provider-generation transition, migration certificate, or activation-authority transition). It is never an untyped hash of arbitrary bytes.

The three `resulting_*` digests make each link commit the complete construction-relevant post-state, not only the event that occurred. This prevents a valid event payload from being replayed against a different provider head, authority descriptor, or schema state.

## Event kinds

V1 numeric event kinds are protocol constants:

```text
1  INITIALIZATION
2  PROVIDER_GENERATION_TRANSITION
3  SCHEMA_MIGRATION
4  ACTIVATION_AUTHORITY_TRANSITION
```

Unknown event kinds fail closed. Event-kind numbers are semantic protocol values and cannot be reused for a different meaning in V1.

## Genesis and initialization

Initialization is the only event allowed without a previous persisted link.

V1 does **not** use an all-zero digest as a magic parent. Instead define a domain-separated genesis record:

```text
ytim.provenance-chain-genesis.v1
```

Fields:

```text
1 logical_database_identity_digest DIGEST32
2 initialization_nonce             BYTES   # exactly 32 bytes
3 chain_protocol_version           U64
```

`genesis_digest = SHA-256(canonical_genesis_bytes)`.

The initialization chain link has:

```text
epoch = 0
parent_link_digest = genesis_digest
event_kind = INITIALIZATION
event_payload_digest = initialization_certificate_digest
```

The initialization certificate's `initial_authenticated_chain_root_digest` is the digest of this exact epoch-0 link, creating a closed construction invariant rather than an implicit sentinel.

Because that creates an apparent circular dependency if encoded naively, the frozen construction order is:

1. build canonical genesis record;
2. build an initialization certificate **preimage** whose chain-root field is the genesis digest;
3. digest the initialization certificate;
4. build epoch-0 initialization link committing that certificate;
5. treat epoch-0 link digest as the durable authenticated chain root/head after initialization.

Accordingly, the prior LAB-097 field name `initial_authenticated_chain_root_digest` is clarified for implementation: in V1 it binds the **genesis digest**, while the resulting epoch-0 link digest becomes the first stored chain head. Do not attempt a certificate<->link self-referential fixed point.

## Parent rules by transition type

### Provider-generation transition

The event payload is the authenticated provider-generation transition record, including its LAB-099 activation-ticket digest when LAB-090 fencing governs the transition.

Required precondition:

```text
transition.previous_chain_link_digest == current_chain_head_digest
```

The resulting chain link must commit:

- the new provider-generation head digest;
- unchanged activation-authority descriptor digest unless an explicit LAB-100 transition follows;
- unchanged schema-state digest.

A provider-generation transition cannot implicitly change authority implementation or migration state.

### LAB-092 schema migration

The migration certificate must include the current chain-head digest as an authenticated field when implemented.

Add to the LAB-092 V1 schema:

```text
14 parent_chain_link_digest DIGEST32
```

A pure schema migration requires:

- old/new activation-authority descriptor digests equal;
- provider-generation head unchanged during the migration event;
- `parent_chain_link_digest == current_chain_head_digest`;
- resulting schema-state digest changes exactly to the certified repository-owned definition set.

If an authority upgrade is also required, it is a separate subsequent LAB-100 event with its own epoch/link. Combining both under one event is not supported in V1.

### LAB-100 activation-authority transition

Add to the LAB-100 authority transition V1 schema:

```text
7 parent_chain_link_digest DIGEST32
```

The authority transition must consume the current head and produce a link that changes only `resulting_authority_digest`, while preserving the provider head and schema state unless another explicit event follows.

For unresolved activation state, the already frozen handoff digest remains mandatory; the chain link does not replace that proof.

## Epoch rules

- epoch is a strict U64 counter local to one logical database identity;
- initialization link epoch is exactly 0;
- every accepted successor has `epoch == current_epoch + 1`;
- gaps fail closed;
- duplicates fail closed unless they are byte-identical observation of the already authenticated current head during idempotent restart;
- lower epochs never become current again during ordinary startup;
- U64 exhaustion is fail closed; there is no wraparound;
- epoch is not a timestamp and must not be derived from wall-clock time.

The authenticated head therefore consists of at least:

```text
(logical_database_identity_digest, epoch, chain_link_digest)
```

and must be verified together.

## Fork and replay rules

V1 admits exactly one successor for each authenticated head.

If durable storage contains two different valid-looking links with the same parent and same next epoch, startup fails closed before provider reconciliation or repair writes. The verifier must not choose by insertion order, rowid, timestamp, lexicographic digest, or "latest" heuristic.

A byte-identical duplicate row may be treated as storage duplication only if the schema intentionally permits duplicates; preferred implementation is a uniqueness constraint preventing it. Semantically distinct children are always corruption.

Replay checks:

1. old link copied after a newer head -> fail because epoch/head disagree;
2. valid migration certificate replayed later -> fail parent digest;
3. valid authority transition replayed after provider rotation -> fail parent/provider-head commitment;
4. provider transition replayed into another logical DB -> fail DB identity and parent digest;
5. event payload copied under another event kind -> fail chain-link event kind/domain expectations;
6. same event payload digest with different resulting state -> fail event-specific postcondition and chain-link state commitments.

## Schema-state digest

`resulting_schema_state_digest` must itself be a domain-separated digest over the complete security-relevant schema set, not merely the last migration id.

Add domain:

```text
ytim.schema-state.v1
```

V1 fields:

```text
1 schema_epoch                         U64
2 activation_table_definition_digest  DIGEST32
3 activation_trigger_definition_digest DIGEST32
4 migration_protocol_version          U64
```

For a legacy pre-LAB-092 database, explicit trusted migration is required before this V1 chain model can claim a V1 schema-state digest. There is no automatic invented legacy digest.

## Provider-head and authority post-state commitments

`resulting_provider_head_digest` is the already frozen `ytim.provider-generation-head.v1` digest.

`resulting_authority_digest` is the already frozen LAB-100 activation-authority descriptor digest.

Every event validates which post-state fields are allowed to change:

| Event | Provider head | Authority | Schema |
|---|---|---|---|
| INITIALIZATION | establish | establish | establish | 
| PROVIDER_GENERATION_TRANSITION | may change | must stay equal | must stay equal |
| SCHEMA_MIGRATION | must stay equal | must stay equal | may change |
| ACTIVATION_AUTHORITY_TRANSITION | must stay equal | may change | must stay equal |

Any cross-column change outside this matrix is fail closed even if all individual digests are otherwise authentic.

## Startup verification order

Before any provider reconciliation, release, repair, or worker delegation:

1. reconstruct the construction-bound retained authority graph (LAB-094..096);
2. verify logical DB identity and genesis record;
3. verify initialization certificate and epoch-0 link;
4. walk/verify the authenticated provenance chain monotonically to exactly one head;
5. for every link, verify event-domain payload, parent digest, epoch increment, event-specific allowed state delta, and post-state digests;
6. verify the final provider-generation head and LAB-099 activation-ticket provenance;
7. verify final LAB-100 activation authority against registered implementation/version/protocol and durable state;
8. verify final schema state / LAB-092 DDL provenance;
9. only then execute unresolved activation recovery/reconciliation;
10. only after successful recovery open LAB-093 restricted worker delegation.

No verification failure in steps 1-8 authorizes a repair write.

## Crash and UNKNOWN semantics

Appending an event and advancing the chain head must be recoverable under timeout-after-commit/UNKNOWN.

V1 requires event persistence and link persistence to be classified as one logical transition with explicit PREPARED/COMMITTED recovery semantics at the durable ledger layer. The verifier may observe:

- neither event nor link -> operation did not durably happen;
- exact authenticated event PREPARED without committed link -> recover only through the event-specific protocol;
- exact committed event + exact committed successor link -> operation happened;
- committed event with missing/mismatched successor link -> fail closed unless the event-specific protocol contains independently authenticated evidence sufficient to deterministically complete the exact link;
- successor link without the exact event payload -> corruption.

A generic "recompute whatever link current rows imply" repair is forbidden because that would turn mutable rows into provenance authority.

## RED-first chain matrix

Freeze these tests before production implementation:

1. initialization produces exact genesis, epoch-0 link and head reference vector;
2. normal provider transition advances epoch by exactly one;
3. migration after provider transition consumes that exact parent;
4. authority transition after migration consumes that exact parent;
5. replay old migration certificate after later transition -> fail unchanged;
6. replay old authority transition at newer epoch -> fail unchanged;
7. provider transition copied to another logical DB -> fail;
8. parent digest changed by one byte -> fail;
9. epoch gap +2 -> fail;
10. epoch rollback -> fail;
11. same epoch + same parent + two different children -> fail fork;
12. duplicate byte-identical current link -> idempotent observation only, never another transition;
13. event kind changed with same payload digest -> fail;
14. provider transition attempts authority change -> fail;
15. migration attempts provider-head change -> fail;
16. authority transition attempts schema change -> fail;
17. migration certificate parent points to pre-rotation head -> fail;
18. authority transition parent points to pre-migration head -> fail;
19. LAB-099 ticket rebound while chain link/provider transition unchanged -> fail;
20. provider transition rebound together with ticket but parent unchanged and signature/authentication invalid -> fail;
21. old valid subtree restored while authenticated external/current head indicates newer epoch -> fail;
22. committed event row with missing successor link -> fail or exact event-specific recovery only;
23. successor link with missing event payload -> fail;
24. timeout-after-commit returns UNKNOWN, restart discovers exact committed link -> success without duplicate epoch;
25. retry after UNKNOWN is idempotent and cannot create sibling child;
26. schema-state digest copied from another DB -> fail through parent/DB identity;
27. authority descriptor copied from another provider generation -> fail transition/post-state checks;
28. chain parser rejects bool/REAL/text epochs through shared canonical typing;
29. U64 max epoch successor attempt -> fail closed, no wrap;
30. LAB-093 restricted worker cannot append links or obtain raw chain-signing/anchor capability;
31. LAB-087 broker restart verifies complete chain before opening worker endpoint;
32. full LAB-080/081 durable-ledger compatibility remains green after chain implementation.

## Implementation notes

- Keep one chain verification implementation. LAB-092/LAB-097/LAB-100 must not each walk history independently with subtly different rules.
- Persist domain-specific event payloads and chain links separately so audit/recovery can prove both the event semantics and the global ordering.
- Prefer database uniqueness over `(logical_database_identity, epoch)` and over `parent_link_digest` successor identity where compatible with the existing ledger schema, but constraints are defense-in-depth; authenticated verification remains authoritative.
- Do not let SQLite rowid/insertion order define chain order.
- Do not derive missing links from current mutable tables.
- Do not make the chain self-authenticating with an unhashed mutable `current_head` row alone; the head pointer is verified against authenticated links and existing external/shared-anchor continuity.

## Interaction with external/shared anchor

The chain does not replace LAB-080/LAB-081/LAB-086 external/shared-anchor guarantees. The chain orders construction provenance inside the ledger; the existing external anchor provides rollback/equivocation resistance beyond a rewritable SQLite file.

The implementation must bind authenticated chain-head advancement into the same durable authority path used by provider-generation transition evidence, so restoring an old SQLite chain cannot become valid merely because all internal hashes still match.

Exact anchoring mechanics remain implementation-gated until LAB-086 and the downstream exact-source tests can execute.

## Verdict

`AUTHENTICATED_PROVENANCE_CHAIN_LINK_V1_FROZEN`

The initialization, provider-generation, migration and activation-authority provenance designs now have one linear parent-linked history, strict epoch semantics, explicit allowed state deltas, fork/replay failure rules, and a precise startup verification order. Production implementation remains intentionally RED-first once exact executable repository source is available.
