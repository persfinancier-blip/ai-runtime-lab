# Continuous-assurance authority lifecycle, invalidation independence, event-loss recovery, and reclosure compaction v1

Status: **FROZEN DESIGN CONTRACT / RED-first**

Contract name: `CONTINUOUS_ASSURANCE_AUTHORITY_LIFECYCLE_INVALIDATION_INDEPENDENCE_EVENT_LOSS_COMPACTION_V1_FROZEN`

Date: 2026-09-08

Related: LAB-093 / #178. This is a design follow-up only; it does not substitute for exact executable RED/GREEN evidence.

## Objective

Extend the previously frozen convergence/continuous-assurance model so that:

1. the authority allowed to issue `ConvergenceInvalidationV1` is itself explicitly versioned, rotated, revoked, freshness-bounded, and appraised;
2. no single compromised monitor can become unilateral ecosystem-wide revocation authority merely because it can emit a syntactically valid contradiction;
3. a relying party that misses an unknown interval of topology/invalidation events can recover without silently assuming that the last cached convergence verdict remained current;
4. old verdict/invalidation chains can be compacted for bounded storage/read cost without deleting contradiction provenance, creating rollback ambiguity, or changing historical truth;
5. historical transparency receipts remain verifiable while current authority is monotonic and freshness-bounded.

## Core distinctions

The implementation MUST preserve these separations:

```text
VALID_INVALIDATION_SIGNATURE
    != CURRENT_INVALIDATION_ISSUER_AUTHORITY
    != INDEPENDENT_INVALIDATION_EVIDENCE
    != APPRAISED_CONTRADICTION
    != CURRENT_CONVERGENCE_INVALIDATION

EVENT_STREAM_SILENCE
    != PROOF_OF_NO_INTERVENING_EVENTS

CHECKPOINT_COMPACTION
    != HISTORY_DELETION
    != CONTRADICTION_ERASURE
```

A cryptographically valid statement is evidence from an issuer. It is not automatically an authoritative invalidation decision.

## Donor mechanisms and primary-source evidence

### RFC 9334 — RATS

RATS explicitly separates Evidence, Verifier appraisal, Attestation Results, and relying-party appraisal. A relying party may need to establish trust in the Verifier itself, and appraisal policy must itself be obtained securely. RATS also makes freshness a relying-party/appraisal-policy decision and warns against use beyond the accepted freshness period.

Mechanisms reused here:

- issuer/verifier trust is itself appraised rather than assumed;
- freshness is part of authorization, not merely telemetry metadata;
- evidence and appraisal result are separate authority layers;
- a compromised verifier or appraisal-policy owner invalidates downstream trust assumptions.

Source: https://www.rfc-editor.org/rfc/rfc9334.html

### RFC 5280 — revocation status lifecycle

PKIX separates certificate validity from current revocation status and uses signed, numbered, freshness-bounded CRLs/delta CRLs. It also recognizes propagation latency: a newly accepted revocation is not reliably known to all relying parties until current status information reaches them.

Mechanisms reused here:

- current revocation state has a generation/number and freshness interval;
- a base checkpoint plus ordered deltas may reconstruct current state only when scope and sequence match;
- missing or unsupported scope must degrade to unknown rather than silently to good/current;
- distribution is not itself authority: signed status and freshness are verified by relying parties.

Source: https://www.rfc-editor.org/rfc/rfc5280.html

### RFC 9943 — SCITT

SCITT provides append-only, receipted registration of signed statements. A receipt proves that a statement was registered in a transparency service; it does not make the semantic claim true.

Mechanisms reused here:

- verdicts, invalidations, policy rotations, checkpoints, and supersession statements get durable append-only receipts;
- compaction cannot erase prior receipted statements;
- a compacted checkpoint must commit to the historical prefix it summarizes.

Source: https://www.rfc-editor.org/rfc/rfc9943.html

### RFC 9162 — Certificate Transparency

CT requires clients/monitors to check append-only consistency and recognizes split-view detection as a separate problem requiring comparison/gossip among independently observed log views.

Mechanisms reused here:

- independent observation matters; one monitor cannot prove global consistency alone;
- conflicting signed views are contradiction/fraud evidence, not candidates for last-writer-wins resolution;
- compact checkpoints must remain consistency-linkable to prior history.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### Kubernetes list/watch / `resourceVersion`

Kubernetes explicitly permits event history to age out. A watch from an old `resourceVersion` may return `410 Gone`; the client must re-list/re-establish state rather than pretend watch continuity. A list snapshot plus subsequent watch establishes a new continuity frontier.

