# Semantic event-ingestion completeness / source-inventory authority / omission detection / monitor catch-up v1

Date: 2026-09-08
Status: `SEMANTIC_EVENT_INGESTION_COMPLETENESS_SOURCE_INVENTORY_OMISSION_MONITOR_CATCHUP_V1_FROZEN`
Parent: LAB-093 / #178

## Question

How can a continuous-assurance checkpoint prove not merely that the entries *which reached the log* form an append-only prefix, but that every authority-relevant event from every source that policy requires was actually admitted? How can source membership be changed without letting the producer silently shrink the denominator, and how can an independent monitor turn suspected omission into positive evidence?

## Boundary

The central distinction is:

`APPEND_ONLY_LOG != COMPLETE_EVENT_INGESTION`

and, more precisely:

`SOURCE_EVENT_OCCURRED != SOURCE_EVENT_AUTHENTICATED != LOG_SUBMISSION_ACCEPTED != LOG_INCLUSION_PROVEN != PREFIX_SEMANTICALLY_COMPLETE`

A Merkle/SCITT checkpoint can prove ordering, append-only consistency, inclusion and non-equivocation for the statements it commits. It cannot by itself prove that a producer did not suppress an event before admission. Completeness therefore needs an independently authenticated denominator and independently observable obligations.

## Primary donors

### RFC 9162 — Certificate Transparency

Useful mechanism: an SCT is a signed promise that a submitted certificate will appear in the log within the Maximum Merge Delay. A client/monitor that has the SCT can later demand an inclusion proof; inability to provide one after the deadline is signed evidence of incorrect log operation. Monitors separately reconstruct/check the log view.

Reusable mechanism: **pre-inclusion signed obligation + bounded inclusion deadline + later independently checkable inclusion proof**.

Important limit: CT append-only proofs do not prove that every certificate that should have existed was submitted. They prove misbehavior when an independently observed submission promise is violated.

Source: RFC 9162.

### RFC 9943 — SCITT Architecture

Useful mechanism: Signed Statements carry issuer-authenticated content; Transparency Service Receipts prove registration in a verifiable data structure. Append-only, non-equivocation and replayability are properties of the registered sequence.

Reusable mechanism: keep **issuer statement authenticity** separate from **transparency registration evidence**. A Receipt proves registration, not the truth/completeness of the universe of statements.

Source: RFC 9943.

### NIST SP 800-53 Rev. 5 AU-12

Useful mechanism: audit generation is defined over organization-selected event types on organization-defined system components, and AU-12(1) compiles records from defined components into a system-wide audit trail.

Reusable mechanism: completeness requires a governed definition of **which components/sources and event classes are required**, rather than deriving the denominator from whichever sources happen to report.

Source: NIST SP 800-53 Rev. 5 AU-12 / AU-12(1).

### Apache Kafka producer sequence/idempotence semantics

Useful mechanism: producer sequencing/idempotence distinguishes duplicates and out-of-order/lost sequence situations; an unexpected sequence can indicate that data may have been lost.

Reusable mechanism: authenticated source-local sequence/epoch identifiers make duplicate, reorder and gap conditions explicit, but do not alone prove whether a missing sequence corresponds to a policy-relevant event unless source semantics require contiguous issuance.

Source: Apache Kafka producer documentation / `OutOfOrderSequenceException` semantics.

## Frozen model

### 1. `EventSourceInventoryV1`

The policy denominator MUST be a separately authenticated object, not a query over currently reporting sources.

```text
EventSourceInventoryV1 {
  lineage_id
  inventory_generation
  predecessor_digest
  effective_from_frontier
  sources[]
  required_event_classes_by_source
  source_identity_keys / authority refs
  source_epoch_rules
  sequence_semantics
  maximum_admission_delay
  retirement_rules
  signer_policy
  signatures
}
```

Properties:

