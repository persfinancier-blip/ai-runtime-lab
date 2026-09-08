# Continuous-assurance checkpoint authority, archive survivability, split-view detection, and proof-of-prefix completeness v1

Status: **FROZEN DESIGN CONTRACT / RED-first**

Contract name: `CONTINUOUS_ASSURANCE_CHECKPOINT_AUTHORITY_ARCHIVE_SURVIVABILITY_SPLIT_VIEW_PREFIX_COMPLETENESS_V1_FROZEN`

Date: 2026-09-08

Related: LAB-093 / #178. This is a design follow-up only; it does not substitute for exact executable RED/GREEN evidence.

## Objective

Extend the frozen `ContinuousAssuranceCheckpointV1` model so that checkpoint compaction remains safe even when archives are partially unavailable, replica infrastructure is lost, a checkpoint signer is compromised, or different relying parties are shown conflicting checkpoint roots.

The contract must answer four questions:

1. who may issue, rotate, retire, or revoke checkpoint authority;
2. what survives if one or more archive replicas disappear;
3. how split views are detected and adjudicated without last-writer-wins;
4. what evidence proves that a compact checkpoint really commits to the complete historical prefix it claims to summarize.

## Core distinctions

The implementation MUST preserve these separations:

```text
VALID_CHECKPOINT_SIGNATURE
    != CURRENT_CHECKPOINT_ISSUER_AUTHORITY
    != CONSISTENT_APPEND_ONLY_CHECKPOINT
    != COMPLETE_PREFIX_CHECKPOINT
    != AVAILABLE_ARCHIVE

ARCHIVE_UNAVAILABLE
    != HISTORY_PROVEN_PRUNED

CHECKPOINT_RECEIPT
    != CHECKPOINT_TRUTH
    != PREFIX_COMPLETENESS

SAME_PREFIX_GENERATION_DIFFERENT_ROOT
    != NEWER_WINNER
    == EQUIVOCATION
```

A checkpoint can be correctly signed while still being unauthorized, incomplete, inconsistent with prior trusted history, or produced from a selectively pruned archive.

## Donor mechanisms and primary-source evidence

### RFC 9162 — Certificate Transparency v2

Certificate Transparency uses signed tree heads plus Merkle consistency proofs to prove append-only evolution. A consistency proof between tree sizes proves that the older tree is a prefix of the newer tree. Monitors are expected to inspect every new entry; if new entries remain unavailable for an extended period, the RFC treats that as log misbehavior. A monitor may retain full copies of logs or verify consistency incrementally.

Mechanisms reused here:

- every checkpoint commits to a specific prefix size/range plus root;
- append-only continuity is proven cryptographically from a previously trusted checkpoint, not inferred from timestamps;
- underlying entries remaining unavailable for an extended interval is an explicit auditability failure, not evidence that no entries exist;
- a relying party may retain only compact checkpoints/proofs while independent monitors/archives retain full history.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### RFC 9943 — SCITT

SCITT defines an append-only registration history and an Auditor role that checks correctness and consistency of Transparent Statements or the Statement Sequence. Receipts prove registration of a specific signed statement; they do not prove that the semantic claim inside that statement is true.

Mechanisms reused here:

- checkpoint, authority-rotation, archive-manifest, contradiction, and supersession statements receive append-only transparency receipts;
- independent auditors can compare the statement sequence against checkpoint claims;
- receipt presence prevents silent historical rewriting but does not replace semantic prefix verification.

Source: https://www.rfc-editor.org/rfc/rfc9943.html

### transparency-dev/witness / witness-cosigned checkpoints

The transparency witness model tracks a previous checkpoint and verifies a consistency proof before countersigning a new checkpoint. The witness therefore refuses to cross an inconsistent fork. Multiple independently operated witnesses give relying parties independently observed views rather than one operator-controlled checkpoint stream.

Mechanisms reused here:

- checkpoint acceptance in high-assurance mode requires a witness policy, not only the archive/checkpoint operator signature;
- witnesses keep monotonic per-log/checkpoint state and do not sign inconsistent successors;
- conflicting witness-observed roots are fraud evidence requiring quarantine and investigation.

Sources:
- https://github.com/transparency-dev/witness
- https://www.sigsum.org/

### RFC 4998 / RFC 6283 — long-term Evidence Records

