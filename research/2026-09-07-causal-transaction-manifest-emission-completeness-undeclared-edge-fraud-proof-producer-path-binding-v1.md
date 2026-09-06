# Causal / Transaction Manifest Emission Completeness — Undeclared-Edge Fraud Proof — Producer-Path Binding V1

Status: `CAUSAL_TRANSACTION_MANIFEST_EMISSION_COMPLETENESS_UNDECLARED_EDGE_FRAUD_PROOF_PRODUCER_PATH_BINDING_V1_FROZEN`

Date: 2026-09-07

Scope: LAB-093 / #178 follow-up to the federated finalization barrier contract. This is a design freeze and RED-first contract, not a claim of exact repository behavioral execution.

## Problem

The federated finalization barrier is only sound if consequential producers cannot execute an effect while omitting a material causal edge or transaction participant from the evidence used to decide finalization and GC reachability.

A passive observer is insufficient. A buggy or malicious producer can emit the effect and suppress the observer-visible declaration. If the barrier sees only declarations, the graph can look closed while a real cross-domain consequence remains undeclared.

Therefore the manifest must be on the same authenticated authority path as the consequential effect, not an optional side channel.

## Donor mechanisms checked

Primary-source mechanisms used as design donors:

1. Apache Kafka transactions: transaction identity carries producer id/epoch and the coordinator tracks the partitions added to a transaction; transaction markers are written for the participating topic partitions. This demonstrates that participant membership can be part of the authoritative commit protocol rather than inferred later.
   - https://kafka.apache.org/41/design/protocol/
   - https://kafka.apache.org/11/design/protocol/

2. PostgreSQL logical decoding: `pg_logical_emit_message(transactional=true, ...)` places a logical message in the current transaction and flushes it with that transaction. This is a donor for binding metadata emission atomically to the same database commit that creates the effect.
   - https://www.postgresql.org/docs/18/functions-admin.html

3. in-toto: signed link/attestation metadata records step subjects/products and materials, but the official documentation explicitly notes that artifacts not passed/recorded are not magically discovered. This is a useful negative donor: authenticated metadata is not a completeness proof unless the authority path constrains what may be omitted.
   - https://in-toto.io/docs/getting-started/
   - https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md

## Threat model

Adversaries include:

- buggy producer code that forgets one participant/edge;
- malicious producer intentionally hiding an edge to permit early finalization or GC;
- producer and reporter sharing the same common-mode bug;
- stale producer schema that does not know a newly material edge class;
- split-brain producer identities or replayed manifests;
- downstream side effects created after commit from a cause that was known at commit time;
- a producer declaring a broad manifest but executing an effect outside it;
- a producer claiming `no_outgoing_edges` without evidence;
- a late auditor discovering an undeclared effect after the source frontier has advanced.

Out of scope: proving arbitrary future semantic consequences that no policy/schema could know existed. Unknown semantics fail closed when they become material; they are not retroactively fabricated as known-at-commit facts.

## Core decision: producer-path binding

Every consequential mutation MUST be accepted only through an authority path that binds the effect identity to a canonical `EffectManifestV1` before or atomically with effect commit.

An effect is not `BARRIER_VISIBLE_COMMITTED` merely because its business-state mutation exists. It is visible/eligible only when both are authenticated under the same producer transaction/authority generation:

- canonical effect commitment;
- canonical manifest commitment.

The effect record MUST carry (directly or through an authenticated transaction envelope) the manifest digest. The manifest MUST carry the effect digest / stable effect identity. This bidirectional binding prevents independent replacement.

For stores supporting atomic transactional metadata, manifest + effect commit in the same transaction is preferred. Where domains cannot share one atomic store, a prepare/commit protocol MUST make the manifest immutable before external effect release and make release conditional on the exact manifest digest.

## Canonical EffectManifestV1

Minimum authority-relevant fields:

- `manifest_version`
- `schema_generation`
- `producer_identity`
- `producer_authority_generation`
- `transaction_id`
- `transaction_epoch` / anti-replay generation
- `effect_id`
- `effect_digest`
- `cause_set_root`
- `participant_set_root`
- `outgoing_edge_set_root`
- `delayed_consequence_class_set_root`
- `membership_epoch`
- `policy_frontier`
- `trust_frontier`
- `declaration_mode`: `EXPLICIT_SET | SCHEMA_COMPLETE_EMPTY`
- `manifest_nonce`
- `created_at_logical_frontier`
- authenticated signature/MAC/certificate according to the retained authority graph.