1. Inventory generations are monotonic and hash-linked.
2. A producer/log cannot self-authorize removal of an inconvenient source.
3. Routine inventory rotation requires predecessor-authorized succession plus current inventory-authority policy.
4. Source retirement is effective only after a **drain frontier** proves every obligation up to the retirement boundary is either included or explicitly resolved.
5. An offline/non-reporting required source remains in the denominator until authenticated retirement completes.
6. Same inventory generation with different source sets is equivocation.

Therefore:

`CURRENTLY_REPORTING_SOURCES != REQUIRED_EVENT_SOURCE_SET`.

### 2. `SourceEventEnvelopeV1`

Every authority-relevant event emitted by a governed source SHOULD carry enough authenticated source-local structure to make omission/reorder claims decidable:

```text
SourceEventEnvelopeV1 {
  lineage_id
  source_id
  source_epoch
  source_sequence
  event_class
  event_id
  event_digest
  predecessor_event_digest | null
  source_time / uncertainty
  policy_context_digest
  source_signature
}
```

For source classes whose semantics are contiguous, `(source_epoch, source_sequence)` MUST advance exactly according to declared rules. For naturally sparse/non-contiguous sources, the inventory must declare a different obligation mechanism; monitors must not infer missing events merely from integer gaps.

### 3. `IngestionPromiseV1`

When the transparency/ingestion boundary accepts an event, it returns an authenticated promise analogous to CT's SCT:

```text
IngestionPromiseV1 {
  event_digest
  source_id
  source_epoch
  source_sequence
  accepted_at
  inclusion_deadline
  log_lineage
  promise_generation
  signer
  signature
}
```

After `inclusion_deadline`, a valid promise plus a checkpoint that covers the deadline but lacks the event is **positive omission evidence**, not merely suspicion.

The producer cannot make omission unverifiable by withholding the promise if policy requires sources or independent ingress witnesses to retain submission evidence; see challenge semantics below.

### 4. `SourceFrontierStatementV1`

Each required source periodically authenticates its own emitted frontier:

```text
SourceFrontierStatementV1 {
  source_id
  source_epoch
  highest_emitted_sequence_or_semantic_frontier
  chain_digest
  previous_frontier_digest
  interval_start
  interval_end
  signature
}
```

Independent monitors retain these statements outside the checkpoint log. A checkpoint's claimed per-source admitted frontier can then be reconciled against independently observed source frontiers.

Important: a frontier statement proves what the source claims it emitted. It does not prove real-world events the source maliciously never recorded. The security boundary is completeness of **governed event sources**, not omniscience about external reality.

### 5. `IngestionCoverageLedgerV1`

A checkpoint must carry or commit to a per-required-source coverage ledger:

```text
IngestionCoverageLedgerV1 {
  inventory_generation
  checkpoint_generation
  per_source: {
    source_epoch
    source_frontier_consumed
    admitted_frontier
    unresolved_gaps[]
    delayed_obligations[]
    duplicate_event_ids[]
    conflicting_event_ids[]
    partition_state
  }
  coverage_digest
}
```

A checkpoint cannot be `PREFIX_COMPLETE_PROVEN` merely because its Merkle tree is internally consistent. It must reconcile every required source in the active inventory.

## Completeness verdicts

- `PREFIX_COMPLETE_PROVEN`: active inventory is authenticated; every required source is reconciled through the checkpoint frontier; no unresolved required gap, expired ingestion promise, conflicting source event, or unknown source interval exists.
- `PREFIX_APPEND_ONLY_COMPLETENESS_UNPROVEN`: log consistency is valid but source coverage evidence is insufficient.
- `PREFIX_INCOMPLETE_PROMISE_VIOLATION`: an authenticated ingestion promise expired without inclusion.
- `PREFIX_INCOMPLETE_SOURCE_GAP_PROVEN`: source-local authenticated frontier/chain proves an event interval exists that the log omitted.
- `PREFIX_SOURCE_PARTITION_PENDING`: source is required but its latest admissible frontier is unavailable and policy delay has not expired.
- `PREFIX_CURRENT_STATUS_UNKNOWN_SOURCE_GAP`: bounded delay expired and monitor lacks evidence to distinguish source silence from ingestion omission.
- `PREFIX_SOURCE_INVENTORY_CONFLICT`: incompatible authenticated inventory generations/views.
- `PREFIX_SOURCE_EVENT_EQUIVOCATION`: same source epoch/sequence or event id is authenticated with conflicting content.

