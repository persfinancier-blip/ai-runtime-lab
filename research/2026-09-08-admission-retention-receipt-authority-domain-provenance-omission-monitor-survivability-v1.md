# Admission-retention receipt authority, destructive-domain provenance, and omission-monitor survivability v1

Status: **ADMISSION_RETENTION_RECEIPT_AUTHORITY_DOMAIN_PROVENANCE_OMISSION_MONITOR_SURVIVABILITY_V1_FROZEN**

Date: 2026-09-08

Scope: design/evidence contract only. This does not substitute for executable RED/GREEN proof on LAB-086/LAB-093.

## Problem

The previous freeze introduced `AdmissionRetentionReceiptV1` so admission existence can survive loss of one storage/control domain, and allowed exhaustive authenticated-prefix reconstruction as a positive semantic absence proof. Three unresolved questions remain:

1. Who may issue, revoke, supersede, or invalidate retention receipts without allowing the receipt authority to erase prior admission existence?
2. How is claimed independence of storage/retention domains authenticated and later re-appraised when a supposedly independent replica is found to share a destructive dependency?
3. How can an exhaustive-prefix omission proof remain reproducible after one monitor/archive disappears or is later found compromised?

## Primary-source donors

### RFC 9162 / Certificate Transparency

RFC 9162 requires a monitor to inspect every new entry in each watched log. For full reconstruction it specifies: fetch the signed tree head, fetch all entries corresponding to that tree, rebuild the Merkle tree, and verify the root against the signed tree head. For incremental operation it permits retaining the full log or using consistency proofs plus the new entries. Failure to provide promised inclusion or entries can yield signed evidence of log misbehavior.

Mechanisms reused here:
- complete authenticated prefix as the basis for semantic absence;
- retained signed checkpoints/frontiers;
- independently reproducible tree-root verification;
- append-only re-evaluation instead of rewriting prior conclusions.

Source: RFC 9162, sections 8.2 and 8.3.

### RFC 9943 / SCITT

SCITT separates the statement issuer from the Transparency Service and allows the same Signed Statement to be registered in multiple Transparency Services, producing multiple independent receipts. A receipt demonstrates registration in a VDS; it does not make the statement semantically true. Auditors/relying parties need not be trusted by other actors, and multiple independent TSs reduce single-service dependence.

Mechanisms reused here:
- separate issuer and retention/transparency roles;
- multiple independently retained receipts for the same admission envelope;
- receipt proves registration/retention under a defined policy, not truth of all provenance claims;
- multi-service survivability without collapsing all replicas into one trust root.

Source: RFC 9943, sections 4, 5, 6.3, and 9.7.

### TUF role separation and threshold recovery

TUF separates root, targets, snapshot, and timestamp roles. Root metadata defines trusted role keys and thresholds. If less than a root threshold is compromised, keys can be replaced through new root metadata; if the root threshold itself is compromised, recovery requires out-of-band reissuance. Short-lived timestamp metadata helps detect freeze/withholding without giving the timestamp role root authority.

Mechanisms reused here:
- receipt-authority lifecycle is separate from admission truth and storage custody;
- authority rotation requires an independently authorized continuity chain;
- compromise of the receipt authority cannot self-authorize a clean successor if its recovery threshold is lost;
- liveness/freshness role cannot erase historical records.

Sources: TUF Roles and Metadata; TUF FAQ on compromised root keys.

## Core separations

Freeze these boundaries:

`RETENTION_RECEIPT_SIGNATURE != ADMISSION_EXISTENCE`

`RETENTION_RECEIPT_REVOCATION != ADMISSION_ERASURE`

`REPLICA_COUNT != INDEPENDENT_DESTRUCTIVE_DOMAIN_COUNT`

`ARCHIVE_AVAILABILITY != EVIDENCE_VALIDITY`

`MONITOR_COMPROMISE != LOG_HISTORY_REWRITE`

`ONE_MONITOR_RECONSTRUCTION != EXHAUSTIVE_PREFIX_REPRODUCIBILITY`

