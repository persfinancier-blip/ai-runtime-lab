# Application Idempotency Archive Loss / Disaster-Recovery Authority V1

Status: `APPLICATION_IDEMPOTENCY_ARCHIVE_LOSS_DISASTER_RECOVERY_AUTHORITY_V1_FROZEN`
Date: 2026-09-05
Scope: LAB-093 / #178 follow-up to consumed-key archival/checkpoint, authenticated archive retrieval, and manifest/index/replica lifecycle.

## Problem

The prior archive contracts ensure that a historically consumed application key cannot become `MISS` merely because active storage was compacted, a replica moved, or a locator changed. The remaining hard case is real disaster: an authority-required sealed epoch becomes unreadable or appears permanently lost.

The safety requirement is stronger than ordinary backup recovery. The broker must restore availability without accepting a substituted history and without silently shrinking the set of historical keys that are known to be consumed. A missing archive epoch is therefore an **authority failure**, not merely a storage warning.

This note freezes the V1 disaster-recovery authority protocol. It does not authorize production implementation before executable RED/GREEN is available.

## External evidence / donor mechanisms

1. **TUF consistent snapshots and rollback protection.** TUF snapshot metadata binds hashes/versions so a client cannot safely combine metadata from inconsistent repository states; clients also reject metadata older than trusted state. This is the right donor for the rule that recovery must advance from the currently authenticated history and may not replace it with an older, internally valid archive view.
2. **TUF root recovery / threshold trust.** TUF separates high-authority root trust from ordinary online roles and requires out-of-band recovery if a threshold of root keys is compromised. This supports a distinct, stronger disaster-recovery authority rather than letting the ordinary storage operator rewrite historical authority.
3. **RFC 6962 append-only consistency.** A checkpoint/root proves a particular committed append-only history only when continuity from the previously trusted state is verified; a new root by itself is not authority to substitute history.
4. **S3 Versioning/Object Lock/Replication.** Versioning and WORM retention protect historical object versions; replication improves availability but does not make replica location authoritative. AWS also documents that object immutability does not protect against loss of decryption-key access, reinforcing that retrievable exact bytes plus cryptographic identity are both required.
5. **NIST SP 800-34 Rev.1.** Backup media should be tested for successful retrieval, including at the alternate site. For this design, an untested backup is not eligible as authoritative disaster-recovery coverage.

## Core invariants

1. **Loss never becomes absence.** An epoch that is required by the current authenticated manifest remains authority-required while unavailable, lost, restoring, or under investigation.
2. **No retirement-by-disaster.** V1 has no operation that removes a lost epoch from required historical lookup coverage merely because recovery is expensive or impossible.
3. **Startup/delegation fail closed.** If any authority-required epoch cannot participate in complete exact negative lookup, startup may expose only recovery/diagnostic authority; worker delegation and new effect admission remain closed.
4. **Previously consumed keys never become `MISS`.** Archive loss may reduce availability, never enlarge the set of requests eligible for new side effects.
5. **Restore must reproduce the authenticated epoch identity.** Byte-identical restoration to the frozen digest/length/canonical encoding is ordinary recovery. Semantic re-creation with different bytes is not restoration.
6. **Locator/domain is not authority.** Offline media, another cloud account, another administrative domain, or a DR region may supply bytes, but those bytes become usable only after verification against the already trusted epoch identity and chain.
7. **Current trusted history is the recovery root.** Recovery begins from the broker's authenticated manifest/provenance checkpoint that predates the outage. A backup cannot bring its own independent head and ask the broker to trust it.
8. **Rollback/substitution is forbidden.** A backup containing an older but valid manifest/checkpoint cannot replace a newer trusted manifest. A backup epoch with a different digest cannot be accepted under the old epoch id.
9. **Disaster authority is separate from ordinary lifecycle authority.** Declaring `LOST`, importing from another administrative domain, and resolving a loss require explicit broker-admin DR authority and authenticated provenance transitions.
10. **Recovery cannot mint worker/session authority.** Archive recovery restores evidence only; all worker sessions remain governed by normal startup/re-entry rules after the archive becomes complete again.

