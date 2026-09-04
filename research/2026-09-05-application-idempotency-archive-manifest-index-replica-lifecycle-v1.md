# Application Idempotency Archive Manifest / Index / Replica Lifecycle V1

Status: `APPLICATION_IDEMPOTENCY_ARCHIVE_MANIFEST_INDEX_REPLICA_LIFECYCLE_V1_FROZEN`
Date: 2026-09-05
Scope: LAB-093 / #178 follow-up to consumed-key archival/checkpoint and authenticated archive retrieval.

## Problem

The archive retrieval contract establishes that locators are retrieval hints, authenticated object identity is authority, and a negative lookup is complete only when every authority-required archive epoch is covered. That leaves a mutation problem: replicas, cold-tier locations and exact-index generations must change over time without accidentally changing historical authority, creating a transient coverage gap, or letting a crash turn a once-consumed application key back into an apparent `MISS`.

This note freezes the V1 control-plane protocol for those availability mutations. It does **not** authorize production implementation before executable RED/GREEN becomes available.

## Core invariants

1. **Historical object authority is immutable.** A sealed epoch's logical identity, canonical encoding/version, byte length, digest, record count/range/root and parent checkpoint never change through replica or locator maintenance.
2. **Locators are non-authoritative.** Adding/removing a path, bucket, object version, cold-tier key or replica does not alter the authenticated epoch identity.
3. **Manifest generations are append-only authenticated state.** Availability metadata changes produce a new manifest generation linked to the previous generation; old generations remain historical evidence.
4. **No coverage gap.** A new manifest generation becomes current only after every authority-required epoch still has at least one retrievable-or-provably-restoring authenticated copy, or is covered by a manifest-bound exact index whose backing epoch objects remain recoverable under the same rule.
5. **Removal is last.** A locator/replica may be deleted only after replacement coverage is durable, authenticated, independently verified, and the new manifest generation is committed.
6. **Index is derivative, not authority.** Exact indexes accelerate membership but do not replace authenticated epoch identities. An index generation must bind the exact manifest generation and the exact set of covered epochs.
7. **Crash never widens acceptance.** After any crash, startup chooses the last fully authenticated manifest generation. Partially staged additions/removals are ignored or reconciled; they never produce a broader `MISS` surface.
8. **Concurrent maintenance is serialized by manifest generation CAS.** Two operators may stage work concurrently, but only one transition from manifest generation `g` to `g+1` may commit. Losers must re-read and re-plan.
9. **No historical key reuse.** Any maintenance uncertainty, unavailable epoch, stale index, failed restore, deleted replica, or partial migration causes `PENDING_RETRIEVAL`/fail-closed, never `MISS`.
10. **Worker sessions cannot mutate archive lifecycle state.** Archive lifecycle writes are broker/admin maintenance capability only and remain outside delegated worker façades.

## Canonical state model

### Archive epoch identity

Each sealed epoch has immutable `epoch_identity`:

- logical history / namespace identity;
- epoch number or immutable epoch id;
- canonical encoding id + version;
- exact byte length;
- content digest;
- record count;
- key/range summary needed for exact lookup routing;
- authenticated set/root commitment;
- parent checkpoint / previous epoch linkage.

### Locator record

A locator record is availability metadata only:

- `locator_id` (stable manifest-local identifier);
- backend kind;
- retrieval coordinates (path/object key/version id/etc.);
- expected `epoch_identity`;
- lifecycle state: `STAGED`, `VERIFIED`, `CURRENT`, `DRAINING`, `RETIRED`, `RESTORING`, `UNAVAILABLE`;
- optional retrieval class / cold-tier metadata;
- last verified digest/time evidence.

Changing retrieval coordinates creates a new locator record; locator contents are not edited in place after authentication.

### Manifest generation

`manifest_generation` is authenticated and parent-linked:

- monotonically increasing generation number;
- parent manifest digest;
- exact set of sealed epoch identities;
- per-epoch current locator set;
- exact-index generation identity if present;
- policy/version controlling minimum replica/retrievability requirements;
- canonical transition operation digest;
- transition provenance reference.

A manifest generation is current only after the global provenance transition that commits it is itself authenticated and restart-verifiable.

### Exact-index generation

An exact index generation binds:

- index format/version;
- exact bytes digest/length;
- covered manifest generation digest;
- exact covered epoch identity set;
- deterministic build parameters;
- optional shard map, each shard independently digested.

An index that binds manifest `g` cannot be silently reused as proof for `g+1` unless `g+1` explicitly authenticates the same index identity and proves the covered epoch set is unchanged.

## Canonical operations

V1 allows only these lifecycle operations. Each is planned from an authenticated current manifest and commits through a single new manifest generation.

### `ADD_LOCATOR`

Purpose: add a new replica or cold-tier copy without changing historical authority.