Participant and edge sets MUST be canonical, duplicate-free, ordered by canonical key before Merkleization, and typed. Ambiguous string concatenation is prohibited.

## Completeness authority

A producer cannot prove completeness merely by signing the set it chose to report.

Completeness comes from the combination of:

1. **closed-world effect schema**: for the declared `schema_generation`, every consequential operation kind has a finite typed declaration rule describing all material edge/participant slots it may instantiate;
2. **authority-path enforcement**: effect execution API requires those slots/commitments and refuses release if required declarations are absent;
3. **independent verifier**: a verifier that is not the producer implementation re-derives required declaration slots from the operation type/schema and validates the manifest before barrier admission;
4. **post-effect reconciliation**: independently observable durable writes/messages are checked against the committed manifest where such observation exists;
5. **fraud proofs**: a later observed effect/participant can be proven absent from the committed set using the original manifest commitment plus the effect's authenticated producer-path binding.

`SCHEMA_COMPLETE_EMPTY` is valid only when the schema independently states that this operation kind has zero material outgoing slots. Producer assertion alone is insufficient.

## Edge taxonomy

Each outgoing declaration is typed:

- `CAUSES_IMMEDIATE_EFFECT`
- `CAUSES_DELAYED_DETERMINISTIC_EFFECT`
- `TRANSACTION_PARTICIPANT`
- `REVOCATION_PROPAGATION`
- `REPAIR_PROPAGATION`
- `APPEAL_PROPAGATION`
- `ARCHIVE_RELOCATION`
- `GC_REACTIVATION`
- `RECOVERY_DEPENDENCY`
- `AUTHORITY_TRANSITION`

Edges carry destination domain, destination object/effect identity or committed derivation key, materiality class, and whether completion may occur after the source transaction.

## Delayed consequences

A delayed deterministic consequence known from the source operation MUST be declared at source commit even if its destination effect executes later.

The source manifest creates an in-flight obligation root. Completion replaces that obligation with an authenticated destination effect reference. Cancellation requires an authenticated terminal cancellation allowed by policy; timeout alone is not cancellation.

A scheduler/queue that will later choose among multiple destinations must commit to a bounded destination class and derivation key sufficient for independent reconciliation. An unbounded `maybe something later` declaration does not satisfy completeness.

## Undeclared-edge fraud proof

`UndeclaredEdgeFraudProofV1` proves that a material destination effect/participant is authentic and should have been declared by a specific source manifest, yet no matching declaration exists.

Minimum inputs:

- source `EffectManifestV1` + authentication path;
- authenticated source effect binding to that manifest;
- destination effect/participant evidence + producer/transaction identity;
- deterministic causality/participant binding evidence defined by the effect schema;
- Merkle non-membership or complete-set proof against the committed participant/outgoing-edge root;
- schema generation and rule showing this edge class was declaration-required;
- trust/policy frontiers used for verification.

Verdict: `OMITTED_MATERIAL_EDGE_PROVEN`.

Consequences:

- source transaction/campaign closure becomes `REVALIDATION_REQUIRED`;
- dependent finalization certificates become stale;
- affected evidence closure becomes a GC root;
- producer authority may be quarantined according to policy;
- historical repair must add an authenticated repair edge; history is not rewritten.

## Compact non-membership

For large sets, use a canonical sorted Merkle map / sparse commitment supporting membership and non-membership proofs. A Bloom filter is insufficient for destructive authority because false positives/absence ambiguity do not prove exact set membership.

If the commitment construction lacks sound non-membership, the full canonical set must be retained until the challenge/revocation/repair horizon closes.

## Common-mode failure control

The producer implementation and completeness verifier MUST NOT be the sole copies of the same extraction routine for consequential E2/E3/E4-class edges.

Acceptable independence examples:

- producer declares from runtime operation parameters; verifier derives required slots from a separately versioned declarative schema;
- database transaction emits a transactional manifest message while an independent CDC/reconciliation path checks durable affected rows/keys;
- external broker transaction coordinator supplies authoritative partition/participant metadata that is compared with the producer manifest.