ERS protects long-lived evidence with hash trees plus archive timestamps and supports renewal when cryptographic algorithms or certificates age. It also permits reduced hash-tree evidence sufficient to prove a particular archived object without retaining every sibling object locally.

Mechanisms reused here:

- archive objects and checkpoint-prefix evidence may be independently replicated while preserving compact membership paths;
- long-term evidence must be renewable before cryptographic mechanisms become obsolete;
- proof material can be stored separately from the archived object but must remain sufficient to reconstruct and verify the claimed relationship.

Sources:
- https://www.rfc-editor.org/rfc/rfc4998.html
- https://www.rfc-editor.org/rfc/rfc6283.html

## 1. Checkpoint authority is first-class governed authority

Define:

```text
CheckpointAuthorityV1 {
  lineage_id
  generation
  predecessor_generation
  issuer_key_set_digest
  threshold_policy_digest
  witness_policy_digest
  archive_policy_digest
  scope
  valid_from_frontier
  valid_until / freshness policy
  predecessor_authorization
  successor_authorization
  status
  transparency_receipt
}
```

`status` is append-only lifecycle state such as `ACTIVE`, `RETIRED`, `REVOKED_COMPROMISE`, `REVOKED_POLICY_FAILURE`, or `HISTORICAL_ONLY`.

Rules:

1. A checkpoint is authoritative only if its issuer generation was authorized for the exact lineage/scope at issuance time.
2. Routine authority rotation requires predecessor + successor authorization over one canonical transition payload.
3. A successor authority cannot self-authorize its predecessor edge.
4. A retired authority may remain historically valid for issuance before retirement, subject to compromise adjudication.
5. Known compromise onset invalidates affected checkpoint issuance after the boundary.
6. Unknown compromise onset yields `UNKNOWN_HISTORICAL_CHECKPOINT_AUTHORITY` for dependent intervals until independently reconstructed or adjudicated.
7. Checkpoint authority and archive custody SHOULD be separate failure/control domains in the high-assurance profile.

## 2. Checkpoint statement

Refine the earlier checkpoint into:

```text
ContinuousAssuranceCheckpointV1 {
  lineage_id
  checkpoint_generation
  prefix_start
  prefix_end
  prefix_count
  previous_checkpoint_digest
  historical_statement_root
  ordered_event_chain_digest
  summarized_verdict_frontier
  summarized_invalidation_frontier
  authority_frontier
  topology_frontier
  unresolved_contradiction_set_digest
  archive_manifest_digest
  checkpoint_authority_generation
  witness_policy_digest
  policy_digest
  issuer_authorizations
  witness_cosignatures
  transparency_receipts
}
```

The checkpoint MUST bind both a set commitment (`historical_statement_root`) and an ordering/sequence commitment (`ordered_event_chain_digest` or equivalent). A Merkle root over an unordered bag is insufficient because deleting/reordering semantically ordered events can preserve a set-like membership story while changing authority semantics.

## 3. Proof-of-prefix completeness

A checkpoint that claims `[prefix_start, prefix_end]` is accepted as **complete** only when all of the following hold:

1. the previous trusted checkpoint links cryptographically to this checkpoint;
2. the prefix range is contiguous with no unaccounted sequence gap;
3. every event class required by policy is committed under canonical serialization, including:
   - convergence verdicts;
   - invalidations and reclosures;
   - issuer/key/policy rotations and revocations;
   - topology/cutover statements;
   - contradictions, disputes, losing forks, and adjudications;
   - archive/checkpoint authority lifecycle changes;
4. the event ordering commitment verifies the exact authoritative sequence;
5. unresolved contradictions at the prefix boundary are carried into the checkpoint state;
6. independent archive/auditor evidence can reproduce the root or verify sufficient inclusion/range proofs against it;
7. the checkpoint is consistency-linked from the relying party's previously trusted checkpoint or an independently trusted witness frontier.

### Completeness verdicts

Use explicit states:

- `PREFIX_COMPLETE_PROVEN`
- `PREFIX_CONSISTENT_BUT_COMPLETENESS_UNPROVEN`
- `PREFIX_INCOMPLETE_PROVEN`
- `PREFIX_CONFLICT_EQUIVOCATION`
- `PREFIX_ARCHIVE_UNAVAILABLE_AUDIT_DEGRADED`