Mechanisms reused here:

- a watch gap is a first-class loss-of-continuity state;
- event retention expiry requires consistent snapshot/reconciliation and a fresh stream frontier;
- silence after an unknown gap is not evidence that no changes occurred.

Source: https://kubernetes.io/docs/reference/using-api/api-concepts/

## 1. Invalidation authority is a first-class governed authority

Define:

```text
ContinuousAssuranceAuthorityV1 {
  authority_lineage_id
  generation
  predecessor_generation
  issuer_key_set_digest
  threshold_policy_digest
  independence_policy_digest
  scope
  valid_from_frontier
  valid_until / freshness policy
  rotation_authorizations
  status
  transparency_receipt
}
```

`status` is append-only lifecycle state such as `ACTIVE`, `RETIRED`, `REVOKED_COMPROMISE`, `REVOKED_POLICY_FAILURE`, or `HISTORICAL_ONLY`.

An invalidation artifact is current-authoritative only if its issuer generation was authorized for the relevant scope at issuance time and remains historically trustworthy for that issuance interval.

Routine rotation MUST require continuity authorization from the predecessor authority and authorization by the successor policy/key set. A newly proposed authority cannot authorize its own predecessor edge.

If compromise onset is known, artifacts issued after the affected boundary lose authority. If compromise onset is unknown and the invalidation/reclosure decision depends on that issuer, the corresponding interval becomes `UNKNOWN_HISTORICAL_INVALIDATION_AUTHORITY` until independently re-appraised.

## 2. One monitor is not unilateral revocation authority

Separate three roles:

```text
Observer -> emits ObservationEvidenceV1
Appraiser -> decides whether evidence proves a contradiction
InvalidationAuthority -> emits ecosystem authority transition after threshold appraisal
```

A monitor that discovers `L0` acceptance, a resurrected endpoint, probe steering, topology omission, or key compromise MAY trigger an immediate local fail-safe/quarantine, but MUST NOT by itself create a globally authoritative permanent `ConvergenceInvalidationV1` unless policy explicitly defines that monitor as a singleton catastrophic oracle. Such singleton policy is forbidden for the high-assurance profile frozen here.

For high-assurance invalidation, require a threshold over independent appraisal/control domains. Independence is evaluated before threshold counting across at least:

- operator/control owner;
- key custody;
- implementation/build lineage;
- runtime/deployment domain;
- topology/evidence source dependencies;
- network/provider path where material;
- appraisal-policy owner.

Multiple signatures from correlated replicas are one failure domain, not multiple independent votes.

### Emergency local safety exception

Any relying party may immediately move from `CURRENTLY_VALID` to `LOCALLY_QUARANTINED_PENDING_APPRAISAL` on a single strong contradiction. This is a safety reaction, not a globally durable invalidation verdict.

Consequential operations fail closed while quarantined. Historical verification remains available.

This avoids two bad extremes:

- allowing one compromised monitor to revoke the ecosystem globally;
- forcing a relying party to keep accepting known-dangerous authority while waiting for quorum adjudication.

## 3. Contradiction classification and appraisal

Define `ContinuousAssuranceObservationV1` with exact subject/topology/verdict frontier, observation type, raw evidence digest, issuer identity/generation, challenge/freshness binding, and transparency receipt where applicable.

Contradictions fall into classes with different evidence thresholds:

1. **cryptographic contradiction** — e.g. same-generation/different-content signed artifacts; normally self-proving after key validity appraisal;
2. **effective-path contradiction** — direct proof that forbidden old-lineage authority was accepted after cutover;
3. **topology contradiction** — authenticated endpoint exists but was absent from the claimed complete coverage set;
4. **issuer compromise** — authoritative lifecycle statement intersects relied-on issuance interval;
5. **probe-steering contradiction** — evidence that challenge traffic was selectively routed away from stale replicas;
6. **continuity loss** — watch/event chain has an unknown interval; this produces `UNKNOWN_STALE`, not automatically `INVALIDATED` unless an actual contradiction is later proved.

No majority, latest timestamp, newest monitor report, or LWW rule may erase a cryptographic/effective contradiction.

## 4. Event-loss recovery

A relying party stores:

```text
ContinuousAssuranceFrontierV1 {
  convergence_lineage
  verdict_generation
  invalidation_generation
  authority_generation
  topology_frontier
  event_stream_frontier
  compact_checkpoint_digest?
  freshness_deadline
}
```

If the event stream resumes with provable continuity from `event_stream_frontier`, normal processing continues.

