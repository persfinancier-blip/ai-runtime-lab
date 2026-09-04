# Application idempotency archive object identity / availability / authenticated retrieval V1

Status: `APPLICATION_IDEMPOTENCY_ARCHIVE_OBJECT_RETRIEVAL_V1_FROZEN`

Date: 2026-09-05

Scope: LAB-093 / #178 follow-up to `APPLICATION_IDEMPOTENCY_CONSUMED_KEY_ARCHIVAL_CHECKPOINT_V1_FROZEN`.

## Question

How can a broker safely retrieve compacted application-idempotency history from online, cold, mirrored, or temporarily unavailable storage without allowing an unavailable, substituted, rolled-back, or partially queried archive epoch to become a false `MISS` and authorize a duplicate side effect?

## Executive decision

V1 freezes the following safety boundary:

1. **Archive locators are hints, never authority.** Bucket/key, path, URL, storage class, replica name, mount point, and provider object version are retrieval coordinates. The authority identity is an authenticated manifest entry committed into the existing global provenance chain.
2. **Every sealed epoch has an immutable content identity.** The manifest binds the canonical archive format/version, logical history identity, epoch id, exact byte length, cryptographic object digest, exact record count/range, exact-record root, and parent checkpoint.
3. **A successful read is not trusted until re-authenticated.** Bytes from any copy must match the authoritative length/digest and the archive's internal canonical identity before records or membership results are accepted.
4. **A negative answer is complete only if all authority-required history is covered.** Active exact state plus every sealed epoch in the authenticated manifest must be queried, or an authenticated exact global index that provably covers those epochs must answer. One missing/unavailable required epoch converts the result to `ARCHIVE_INCOMPLETE` / `PENDING_ARCHIVE_LOOKUP`, never `MISS`.
5. **Multi-copy improves availability, not trust.** Any replica may satisfy retrieval if its bytes authenticate to the same authority identity. Replica agreement is not required for correctness, and two matching unauthenticated replicas do not override the manifest.
6. **Cold restore is an availability state, not absence.** An archived object that exists but requires restore yields `PENDING_ARCHIVE_RESTORE`; the broker does not admit a fresh key while the required epoch is unavailable.
7. **Restoring an exact copy is not a new authority event; changing representation is.** A byte-identical copy may be recreated at a new locator after digest verification. A semantically equivalent re-encoding has a different object identity and requires a separately authenticated migration/repack transition while the old exact history remains provably available.
8. **Startup/delegation cannot silently skip unavailable epochs.** Any mode that may authorize new effects must establish complete authenticated historical coverage under its declared policy. If that cannot be established, worker effect admission stays closed. Existing exact recovery/result reads may proceed where their required evidence is independently available.

This contract deliberately prefers availability loss over duplicate side effects.

## Donor mechanisms / primary evidence

### Content identity versus storage location

Amazon S3 Versioning demonstrates why locator and object identity must be separate: one object key can have multiple versions, and a specific historical version is retrieved by version ID rather than by the key alone. S3 also exposes checksums/metadata for object-integrity verification. These are useful storage mechanisms, but V1 does not elevate a provider key or version ID into application authority; provider identifiers remain locators bound beneath the lab's authenticated manifest.

Primary references:

- AWS, *How S3 Versioning works*: https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html
- AWS, *Retrieving object versions from a versioning-enabled bucket*: https://docs.aws.amazon.com/AmazonS3/latest/userguide/RetrievingObjectVersions.html
- AWS, *ObjectVersion API*: https://docs.aws.amazon.com/AmazonS3/latest/API/API_ObjectVersion.html

### Consistent authenticated snapshots and rollback resistance

The Update Framework separates signed authority metadata from target-file retrieval. Snapshot metadata commits to versions/hashes so a client cannot safely combine files from different repository states; clients also reject metadata older than state already seen. This is the relevant donor mechanism for the archive manifest: one authenticated manifest defines the complete epoch set and object identities for a snapshot, while storage locations merely provide bytes.

Primary references:

- TUF, *Roles and metadata*: https://theupdateframework.io/docs/metadata/
- TUF, *Security*: https://theupdateframework.io/docs/security/

### Append-only checkpoint continuity

