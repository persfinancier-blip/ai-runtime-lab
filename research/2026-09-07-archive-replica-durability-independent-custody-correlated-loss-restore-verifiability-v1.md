# Archive replica durability / independent custody / correlated-loss / restore-verifiability v1

Status: **ARCHIVE_REPLICA_DURABILITY_INDEPENDENT_CUSTODY_CORRELATED_LOSS_RESTORE_VERIFIABILITY_V1_FROZEN**

Date: 2026-09-07

Related durable chain: LAB-093 / #178; follows `HISTORICAL_TRUST_BUNDLE_CAPTURE_ATOMICITY_PRE_DECOMMISSION_FREEZE_COMPLETENESS_PROOF_V1_FROZEN`.

## Question

When may destructive GC, provider/key/log/account decommission, or other irreversible state reduction rely on a sealed historical-evidence archive?

A complete archive is not sufficient if every copy can be destroyed, rolled back, made unreadable by one administrative action, or found to be unrestorable only after the primary authority has already been deleted. This note freezes the durability/custody contract that must sit between archive-completeness closure and destructive GC.

## Executive decision

`FINAL_ARCHIVE_CLOSED` proves semantic completeness and causal closure of one archive generation. It does **not** prove durable survivability.

Introduce a distinct verdict:

`ARCHIVE_DURABILITY_CLOSED`

It requires all of the following:

1. immutable replica identity and exact sealed-root agreement;
2. enough independent custody/failure domains to survive the declared threat model;
3. encryption/decryption key survivability that is independent from any single data replica or administrator;
4. anti-rollback and anti-equivocation checks across replicas;
5. observed full restore of the authoritative bytes into an isolated verifier;
6. successful re-verification of the restored archive's seal, completeness proof and historical trust material;
7. a freshness-bounded restore drill, not merely a provider statement that the object exists;
8. no unresolved `UNKNOWN` for any required replica/custody/key domain.

Destructive GC may depend on archived evidence only when both are true:

`FINAL_ARCHIVE_CLOSED && ARCHIVE_DURABILITY_CLOSED`

and the durability closure remains within its declared drill/renewal validity interval.

## Core invariants

### D1. Replication is not custody independence

Two copies in one account, one organization root, one KMS administrative plane, one provider control plane, or one shared delete/retention authority count as correlated copies for the corresponding threat.

Physical placement is only one failure dimension. Independence must be stated separately for:

- storage hardware / zone / region;
- provider control plane;
- tenant/account/organization root;
- IAM/administrator authority;
- encryption/decryption key custody;
- billing/account-lifecycle authority;
- retention/WORM policy administration;
- software/adapter implementation;
- legal/commercial/provider shutdown exposure.

A topology can be independent for disk loss yet fully correlated for credential compromise.

### D2. WORM is necessary for rollback resistance but not sufficient for durability

Provider immutability primitives are useful donors:

- Amazon S3 Object Lock protects specific object versions; Object Lock requires versioning, and protected versions cannot be overwritten/deleted during retention or legal hold. S3 replication can asynchronously copy locked objects and retention metadata to other Object-Lock-enabled buckets.
- AWS Backup Vault Lock compliance mode becomes immutable after its grace period and blocks deletion/lifecycle shortening even by the account root user while retention applies.
- Google Cloud Bucket Lock can permanently prevent reducing/removing a bucket retention policy.
- Azure immutable Blob Storage provides time-based and legal-hold WORM semantics.

These mechanisms prevent a class of mutation/deletion. None by itself proves that every required archive object exists in an independent custody domain, that encryption keys remain recoverable, or that a full historical verifier can restore and validate the bytes.

### D3. Same-provider cross-region copies are not automatically independent

Cross-region replication reduces regional data-loss risk. It does not eliminate provider-wide control-plane, account-root, policy, billing, KMS, software or legal correlated failures.

The archive durability manifest must therefore declare which failure domains each replica is independent from. A design may deliberately accept one provider-wide correlated risk, but then it cannot claim survivability against that risk.

### D4. Independent administration is material