## Canonical loss states

For each authority-required epoch, V1 distinguishes:

- `AVAILABLE_VERIFIED` — at least one currently retrievable copy re-authenticates to the frozen epoch identity;
- `UNAVAILABLE` — known locator exists but exact bytes cannot currently be retrieved;
- `RESTORING` — a known copy is in an asynchronous restore process;
- `SUSPECT` — bytes are retrievable but fail identity/integrity verification;
- `DECLARED_LOST` — authenticated DR authority has established that no currently registered replica can supply exact bytes;
- `RECOVERY_CANDIDATE` — external/offline bytes have been discovered but are not yet authoritative;
- `RECOVERED_VERIFIED` — restored bytes re-authenticate exactly and a recovery provenance transition has committed;
- `IRRECOVERABLE` — operational conclusion that exact bytes are unavailable from known domains. In V1 this is still fail-closed historical authority, not permission to retire the epoch.

State labels are evidence about availability, not replacements for the immutable epoch identity.

## Declaring loss

`DECLARED_LOST` requires an authenticated DR transition containing at least:

- current manifest generation + digest;
- exact immutable epoch identity;
- all registered locators/replicas examined;
- observed retrieval outcomes and timestamps;
- whether encryption/decryption/key access was tested;
- restore-job state for cold copies;
- DR policy/version;
- declaring principal/authority digest;
- canonical incident id and operation digest.

The declaration does not delete locators or modify the epoch identity. It records that normal lookup coverage is unavailable and therefore keeps admission closed.

A single transient backend error is not enough to declare permanent loss. Conversely, inability to prove permanent loss is not permission to return `MISS`; uncertainty remains fail-closed.

## Recovery sources

V1 permits candidate bytes from:

- another registered replica/region/account;
- offline backup media;
- immutable backup vault;
- another administrative domain explicitly named by DR policy;
- a previously exported exact archive bundle.

A recovery source is never trusted because of its location or administrator. It must supply bytes that match the pre-existing authenticated epoch identity.

### Required candidate verification

Before a candidate may affect the current manifest:

1. retrieve the complete candidate bytes;
2. require exact expected byte length;
3. require exact cryptographic digest;
4. parse under the frozen canonical encoding/version;
5. verify record count/range/root and parent checkpoint linkage;
6. if encrypted, verify that plaintext identity after authenticated decryption matches the frozen epoch identity;
7. perform exact membership/structural verification appropriate to the archive format;
8. re-read through the intended production retrieval path and repeat identity verification.

Only then can the candidate be staged as a verified locator.

## Cross-domain import

Another administrative domain may hold a valid copy while the primary domain is damaged. V1 therefore separates **transport authenticity** from **historical authority**.

The importing domain must already trust the epoch identity from its own pre-disaster authenticated manifest/provenance history. The exporting domain may provide:

- exact archive bytes;
- its locator/version metadata;
- optional signed custody/export statement;
- optional transparency/checkpoint evidence.

These can improve auditability, but none can override a digest mismatch against the importing domain's already trusted epoch identity.

If the importing domain has lost both the bytes **and** the last authenticated identity/checkpoint needed to verify them, automatic recovery is forbidden. That is root-of-trust recovery and requires an explicitly separate out-of-band administrative process; V1 does not infer authority from the backup alone.

## Restore ordering

Recovery uses additive ordering:

1. authenticate the last trusted current manifest/provenance head;
2. mark or retain the affected epoch as non-covering (`UNAVAILABLE` / `DECLARED_LOST`);
3. obtain candidate bytes;
4. verify exact identity independently;
5. write candidate to a recovery destination;
6. production-path re-fetch and re-verify;
7. create a new manifest generation that **adds** the recovered verified locator while preserving the same immutable epoch identity;
8. authenticate/commit the manifest transition through normal global provenance;
9. re-read current manifest and execute complete lookup coverage verification;
10. only after full startup verification succeeds may worker delegation/new-effect admission reopen.

A restore never rewrites the old epoch object identity or previous manifest generations.

## Crash and UNKNOWN semantics

