# Historical trust-bundle capture atomicity / pre-decommission freeze / completeness proof v1

Status: `HISTORICAL_TRUST_BUNDLE_CAPTURE_ATOMICITY_PRE_DECOMMISSION_FREEZE_COMPLETENESS_PROOF_V1_FROZEN`

Date: 2026-09-07

Parent line: LAB-093 / portable provider receipts / historical trust survivability.

## Question

The prior contract makes historical verification time-indexed and requires exact provider-origin receipt bytes, historical root/key material, CRL/OCSP/status evidence, event-time anchors, transparency checkpoints, frozen schemas/policies and archive-renewal evidence. That is still insufficient if shutdown/decommission captures only a subset of the material that was required at the historical boundary.

The remaining question is therefore not merely **how to preserve evidence**, but **how to prove that the evidence archive was complete at a causally closed cut before the authority that could produce or clarify that evidence disappeared**.

Examples of unsafe partial capture:

- receipts are copied, but the final CRL/OCSP/status frontier is not;
- a transparency entry is copied, but the historical log key/checkpoint needed to verify it is not;
- roots and schemas are copied, but a provider request accepted just before account shutdown is absent;
- a provider is disabled before final asynchronous audit/digest delivery finishes;
- the archive contains every object currently visible to one API endpoint, while another region or queue still contains accepted events;
- a crash happens after the provider is frozen but before the manifest root is durably committed, and recovery guesses that the partial directory is complete;
- decommission deletes a key/account/log while some historical receipt still depends on online-only validation material.

A safe design must make incomplete capture fail closed as `UNKNOWN`, not silently upgrade it to historical finality.

## Donor mechanisms checked

### RFC 4998 — Evidence Record Syntax

Primary: https://www.rfc-editor.org/rfc/rfc4998.html

Useful mechanism:

- preservation evidence covers a defined archived data object or object group;
- Merkle/hash-tree roots bind a complete selected object set;
- timestamp/hash-tree renewal extends proof lifetime before cryptographic primitives become unsafe;
- hash-tree renewal requires access to the archived data objects, not just the previous timestamp.

Boundary:

RFC 4998 can prove integrity/existence of the object group that was selected. It does **not** prove that the selector included every object the application semantics required. LAB-093 therefore needs a separately authenticated semantic inventory/completeness proof.

### RFC 3161 — Time-Stamp Protocol

Primary: https://www.rfc-editor.org/rfc/rfc3161.html

Useful mechanism:

An independent timestamp can establish that a digest existed no later than a stated time. This is useful for sealing the final archival manifest/checkpoint before decommission.

Boundary:

A timestamp proves time-of-existence of the submitted digest. It does not prove that the manifest was complete, that the provider accepted every represented event, or that no accepted event was omitted.

### AWS CloudTrail digest chaining and final digest

Primary:

- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-cli.html

Useful mechanism:

- each digest references hashes of delivered log files and the previous digest, producing a verifiable chain;
- deletion/modification inside the covered chain can be detected;
- when logging is stopped or a trail is deleted, CloudTrail documents delivery of a final digest that can cover remaining log files through the stop event;
- delivery can be delayed/out of order after disruption, so an apparently broken or incomplete local set cannot be treated as final immediately.

Boundary:

CloudTrail explicitly validates only log files referenced by digest files. Therefore signed digest-chain integrity is not equivalent to semantic completeness of every consequential provider event. This is a direct donor for the rule `AUTHENTIC_ARCHIVE != COMPLETE_ARCHIVE`.

### Sigstore bundle / offline verification

Primary:

- https://docs.sigstore.dev/about/bundle/
- https://docs.sigstore.dev/cosign/verifying/verify/

Useful mechanism:

A bundle can retain certificate/key verification material, transparency entries, signed-entry timestamps/inclusion evidence and optional RFC3161 timestamps so later verification need not query the live log.

Boundary:

A self-contained bundle proves the event represented by that bundle. It does not prove that every event that should have a bundle is present in an archive.

## Core distinction

The contract freezes four different properties. None may be substituted for another:

1. **Object authenticity** — an archived object is authentic provider/log/CA-origin evidence.
2. **Archive integrity** — archived bytes and their ordering/grouping have not been modified or deleted after sealing.
3. **Semantic completeness** — every evidence object required by the exact historical policy/schema/inventory at the cut is represented, or an authenticated `NOT_APPLICABLE` witness exists.
4. **Causal closure** — after the cut there is no still-authorized path that can create an earlier-generation consequential event whose required proof would belong in the supposedly final archive.

`FINAL_ARCHIVE_CLOSED` requires all four.

## Frozen model

### 1. ArchiveCaptureCampaignV1

```text
ArchiveCaptureCampaignV1 {
  campaign_id
  authority_scope
  provider/account/log/key identities
  source_generation
  target_archive_generation
  semantic_inventory_root
  schema_root
  policy_root
  trust-policy-generation
  freeze_nonce
  freeze_requested_at
  status
}
```

Allowed statuses:

```text
OPEN
FREEZE_REQUESTED
FROZEN
CAPTURING
CAPTURED_UNSEALED
SEALED_PENDING_COMPLETENESS
CLOSED
UNKNOWN
ABORTED
```

No transition out of `UNKNOWN` may be based on absence of new observations alone. Recovery requires positive evidence that closes the missing causal/evidence frontier.

### 2. PreDecommissionFreezeV1

A freeze is an authenticated authority transition, not an operator note.

```text
PreDecommissionFreezeV1 {
  campaign_id
  scope
  predecessor_generation
  frozen_generation
  authority_epoch
  provider_fence_generation
  no_new_issue_generation
  no_new_renew_generation
  no_new_receipt_generation
  no_new_async_delivery_generation
  freeze_commit_token
  provider_native_readbacks[]
  independent_witnesses[]
}
```

The freeze is valid only when every material producer path is either:

- mechanically denied for the frozen generation; or
- bounded by a finite, independently proven drain horizon and classified as `DRAINING` until that horizon and all corresponding final delivery/checkpoint evidence have passed.

An administrative API returning `disabled=true` is not sufficient if already accepted work, queues, replication, digest delivery, log integration or status publication can still produce evidence relevant to pre-freeze events.

### 3. EvidenceRequirementManifestV1

Completeness is evaluated against an authenticated manifest derived from the exact historical semantic inventory + schema + policy generation.

```text
EvidenceRequirementManifestV1 {
  campaign_id
  source_generation
  semantic_inventory_root
  schema_root
  policy_root
  required_slots[]
}

RequiredSlot {
  stable_slot_id
  evidence_class
  resource_scope
  selector
  source_authority
  expected_cardinality_rule
  closure_rule
  historical_verifier_requirement
}
```

Example slots:

- provider-origin acceptance receipt for every consequential request in operation range;
- final provider fence/readback for each authority region;
- historical certificate chain/root generation;
- CRL/OCSP/status material covering every receipt signer at event time;
- RFC3161/event-time anchor where policy requires one;
- transparency entry + inclusion/SET/checkpoint + historical log key;
- exact historical schema/policy/verifier generation;
- provider-native final audit/digest frontier;
- archive-renewal material required before any cryptographic retirement boundary.

Stable slot IDs are non-reusable. A later schema cannot redefine the meaning of an old slot.

### 4. CapturedEvidenceObjectV1

```text
CapturedEvidenceObjectV1 {
  campaign_id
  slot_id
  object_id
  origin_class
  raw_bytes_digest
  raw_bytes_location
  source_native_identity
  source_order_token
  event_time_evidence
  signer_or_log_epoch
  capture_time
  capture_reader_identity
}
```

Model-generated normalized JSON is never the authoritative archival object when provider-native bytes exist. Normalized views may be indexed separately, but the archive root binds exact retained bytes.

### 5. ArchiveCaptureManifestV1

```text
ArchiveCaptureManifestV1 {
  campaign_id
  freeze_digest
  requirement_manifest_digest
  captured_objects_root
  slot_discharge_root
  provider_final_frontiers[]
  independent_readback_root
  missing_or_unknown_slots[]
  final_manifest_generation
}
```

Every required slot must discharge as exactly one of:

```text
PRESENT_AUTHENTIC
NOT_APPLICABLE_AUTHENTIC
UNKNOWN_MISSING
CONTRADICTORY
```