If continuity cannot be proved — retention expired, `410 Gone`, missing sequence, restored snapshot, lost cursor, unknown interval — state becomes:

`CONVERGENCE_CURRENT_STATUS_UNKNOWN_EVENT_GAP`

The relying party MUST NOT infer no invalidation from absence of received events.

### Recovery protocol after an unknown interval

1. Freeze consequential reliance on the cached convergence verdict.
2. Obtain a fresh authenticated snapshot of:
   - current invalidation authority generation/status;
   - current convergence verdict/invalidation generation;
   - current topology snapshot/version;
   - unresolved contradiction ledger;
   - latest compact checkpoint, if used.
3. Verify snapshot authority and freshness.
4. Verify checkpoint/history consistency from a previously trusted digest/frontier where possible.
5. Reconcile all currently effective endpoints and enforcement surfaces against the snapshot.
6. Re-run required negative old-lineage checks for endpoints whose continuity cannot be proven through the gap.
7. Establish a new event-stream frontier from that consistent snapshot.
8. Only then restore `CURRENTLY_VALID` if no intervening unresolved invalidation/contradiction exists.

If the system cannot prove whether a missing interval contained an invalidation and cannot reconstruct the authoritative current state, remain fail-closed at `CURRENT_STATUS_UNKNOWN`; do not fabricate a continuous chain.

## 5. Reclosure after invalidation

A reclosure artifact MUST reference:

- the prior verdict generation;
- every invalidation/contradiction generation since that verdict;
- remediation evidence for each contradiction;
- current topology frontier;
- current invalidation-authority generation;
- fresh independent verifier/appraiser evidence;
- the historical-prefix/checkpoint digest consumed.

It creates a new verdict generation. It never changes or deletes the earlier `PROVEN -> INVALIDATED -> REOPENED` history.

If an old contradiction was later shown to be a false positive, record a new adjudication/supersession artifact; do not delete the original observation or receipt.

## 6. Safe compaction semantics

Compaction is permitted only as a **cryptographic summary of an immutable prefix**, never as replacement history.

Define:

```text
ContinuousAssuranceCheckpointV1 {
  lineage_id
  checkpoint_generation
  prefix_start
  prefix_end
  previous_checkpoint_digest
  summarized_verdict_frontier
  summarized_invalidation_frontier
  authority_frontier
  topology_frontier
  unresolved_contradiction_set_digest
  historical_statement_merkle_root_or_equivalent
  policy_digest
  issuer_authorizations
  transparency_receipt
}
```

A checkpoint is acceptable only if:

- its prefix is contiguous and ends at a known trusted frontier;
- it commits to all verdicts, invalidations, authority rotations/revocations, contradiction statements, and adjudications in the prefix;
- unresolved contradictions are explicitly carried forward;
- it chains to the previous trusted checkpoint;
- relying parties can request or audit the underlying historical statements from durable archival/transparency storage;
- compaction does not alter historical issuance-time validity semantics.

### Forbidden compaction

Never:

- discard an invalidation because a later reclosure exists;
- collapse `PROVEN -> INVALIDATED -> PROVEN` into a single `PROVEN` state;
- omit a losing fork/equivocation branch;
- permit a checkpoint to be self-authorized by a new authority not authorized at the checkpoint boundary;
- garbage-collect the only durable copy of contradiction evidence required to audit the checkpoint;
- accept a checkpoint with a lower generation/frontier than already trusted state.

## 7. Current-state evaluation

A relying party evaluates current convergence roughly as:

```text
current =
  valid_checkpoint_or_full_history
  AND monotonic trusted frontier
  AND current/fresh invalidation-authority state
  AND no unresolved authoritative invalidation after the last convergence verdict
  AND no unresolved local strong contradiction
  AND topology/event continuity OR successful gap recovery
  AND freshness within policy
```

The transparency receipt of an old convergence verdict remains historically valid even if `current == false`.

## 8. Failure and conflict rules

- Lower authority/verdict/invalidation/checkpoint generation than already trusted -> `ROLLBACK_DETECTED_NO_CURRENT_AUTHORITY`.
- Same generation, different authenticated content -> `EQUIVOCATION_CONFLICT_NO_CURRENT_AUTHORITY`.
- Valid signatures from a revoked/compromised issuer whose compromise interval intersects issuance -> re-appraise; normally invalid/unknown for current reliance.
- Independent invalidation sources disagree on whether evidence proves a contradiction -> `INVALIDATION_APPRAISAL_DISPUTE`; consequential reliance remains quarantined until resolved by the governed policy.
- Missing event interval with no reconstructable authoritative snapshot -> `CURRENT_STATUS_UNKNOWN_EVENT_GAP`.
- Checkpoint omits a previously trusted contradiction/invalidation -> `COMPACTION_PROVENANCE_VIOLATION`.
- Archive unavailable but current checkpoint valid -> current operation may follow policy if full-history availability is not a runtime requirement, but auditability is degraded and MUST be surfaced; checkpoint must never be described as proof that erased history never existed.