- Crash before manifest commit: recovered bytes are staged/non-authoritative; startup still treats the epoch as unavailable.
- Crash after manifest commit but before acknowledgement: recovery re-reads global provenance/current manifest; if the exact transition committed, it resumes from that state and does not append a second recovery transition.
- Timeout during restore/import: candidate remains non-authoritative until exact re-fetch verification succeeds.
- Candidate digest mismatch: classify `SUSPECT`, preserve evidence, reject it, keep lookup/admission closed.
- Two competing recovery candidates: identical bytes may converge to multiple locators; different bytes cannot both satisfy the same frozen epoch identity.
- Concurrent lifecycle maintenance: manifest CAS forces stale maintenance/recovery plans to re-read and re-plan.

## Can a lost epoch ever be retired?

**Not in V1.** If the system promises that a historically consumed application key never becomes reusable, then deleting the last exact membership authority for that history without an equivalent no-false-negative replacement breaks the promise.

A future protocol could replace exact epochs only with a separately proven archival representation whose membership semantics preserve zero false negatives and whose installation is authenticated before old coverage is retired. Disaster itself is not such a proof.

Therefore `IRRECOVERABLE` means permanent or operator-resolved loss of availability for new application keys in the affected authority scope unless a valid exact/equivalent authenticated history representation is later recovered. It does not mean "forget history and continue."

## Startup and delegation gate

The broker may open normal startup/delegation only if all are true in one fresh verification cycle:

- current global provenance head authenticates;
- current archive manifest authenticates and is not rolled back;
- every authority-required epoch has complete lookup coverage;
- no required epoch is `UNAVAILABLE`, `RESTORING`, `SUSPECT`, `DECLARED_LOST`, `RECOVERY_CANDIDATE`, `IRRECOVERABLE`, or otherwise UNKNOWN;
- current exact index, if used, is manifest-bound and fully available;
- recovery planner returns `NONE`;
- existing LAB-090/LAB-100 activation and LAB-093 session/effect gates also pass.

A successful restore command alone is insufficient; the broker must perform a new full verification/delegation cycle.

## Security consequences

### What DR may improve

- availability of historical membership evidence;
- regional/account/storage-provider resilience;
- ability to recover from operator deletion or backend loss;
- audit evidence about custody and recovery actions.

### What DR must never change

- consumed-key semantics;
- canonical operation identity;
- epoch identity/digest;
- provenance history;
- LAB-080 request identity;
- authority for worker effects;
- current provider/activation authority.

## RED-first matrix (64 cases)

Freeze at least these classes before implementation:

### Loss classification
1. one replica temporarily unavailable -> fail closed, no `MISS`;
2. all replicas unavailable -> fail closed;
3. cold copy restoring -> fail closed until verified;
4. retrievable copy has digest mismatch -> `SUSPECT`;
5. locator says missing while another verified replica works -> lookup remains available;
6. all registered copies exhausted -> authenticated `DECLARED_LOST`;
7. unauthorized principal attempts loss declaration -> reject;
8. stale manifest principal declares loss for superseded generation -> reject.

### Exact restore
9. byte-identical offline copy -> eligible after full verification;
10. same records but different serialization -> reject as ordinary restore;
11. truncated object -> reject;
12. wrong epoch id with matching shape -> reject;
13. correct digest metadata supplied by untrusted source but wrong bytes -> reject;
14. correct bytes restored to new locator -> accept after manifest commit;
15. source locator reused but object version changed -> verify bytes, never trust locator;
16. encryption key unavailable -> remain fail closed.

### Rollback / substitution
17. backup manifest older than current trusted generation -> reject rollback;
18. backup has internally valid but foreign history root -> reject;
19. backup omits newer epoch -> reject incomplete history;
20. backup substitutes an older object under same path -> digest reject;
21. backup provides new manifest signed by foreign admin only -> no authority;
22. attacker replays previous `RECOVERED_VERIFIED` transition -> idempotent/no new authority;
23. current trusted manifest lost locally but checkpoint retained elsewhere -> require explicit root recovery path;
24. both bytes and trusted checkpoint lost -> automatic recovery forbidden.