Only the first two are closure-compatible.

`NOT_APPLICABLE_AUTHENTIC` must be produced by an authority independent of the archive builder when omission of that slot could conceal consequential history.

### 6. ArchiveSealV1

The final manifest digest is sealed by an independent time/integrity mechanism after capture and after final provider/log/status frontiers are known.

```text
ArchiveSealV1 {
  campaign_id
  manifest_digest
  previous_archive_seal
  sealed_at_evidence
  seal_authority_generation
  archive_timestamp_or_checkpoint
  storage_immutability_evidence
}
```

RFC3161 or a transparency/checkpoint mechanism may serve as time-of-existence evidence. A Merkle/Evidence-Record root may bind the object group. Neither substitutes for the semantic completeness proof.

### 7. ArchiveCompletenessProofV1

```text
ArchiveCompletenessProofV1 {
  campaign_id
  freeze_digest
  requirement_manifest_digest
  capture_manifest_digest
  archive_seal_digest
  all_slots_discharged
  producer_paths_closed
  async_delivery_frontiers_closed
  provider_readbacks_closed
  status_publication_frontiers_closed
  transparency_frontiers_closed
  independent_checker_generation
  verdict
}
```

Verdicts:

```text
CLOSED
UNKNOWN_PARTIAL_CAPTURE
UNKNOWN_ASYNC_FRONTIER
UNKNOWN_STATUS_FRONTIER
UNKNOWN_PROVIDER_FRONTIER
CONTRADICTORY_EVIDENCE
INVALID
```

There is intentionally no `BEST_EFFORT_CLOSED` state usable for destructive decommission/finality.

## Capture protocol

### Phase A — derive the closure universe before freezing

1. Resolve exact semantic inventory, schema, policy and historical verifier generation.
2. Compile `EvidenceRequirementManifestV1`.
3. Independently verify operation-kind/slot coverage.
4. Enumerate every producer, renewal, audit, log, status, timestamp and asynchronous delivery path capable of creating material historical evidence.
5. If an unknown plugin/provider/region/queue/status path exists, stop with `UNKNOWN` before decommission.

This phase prevents a malicious or defective archive builder from defining the universe as merely “whatever files I happened to copy.”

### Phase B — install freeze barrier

1. Enter `FREEZE_REQUESTED`.
2. Revoke/deny new issuance, renewal and consequential operation authority for the target generation.
3. Fence all regions/issuers using the previously frozen issuer/provider-fence contracts.
4. Prevent new asynchronous jobs from being accepted for the target generation.
5. Record provider-native fence/readback evidence.
6. Transition to `FROZEN` only when no new target-generation causal root can be created.

If a system cannot prevent new events but provides finite immutable expiries, remain `DRAINING` until the maximum horizon has passed and all final frontiers are reconciled.

### Phase C — drain and close asynchronous evidence production

The system must distinguish **new consequential event production** from **late evidence delivery about an already frozen event**.

After freeze, late evidence delivery may continue and must be captured. Examples:

- delayed CloudTrail digest/log delivery;
- transparency integration/checkpoint advancement;
- delayed CRL/OCSP/status publication;
- provider replication/readback settling;
- queued receipt export.

Each path needs a positive closure rule, such as:

- provider-native final digest/checkpoint covering through freeze token;
- final sequence/order token plus proof that no earlier token is missing;
- independently bounded drain horizon plus complete reconciliation at/after horizon;
- explicit provider finalization receipt bound to the freeze generation.

A quiet period with no new observations is not a closure proof.

### Phase D — capture exact evidence

1. Read every required slot using the required independent/provider-native path.
2. Retain exact bytes and source-native identity/order tokens.
3. Verify authenticity at capture time but do not discard bytes merely because verification succeeds.
4. Build deterministic Merkle/hash roots over exact objects and slot discharges.
5. Re-read authoritative frontiers after object capture to detect racing late delivery.
6. If any frontier advanced, capture the newly materialized evidence and repeat until the frozen-generation closure rule is satisfied.

This is a fixed-point procedure over a **frozen causal generation**, not an unbounded poll-until-quiet loop.

### Phase E — independent completeness check