A retention receipt is evidence that a specific retention service accepted and committed a specific admission envelope under a specific policy. It is not the authority to declare that the underlying admission never existed.

## Objects

### `AdmissionRetentionReceiptAuthorityV1`

Fields:
- `authority_lineage_id`
- `generation`
- `predecessor_digest`
- `threshold_policy`
- `authorized_receipt_key_ids`
- `authorized_retention_service_ids`
- `revocation_adjudication_policy_id`
- `recovery_root_id`
- `valid_from_frontier`
- `expiry_or_review_bound`
- `signature_set`

Properties:
- monotonic generation;
- same generation + different authenticated digest is equivocation;
- ordinary key rotation must preserve authority lineage and predecessor continuity;
- threshold compromise cannot self-bootstrap a trusted successor;
- authority replacement does not delete prior valid receipts.

### `AdmissionRetentionReceiptV2`

Fields:
- `admission_envelope_digest`
- `admission_lineage_id`
- `retention_service_id`
- `receipt_authority_generation`
- `retention_commit_id`
- `retention_commit_frontier`
- `storage_domain_attestation_digest`
- `retention_policy_id`
- `issued_at_evidence`
- `content_digest`
- `signature`

Required semantic statement:

> service S durably retained envelope E under policy P at frontier F using the storage/destructive-domain provenance described by attestation D.

The receipt MUST NOT assert that E is globally unique, semantically valid, or still independently survivable after later common-mode discoveries unless those properties are separately proven.

### `DestructiveDomainAttestationV1`

Fields:
- `logical_retention_service_id`
- `physical_storage_domains[]`
- `credential/control_domains[]`
- `operator/admin_domains[]`
- `cloud_accounts[]`
- `regions/failure_zones[]`
- `replication_software_or_firmware_domains[]`
- `key-management_domains[]`
- `backup/root-of-delete domains[]`
- `shared_upstream_dependencies[]`
- `attestation_generation`
- `predecessor_digest`
- `evidence_refs[]`
- `attester_id`
- `signature_set`

Independence is evaluated over destructive capability, not network endpoint diversity.

Two replicas are **not independent** if a single credential, cloud account, operator role, KMS authority, replication controller, deletion API, backup root, or shared administrative automation can destroy or rewrite both.

### `RetentionIndependenceAssessmentV1`

Fields:
- `assessment_generation`
- `receipt_set_digest`
- `domain_attestation_digests[]`
- `independent_destructive_domain_count`
- `shared_dependency_classes[]`
- `required_threshold`
- `result`
- `assessor_policy_id`
- `signature_set`

Results:
- `INDEPENDENCE_PROVEN_WITHIN_DECLARED_MODEL`
- `INDEPENDENCE_INSUFFICIENT`
- `INDEPENDENCE_UNKNOWN`
- `COMMON_MODE_COMPROMISE_DISCOVERED`

## Receipt lifecycle

### Issuance

A receipt may be issued only after the retention service has durably committed the exact admission envelope and can later retrieve bytes or a content-addressed equivalent sufficient to reconstruct the envelope.

A receipt created before durable retention is invalid. `RECEIPT_BEFORE_RETENTION` is a protocol violation.

### Supersession

A newer receipt may supersede operational details such as storage location, key, or service implementation while preserving the same admission-envelope identity. Supersession creates a new append-only statement; it does not mutate or remove the previous receipt.

`NEW_RECEIPT != OLD_RECEIPT_ERASED`

### Revocation

Receipt-key compromise, service fraud, or provenance falsification can revoke **current reliance on that receipt**. Revocation MUST NOT assert that the admission envelope never existed if another retained copy or independently authenticated historical evidence proves it did.

Freeze:

`RECEIPT_RELIANCE_REVOKED != ADMISSION_EXISTENCE_REVOKED`

The historical receipt remains part of evidence history with status metadata indicating why it is no longer sufficient for current reliance.

### Authority compromise

If the receipt-authority threshold is compromised:
- new receipts under the compromised lineage cannot restore trust by self-signed key rotation;
- already retained receipts are re-appraised according to compromise interval and independent evidence;
- recovery uses a separately trusted recovery root or explicit new-lineage/out-of-band rebootstrap;
- the compromised authority cannot command deletion of independent retained admission envelopes.