At least one required replica for a high-assurance destructive-GC claim must not be deletable or retention-shortenable by the same single principal set that controls the operational source archive.

Acceptable mechanisms include, depending on threat model:

- separately administered account/tenant with explicit cross-account restore path;
- compliance/WORM configuration that the ordinary account administrator cannot bypass after activation;
- multi-party approval for recovery/admin mutation;
- offline or separately governed custody whose release requires independent authorization.

AWS Backup logically air-gapped vaults are a useful donor because they combine compliance-mode Vault Lock with cross-account sharing/recovery and optional multi-party approval. This is evidence that administrative separation is a distinct mechanism from mere storage replication.

### D5. Data durability without key durability is not archive durability

For every encrypted authoritative object there must be a `KeyRecoveryBindingV1` proving how decryption survives loss of any one declared key/admin domain.

Forbidden closure patterns include:

- all replicas encrypted only under one deletable KMS key;
- replica in a second account but CMK controlled solely by the first account;
- offline encrypted media whose only unwrap secret lives in the decommissioned provider;
- archived trust bundle whose historical signing/status evidence can be read only through a key scheduled for destruction.

Key survival must not weaken confidentiality: independent custody may use threshold/wrapped recovery material rather than plaintext key duplication.

### D6. Replica identity is immutable and content-addressed

Define:

`ArchiveReplicaManifestV1`

Minimum fields:

- `archive_campaign_id`;
- `archive_generation`;
- `archive_seal_digest`;
- `completeness_proof_digest`;
- `replica_id`;
- `replica_provider`;
- `replica_account_or_tenant_id`;
- `region_or_physical_domain`;
- `storage_object_ids_and_version_ids`;
- `object_root_digest`;
- `retention_mode` and immutable retention frontier;
- `encryption_scheme`;
- `key_recovery_binding_digest`;
- `custody_domain_set`;
- `administrative_authority_digest`;
- `created_at_anchor`;
- `predecessor_replica_manifest_digest`;
- `verifier_policy_digest`.

Replica path names, mutable tags, current object aliases and provider console labels are not identity.

### D7. Every authoritative replica must commit to the same sealed root

A replica can be byte-different only if the representation is explicitly canonicalized and independently proves equivalence to the authoritative sealed byte set. The preferred v1 route is exact-byte replication.

`archive_seal_digest`, `object_root_digest`, and all authoritative object digests must be compared across custody domains.

A copy with a different root is not a degraded replica; it is `CONTRADICTORY_REPLICA` until independently reconciled.

### D8. Anti-rollback requires an external monotonic witness

A storage API returning an older but authentic immutable version can still cause rollback if the verifier has forgotten the newest accepted archive generation.

Introduce:

`ArchiveGenerationWitnessV1`

It binds:

- archive lineage id;
- highest accepted archive generation;
- seal digest;
- predecessor digest;
- witness epoch;
- independent signatures/checkpoints.

At least one monotonic witness must be outside the mutable authority of any single archive replica. Candidate mechanisms include threshold-signed append-only checkpoints, transparency-log inclusion, or separately administered monotonic state.

A replica claiming generation N while an authenticated witness proves N+1 is `STALE_ROLLBACK` even if N is itself authentic.

### D9. Anti-equivocation is a quorum/independent-witness property

An administrator/provider can potentially present two individually authentic roots for the same generation unless generation uniqueness is checked outside that single view.

For each archive generation, independently gathered replica manifests and external witnesses must agree on one seal/root.

Two valid manifests with the same `(archive_lineage_id, generation)` and different roots yield:

`ARCHIVE_EQUIVOCATION_PROVEN`

All destructive proofs depending on that lineage become stale until repaired through an additive superseding generation with explicit contradiction history.

### D10. Availability claims require restore, not HEAD/list

`GET`, `HEAD`, inventory listing, replication status, checksum metadata and provider durability statements are useful telemetry, not proof that the complete archive can be recovered and interpreted.

Define:

`ArchiveRestoreDrillV1`

A successful drill must:

1. select a replica without relying on the operational source copy;
2. obtain required decryption authority through the declared recovery path;
3. restore all authoritative archive bytes to an isolated scratch environment;
4. verify exact object digests and archive Merkle/root/seal;
5. run the frozen independent archive completeness verifier;
6. run the historical trust verifier without live-provider assumptions;
7. verify archive-generation witness/non-rollback state;
8. record all missing/extra/contradictory objects;
9. emit one authenticated result bound to replica manifest, verifier policy and drill time.

AWS Backup Restore Testing is a production donor for the principle that restore must be periodically exercised rather than inferred from backup-job success. Its documentation explicitly supports scheduled restore-test selection and post-restore validation windows.

### D11. Sampling/proof-of-retrievability cannot replace periodic full restore

Cryptographic proof-of-storage/retrievability protocols can cheaply detect many storage failures and are valuable between full drills. However, a proof over encoded blocks does not prove:

- decryption-key recovery;
- archive semantic completeness;
- historical schema/verifier availability;
- provider-independent restore permissions;
- executable interpretation of restored evidence.

Therefore v1 permits lightweight periodic possession/integrity challenges as an additional signal, but destructive GC must be backed by an observed full restore drill within policy freshness.

### D12. Erasure coding is a durability mechanism, not an independence declaration

Erasure coding across correlated domains can improve tolerance to disk/node loss. It does not provide independent administration, anti-rollback, or key survivability.

`k-of-n` fragments count toward closure only when the closure verifier proves that at least `k` fragments remain recoverable after removing every one declared failure domain. The same independence analysis applies to parity fragments as to full replicas.

### D13. Restore freshness is policy-bound

A restore that passed years ago cannot authorize present destructive GC after key rotation, replica migration, provider changes or archive renewal.

Define:

`RestoreFreshnessPolicyV1`

It sets maximum age and invalidation triggers. Immediate re-drill is required after any material change to:

- replica provider/account/region;
- retention policy;
- encryption/key recovery path;
- archive representation/root;
- historical verifier package;
- trust bundle renewal;
- custody principals;
- restore API/provider semantics.

### D14. Renewal must propagate atomically enough to preserve minimum survivability

When historical trust material is renewed or archive generation N+1 supersedes N, the system must not GC N while N+1 exists in only one fragile domain.

Introduce lifecycle states:

- `NEW_GENERATION_CREATED`
- `REPLICA_SET_INCOMPLETE`
- `REPLICA_SET_DURABLE`
- `RESTORE_VERIFIED`
- `GC_DEPENDENCY_ELIGIBLE`

Old-generation GC is forbidden until the successor reaches `GC_DEPENDENCY_ELIGIBLE` under the same declared threat model.

### D15. Correlated-loss analysis is explicit

Define `FailureDomainMatrixV1`. Rows are replicas/fragments/key shares/witnesses; columns are declared failures, for example:

- one disk/node;
- one AZ/datacenter;
- one region;
- one cloud provider;
- one tenant/account root compromise;
- one organization-level administrator compromise;
- one KMS key loss;
- one billing/account suspension;
- one archive software bug;
- one malicious archive builder;
- one transparency/witness service loss.

For each declared failure scenario the verifier must mechanically show that a sufficient restore set + key set + witness set remains.

"Three copies" is not a proof if all three fail in the same column.

## Required objects

### `ArchiveReplicaSetV1`

- lineage/generation;
- required minimum restore threshold;
- replica manifest digests;
- declared threat model/failure domains;
- key-recovery bindings;
- external generation witnesses;
- restore freshness policy;
- predecessor set digest.

### `ArchiveDurabilityProofV1`

- exact archive seal/completeness proof digests;
- independently fetched replica manifests;
- failure-domain matrix result;
- retention/WORM verification results;
- key-recovery viability proof;
- anti-rollback witness result;
- anti-equivocation result;
- latest successful full restore drill digest/time;
- verifier implementation/policy digest;
- verdict.

Verdicts:

- `CLOSED`
- `UNKNOWN_REPLICA`
- `UNKNOWN_CUSTODY`
- `UNKNOWN_KEY_RECOVERY`
- `UNKNOWN_RESTORE`
- `STALE_RESTORE`
- `CONTRADICTORY_REPLICA`
- `ROLLBACK_PROVEN`
- `EQUIVOCATION_PROVEN`
- `INSUFFICIENT_FAILURE_DOMAIN_INDEPENDENCE`

Only `CLOSED` may satisfy an archive durability dependency for destructive GC.

## Minimum v1 topology for high-assurance GC

The implementation should not hard-code a cloud vendor, but the default policy target is:

- at least 3 authoritative restore-capable copies or an equivalent independently verifiable erasure-coded set;
- at least 2 administrative custody domains;
- at least 2 geographic failure domains;
- at least one copy protected by non-bypassable/compliance WORM for the relevant retention period;
- at least one restore path that remains available if the primary operational account is unavailable;
- decryption/recovery authority that survives loss of any single declared key/admin domain;
- at least one external monotonic generation witness outside the primary archive account;
- a recent successful full restore + historical verification from a non-primary replica.

This is a policy baseline, not a universal theorem. A weaker threat model may choose less, but its proof must state the weaker survivability claim.

## Destructive GC gate

`ArchiveBackedDestructiveAuthorizationV1` may be issued only when all predicates hold:

1. source archival campaign: `FINAL_ARCHIVE_CLOSED`;
2. replica set: `ARCHIVE_DURABILITY_CLOSED`;
3. latest archive generation is proven against external witness;
4. no contradictory same-generation root exists;
5. latest full restore drill is within freshness policy;
6. no material topology/key/policy/provider change occurred since that drill;
7. retention horizon extends beyond the period in which historical verification may be required;
8. successor/renewal generation, if any, has itself reached `GC_DEPENDENCY_ELIGIBLE`;
9. required archive objects, verifier package and trust material are all included in the restore-verified set.

If any predicate is unknown, destructive GC is denied.

## Failure and recovery semantics

### Lost replica

If remaining replicas still satisfy the declared failure-domain matrix, durability becomes `DEGRADED_REPAIR_REQUIRED`; destructive GC is paused until redundancy is restored and a new durability proof is produced.

If the remaining set no longer meets the minimum restore threshold, verdict is `UNKNOWN_REPLICA` or `INSUFFICIENT_FAILURE_DOMAIN_INDEPENDENCE`; no destructive GC.

### Lost key share / unavailable KMS

Do not infer recoverability from encrypted-object existence. Exercise the alternate key-recovery path. If it cannot be demonstrated, verdict is `UNKNOWN_KEY_RECOVERY`.

### Replica mismatch

Do not auto-heal first. Preserve both observations, emit contradiction evidence, compare with external generation witness and independently authenticated predecessor chain, then repair additively. Silent overwrite destroys forensic evidence.

### Restore drill failure

A failed restore invalidates durability closure immediately for destructive-GC purposes. The failure may be operational/transient, but until a subsequent successful drill establishes the required semantics the state remains `UNKNOWN_RESTORE`.

### Provider/account decommission

Before decommissioning any custody domain, recompute the failure-domain matrix **as if that domain were already gone**, execute a restore drill through the surviving path, then create a successor durability proof. Decommission first / prove later is forbidden.

## Independent verifier requirements

The durability verifier must not rely solely on the archive writer/replicator's database. It must independently query/read each required custody domain and verify provider-origin version/retention evidence where available.

It must fail closed on:

- missing replica manifest;
- same-generation root mismatch;
- rollback relative to witness;
- unverifiable retention status;
- common administrator/key domain where policy demands independence;
- incomplete restore;
- missing frozen verifier/trust material;
- restore drill older than policy;
- provider/API semantics outside the frozen adapter-verifier mapping.

## RED-first matrix (80 cases)