`CONSISTENT_BUT_COMPLETENESS_UNPROVEN` is important: a Merkle consistency proof can prove that one committed tree is an append-only extension of another, but it cannot by itself prove that the producer inserted every semantically required event into that tree. Completeness additionally depends on governed event-ingestion coverage, independent observation, and archive/auditor reconciliation.

## 4. Archive survivability and replica independence

Define:

```text
CheckpointArchiveManifestV1 {
  lineage_id
  manifest_generation
  covered_prefix_start
  covered_prefix_end
  canonical_archive_digest
  replica_descriptors[]
  independence_profile_digest
  erasure_or_replication_policy
  retrieval_proof_policy
  renewal_policy
  last_verified_at
  issuer_authority_generation
  transparency_receipt
}
```

A `replica_descriptor` identifies at least operator/control domain, storage/account boundary, region/provider, key custody, retrieval endpoint or offline-medium identity, and the exact prefix/digest held.

High-assurance archive policy MUST NOT count these as independent copies:

- two buckets under the same account/administrator when one credential can delete both;
- two replicas generated from the same mutable source after the source has already been pruned;
- a primary database plus a backup whose retention lifecycle is controlled by the same destructive automation;
- two endpoints fronting one physical object store;
- a replica and its cache.

At least one durable copy of contradiction-bearing history SHOULD exist outside the checkpoint issuer's direct deletion domain.

## 5. Availability failure versus malicious pruning

Archive unavailability alone is not cryptographic proof of pruning.

Classify separately:

```text
ARCHIVE_TEMPORARILY_UNAVAILABLE
ARCHIVE_PARTIAL_REPLICA_LOSS
ARCHIVE_RECOVERABLE_FROM_INDEPENDENT_REPLICA
ARCHIVE_AUDITABILITY_DEGRADED
ARCHIVE_PRUNING_PROVEN
ARCHIVE_PROVENANCE_UNRECOVERABLE
```

### Temporary/unproven unavailability

If the current checkpoint is fresh, authority-valid, witness-consistent, and linked from prior trusted state, a policy MAY permit current consequential operation for a bounded interval while historical auditability is degraded. The system MUST surface this degraded state.

It MUST NOT say that unavailable history never existed.

### Pruning proof

`ARCHIVE_PRUNING_PROVEN` requires positive contradiction evidence, e.g.:

- a previously receipted/included event has a valid inclusion proof under an earlier checkpoint but is missing from a purported same-or-later complete archive reconstruction;
- two independent replicas claim the same prefix/root policy but one cannot reproduce a leaf/range that the other proves was committed;
- a later checkpoint claims a prefix root incompatible with a previously trusted checkpoint and no valid consistency proof exists;
- an archive manifest attests a replica held a prefix/digest, followed by authenticated evidence of selective deletion or impossible reconstruction while sibling data remains;
- a checkpoint claims no unresolved contradiction while an independently receipted contradiction is provably within its covered prefix.

A timeout or HTTP 404 alone is availability evidence, not pruning proof.

## 6. Minimum survivable evidence after archive loss

To keep a compacted prefix auditable after losing some archival infrastructure, the high-assurance profile requires at minimum:

1. at least one previously trusted checkpoint before or at the compacted prefix boundary;
2. the new checkpoint statement and its authority chain;
3. witness cosignatures from the required independent witness threshold;
4. transparency receipts for the checkpoint and authority transitions;
5. a surviving independently controlled archive replica OR sufficient object/range proofs for all policy-critical contradiction/authority-transition records;
6. the archive manifest that identifies what was supposed to survive and where;
7. consistency proof(s) linking previous trusted checkpoint -> compact checkpoint -> later checkpoint where applicable;
8. cryptographic renewal evidence when algorithms/keys age.

If only the compact checkpoint root survives and no independent archive or critical inclusion/range evidence remains, the result may still prove that a particular root was once signed/witnessed, but it does **not** prove prefix semantic completeness. Verdict: `CHECKPOINT_ROOT_SURVIVES_PREFIX_AUDITABILITY_LOST`.

## 7. Split-view detection

Same lineage + same checkpoint generation/prefix boundary + different authenticated roots is immediate equivocation:

```text
CHECKPOINT_EQUIVOCATION_PROOF_V1 {
  lineage_id
  checkpoint_generation
  prefix_end
  checkpoint_a
  checkpoint_b
  signer_authority_evidence
  witness_observations
  transparency_receipts
}
```