## 9. RED-first regression matrix

Freeze at least these 48 cases before implementation.

### Authority lifecycle (1-10)
1. valid current invalidation issuer accepted;
2. retired issuer cannot issue new invalidation;
3. historically valid pre-retirement artifact remains auditable;
4. known compromise boundary invalidates affected issuance;
5. unknown compromise onset yields historical-authority unknown;
6. successor cannot self-authorize rotation;
7. predecessor-only rotation insufficient;
8. successor-only rotation insufficient;
9. rollback to prior authority generation rejected;
10. same-generation/different-authority content is equivocation.

### Independence and local quarantine (11-20)
11. one monitor contradiction causes local quarantine, not global invalidation;
12. independent threshold proves global invalidation;
13. two keys under one custody domain count once;
14. two replicas of one implementation/control plane count once;
15. apparently separate monitors sharing same evidence oracle fail independence policy;
16. compromised singleton monitor cannot permanently revoke ecosystem;
17. strong effective-path contradiction blocks local consequential operations immediately;
18. weak/stale observation does not trigger authoritative invalidation;
19. conflicting independent appraisals remain disputed/fail-closed;
20. forged monitor evidence rejected before threshold counting.

### Event-loss recovery (21-32)
21. continuous stream from trusted frontier advances normally;
22. duplicate event idempotent;
23. lower sequence rejected;
24. sequence gap enters unknown state;
25. retention-expired/410-style gap requires fresh snapshot;
26. snapshot proves an invalidation occurred during gap -> remain invalidated;
27. snapshot proves later reclosure consumed intervening invalidation -> may accept new verdict after verification;
28. snapshot cannot be linked/reconciled -> remain unknown;
29. event silence after gap is not proof of no invalidations;
30. VM snapshot restores old cursor -> rollback/gap detected;
31. topology changed during gap -> affected endpoints require fresh effective-path proof;
32. new stream is accepted only after consistent snapshot establishes new frontier.

### Reclosure (33-39)
33. reclosure references/remediates every intervening contradiction;
34. omitted contradiction blocks reclosure;
35. false-positive adjudication preserves original observation;
36. reclosure uses current authority generation;
37. stale reclosure freshness rejected;
38. conflicting same-generation reclosures fail closed;
39. later reclosure never makes historical invalidation disappear.

### Compaction (40-48)
40. contiguous prefix checkpoint accepted;
41. checkpoint chain to previous trusted digest verified;
42. checkpoint omitting an invalidation rejected;
43. checkpoint omitting unresolved contradiction rejected;
44. lower checkpoint generation rejected;
45. same generation/different root is equivocation;
46. checkpoint signed only by unauthorized successor rejected;
47. archived underlying statements reproduce checkpoint root/digest;
48. reclosure after checkpoint correctly consumes pre-checkpoint unresolved state carried forward by the checkpoint.

## 10. Implementation guidance for LAB-093

When exact source execution becomes available, implement tests before production code. Prefer a small append-only authority/verdict/checkpoint model with canonical serialization and explicit generation fields. Do not add a mutable `current=true/false` column as the only source of truth; derive current status from the authenticated monotonic chain plus freshness.

The minimum executable slice should prove:

1. invalidation-authority rotation/revocation semantics;
2. single-monitor local quarantine vs independent global invalidation;
3. event-gap transition to unknown and snapshot-based recovery;
4. reclosure consuming all contradictions;
5. compact checkpoint rejection when any known contradiction is omitted.

Then compose with the already frozen rebootstrap/convergence/topology/evidence contracts and LAB-087 isolation.

## Decision

Freeze:

`CONTINUOUS_ASSURANCE_AUTHORITY_LIFECYCLE_INVALIDATION_INDEPENDENCE_EVENT_LOSS_COMPACTION_V1_FROZEN`

The essential security rule is:

> **A convergence verdict is current only under a current, independently appraised assurance authority and a continuity-complete or explicitly recovered event/topology frontier. Compaction may summarize immutable history, never erase it.**

No executable PASS is claimed by this research freeze.