The checker must not use the archive builder's object list as its sole source of required objects.

It recomputes requirements from:

- frozen semantic inventory;
- frozen schema/policy;
- provider-native final frontiers;
- independent regional/readback reconciliation;
- source-native sequence/order commitments where available.

For each slot it verifies `PRESENT_AUTHENTIC` or independently justified `NOT_APPLICABLE_AUTHENTIC`.

If source semantics do not expose enough information to distinguish “zero objects existed” from “objects existed but were omitted”, the slot remains `UNKNOWN_MISSING` and destructive decommission is forbidden.

### Phase F — seal, then decommission

Order is mandatory:

```text
freeze
  -> drain final evidence
  -> capture
  -> independent completeness check
  -> seal exact manifest/object root
  -> verify seal from a second reader
  -> commit CLOSED
  -> only then destroy/decommission provider/key/log/account material
```

Destroying a verification dependency before `CLOSED` is itself a protocol violation.

## Atomicity semantics

There is generally no single cross-provider transaction that atomically freezes a SaaS account, exports all logs, publishes final OCSP/CRL, obtains transparency checkpoints and commits local archive storage. Therefore “atomicity” here is **protocol atomicity**, not distributed ACID.

The safety property is:

> A decommission becomes authorized only after one immutable campaign generation binds (a) the causal freeze, (b) the exact requirement universe, (c) the captured object root, (d) positive closure of every asynchronous evidence frontier, (e) an independent completeness verdict and (f) the archive seal.

Any crash before the final `CLOSED` commit leaves decommission unauthorized.

## Crash recovery

### Crash before freeze commit

Campaign remains `OPEN/FREEZE_REQUESTED`. No completeness is claimed. Reconcile provider fence state before retry.

### Crash after freeze, before capture completes

The frozen generation remains immutable. Resume capture against the same `campaign_id`, `freeze_digest`, inventory/schema/policy roots and source generation. Never mint a new semantic universe merely to make the partial archive pass.

### Crash after object capture, before seal

Recompute all object digests from retained bytes, re-read final source frontiers and rerun completeness. Existing files are untrusted until re-bound to the campaign manifest.

### Crash after seal, before CLOSED

Verify seal and completeness proof independently; if byte-identical and all source closure conditions remain historically demonstrable, commit `CLOSED`. Otherwise remain `UNKNOWN`.

### Crash after CLOSED, before physical provider deletion

Safe to retry decommission only if the current deletion request is bound to the same closed campaign/generation and no newer authority generation has re-enabled the provider.

### Evidence source disappears before CLOSED

`UNKNOWN_PARTIAL_CAPTURE`. Do not reconstruct missing provider-origin evidence from application logs or adapter caches and call it equivalent.

## Decommission authorization

`DecommissionAuthorizationV1` requires:

```text
campaign.status == CLOSED
archive_completeness_proof.verdict == CLOSED
archive_seal.manifest_digest == capture_manifest.digest
all provider/key/log/account dependencies classified as historically self-contained
no renewal/issuer/provider path remains enabled for frozen generation
current decommission target identity == campaign target identity
```

Deletion is rejected on any mismatch.

## Fraud / contradiction proofs

### `ARCHIVE_OMITTED_REQUIRED_OBJECT_PROVEN`

Inputs:

- closed campaign manifest;
- authenticated source-native evidence for an event/object that belonged to the frozen generation;
- requirement rule proving its slot was mandatory;
- Merkle/non-membership proof or manifest evidence showing absence.

Effect:

- invalidate `ArchiveCompletenessProofV1`;
- invalidate dependent historical finalization/GC proofs;
- reopen affected closure as `UNKNOWN`/`INVALID`;
- require additive repair if source evidence still exists;
- never rewrite the original closed manifest as if omission never happened.

### `DECOMMISSION_BEFORE_ARCHIVE_CLOSED_PROVEN`

Inputs:

- authenticated destruction/decommission event;
- campaign state proving `CLOSED` had not been committed first.

Effect:

- permanent `UNKNOWN` for any required evidence that cannot subsequently be independently recovered;
- security incident/audit finding; no fabricated reconstruction.

### `POST_FREEZE_TARGET_GENERATION_EVENT_PROVEN`