If both sides use one buggy helper, the result is `SINGLE_DOMAIN_ASSURANCE`, not independent completeness.

## Schema evolution

Manifest `schema_generation` is immutable historical context.

A new schema that discovers a previously unmodelled material edge class does not reinterpret old bytes silently. It starts a historical repair campaign:

- identify affected operation kinds/generations;
- scan retained originals/observable effects;
- publish authenticated repair edges or explicit unaffected proofs;
- root affected closures while scan coverage is incomplete;
- invalidate stale GC/finalization proofs whose dependency universe changed.

Unknown/unscanned historical ranges are `UNKNOWN`, not complete.

## Producer identity, epochs and replay

Producer authority is generation/epoch-bound. A stale producer cannot emit a manifest under an old epoch after authority rotation. `transaction_id + epoch + effect_id + manifest_nonce` must be replay-protected.

A replayed old manifest cannot authorize a new effect digest. A new effect under the same logical id requires a new allowed generation and explicit supersession semantics.

## Partial transaction detection

For multi-participant operations, the participant-set commitment is immutable before commit/release. Each participant's durable commit evidence references the same transaction id, epoch and participant-set root.

A participant observed with a mismatched root is `TRANSACTION_EQUIVOCATION`. A participant absent at barrier time remains in-flight if declared; if it was required by schema but absent from the set, that is eligible for an undeclared-participant fraud proof.

## Finalization and GC interlocks

A federated campaign cannot finalize while any of these remain:

- manifest validation `UNKNOWN`;
- unresolved declared delayed consequence;
- participant-set mismatch;
- undeclared-edge challenge under adjudication;
- schema-repair scan gap covering the campaign universe;
- producer authority equivocation;
- manifest/effect digest mismatch.

The committed manifests, fraud-proof evidence, repair edges and unresolved obligations remain GC roots until all applicable challenge/revocation/recovery contracts permit deletion.

## RED-first executable matrix (80 cases)

### A. Basic binding
1. effect without manifest -> reject before release.
2. manifest without effect -> no committed effect.
3. effect references wrong manifest digest -> reject.
4. manifest references wrong effect digest -> reject.
5. manifest modified after effect prepare -> reject.
6. duplicate canonical participant -> reject.
7. duplicate canonical edge -> reject.
8. ambiguous encoding collision attempt -> reject.
9. stale manifest version -> fail by policy.
10. unknown declaration mode -> reject.

### B. Required-slot completeness
11. required immediate edge omitted -> RED fraud proof.
12. required delayed edge omitted -> RED fraud proof.
13. required participant omitted -> RED fraud proof.
14. required recovery dependency omitted -> RED fraud proof.
15. zero-edge schema + empty manifest -> accept.
16. producer says empty but schema has slot -> reject.
17. optional non-material edge omitted -> accept.
18. materiality class downgraded by producer -> reject.
19. wildcard destination where schema requires exact -> reject.
20. exact destination where bounded class allowed -> accept.

### C. Atomicity / release
21. DB effect commits but transactional manifest aborts -> fail closed/reconcile.
22. manifest commits but DB effect aborts -> no effect completion.
23. prepare manifest then crash before effect -> recover no released effect.
24. effect write then crash before release marker -> recover using same digest.
25. release with different manifest digest -> reject.
26. concurrent manifest replacement -> one authority generation only.
27. retry identical transaction -> idempotent.
28. retry changed participant set -> reject/equivocation.
29. stale epoch retry -> reject.
30. manifest nonce replay -> reject.

### D. Delayed consequences
31. declared delayed effect pending -> barrier open.
32. delayed effect completes with matching derivation -> close obligation.
33. delayed effect completes under different source -> reject binding.
34. timeout with no cancellation -> barrier stays open.
35. authenticated allowed cancellation -> terminal disposition.
36. delayed scheduler changes chosen destination within committed class -> accept if derivation valid.
37. destination outside committed class -> fraud/equivocation.
38. queue message exists but source omitted delayed class -> fraud proof.
39. duplicate delayed completion -> exact-one enforcement.
40. delayed completion after candidate F1 -> campaign universe expands/fixed-point rerun.