Order:
1. read and authenticate current manifest `g`;
2. copy/retrieve exact epoch bytes from an authenticated source;
3. write destination bytes;
4. re-read destination through the same retrieval path production will use;
5. verify exact length + digest + canonical epoch identity;
6. stage locator as `VERIFIED`;
7. create manifest `g+1` = `g` plus the verified locator;
8. authenticate/commit `g+1`;
9. after restart-verifiable commit, mark the locator operationally `CURRENT` if a separate cache/status layer exists.

A failed copy never changes the current manifest.

### `REMOVE_LOCATOR`

Purpose: retire one location while preserving coverage.

Precondition: excluding the candidate locator, every affected epoch still satisfies the manifest policy with independently verified locators / restore guarantees.

Order:
1. authenticate current manifest `g`;
2. verify all replacement coverage now, not from stale telemetry;
3. create manifest `g+1` without the locator;
4. authenticate/commit `g+1`;
5. re-read `g+1` and verify lookup coverage;
6. only then delete/expire the physical replica;
7. physical deletion failure is availability debt, not a reason to roll back authority.

If the process crashes after step 4 but before physical deletion, the extra old copy is harmless. If it crashes before step 4, deletion is forbidden.

### `MIGRATE_LOCATOR`

Cold-tier or backend migration is compositionally `ADD_LOCATOR(new)` then `REMOVE_LOCATOR(old)`. V1 forbids one-shot move semantics because they create an avoidable coverage gap.

For async cold restore, the new locator remains `RESTORING` and is not counted as coverage until exact bytes are retrievable and verified.

### `REBUILD_EXACT_INDEX`

Order:
1. authenticate current manifest `g` and all epoch objects required for the build;
2. build the index from exact authenticated records;
3. deterministically verify index semantics against the source epochs, including positive samples and exhaustive/structural checks sufficient for the chosen exact index representation;
4. persist and re-fetch exact index bytes;
5. authenticate a new index generation bound to manifest `g`;
6. create manifest `g+1` that references the new index identity while preserving the same epoch authority set;
7. commit `g+1`;
8. retire the prior index only after `g+1` is restart-verifiable.

An index rebuild cannot make an unavailable epoch disappear from authority. If source coverage is incomplete, rebuilding is forbidden.

### `REPACK_EPOCH`

Byte-identical copy is locator maintenance. Any semantic re-encoding/repack that changes bytes is **not** locator maintenance. It creates a new epoch object identity and requires an authenticated migration transition that proves semantic equivalence and preserves consumed-key membership. V1 does not allow repack to overwrite the old identity in place.

## Concurrency protocol

Every lifecycle plan captures:

- `expected_manifest_generation`;
- `expected_manifest_digest`;
- affected epoch identities;
- intended operation digest.

Commit is compare-and-swap against the current authenticated manifest identity. If another maintenance operation wins first, the stale plan aborts without physical deletion and must be re-planned from the new manifest.

Compaction and locator maintenance may stage concurrently, but neither may commit against a stale parent manifest. A compaction that creates a new sealed epoch set necessarily forces any stale index/locator-removal plan to restart.

## Crash / UNKNOWN semantics

### Before manifest commit

Staged destination copies and indexes are untrusted garbage from the authority perspective. They may be cleaned up later. They cannot satisfy lookup or removal preconditions.

### After manifest commit, before acknowledgement

Recovery re-reads the authenticated provenance head and manifest generation. If the intended transition is present with the exact operation digest, it is treated as committed. Otherwise it is not replayed blindly; the maintenance planner re-evaluates from current state.

### After manifest commit, before physical deletion

The old replica remains an extra copy. Recovery may safely retry deletion only after re-verifying that the committed current manifest excludes it and replacement coverage still satisfies policy.

### During deletion

Deletion has no authority effect. A backend timeout is reconciled by checking object existence/version. If existence is UNKNOWN, keep the locator operationally retired but do not claim deletion success.

### Index publication crash

Until a manifest generation authenticates the new exact-index identity, the old manifest/index remains authoritative. A partially uploaded index is ignored.

## Coverage rule

For every exact application-idempotency lookup, the broker must derive coverage from one authenticated current manifest generation only. It may not mix locator/index membership from incompatible generations unless the current manifest explicitly authenticates those exact object identities.

A complete negative requires:

- active exact registry negative;
- every sealed epoch required by the current manifest either queried exactly or covered by the current manifest-bound exact index;
- all required exact index shards/epoch objects authenticated and available enough to establish that negative;
- no unresolved manifest transition, restore, rollback, substitution or UNKNOWN affecting coverage.

Otherwise return a non-MISS fail-closed state.

## Replica deletion eligibility

A physical replica is deletion-eligible only when all are true:

- it is absent from the current authenticated manifest;
- the manifest transition removing it is committed and restart-verifiable;
- every affected epoch still meets current replica/retrievability policy without it;
- no restore/repack/index build currently depends on it as sole authenticated source;
- no unresolved recovery state refers to it as required evidence;
- deletion authority is held by broker/admin maintenance, never a worker session.