## Omission detection

### Strong positive evidence class A — violated ingestion promise

Evidence bundle:

1. valid `SourceEventEnvelopeV1`;
2. valid `IngestionPromiseV1` for its digest;
3. authenticated checkpoint whose covered time/frontier is later than the promise deadline;
4. valid non-inclusion proof where supported, or complete monitor reconstruction of the covered prefix demonstrating absence.

Verdict: `INGESTION_OMISSION_PROVEN`.

This is the closest direct donor from CT's SCT/MMD model.

### Strong positive evidence class B — authenticated contiguous source chain gap

If source semantics require contiguous sequences and independent monitors possess authenticated source events/frontiers proving sequence `n` and `n+2`, while the log claims complete coverage through `n+2` but lacks `n+1`, completeness fails.

The monitor must distinguish:

- `n+1` was emitted but omitted;
- source itself violated its declared contiguous-source contract.

Either is a policy contradiction, but attribution differs. The checkpoint cannot remain `PREFIX_COMPLETE_PROVEN`.

### Strong positive evidence class C — external authority transition absent from log

For authority-relevant state transitions already authenticated by another durable subsystem (for example provider-generation transition, invalidation generation, recovery-policy generation), monitors compare that subsystem's authenticated frontier to the ingestion log's coverage ledger. If transition `g` exists in the authority source but no bound event exists in the log after the maximum admission delay, omission is proven relative to the governed source.

This is especially valuable because the completeness oracle is not the log itself.

## Monitor challenge / reconciliation protocol

`SemanticIngestionChallengeV1` is bounded and target-fixed before challenge randomness is revealed:

```text
SemanticIngestionChallengeV1 {
  inventory_generation
  checkpoint_generation
  selected_sources[]
  expected_source_frontiers
  challenge_nonce
  challenge_deadline
  requested_proofs
  monitor_signature
}
```

The challenged system must return, as applicable:

- source inventory proof;
- source frontier statements;
- ingestion promises;
- inclusion/non-inclusion proofs;
- ordered event-chain fragments;
- gap-resolution evidence;
- source retirement/drain proof.

Rules:

1. Challenge target set is committed before nonce disclosure so a producer cannot silently select only healthy sources.
2. Random sampling may bound confidence for very large fleets, but cannot yield `PREFIX_COMPLETE_PROVEN` unless policy explicitly defines a statistical assurance profile. Critical bounded authority sources require exhaustive reconciliation.
3. Failure/timeout does not by itself prove malicious omission; it yields an availability/unknown verdict unless independent positive contradiction evidence exists.
4. A challenge response signed only by the log producer cannot prove source truth; source-origin or independent witness evidence is required where the claim depends on source emission.
5. A monitor that missed an interval must catch up from an authenticated inventory/frontier checkpoint, not infer continuity from the newest response.

## Catch-up after monitor loss

A monitor stores monotonic frontiers for:

- source inventory generation;
- per-source source epoch/frontier;
- ingestion promise frontier;
- log checkpoint generation/root;
- unresolved contradiction set.

If any required stream continuity is lost:

1. mark current completeness `UNKNOWN`;
2. fetch a fresh authenticated `EventSourceInventoryV1` plus predecessor proof to the retained inventory frontier;
3. obtain fresh source frontier statements for every required source or an authenticated retirement/drain proof;
4. reconstruct the log prefix/checkpoint interval and promise obligations;
5. reconcile every unresolved source gap and expired promise;
6. only then install a new monitor frontier.

A monitor MUST NOT use `latest checkpoint looks healthy` as proof that no omission occurred during its outage.

## Duplicate and reorder semantics