### Replica identity and exact-root agreement (1-10)
1. Three replicas same exact root -> pass identity stage.
2. One object differs -> contradiction.
3. Same path but different provider version ID -> require manifest reconciliation.
4. Missing object -> fail.
5. Extra unauthoritative object -> report, do not alter authoritative root.
6. Mutable alias points to older version -> rollback detection.
7. Replica manifest digest mismatch -> fail.
8. Same generation, two seal digests -> equivocation proof.
9. Canonicalized-but-byte-different copy without equivalence proof -> fail.
10. Exact-byte restored copy with matching root -> pass.

### Custody/failure-domain independence (11-20)
11. Three copies, same account/root admin -> insufficient admin independence.
12. Two accounts, same org admin with delete authority over both -> correlated.
13. Cross-account copy with independent retention admin -> distinct custody.
14. Two regions, same provider/account -> geographic independence only.
15. Two providers, same locally stored credentials able to delete both -> credential-correlated.
16. Primary account unavailable, secondary restore succeeds -> pass corresponding failure row.
17. One AZ loss leaves threshold -> pass.
18. One region loss leaves threshold -> pass if declared.
19. Provider-wide loss leaves no threshold -> cannot claim provider-independent durability.
20. Failure-domain manifest omits shared KMS -> completeness failure.

### Immutability/rollback/equivocation (21-30)
21. Compliance WORM active on required version -> pass retention predicate.
22. Governance WORM with bypass principal in custody set -> not non-bypassable.
23. Retention expired before required evidence horizon -> fail.
24. Delete marker hides protected version -> version-specific restore still required.
25. Replication copies data but not expected retention metadata -> fail policy.
26. Authentic generation N returned while witness says N+1 -> rollback.
27. Witness unavailable -> UNKNOWN, not accept N.
28. Two witnesses conflict -> contradiction/escalated repair, no GC.
29. New replica seeded from stale N after N+1 accepted -> reject.
30. Silent repair overwrites contradictory root -> test must fail audit.

### Key durability (31-40)
31. All data under one destroyed CMK -> unrecoverable.
32. Independent wrapped recovery share reconstructs key -> pass.
33. Secondary account data encrypted with primary-only key -> correlated.
34. Key metadata exists but decrypt denied -> restore fails.
35. Threshold key recovery tolerates one custodian loss -> pass declared row.
36. Threshold requires all custodians -> no single-custodian-loss tolerance.
37. Key rotation without archived unwrap lineage -> fail historical restore.
38. Old archive bytes decrypt after current operational key deletion via archived recovery path -> pass.
39. Recovery secret stored inside same encrypted archive only -> circular/unusable.
40. Restore drill never exercises key recovery -> insufficient proof.

### Restore semantics (41-50)
41. HEAD/list succeeds but GET restore fails -> fail.
42. All bytes restore, seal matches -> continue.
43. Seal matches but completeness verifier package missing -> fail.
44. Completeness proof restores but historical trust verifier cannot execute -> fail.
45. Full isolated historical verification succeeds -> pass.
46. Restore relies on source operational account -> does not test independent path.
47. Random sampling passes but full restore has missing cold object -> fail.
48. Full restore passes but exceeds policy freshness after topology change -> stale.
49. Scheduled restore selects no eligible recovery point -> not a pass.
50. Restore succeeds but output is normalized rather than authoritative bytes -> fail.

### Erasure coding/replication threshold (51-60)
51. n=5,k=3 fragments across five independent domains, one lost -> pass threshold.
52. n=5,k=3 but three fragments in one failed domain -> matrix catches failure.
53. parity validates but decryption key lost -> fail.
54. fragment checksum metadata only, no reconstruction drill -> insufficient.
55. reconstructed root equals sealed root -> pass data stage.
56. reconstructed bytes differ despite provider checksums -> fail.
57. one fragment silently stale generation -> reject using generation binding.
58. mixed-generation fragments reconstruct something -> must reject lineage mismatch.
59. repair fragment produced from unverified stale replica -> reject.
60. repair from verified latest root then new drill -> pass.