## Cold-tier migration

Cold-tier copies may be counted as durability replicas only if policy explicitly allows their restore latency. They are not counted as **immediate lookup coverage** while `RESTORING` or otherwise non-readable. Lookup behavior while the only remaining copy is cold/unavailable is fail-closed/pending retrieval, not `MISS`.

A hot-to-cold move therefore follows add-verify-commit-remove ordering, and the system must explicitly accept the resulting availability/latency class in authenticated policy before deleting the last hot copy.

## Policy changes

Replica-count, backend-diversity, restore-latency and index requirements are policy authority, not operational hints. Policy changes are authenticated transitions. A looser policy cannot retroactively justify a deletion that was unauthorized under the policy current when that deletion was committed.

## Audit requirements

For each committed lifecycle transition retain:

- parent/current manifest identities;
- canonical operation digest;
- actor/authority class;
- affected epoch identities;
- new locator/index identities;
- exact verification evidence summaries;
- provenance transition identity;
- physical deletion outcome separately from manifest authority.

Do not record backend success as proof of object identity without re-fetch/digest verification.

## RED-first matrix (72 cases)

### Add locator / copy integrity
1. valid add of byte-identical replica;
2. destination truncation;
3. destination bit corruption;
4. wrong epoch copied;
5. semantically equivalent but different serialization;
6. stale source locator;
7. copy completes but re-fetch fails;
8. copy verified then process crashes before manifest commit;
9. manifest commit succeeds after verified copy;
10. duplicate add of same exact locator identity;
11. duplicate physical bytes under distinct locator id;
12. locator backend metadata rebinding after commit.

### Remove locator / no-gap ordering
13. remove one of two healthy replicas;
14. attempt remove sole replica;
15. replacement locator only STAGED;
16. replacement locator RESTORING;
17. replacement last verification stale/invalid;
18. crash before manifest removal commit;
19. crash after manifest commit before physical delete;
20. physical delete timeout after manifest commit;
21. old object still exists after logical retirement;
22. concurrent reader uses current manifest during retirement;
23. delete attempted by worker capability;
24. delete attempted under stale policy.

### Manifest generation / concurrency
25. two concurrent ADDs from same parent;
26. ADD versus REMOVE from same parent;
27. compaction versus REMOVE;
28. index rebuild versus manifest locator change;
29. stale expected manifest generation;
30. stale digest with same apparent generation number;
31. parent-link break;
32. rollback to prior manifest generation;
33. manifest substitution from another logical history;
34. partial manifest write / malformed canonical encoding;
35. UNKNOWN commit reconciles to exact committed transition;
36. UNKNOWN commit with different winning transition forces re-plan.

### Exact index lifecycle
37. correct exact-index build;
38. index built from incomplete epoch set;
39. index built from corrupt epoch bytes;
40. index digest mismatch after upload;
41. index bound to wrong manifest generation;
42. stale index reused after compaction changes epoch set;
43. missing index shard;
44. corrupt index shard;
45. old index retired before new manifest commit;
46. crash after index upload before manifest commit;
47. crash after manifest commit before old index deletion;
48. negative lookup with index unavailable must not return MISS.

### Cold-tier / restore
49. add verified cold replica;
50. cold replica RESTORING not counted as immediate lookup coverage;
51. remove last hot replica without policy authorization;
52. policy explicitly allows cold-only durability;
53. cold restore returns wrong bytes;
54. cold restore timeout;
55. restored copy written to a new locator with same epoch authority;
56. lost cold locator recovered from another authenticated replica;
57. all replicas unavailable -> pending/fail-closed;
58. backend says NOT_FOUND for one replica but another authentic copy exists;
59. all locators NOT_FOUND for authority-required epoch -> fail-closed archive-loss condition;
60. recovered archive object from backup with exact identity.

### Repack / authority separation
61. byte-identical relocation treated as locator change;
62. compressed/re-encoded equivalent bytes rejected as same identity;
63. authenticated repack transition creates new identity;
64. attempt to overwrite old epoch identity with repacked bytes;
65. repack loses one consumed key;
66. repack adds spurious key;

### Lookup/startup/delegation safety
67. lookup uses exactly one authenticated manifest generation;
68. mixed-generation locator set rejected;
69. unresolved manifest transition blocks complete negative;
70. startup with missing authority-required epoch fails closed;
71. worker delegation blocked while required archive coverage is unresolved;
72. after successful maintenance, historical consumed key still never returns MISS.

## Decision

V1 chooses **copy-before-publish, publish-before-delete** with parent-linked authenticated manifest generations and manifest-bound exact-index generations. Replica maintenance may improve or reduce availability but may never mutate historical object authority. Any uncertainty that could hide a previously consumed application key degrades to availability failure, never to a false negative.

Production implementation remains blocked on exact executable RED/GREEN. This note is architecture/evidence only.