- duplicate same `event_id` + same canonical digest: harmless transport duplication; count once and retain duplicate observation metadata if useful;
- same identity/sequence + different digest: equivocation/fail closed;
- reordered delivery with intact authenticated source sequence: normalize only at ingestion if policy permits; checkpoint semantic chain remains source-order aware;
- missing contiguous sequence before maximum admission delay: pending gap;
- missing contiguous sequence after maximum admission delay: completeness cannot be proven; becomes positive omission only when independent evidence proves the event/obligation existed;
- late arrival after a checkpoint already claimed `PREFIX_COMPLETE_PROVEN`: issue `ConvergenceInvalidationV1`/checkpoint invalidation and reopen; never rewrite the old checkpoint.

## Source retirement and denominator shrinkage

A source may leave the required denominator only via `SourceRetirementProofV1`:

```text
SourceRetirementProofV1 {
  source_id
  old_inventory_generation
  new_inventory_generation
  retirement_effective_frontier
  final_source_frontier
  final_chain_digest
  final_ingested_frontier
  unresolved_obligations == empty
  authority_signatures
}
```

No heartbeat timeout, scaling event, DNS disappearance, CMDB deletion, or producer-side configuration edit is sufficient.

If a supposedly retired source later emits authenticated events under the retired epoch after its final frontier, that is a contradiction requiring investigation/invalidation; it cannot silently re-enter under the old identity.

## Fraud / contradiction classes

1. `SOURCE_INVENTORY_GENERATION_ROLLBACK`
2. `SOURCE_INVENTORY_EQUIVOCATION`
3. `UNAUTHORIZED_DENOMINATOR_SHRINK`
4. `SOURCE_RETIREMENT_WITH_UNRESOLVED_OBLIGATION`
5. `INGESTION_PROMISE_EXPIRED_WITHOUT_INCLUSION`
6. `SOURCE_CHAIN_GAP_UNRESOLVED`
7. `SOURCE_SEQUENCE_EQUIVOCATION`
8. `SOURCE_EVENT_ID_REBINDING`
9. `CHECKPOINT_CLAIMS_COMPLETE_WITH_REQUIRED_SOURCE_UNKNOWN`
10. `MONITOR_CATCHUP_SKIPS_UNKNOWN_INTERVAL`
11. `LOG_SELF_ATTESTS_SOURCE_COMPLETENESS`
12. `POST_RETIREMENT_SOURCE_RESURRECTION`

## RED-first matrix

### Inventory authority
1. remove required source without authorized inventory transition -> reject;
2. same generation, different source set -> equivocation;
3. replay older inventory -> rollback;
4. add source legitimately -> required from effective frontier;
5. retirement without drain proof -> reject;
6. offline source silently disappears from telemetry -> remains denominator;
7. producer changes local config only -> no inventory effect;
8. source key rotates with authenticated inventory transition -> accept.

### Promise / inclusion
9. event + promise included before deadline -> complete candidate;
10. event + promise absent after deadline -> omission proven;
11. promise replay for different digest -> reject;
12. promise deadline rewritten -> signature failure;
13. promise exists only inside omitted log -> insufficient external proof;
14. independent monitor retains promise -> actionable;
15. event arrives late after complete checkpoint -> invalidate/reopen;
16. inclusion proof for different event -> reject.

### Sequence / chain
17. contiguous n,n+1,n+2 -> pass;
18. n,n+2 before delay -> pending;
19. n,n+2 after delay with independent proof n+1 existed -> omission proven;
20. naturally sparse source with numeric gap -> no false omission;
21. same sequence/different digest -> equivocation;
22. duplicate same digest -> dedupe;
23. reordered transport -> preserve source semantic order;
24. source epoch reset without authorization -> reject.

### Partitions / delayed ingestion
25. required source partition within grace -> pending;
26. partition exceeds grace without positive omission evidence -> unknown, not fabricated fraud;
27. producer reachable but source unreachable -> unknown source coverage;
28. source reachable independently, log omits current frontier -> contradiction;
29. delayed event included before bounded deadline -> valid;
30. checkpoint claims complete while delayed obligation pending -> reject completeness;
31. stale source frontier reused across checkpoints past freshness -> reject;
32. partition heals, reconciliation covers interval -> completeness may re-establish in new generation.