### E. Participant transactions
41. all declared participants commit same root -> eligible.
42. one declared participant missing -> in-flight.
43. participant commits mismatched root -> equivocation.
44. participant commits mismatched epoch -> reject.
45. undeclared participant observed -> fraud proof.
46. schema requires participant B but manifest only A -> reject before release where derivable.
47. participant removed after prepare -> reject.
48. participant added after prepare -> reject unless new transaction generation.
49. participant abort -> transaction terminal abort semantics.
50. participant duplicate replay -> idempotent/no double completion.

### F. Independent reconciliation
51. CDC observes undeclared durable row -> fraud proof candidate.
52. broker observes undeclared topic partition -> fraud proof candidate.
53. producer+reporter share same omitted helper -> independence test marks assurance weak.
54. independent schema verifier catches producer omission -> reject pre-release.
55. observer unavailable -> no false completeness claim where observer is required.
56. observer lag below resolved frontier -> barrier waits.
57. observer catches effect after earlier local ack -> invalidate stale ack.
58. reconciliation sees declared-but-never-written effect -> remains in-flight/cancellable only by policy.
59. reconciliation sees unrelated effect -> no false causal link.
60. destination evidence forged -> fraud proof rejected.

### G. Schema evolution / repair
61. new schema adds material slot -> old closure rooted pending scan.
62. old manifest decoded with original schema -> stable history.
63. new schema silently reinterprets old manifest -> reject.
64. repair edge authenticated and independently verified -> update effective graph.
65. repair scan gap -> UNKNOWN.
66. repair says unaffected without coverage proof -> reject.
67. late discovered omitted edge -> stale finalization invalidated.
68. historical original deleted before repair scan -> quarantine/degrade, never fabricate completion.
69. repair edge creates cycle -> no self-root authority except real roots.
70. schema downgrade removes material edge without adjudication -> reject.

### H. Finalization / GC / recovery
71. open omission challenge -> GC root retained.
72. proven omission -> dependent finalization stale.
73. rejected fraud proof -> no artificial permanent pin beyond policy horizon.
74. manifest GC before challenge horizon -> reject deletion.
75. non-membership structure absent -> retain full set.
76. restart with unresolved manifest obligation -> recover barrier-open state.
77. archive relocation of manifest without verified retrieval -> no hot delete.
78. producer authority revoked -> affected manifests revalidate/root.
79. offline late auditor verifies source+manifest+non-membership proof -> same fraud verdict.
80. disaster recovery reconstructs transaction participant roots and unresolved obligations -> no false closed state.

## Acceptance verdicts

The implementation contract should expose explicit verdicts, not booleans:

- `MANIFEST_BOUND_COMMITTED`
- `MANIFEST_INCOMPLETE`
- `MANIFEST_SCHEMA_UNKNOWN`
- `DECLARED_INFLIGHT`
- `PARTICIPANT_SET_MISMATCH`
- `TRANSACTION_EQUIVOCATION`
- `OMITTED_MATERIAL_EDGE_PROVEN`
- `FRAUD_PROOF_REJECTED`
- `REVALIDATION_REQUIRED`
- `UNKNOWN`

`UNKNOWN != SAFE_TO_FINALIZE` and `UNKNOWN != SAFE_TO_GC`.

## Implementation direction

When executable source becomes available, implement tests before production changes. Prefer a small authority object that validates `EffectManifestV1` at the actual effect-release boundary and returns an opaque release token bound to the manifest digest. Do not bolt on a passive post-hoc observer and call it completeness.

For SQLite-backed lab paths, the first executable prototype can model effect row + canonical manifest row + participant/edge rows in one transaction, plus an independent schema verifier and deterministic Merkle/non-membership fixture. The cross-domain prototype should then compose with LAB-087 process isolation and the previously frozen federated barrier.

## Frozen conclusion

`CAUSAL_TRANSACTION_MANIFEST_EMISSION_COMPLETENESS_UNDECLARED_EDGE_FRAUD_PROOF_PRODUCER_PATH_BINDING_V1_FROZEN`.

A consequential effect is not eligible for federated finalization or destructive GC unless its causal/transaction declaration is cryptographically/transactionally bound to the same authority path that releases the effect. Signed producer metadata alone is not a completeness proof. Completeness requires closed-world schema obligations, enforced declaration at the effect boundary, independent validation, and a durable fraud-proof path for later observed omissions.