### Cross-domain
25. DR account supplies exact bytes -> accept only against local trusted identity;
26. DR account supplies signed but mismatched bytes -> reject;
27. two domains disagree on epoch digest -> no automatic choice;
28. exporter is compromised but bytes still match trusted digest -> bytes may be usable, exporter statement not authority;
29. copied custody metadata without bytes -> insufficient;
30. cross-domain import races with ordinary replica restore -> CAS/converge;
31. imported exact copy later becomes unavailable -> remaining coverage rules apply;
32. foreign domain attempts to replace local provenance head -> reject.

### Crash / concurrency
33. crash after candidate download before verify -> staged only;
34. crash after verify before write -> no authority change;
35. crash after destination write before manifest commit -> staged only;
36. crash after manifest commit before ack -> detect committed transition;
37. timeout during destination re-fetch -> no commit;
38. concurrent identical restores -> one or multiple verified locators, one manifest parent wins;
39. concurrent different candidate bytes -> only matching identity can progress;
40. lifecycle REMOVE races with DR ADD -> stale CAS abort/re-plan.

### Lookup / admission
41. active registry negative + lost epoch -> never `MISS`;
42. exact index covers all except lost epoch -> never `MISS`;
43. probabilistic summary says negative while epoch lost -> never `MISS`;
44. positive hit in active registry while archive lost -> return known duplicate result if otherwise authorized; do not require negative completeness for that positive;
45. exact positive archive hit from another verified replica -> duplicate convergence remains valid;
46. worker asks for new key during restore -> reject/pending before effect;
47. stale worker session survives DR event -> session invalid/re-entry required;
48. successful restore without fresh startup verification -> delegation remains closed.

### Irrecoverable
49. operator marks `IRRECOVERABLE` -> no key reuse;
50. retention policy tries to retire lost epoch -> reject;
51. quota pressure plus lost epoch -> no deletion/reuse;
52. admin attempts scope shrink to bypass lost history -> require separate authority migration, not DR shortcut;
53. namespace deletion requested while epoch lost -> historical non-reuse remains authenticated per policy;
54. tombstone archive loss -> same fail-closed rule;
55. disaster lasts across restart -> state reconstructs as unavailable/lost, not empty;
56. new software version starts with lost epoch -> upgrade cannot bypass gate.

### Audit / authority
57. DR transition missing incident id -> reject;
58. DR transition missing current manifest digest -> reject;
59. candidate accepted without production-path re-fetch -> regression failure;
60. recovery authority delegated to worker façade -> regression failure;
61. current manifest changes between verify and commit -> CAS reject;
62. recovery commit not parent-linked in global provenance -> reject;
63. audit shows old manifest generation silently removed -> reject;
64. full restore followed by fresh verify -> only then normal startup/delegation may reopen.

## Audit conclusions

- Disaster recovery is an availability mechanism, not authority to rewrite historical membership.
- Exact pre-disaster authenticated identity is the acceptance root for restored bytes.
- A lost epoch remains required indefinitely in V1; there is no safe "forget and continue" operation.
- Cross-domain/offline backup is acceptable only as a byte source verified against local trusted history.
- Full fresh startup verification is mandatory after recovery before effects/delegation resume.
- This design composes with the existing archive manifest lifecycle contract: recovery is effectively a privileged `ADD_LOCATOR` whose source is outside normal registered availability, preceded by explicit loss evidence and followed by the same authenticated manifest CAS.

## Sources

- The Update Framework, Roles and metadata: https://theupdateframework.io/docs/metadata/
- The Update Framework, Security: https://theupdateframework.io/docs/security/
- The Update Framework, FAQ / key compromise recovery: https://theupdateframework.io/docs/faq/
- RFC 6962, Certificate Transparency: https://www.rfc-editor.org/rfc/rfc6962
- Amazon S3, Object Lock considerations: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html
- Amazon S3, Versioning workflows: https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html
- NIST SP 800-34 Rev.1, Contingency Planning Guide for Federal Information Systems: https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-34r1.pdf