Shows that a supposedly closed producer path still accepted a new target-generation consequential event after freeze. The freeze and all dependent completeness/finality claims are invalid.

### `ASYNC_FRONTIER_OMISSION_PROVEN`

Shows source-native sequence/digest/checkpoint evidence skipped a required predecessor or final delivery. Closure becomes `UNKNOWN` until the missing range is reconciled.

### `ARCHIVE_BUILDER_SELF_ATTESTED_ABSENCE`

If the only proof that a slot had no objects is an assertion emitted by the same component that selected/captured the archive, the absence is non-authoritative for consequential slots. Verdict remains `UNKNOWN_MISSING`.

## Negative boundaries

The following are explicitly insufficient for `CLOSED`:

- “all currently listed files were copied”;
- a single ZIP/export job succeeded;
- a Merkle root over a directory selected by the archive builder;
- an RFC3161 timestamp over an incomplete manifest;
- a valid Sigstore bundle for every object that happened to be selected;
- a CloudTrail digest chain without proof the semantic event set was fully represented by the trail and final delivery frontier;
- a quiet period;
- current/live OCSP replacing missing historical status evidence;
- current provider state replacing missing pre-decommission provider-origin receipts;
- current root/log key replacing historical roots/log keys;
- eventual cross-region convergence without a proved final frozen-generation frontier;
- model-generated summaries, normalized adapter responses or screenshots in place of provider-origin bytes.

## Composition with previous frozen contracts

The proof chain is now:

```text
EffectCapabilityInventoryV1
  -> CapabilityEnvelopeV1 / delegation lineage
  -> RevocationCampaignV1 / descendant closure
  -> D2 lease renewal linearization
  -> issuer/quorum/provider-fence handoff
  -> ProviderFenceAttestationV1
  -> PortableProviderReceiptV1
  -> HistoricalTrustBundleV1
  -> ArchiveCaptureCampaignV1
  -> ArchiveCompletenessProofV1
  -> DecommissionAuthorizationV1
```

A stronger later layer never repairs an `UNKNOWN` in an earlier layer merely by signing it.

LAB-087 remains the process/filesystem sole-writable-handle boundary. LAB-093 implementation must prevent the archive-builder process from being its own independent completeness authority where the same process can omit evidence and rewrite manifests.

## RED-first executable matrix (80 cases)

The implementation phase must encode these as exact behavioral tests before production refactor.

### A. Freeze barrier — 10

1. clean global freeze closes;
2. one unfenced region -> no `FROZEN`;
3. stale issuer still renews -> reject;
4. plugin path still issues -> reject;
5. queued new consequential job accepted after freeze -> reject;
6. old target generation event after freeze -> fraud proof;
7. provider disable response without fence proof -> `UNKNOWN`;
8. bounded lease drain before horizon -> not closed;
9. bounded lease drain after proved horizon -> eligible;
10. crash during freeze -> reconcile, never infer success.

### B. Requirement universe — 10

11. all stable slots mapped;
12. missing provider-receipt slot -> reject completeness;
13. reused slot ID with changed semantics -> reject;
14. unknown operation kind -> `UNKNOWN`;
15. plugin capability absent from inventory -> reject;
16. historical verifier dependency omitted -> reject;
17. independently justified `NOT_APPLICABLE` -> accept;
18. builder-self-attested `NOT_APPLICABLE` -> reject for consequential slot;
19. schema/inventory root mismatch -> invalid;
20. policy generation mismatch -> invalid.

### C. Async drain/frontiers — 10

21. final digest/checkpoint arrives after freeze and is captured;
22. archive seals before late digest -> reject;
23. out-of-order digest delivery reconciles;
24. missing predecessor digest -> `UNKNOWN_ASYNC_FRONTIER`;
25. delayed transparency inclusion unresolved -> no closure;
26. delayed CRL/status publication unresolved -> no closure where required;
27. replicated region readback still stale -> no closure;
28. quiet period without positive frontier -> no closure;
29. provider native finalization receipt closes range;
30. final frontier advances during capture -> fixed-point recapture.

### D. Exact-object capture — 10