### Renewal/migration/provider change (61-70)
61. N+1 exists only primary, N GC requested -> deny.
62. N+1 replica threshold complete but no restore drill -> deny.
63. N+1 restore verified -> N may become GC-eligible subject to retention.
64. provider migration with exact-root continuity and independent restore -> pass.
65. provider migration changes representation without equivalence proof -> fail.
66. KMS migration without new recovery drill -> stale durability proof.
67. retention-policy change -> invalidate drill freshness.
68. historical trust renewal propagated to only one replica -> deny old-generation GC.
69. verifier-policy upgrade without archived old verifier semantics -> fail historical portability.
70. decommission target removed before recomputing matrix -> protocol violation.

### Crash/recovery/fraud (71-80)
71. crash after first replica copy -> resume incomplete; no closure.
72. crash after all copies before durability proof -> recompute from independent reads.
73. crash after proof before GC -> re-check proof freshness/witness before GC.
74. archive builder lies that secondary exists -> independent read fails.
75. secondary admin serves stale authentic version -> witness detects rollback.
76. provider serves different roots to two verifiers -> equivocation proof.
77. restore tester reports success without object-root verification -> reject tester evidence.
78. administrator removes custody independence after last drill -> invalidate closure.
79. later-discovered shared failure domain -> mark dependent GC authorizations historically suspect/stale and preserve contradiction record.
80. all current predicates independently reverified after recovery -> new additive durability proof closes.

## Donor evidence / boundaries

1. AWS S3 Object Lock, official documentation: version-specific retention/legal hold; protected versions are immutable for the configured horizon; Object Lock works with versioning. <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html>
2. AWS S3 Object Lock + Replication, official documentation: locked objects and retention metadata can be asynchronously replicated to Object-Lock-enabled destination buckets. <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html>
3. AWS Backup Vault Lock, official documentation: compliance mode becomes immutable after grace time and denies deletion/lifecycle changes even to root while retention applies. <https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html>
4. AWS Backup logically air-gapped vault, official documentation: compliance-mode lock plus cross-account restore/sharing and optional multi-party approval. <https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html>
5. AWS Backup Restore Testing, official documentation: scheduled recovery-point restore testing with an explicit validation window. <https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html>
6. Google Cloud Bucket Lock, official documentation: locked retention policy cannot be reduced or removed. <https://docs.cloud.google.com/storage/docs/bucket-lock>
7. Azure Immutable Storage for Blob Data, official documentation: time-based and legal-hold WORM semantics. <https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview>

### Negative boundaries from donors

- Asynchronous replication is not instantaneous causal closure.
- WORM protects retained versions; it does not prove a second independent custody/admin/key domain exists.
- Cross-account recovery is useful independence machinery, but accounts under one common compromise domain may remain correlated.
- Provider restore-testing success must still be followed by application-specific archive seal/completeness/historical-trust verification.
- Provider durability percentages or existence checks are not substitutes for a successful exact-byte restore.

## Frozen implementation order

1. Add `ArchiveReplicaManifestV1`, `ArchiveReplicaSetV1`, `FailureDomainMatrixV1` and `KeyRecoveryBindingV1` schemas/tests.
2. Build independent replica reader/verifier adapters; never consume only replicator-local state.
3. Add external `ArchiveGenerationWitnessV1` and same-generation equivocation detector.
4. Implement isolated full `ArchiveRestoreDrillV1` with exact-byte root + completeness + historical-trust replay.
5. Implement `ArchiveDurabilityProofV1` with explicit UNKNOWN states.
6. Gate destructive GC on both archive-completeness and current durability proof.
7. Add renewal/topology-change invalidation and successor-generation sequencing.
8. Execute the full 80-case RED matrix before integrating production GC dependencies.

## Next distinct research question

**Archive restore verifier reproducibility / hermetic verifier supply-chain / executable-obsolescence semantics.**

Even if bytes, roots, keys and custody survive, a historical archive can become practically unverifiable if its verifier depends on vanished package registries, mutable container tags, unsupported runtimes, CPU/ABI assumptions or compromised build tooling. Define how to archive/reproduce a minimal hermetic verifier, bind its source/build/dependency provenance to the archive generation, migrate verifier implementations without changing historical semantics, and distinguish `bytes_retrievable` from `evidence_verifiable` over multi-decade retention.