## Destructive-domain independence rules

### Denominator

Define an authenticated `RetentionDomainRegistryV1` listing required retention services and their declared destructive-domain provenance. A service cannot disappear from the survivability denominator merely because it is offline, renamed, deleted from service discovery, or moved to another endpoint.

`SERVICE_TIMEOUT != SERVICE_RETIREMENT`

Retirement requires:
- authenticated registry transition;
- final retention frontier;
- migration/survival proof for still-live admission envelopes;
- no unresolved retention obligations assigned exclusively to the retiring domain.

### Common-mode discovery

Late discovery that two nominally independent services shared a destructive dependency reopens **current survivability reliance**.

Example:

`R1(AWS acct X, KMS K) + R2(another region, same acct X, same KMS K)`

must not count as two independent destructive domains merely because regions differ.

If the previous assessment counted them separately, append:

`SURVIVABILITY_PROVEN(g7) -> COMMON_MODE_DISCOVERED(g8) -> CURRENT_SURVIVABILITY_REAPPRAISED(g9)`

Historical receipts remain unchanged.

### Required assurance vector

For critical admissions, independence assessment should expose at least:
- delete/control independence;
- signing/key-management independence;
- operator/account independence;
- geographic/failure-zone diversity;
- software/firmware/common-implementation diversity;
- network/provider diversity;
- backup/restore-root independence.

A deployment may meet a threshold on some dimensions and fail others; the result must not be collapsed into a bare replica count.

## Omission evidence monitor authority

### Monitor is not semantic authority

The monitor's role is to perform deterministic reconstruction and emit reproducible evidence. It MUST NOT have unilateral authority to define the canonical event predicate, log checkpoint trust root, retention denominator, or compromise policy.

Freeze:

`MONITOR_RESULT != CANONICAL_TRUTH_BY_AUTHORITY`

A valid omission proof depends on independently versioned inputs:
- canonical predicate/schema generation;
- trusted log/checkpoint lineage;
- complete authenticated prefix boundary;
- retained obligation/admission evidence;
- authenticated deadline/time evidence;
- deterministic reconstruction manifest.

### `ExhaustivePrefixReconstructionManifestV1`

Fields:
- `log_lineage_id`
- `checkpoint_digest`
- `checkpoint_size/frontier`
- `entry_count`
- ordered chunk/segment digests;
- canonical serialization version;
- canonical predicate id + digest;
- parser/schema version;
- reconstruction tool/reference algorithm id;
- resulting Merkle root;
- obligation/admission target digest;
- match count;
- monitor id;
- monitor signature;
- optional independent verifier receipts.

A reconstruction is acceptable only if another implementation can obtain the same authenticated prefix bytes, rebuild the same root, run the frozen predicate, and obtain the same match count.

## Archive/monitor loss survivability

### Loss of one monitor

A monitor disappearing does not invalidate an omission proof if the proof's inputs remain independently reconstructible from:
- the canonical log/transparency service;
- one or more independent archives retaining the exact prefix/chunks;
- retained signed checkpoint and consistency evidence;
- frozen predicate/parser artifacts.

If the original monitor held the only copy of necessary prefix bytes and the source log no longer serves them, the prior proof remains historical evidence but **current reproducibility is lost**:

`OMISSION_PROOF_HISTORICALLY_ISSUED_BUT_CURRENTLY_NONREPRODUCIBLE`.

That state is weaker than a reproducible positive omission proof.

### Archive disappearance

For a prefix to satisfy critical survivability, store content-addressed chunks plus reconstruction manifest across a policy-defined number of independent destructive domains.

A second archive is useful only if independent under `RetentionIndependenceAssessmentV1`.

### Monitor compromise after proof issuance

Late monitor compromise triggers re-appraisal, not history rewrite.

If the proof can be independently reproduced from authenticated prefix bytes and frozen algorithms, monitor compromise does not by itself invalidate the semantic result. The monitor signature becomes merely one historical transport/attestation layer.