Rules:

1. Never choose the newer timestamp, lower root, higher root, first-seen artifact, majority CDN response, or last writer.
2. Relying parties observing a fork enter `CHECKPOINT_SPLIT_VIEW_NO_CURRENT_AUTHORITY` for affected current reliance.
3. Losing branches remain durable evidence even after governance adjudication.
4. A later reconciled checkpoint cannot erase the equivocation; it can only supersede current authority after a governed recovery/reclosure process.
5. Witness disagreement is itself evidence. If one valid witness cosigned root A and another valid witness cosigned incompatible root B under a policy that expected a common consistent history, the ecosystem must not silently count both toward quorum.

Independent checkpoint gossip/witness exchange SHOULD distribute observed checkpoint digests so targeted split views cannot remain isolated to one relying party indefinitely.

## 8. Witness policy and independence

Define a `CheckpointWitnessPolicyV1` that binds:

- required threshold;
- named witness identities or governed witness set;
- witness key generations;
- operator/control independence requirements;
- maximum checkpoint freshness/staleness;
- permitted outage/degraded modes;
- witness rotation/revocation semantics.

A witness signature means: this witness observed the checkpoint and verified append-only consistency from its previously trusted state. It does not prove semantic completeness of event ingestion.

Correlated witnesses count as one failure domain if they share decisive control/key custody/runtime or consume the same unverified checkpoint state without independent consistency tracking.

## 9. Archive recovery and reconstitution

If the primary archive is lost but a valid independent replica survives:

1. freeze destructive compaction/GC;
2. verify replica digest against the last trusted `CheckpointArchiveManifestV1`;
3. rebuild a read-only reconstruction;
4. recompute historical statement root and ordered event-chain digest for the covered prefix;
5. verify critical inclusion/range proofs and unresolved contradiction carry-forward;
6. compare with witness/transparency-observed checkpoints;
7. issue a new archive-manifest generation that records the loss and restored custody;
8. only then resume ordinary retention/compaction.

If no surviving data can reconstruct a policy-critical portion of the prefix, do not fabricate a replacement. Mark `ARCHIVE_PROVENANCE_UNRECOVERABLE` and preserve current-operation behavior only according to an explicit governance policy; historical completeness is permanently unknown unless an independently held copy later appears.

## 10. Garbage collection constraint

A checkpoint MAY permit local hot-store deletion only after the survivability policy is satisfied.

GC MUST fail closed if deletion would remove the last independently recoverable copy of any of:

- unresolved contradiction evidence;
- authority/key/policy lifecycle evidence needed to validate historical signatures;
- losing fork/equivocation evidence;
- checkpoint chain links required to bridge from the retained trusted frontier;
- archive-manifest and renewal evidence needed for long-term validation.

A compact root is not a substitute for every policy-critical leaf when later semantic adjudication may require the leaf contents.

## 11. Failure and conflict rules

- Lower checkpoint generation/frontier than trusted state -> `CHECKPOINT_ROLLBACK_DETECTED`.
- Same generation/prefix with different authenticated root -> `CHECKPOINT_EQUIVOCATION`.
- Valid issuer signature but unauthorized issuer generation -> `CHECKPOINT_UNAUTHORIZED_ISSUER`.
- Checkpoint root consistent with prior root but required event-ingestion completeness cannot be independently established -> `PREFIX_CONSISTENT_BUT_COMPLETENESS_UNPROVEN`.
- Archive unavailable with no positive pruning proof -> availability/auditability degradation, not pruning verdict.
- Previously proven included contradiction absent from purported complete reconstructed prefix -> `ARCHIVE_PRUNING_OR_RECONSTRUCTION_CONTRADICTION`.
- All independent replicas of a policy-critical leaf lost -> `ARCHIVE_PROVENANCE_UNRECOVERABLE`.
- Witness threshold met only by correlated/control-identical witnesses -> threshold not met.
- Current checkpoint fresh but long-term cryptographic renewal overdue -> historical preservation degraded; do not claim indefinite auditability.

## 12. RED-first regression matrix

Freeze at least these 52 cases before implementation.

### Checkpoint authority lifecycle (1-10)
1. current authorized checkpoint signer accepted;
2. retired signer cannot issue new checkpoint;
3. historical pre-retirement checkpoint remains auditable;
4. known compromise boundary invalidates affected issuance;
5. unknown compromise onset yields historical authority unknown;
6. successor-only rotation rejected;
7. predecessor-only rotation rejected;
8. predecessor+successor canonical rotation accepted;
9. checkpoint authority rollback rejected;
10. same-generation/different-authority content is equivocation.