31. exact provider bytes retained and digest matches;
32. normalized JSON only -> insufficient;
33. provider bytes mutated after capture -> seal verification fails;
34. object moved but bytes/identity intentionally portable under policy -> valid if policy permits;
35. wrong provider-native object identity -> reject;
36. wrong source order token -> reject;
37. duplicate object under two slots -> cardinality check;
38. missing historical root bytes -> `UNKNOWN`;
39. missing historical log key -> `UNKNOWN`;
40. missing timestamp/checkpoint evidence required by policy -> `UNKNOWN`.

### E. Completeness checker independence — 10

41. independent checker recomputes same slot set -> pass;
42. builder object list used as sole requirement source -> reject;
43. source-native count/range says 10, archive has 9 -> reject;
44. archive claims zero but independent source proves one -> fraud;
45. two regions contradict object set -> `CONTRADICTORY`;
46. provider receipt exists but slot selector excludes it incorrectly -> reject selector proof;
47. checker binary/policy generation unbound -> invalid;
48. checker uses current schema instead of frozen schema -> invalid;
49. checker uses current trust state instead of historical bundle -> invalid;
50. independent `NOT_APPLICABLE` witness authentic and scoped -> pass.

### F. Seal and storage — 10

51. Merkle root binds all exact objects + discharges;
52. timestamp exists before decommission -> valid time anchor only;
53. timestamp over incomplete manifest -> completeness still fails;
54. storage object deletion after seal -> detectable;
55. manifest deletion after seal -> archive unusable/invalid;
56. previous seal chaining mismatch -> reject;
57. archive timestamp signer invalid at seal time -> reject;
58. seal copied without raw objects -> reject;
59. exact raw objects copied with valid self-contained seal -> historical verification works offline;
60. hash algorithm retirement without renewal -> `UNKNOWN_ARCHIVE_CHAIN`.

### G. Crash/recovery — 10

61. crash pre-freeze -> no closed state;
62. crash post-freeze/pre-capture -> resume same generation;
63. crash mid-object copy -> verify bytes and resume;
64. crash captured/unsealed -> reread frontiers before sealing;
65. crash sealed/pre-CLOSED -> independently verify then commit;
66. crash CLOSED/pre-delete -> idempotent deletion bound to campaign;
67. source deleted mid-capture -> `UNKNOWN_PARTIAL_CAPTURE`;
68. recovery silently drops missing slot -> reject;
69. recovery changes policy/schema root -> new campaign required;
70. recovery sees contradictory authentic evidence -> `CONTRADICTORY`, not latest-wins.

### H. Decommission/fraud/repair — 10

71. decommission only after CLOSED -> allow;
72. deletion before CLOSED -> fraud proof;
73. later omitted object discovered -> invalidate dependent closure;
74. additive repair while source still exists -> new repair generation;
75. missing object permanently unavailable -> remain `UNKNOWN`;
76. old closed manifest overwritten during repair -> reject;
77. provider account decommissioned but archive self-contained -> historical verify succeeds;
78. transparency service offline but bundle/checkpoint/key self-contained -> historical verify succeeds;
79. current OCSP says revoked but historical effective-invalidity boundary proves post-event compromise -> historical policy applies correctly;
80. every object authentic but one required slot absent -> archive is **not** complete.

## Decision

Freeze this contract for LAB-093 design work.

The safe abstraction is not `export_before_delete()`. It is a durable **archive capture campaign** with a causal freeze barrier, independently derived evidence requirement universe, explicit asynchronous frontier closure, exact-byte capture, independent completeness checking, immutable sealing, and decommission authorization that is impossible before `CLOSED`.

If any required source disappears first, or if the system cannot prove whether an omitted object ever existed, the correct result is `UNKNOWN`, potentially permanently.

## Next distinct research hole

`archive replica durability / independent custody / correlated-loss and restore-verifiability semantics`.

Even a complete sealed bundle can still disappear or become jointly corrupt if manifest, raw evidence, historical roots and renewal chain share one storage/admin/failure domain. The next contract should define minimum independent custody/replica failure domains, erasure/replication versus logical independence, periodic proof-of-retrievability/restore drills, anti-rollback of archive replicas, custody-key separation, and the conditions under which historical finalization may depend on archived evidence for destructive GC.