If the proof depended on monitor-private data, non-public parser behavior, mutable query semantics, or a prefix unavailable elsewhere, current reliance becomes `OMISSION_PROOF_REAPPRAISAL_UNKNOWN`.

This creates a strong design goal:

`REPRODUCIBLE_PROOF > TRUSTED_MONITOR_ASSERTION`

### Archive compromise after proof issuance

A compromised archive cannot invalidate bytes already verified against a retained signed checkpoint/Merkle root unless the checkpoint authority itself is also compromised within the relevant interval. Corrupted archive bytes simply fail root reconstruction.

If every surviving archive is in one compromised destructive domain and the canonical source no longer serves the prefix, current reproducibility becomes unknown even though historical receipts remain.

## Positive semantic absence rule

Retain the previous formula:

`PROVABLE_OMISSION = VALID_RETAINED_OBLIGATION + DEADLINE_PROVEN_ELAPSED + AUTHENTICATED_STATE_AFTER_DEADLINE + POSITIVE_NON_PUBLICATION_EVIDENCE`

For dense append-only logs, `POSITIVE_NON_PUBLICATION_EVIDENCE` requires:

1. authenticated checkpoint after deadline;
2. complete retrieval of all entries in that checkpoint prefix;
3. byte/content integrity sufficient to reconstruct the checkpoint root;
4. frozen canonical parser/predicate;
5. exhaustive evaluation showing zero target matches;
6. a reconstruction manifest retained independently enough to remain reproducible.

`SEARCH_RETURNED_ZERO != EXHAUSTIVE_PREFIX_ZERO`

## Fraud / contradiction classes

1. `RECEIPT_BEFORE_DURABLE_RETENTION`
2. `RECEIPT_AUTHORITY_ROLLBACK`
3. `RECEIPT_AUTHORITY_EQUIVOCATION`
4. `RECEIPT_SELF_ERASURE_ATTEMPT`
5. `RECEIPT_REVOCATION_USED_AS_ADMISSION_ERASURE`
6. `RETENTION_SERVICE_SILENT_DENOMINATOR_REMOVAL`
7. `ENDPOINT_ROTATION_MISCOUNTED_AS_NEW_DOMAIN`
8. `COMMON_CREDENTIAL_MISCOUNTED_AS_INDEPENDENCE`
9. `COMMON_KMS_MISCOUNTED_AS_INDEPENDENCE`
10. `COMMON_OPERATOR_MISCOUNTED_AS_INDEPENDENCE`
11. `COMMON_DELETE_ROOT_MISCOUNTED_AS_INDEPENDENCE`
12. `PROVENANCE_ATTESTATION_ROLLBACK`
13. `PROVENANCE_ATTESTATION_EQUIVOCATION`
14. `MONITOR_PRIVATE_PREDICATE`
15. `MONITOR_PRIVATE_PREFIX`
16. `ARCHIVE_PREFIX_ROOT_MISMATCH`
17. `INCOMPLETE_PREFIX_CLAIMED_EXHAUSTIVE`
18. `SEARCH_ZERO_CLAIMED_AS_NONPUBLICATION_PROOF`
19. `LATE_MONITOR_COMPROMISE_NOT_REAPPRAISED`
20. `LATE_COMMON_MODE_DISCOVERY_NOT_REAPPRAISED`

## RED-first executable matrix (48 cases)

### Receipt authority lifecycle (1-12)
1. valid authority generation issues receipt after durable retention -> accept.
2. receipt before durable retention -> reject.
3. lower authority generation -> rollback reject.
4. same generation/different authority digest -> equivocation.
5. ordinary key rotation with valid predecessor continuity -> accept.
6. rotation missing predecessor authorization -> reject.
7. compromised authority self-installs successor -> reject.
8. separately trusted recovery root installs successor -> accept under recovery policy.
9. superseding receipt preserves old receipt history -> accept.
10. revocation marks current receipt reliance invalid but admission existence retained -> accept semantics.
11. revocation tries to delete all historical receipt evidence -> reject.
12. receipt for wrong admission-envelope digest -> reject.