### Prefix consistency/completeness (11-22)
11. contiguous prefix with valid previous-checkpoint link accepted;
12. gap in event sequence rejected as complete;
13. reordered authority/invalidation events rejected;
14. omitted invalidation rejected;
15. omitted losing fork rejected;
16. omitted unresolved contradiction rejected;
17. later reclosure does not permit omission of earlier invalidation;
18. set root valid but ordered-event digest wrong -> reject;
19. consistency proof valid but ingestion completeness unproven -> explicit unproven state;
20. independent archive reproduction matches root -> complete evidence strengthens;
21. previously trusted inclusion contradicts purported complete archive -> pruning/reconstruction contradiction;
22. canonical serialization mismatch cannot be normalized by verifier guesswork.

### Archive survivability (23-34)
23. independent replica loss with another valid replica survives;
24. two buckets under one destructive credential count as one failure domain;
25. cache does not count as independent archive;
26. replica digest mismatch blocks reconstruction;
27. primary loss + valid independent replica reconstructs exact root/order;
28. primary and all critical replicas lost -> provenance unrecoverable;
29. temporary archive timeout is not pruning proof;
30. extended unavailability surfaces degraded auditability;
31. deletion of last unresolved-contradiction copy blocked;
32. deletion of hot copy allowed only after survivability policy satisfied;
33. cryptographic renewal evidence preserves long-term validation;
34. overdue renewal cannot be described as indefinite preservation.

### Split view and witnesses (35-44)
35. same generation/prefix/same root from two sources accepted as same view;
36. same generation/prefix/different root -> equivocation/fail closed;
37. later timestamp does not resolve fork;
38. majority CDN copies do not resolve fork;
39. independent witness consistency signatures satisfy policy;
40. correlated witnesses count once;
41. witness A cosigns root A and witness B incompatible root B -> split-view dispute;
42. witness rotation preserves monotonic checkpoint frontier;
43. revoked witness cannot satisfy new threshold;
44. later reconciled checkpoint preserves fork evidence.

### Archive manifest/recovery (45-52)
45. manifest generation rollback rejected;
46. manifest same generation/different replica set is equivocation;
47. reconstructed archive matches manifest and checkpoint roots;
48. reconstructed archive omits receipted critical leaf -> reject;
49. offline replica restored from older prefix requires explicit catch-up consistency proof;
50. archive reconstitution records loss/recovery in new manifest generation;
51. checkpoint root survives but no critical leaf/archive evidence -> `CHECKPOINT_ROOT_SURVIVES_PREFIX_AUDITABILITY_LOST`;
52. current operation can be policy-bounded during temporary archive outage without claiming historical completeness.

## 13. Implementation guidance for LAB-093

When exact executable source becomes available, implement tests before production code. Prefer a small canonical checkpoint/authority/archive-manifest model rather than a mutable `latest_checkpoint` row with implicit overwrite semantics.

Minimum executable slice:

1. checkpoint-authority predecessor+successor rotation and compromise handling;
2. checkpoint chaining with sequence + Merkle/set commitment;
3. explicit `CONSISTENT_BUT_COMPLETENESS_UNPROVEN` versus `COMPLETE_PROVEN`;
4. same-generation/different-root equivocation fail-closed;
5. independent archive reconstruction and loss states;
6. GC refusal when deleting the last policy-critical contradiction copy.

Compose with all previously frozen LAB-093 convergence, continuous-assurance, invalidation, event-gap, reclosure, time/freshness, rebootstrap, and evidence-authority contracts. None of these design freezes substitute for exact RED/GREEN execution.

## Frozen decision

`CONTINUOUS_ASSURANCE_CHECKPOINT_AUTHORITY_ARCHIVE_SURVIVABILITY_SPLIT_VIEW_PREFIX_COMPLETENESS_V1_FROZEN`

The decisive rule is:

```text
A checkpoint is a compact commitment to history, not a replacement for history.
A valid checkpoint signature does not prove semantic prefix completeness.
Archive unavailability does not prove pruning.
Conflicting authenticated checkpoint roots are equivocation, never a last-writer-wins choice.
```