### Monitor catch-up
33. monitor misses interval, newest checkpoint only -> cannot prove completeness;
34. catch-up reconstructs inventory + all source frontiers + promises -> recover;
35. source frontier unavailable for lost interval -> unknown;
36. expired promise discovered during catch-up -> invalidate historical current verdict;
37. retained inventory generation greater than server view -> rollback detection;
38. conflicting checkpoint during catch-up -> split-view fail closed;
39. unresolved contradictions omitted from catch-up package -> reject;
40. catch-up after archive compaction with valid complete checkpoint bridge -> accept only if bridge commits required source coverage and unresolved set.

### Challenge / sampling
41. target set selected after challenge nonce -> reject anti-steering claim;
42. critical bounded source set exhaustively challenged -> eligible for strong proof;
43. sampled huge noncritical fleet -> statistical verdict only;
44. load balancer routes challenges away from stale source path -> responder identity mismatch/insufficient;
45. log signs its own source frontier with no source authority -> reject;
46. independent source signs frontier -> usable;
47. challenge timeout alone -> unknown/availability, not omission proof;
48. challenge proves expired accepted event absent -> omission proven.

### Retirement / resurrection
49. retirement with exact final frontier and zero obligations -> accept;
50. source emits under retired epoch beyond final frontier -> contradiction;
51. source restarts with new authorized epoch/new inventory generation -> accept;
52. DNS/CMDB deletion alone -> does not retire;
53. source retired while partitioned with unknown obligations -> reject;
54. retired source's old events remain historically verifiable -> yes.

### Crash / atomicity
55. event accepted but promise durable, log crash before inclusion -> deadline later proves omission if not recovered;
56. event included but promise response lost -> inclusion still valid, client may not possess promise;
57. inventory transition crash before publication -> old inventory remains current;
58. inventory transition published but local producer config stale -> enforcement conflict, no complete verdict;
59. coverage checkpoint crash after source frontier consume but before log commit -> retry idempotently; no skipped frontier;
60. duplicate replay after crash -> same event id/digest dedupes without advancing semantic source frontier twice.

## Security conclusions

1. No append-only data structure can prove completeness relative to events it has no independent obligation to know about.
2. The minimum strong pattern is **authenticated required-source inventory + source-authenticated event/frontier semantics + pre-inclusion promise or independent source observation + bounded deadline + independent monitor reconciliation**.
3. Source membership is authority. It must be versioned, authenticated, monotonic and retirement-gated; otherwise the producer can improve completeness by shrinking the denominator.
4. Sequence gaps are evidence only under declared source semantics. Never infer an event from an arbitrary integer hole.
5. `PREFIX_COMPLETE_PROVEN` is an appraisal over source coverage and log consistency, not a property emitted unilaterally by the log.
6. Positive fraud evidence must distinguish producer omission from source failure/misbehavior where attribution matters.
7. Monitor outages create an unknown interval until catch-up reconstructs source obligations; latest-state health cannot erase missing history.

## Implementation composition

When LAB-093 reaches exact RED/GREEN implementation, compose this contract with the already-frozen checkpoint authority/archive survivability contract:

- checkpoint schema gains `source_inventory_generation`, `source_coverage_digest`, and unresolved-obligation commitment;
- new authenticated inventory/source-frontier/promise objects are verified before `PREFIX_COMPLETE_PROVEN`;
- expired promises and post-close omitted events feed the existing continuous-assurance invalidation/reopen path;
- archive GC retains inventory transitions, source retirement proofs, promises needed for unresolved/historical fraud proofs, and monitor catch-up bridges;
- LAB-087 process isolation remains the execution/write boundary.

No production integration is claimed by this design freeze; exact executable RED/GREEN remains required.