### Destructive-domain provenance (13-24)
13. two services, separate accounts/operators/KMS/delete roots -> count two within declared model.
14. two regions, same cloud account and delete root -> count one destructive domain.
15. different endpoints, same credential -> count one.
16. different providers, shared central deletion automation -> shared destructive dependency recorded.
17. endpoint/key rotation only -> no independence increment.
18. late shared-KMS discovery -> reopen current survivability assessment.
19. old receipts remain historical after common-mode re-appraisal.
20. service timeout -> denominator unchanged.
21. service retirement without final survival proof -> reject registry transition.
22. authenticated retirement with migration/survival proof -> accept.
23. provenance generation rollback -> reject.
24. same provenance generation/different digest -> equivocation.

### Exhaustive-prefix proof (25-36)
25. full prefix + matching root + zero canonical matches -> positive absence evidence.
26. one omitted leaf -> root mismatch or incomplete-prefix failure.
27. query/search returns zero without exhaustive retrieval -> UNKNOWN.
28. timeout -> UNKNOWN.
29. 404 -> UNKNOWN.
30. parser/predicate digest differs from frozen contract -> reject proof.
31. same prefix reconstructed independently -> same root/match count.
32. prefix chunks reordered -> reconstruction failure.
33. tampered archive chunk -> root mismatch.
34. checkpoint before deadline -> insufficient for omission.
35. obligation/admission digest differs -> reject.
36. canonical predicate finds one matching publication -> omission disproven.

### Monitor/archive survivability and re-appraisal (37-48)
37. original monitor lost; independent archive + checkpoint reconstruct proof -> current reliance survives.
38. original monitor lost; canonical log still serves complete prefix -> reconstruct and survive.
39. original monitor held only prefix copy and source no longer serves -> historical proof nonreproducible/unknown for current reliance.
40. one archive lost, another independent archive survives -> reconstruct.
41. two archives share same destructive root and that root is lost -> no false two-domain survivability claim.
42. monitor later compromised; proof independently reproducible -> semantic result survives monitor compromise.
43. monitor later compromised; proof used private mutable predicate -> current reliance unknown.
44. archive later compromised; bytes fail retained checkpoint root -> reject corrupted bytes.
45. archive later compromised; independently archived bytes reproduce root -> rely on reproduced evidence.
46. late checkpoint-authority compromise overlaps proof interval -> re-appraise dependent proof.
47. crash after archive commit before local receipt persistence -> recover receipt idempotently from committed retention record.
48. crash after receipt persistence before local state advance -> replay exact receipt; no duplicate admission or new deadline.

## Decisions

1. Retention receipt authorities authenticate retention facts; they do not own admission existence.
2. Receipt revocation changes current reliance, never retroactively erases independently proven admission existence.
3. Critical survivability is measured over authenticated destructive-domain provenance, not endpoint/replica counts.
4. Independence claims are versioned, evidence-backed, and re-appraisable when shared dependencies are discovered later.
5. Omission monitors are deterministic evidence producers, not semantic/root authorities.
6. Critical exhaustive-prefix proofs must be reproducible from retained authenticated inputs without trusting the original monitor's private state.
7. Monitor/archive loss weakens current reproducibility only when the exact authenticated inputs can no longer be reconstructed.
8. Late compromise produces append-only re-appraisal generations; historical receipts/proofs are not rewritten.

## Implementation direction

When executable work resumes, prefer tests and data structures in this order:

1. authority-generation and receipt lifecycle state machine;
2. destructive-domain registry/attestation + threshold evaluator;
3. content-addressed exhaustive-prefix manifest and deterministic reconstruction verifier;
4. re-appraisal state machine for common-mode/monitor/archive compromise;
5. RED matrix above before production integration.

Do not implement these freezes on LAB-086 until LAB-086's retained exact gate is available and clean.

## Next research fallback

If exact source execution is still unavailable after this freeze, investigate **retention-domain attestation authority compromise / hidden common-control discovery incentives and challenge protocol / erasure-coded archive survivability versus independently verifiable full-prefix reconstruction / long-term cryptographic agility for archived omission evidence**.