RFC 6962 defines Merkle consistency proofs for demonstrating that a later tree extends an earlier committed tree without rewriting prior inputs. The lab already uses a parent-linked global provenance chain rather than Certificate Transparency itself; the donor lesson is that a compact root is useful only when continuity from previously trusted state is also checked.

Primary reference:

- RFC 6962, *Certificate Transparency*, sections 2.1.2 and 4.4: https://www.rfc-editor.org/rfc/rfc6962

## Threat model

V1 assumes any archive transport/storage surface may independently experience:

- stale reads;
- missing objects;
- delete markers / lifecycle movement;
- temporary restore requirements;
- locator rebinding;
- partial/corrupt bytes;
- rollback to a valid older object;
- malicious substitution under the same path;
- replica divergence;
- incomplete listings;
- timeout after bytes are delivered;
- local cache rollback;
- operator copy/restore mistakes.

The archive provider is therefore a byte transport/availability service. It is not trusted to define which epochs exist, which object is authoritative, or whether a negative lookup is complete.

## Canonical authority model

### 1. Archive manifest checkpoint

A canonical manifest is committed by a parent-linked transition in the existing global provenance chain. At minimum it binds:

- `logical_history_id`;
- application-idempotency registry schema/version;
- archive format/version;
- manifest generation / checkpoint id;
- parent provenance digest;
- ordered sealed epoch set;
- for each epoch, the authority object identity described below;
- cumulative exact record count/accounting;
- optional authenticated global exact-index identity;
- optional approximate-summary identities;
- policy version governing availability mode and replica/restore behavior.

The manifest set is authoritative. Storage listing results are not.

### 2. Immutable archive object identity

For each sealed epoch, authority commits at least:

- `archive_epoch_id`;
- `logical_history_id`;
- canonical archive encoding/version;
- exact encoded byte length;
- cryptographic digest of exact encoded bytes (V1: SHA-256 or the repository's shared stronger canonical digest profile if frozen elsewhere before implementation);
- exact canonical record count;
- canonical first/last ordering key or another unambiguous range descriptor;
- exact-record Merkle/root digest when present;
- previous archive checkpoint/epoch binding;
- optional summary/index digest;
- seal provenance transition digest.

`locator`, `bucket`, `object_key`, `version_id`, `storage_class`, and `replica_id` are explicitly excluded from authority identity. They may be authenticated as operational metadata, but changing a locator cannot change what bytes are authoritative.

### 3. Retrieval locator set

A broker-owned locator registry may map one authoritative object identity to one or more retrieval candidates:

`authority_object_id -> [locator_1, locator_2, ...]`

Locator changes are availability/configuration events. They MUST NOT be able to:

- replace the authority digest;
- remove a required epoch from manifest coverage;
- convert failed retrieval to negative membership;
- rewrite logical history identity;
- claim a new exact record count/range.

If locator configuration itself is security-sensitive in deployment, it may be authenticated by a separate operations policy, but it remains subordinate to content authority.

## Authenticated retrieval protocol

For an authority-required epoch `E`:

1. Load the already authenticated manifest snapshot and exact `E` object identity.
2. Resolve allowed retrieval locators under current operations policy. Do not discover authority by listing storage.
3. Fetch a candidate object from one locator. A provider-specific version ID MAY pin the fetch but is not sufficient authentication.
4. Require the exact expected byte length when known before parsing.
5. Hash the exact bytes and require equality with the manifest's object digest.
6. Parse only under the manifest-bound canonical archive format/version.
7. Require internal epoch/logical-history/count/range/root fields to match the authority manifest.
8. If an exact-record Merkle/root is part of the format, recompute/verify it.
9. Only after steps 4-8 may an exact key lookup or index proof be accepted.
10. Cache the authenticated object only under `(authority_object_id, manifest_checkpoint)`; cache contents are re-hashed on first use after restart unless a separately authenticated local integrity layer exists.
11. On timeout/UNKNOWN at any stage, classify retrieval as unavailable/unknown. Do not infer absence.

A second replica can be tried after any locator failure. It is safe because acceptance is based on the same immutable authority identity.

## Complete negative lookup

A new application key may reach `MISS` only from a *complete absence proof* over one stable authority snapshot.

The minimum complete set is:

1. current active exact registry snapshot is authenticated and contains no key;
2. current manifest checkpoint is authenticated and stable;
3. every sealed epoch listed by that manifest is covered by either:
   - authenticated exact lookup of that epoch; or
   - an authenticated exact global index whose manifest binding proves complete coverage of that epoch;
4. all approximate summaries used only as accelerators are authenticated and have declared coverage consistent with the manifest;
5. no required epoch is `UNAVAILABLE`, `RESTORING`, `UNKNOWN`, corrupt, or omitted;
6. the manifest/provenance head and active exact snapshot are revalidated immediately before final `BOUND` admission.

An exact global index may accelerate negative proof only if its own immutable identity and complete epoch coverage are authenticated by the same manifest. A storage-provider object listing, database cache, Bloom filter positive/negative outside its frozen one-sided contract, or 'all replicas returned 404' is not a complete absence proof.

### Query result classes

V1 freezes these external classifications:

- `ACTIVE_MATCH`
- `ARCHIVE_MATCH_SAME_OPERATION`
- `ARCHIVE_KEY_CONFLICT`
- `AUTHENTICATED_ABSENT`
- `PENDING_ARCHIVE_LOOKUP`
- `PENDING_ARCHIVE_RESTORE`
- `ARCHIVE_UNAVAILABLE`
- `ARCHIVE_INTEGRITY_FAILURE`
- `ARCHIVE_ROLLBACK_OR_MANIFEST_MISMATCH`
- `STALE_QUERY_SNAPSHOT`

Only `AUTHENTICATED_ABSENT`, followed by final broker revalidation/admission, can authorize first binding of a new key.

## Multi-copy and remote/cold storage

### Replicas

Copies are interchangeable only after authentication to the same object identity.

- One good authenticated copy is sufficient.
- Replica quorum is not required for correctness.
- Matching replica names/version IDs are not sufficient.
- Divergent copy bytes: reject the bad copy and try another; record integrity telemetry.
- If no copy authenticates, the epoch is unavailable/integrity-failed and new effect admission that needs it remains closed.

### Cold archive restore

If a required object is in a storage class needing restore:

1. retrieval classifier returns `PENDING_ARCHIVE_RESTORE`;
2. a broker-admin/operations path may request restore;
3. no application effect is authorized by the restore request itself;
4. once bytes become retrievable, the full digest/identity protocol runs normally;
5. provider restore metadata is availability evidence only, not historical authority.

V1 does not require worker sessions to remain live while a cold restore occurs. A later fresh broker cycle may retry the same application request under normal session/idempotency rules.

## Archive loss / restore / rebuild semantics

### Exact byte-for-byte restoration

If an authenticated object disappears from every current locator but exact bytes are recovered from backup/offline media:

- verify exact length and authority digest before installation;
- install as another locator/copy;
- re-fetch and authenticate if storage semantics require it;
- no new archive-history authority transition is needed merely because identical bytes moved.

The manifest remains unchanged because the authority object identity did not change.

### Semantically equivalent rebuild

Re-serializing the same logical records into different bytes changes object identity. V1 forbids silently substituting such a rebuild under the old epoch identity.

A future repack/migration protocol, if implemented, MUST:

1. start from authenticated exact old history;
2. produce a canonical new object;
3. prove exact record-set equivalence under a deterministic comparison/rebuild algorithm;
4. append a parent-linked authenticated migration transition binding old and new identities;
5. re-authenticate the new manifest/object before old-copy reclamation;
6. preserve permanent consumed-key semantics throughout.

Until that protocol has executable RED/GREEN, V1 treats loss of all exact copies with no byte-identical recovery source as **availability-fatal for affected historical negatives**, not permission to rebuild from untrusted summaries.

### Loss with only a checkpoint/root remaining

A root proves commitment/integrity but is not an exact membership database. If exact archive bytes and all exact authenticated indices are lost, queries that require the lost epoch cannot prove absence. Approximate summary-only emergency mode may conservatively reject positives and authorize negatives only if the previously frozen summary-only policy explicitly permits it and completeness/integrity of that summary is independently authenticated. Otherwise unseen admissions fail closed.

## Startup and delegation composition

The broker startup state machine must distinguish **history authority valid** from **history data sufficiently available for effect admission**.

Startup may perform read-only diagnostics with cold/unavailable epochs, but LAB-093 effect-capable worker delegation is permitted only when the selected deployment policy can establish its required historical query guarantee.

### `EXACT_REQUIRED` policy

Before effect-capable delegation/admission:

- manifest/provenance valid;
- active registry valid;
- every required sealed epoch has at least one currently retrievable authenticated exact copy, or a currently available authenticated exact index covering it.

Any unavailable epoch closes effect delegation/admission.

### `COLD_ON_DEMAND` policy

Delegation of pure compute may proceed, but an effect request whose key requires a cold epoch pauses at `PENDING_ARCHIVE_LOOKUP/RESTORE`. The effect boundary remains closed until the exact lookup completes under a fresh/still-valid broker snapshot.

### `SUMMARY_ONLY_EMERGENCY` policy

Only the already-frozen one-sided approximate semantics apply. This mode must be explicitly authenticated by policy. It cannot redeliver exact historical results from a positive and cannot turn uncertainty into a new effect.

In all modes, an unavailable epoch is never silently removed from the manifest or query coverage.

## Snapshot / TOCTOU rule

Archive query evidence is valid only for one immutable tuple:

`(logical_history_id, provenance_head, manifest_checkpoint, active_registry_snapshot, capacity_policy_version, archive_policy_version)`.

Before `AUTHENTICATED_ABSENT` becomes a new durable `BOUND`, the broker revalidates that tuple inside/adjacent to the sole-writer admission boundary. If compaction, manifest migration, policy change, active completion, provenance append, or recovery changed any component, the query is stale and must restart. Cached negative results never survive a manifest generation change.

## Operational audit evidence

Each archive retrieval attempt should durably or observably record enough audit data to diagnose availability without becoming authority itself:

- manifest checkpoint;
- epoch/object authority id;
- locator id (redacted if secret-bearing);
- provider version id when available;
- fetch outcome/classification;
- observed length/digest;
- integrity-verification outcome;
- restore state;
- retry/fallback locator chosen;
- final query coverage set.

Audit logs cannot override manifest authority and must not contain secrets needed to mutate the archive provider.

## Explicitly forbidden shortcuts

V1 forbids:

- treating `404`, missing path, empty directory, or absent object listing as key absence;
- trusting the newest provider object version without manifest authentication;
- accepting ETag/version ID/replica agreement as substitute for the authority digest;
- skipping one unavailable epoch and querying later epochs only;
- rebuilding authority manifests from whatever objects are currently listed;
- accepting a checkpoint root as exact membership proof by itself;
- changing an archive locator and simultaneously changing authority digest without an authenticated migration;
- deleting a manifest epoch because all replicas are unavailable;
- letting a worker choose or rewrite archive locators/manifest coverage;
- caching `MISS` across manifest/provenance changes;
- importing an archive from another logical history merely because its record format is valid;
- using an approximate summary to reconstruct exact operation/result identity;
- retrying a new effect while historical lookup is `UNKNOWN` or `RESTORING`.

## RED-first matrix

Production implementation MUST begin with exact-source tests. Minimum frozen matrix:

### Object identity / locator separation
1. valid object at original locator authenticates;
2. same exact bytes at new locator authenticate under same authority identity;
3. different bytes at same locator fail digest verification;
4. provider version ID changes but exact bytes/digest match -> may authenticate as another copy;
5. matching provider version ID with different bytes -> fail;
6. object key/path rename does not change authority identity;
7. locator registry cannot alter object digest;
8. worker cannot inject a locator that bypasses broker policy.

### Manifest completeness
9. all manifest epochs queried -> authenticated negative can proceed;
10. one epoch omitted -> no MISS;
11. storage listing omits an epoch -> manifest still requires it;
12. storage listing contains extra object -> extra object has no authority;
13. rolled-back manifest -> startup/query rejects;
14. valid old object under current locator but current manifest expects newer object -> reject;
15. logical-history mismatch -> reject;
16. archive-format version mismatch -> reject before parsing authority records.

### Exact retrieval integrity
17. truncated bytes -> fail length/digest;
18. appended bytes -> fail length/digest;
19. bit flip -> fail digest;
20. canonical digest matches but internal epoch id mismatch is rejected;
21. record count/range mismatch rejected;
22. exact-record root mismatch rejected;
23. malformed parse never degrades to absence;
24. timeout after partial bytes -> UNKNOWN/unavailable, no MISS.

### Multi-copy
25. first replica missing, second exact -> success;
26. first corrupt, second exact -> success plus integrity telemetry;
27. two corrupt replicas -> fail closed;
28. two replicas agree on wrong bytes -> fail against manifest;
29. one correct and one stale -> correct copy sufficient;
30. replica order cannot change authority result;
31. deleting one of several copies preserves availability if another authenticates;
32. deleting all copies closes affected admission.

### Cold restore
33. required epoch in cold restore -> PENDING, no effect;
34. restore completes with exact bytes -> lookup resumes after authentication;
35. restore returns wrong version -> fail digest/identity;
36. restore metadata says complete but bytes unavailable -> remain unavailable;
37. worker session expiry during restore does not resurrect session authority;
38. later fresh session can receive committed historical result only under current disclosure authorization.

### Negative proof
39. active absent + every archive exact absent -> AUTHENTICATED_ABSENT;
40. active absent + one archive unavailable -> no MISS;
41. active absent + approximate positive + exact false-positive disproved -> may proceed after revalidation;
42. global exact index missing one manifest epoch -> index incomplete, no MISS;
43. exact index covers all epochs and authenticates -> negative may avoid object fetch;
44. provider 404 from every locator is not a historical negative proof.

### Restore/rebuild
45. byte-identical backup restore preserves authority identity;
46. semantically same but differently encoded rebuild cannot replace old object silently;
47. untrusted summary cannot rebuild exact archive authority;
48. imported archive from another DB with same keys fails logical-history binding;
49. all exact copies lost + root only -> no exact negative proof;
50. old exact copy recovered after outage authenticates against unchanged manifest.

### Startup/delegation
51. EXACT_REQUIRED + all exact history available -> effect delegation may proceed after normal startup gates;
52. EXACT_REQUIRED + one unavailable epoch -> effect delegation closed;
53. COLD_ON_DEMAND may permit compute but blocks effect on required cold lookup;
54. unavailable epoch cannot be dropped to open delegation;
55. SUMMARY_ONLY mode requires authenticated explicit policy;
56. policy downgrade/change invalidates cached negative evidence.

### TOCTOU / concurrency
57. manifest changes after negative query before BOUND -> stale/retry;
58. active registry gains same key after archive negative before BOUND -> stale/conflict convergence;
59. compaction seals a new epoch after query -> old coverage stale;
60. two brokers query same negative and race BOUND -> sole-writer registry admits at most one canonical binding;
61. locator update during fetch does not alter accepted authority identity;
62. provenance head changes during cold restore -> full query snapshot revalidation required.

### Failure classifications / no mutation
63. integrity failure performs no provider effect/LAB-080 allocation;
64. unavailable archive performs no new BOUND;
65. rollback detection performs no archive auto-repair;
66. failed exact lookup does not mutate approximate summary to force a negative;
67. provider-side delete marker does not delete authority manifest entry;
68. startup diagnostic cannot invoke retention/repack authority.

## Audit conclusion

`APPLICATION_IDEMPOTENCY_ARCHIVE_OBJECT_RETRIEVAL_V1_FROZEN` is internally consistent with the previously frozen consumed-key archival contract:

- exact history remains logically monotonic;
- locators and replicas improve availability without becoming trust anchors;
- complete negative proof is manifest-scoped and cannot skip unavailable epochs;
- content substitution and rollback are fail-closed;
- cold restore delays admission rather than weakening identity checks;
- loss of exact history cannot be repaired from a digest or probabilistic summary by assumption;
- startup/delegation explicitly composes archive authority and archive availability.

No production code is changed by this research. Exact RED/GREEN implementation remains blocked behind source execution capability and LAB-086 priority.

## Next distinct research task if executable source remains unavailable

Freeze the **archive manifest/index mutation + replica lifecycle protocol**: canonical add/remove-locator operations, creation of new exact-index generations, index/object replacement ordering, replica deletion eligibility, cold-tier migration, concurrent compaction versus manifest update, and crash recovery such that availability maintenance cannot accidentally mutate historical authority or create a coverage gap.