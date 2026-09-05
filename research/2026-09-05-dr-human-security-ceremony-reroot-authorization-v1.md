# DR Human Security Ceremony / Re-root Authorization V1

Date: 2026-09-05
Status: `DR_HUMAN_SECURITY_CEREMONY_REROOT_AUTHORIZATION_V1_FROZEN`
Scope: LAB-093 follow-up; composes with LAB-086 public-only historical recovery and the frozen application-idempotency archive/DR/escrow contracts.

## Why this contract exists

The preceding DR contracts deliberately stop automation when the system can no longer prove continuity from an independently retained pre-disaster trust state. Three classes of incident require that stop:

1. the escrow/recovery threshold itself is compromised or plausibly compromised;
2. too few independent custodians/witnesses survive to satisfy the currently authenticated recovery policy;
3. surviving independently authenticated checkpoints form an irreconcilable split view and no append-only consistency proof can establish one as a continuation of the other.

These are not ordinary availability failures. If software were allowed to choose a new trust root from disaster-supplied data in any of these cases, the backup or compromised administrator could silently become the authority that authenticates its own history. The purpose of this V1 contract is therefore not to make recovery automatic. It is to define the narrow human-governed transition by which a new root may be established while preserving all surviving evidence, making the discontinuity explicit, and preventing the procedure from becoming a reusable break-glass master secret.

## Primary-source donors

The contract is informed by the following mechanisms, without copying implementation code:

- The Update Framework (TUF): root metadata is the trust anchor for top-level key material; threshold root signatures and root-key rotation preserve continuity through the already trusted root rather than trusting a merely newer root. See TUF specification / root-role semantics: https://theupdateframework.github.io/specification/latest/
- Sigstore threat model: root-of-trust keys may be offline, threshold-held, geographically and organizationally distributed; rotation and revocation are explicit trust-management operations. https://docs.sigstore.dev/about/threat-model/
- C2SP transparency log witness / cosignature / policy specifications: witnesses retain prior checkpoints, verify consistency before advancing, and quorum policy can span independent witness groups; inconsistent checkpoints are a split-view condition rather than something a client should silently resolve. https://github.com/C2SP/C2SP/blob/main/tlog-witness.md ; https://github.com/C2SP/C2SP/blob/main/tlog-cosignature.md ; https://github.com/C2SP/C2SP/blob/main/tlog-policy.md
- NIST SP 800-57 key-management guidance: separates key lifecycle, compromise, recovery, trust-anchor, authorization, split-knowledge and organizational policy concerns. Current public Rev. 6 draft landing page: https://csrc.nist.gov/pubs/sp/800/57/pt1/r6/ipd

These donors support the separation-of-duty and continuity shape. They do not by themselves define the exact runtime-specific re-root protocol below.

## Threat model

Assume any subset of the following may be unavailable or malicious during the ceremony:

- primary runtime/database/storage domain;
- ordinary system administrators;
- cloud/provider operators;
- worker processes and worker credentials;
- the active broker process;
- some historical escrow custodians/witnesses;
- some backup locations;
- some network paths.

The ceremony MUST NOT assume that disaster-supplied archive bytes, a backup manifest, a current database, an ordinary administrator statement, a cloud version identifier, or a single surviving custodian is authoritative merely because it is internally consistent.

The ceremony is intended only for cases where automated recovery is already fail-closed. It MUST NOT be callable as a routine operational shortcut.

## Non-goals

V1 does not:

- make compromised history trustworthy;
- infer which side of a true split view is morally or commercially correct;
- erase evidence of the old trust state;
- permit automatic threshold downgrade;
- create a universal secret capable of overriding any future policy;
- authorize provider effects while recovery is unresolved;
- treat a human ceremony as evidence that historical bytes are exact when they are not independently verifiable.

## Core invariant

A human ceremony may authorize a **new verification root for future trust decisions**, but it may not rewrite the fact that continuity to the previous root was lost or disputed.

Therefore the durable result is a one-way, explicitly exceptional provenance transition:

`OLD_TRUST_STATE -> REROOT_CEREMONY_PENDING -> REROOT_AUTHORIZED -> NEW_TRUST_ROOT_COMMITTED -> FULL_REVERIFY_REQUIRED -> ACTIVE`

There is no transition back to the old automatic recovery state, and no operation that deletes the old evidence to make the re-root look like ordinary continuity.

## Trigger conditions

The ceremony MAY begin only when automatic recovery has already produced one of the following authenticated terminal conditions:

- `DR_THRESHOLD_COMPROMISED`;
- `DR_QUORUM_UNAVAILABLE` after exhausting the current policy's permitted recovery paths;
- `DR_SPLIT_VIEW`;
- `DR_ROOT_CONTINUITY_UNPROVABLE` where archive bytes may survive but the independently authenticated checkpoint/root needed to validate them does not.

Ordinary `UNAVAILABLE`, `RESTORING`, transient network failure, cold-tier restore delay, single-replica loss, or a still-satisfiable escrow quorum MUST NOT trigger the ceremony.

## Required evidence package before any new root is generated

The broker/runtime must remain stopped for delegated effects while a ceremony evidence package is assembled. The package is append-only and contains, as available:

1. the last locally authenticated pre-disaster root/checkpoint identifiers;
2. every independently retained custodian/witness checkpoint that survived;
3. every conflicting checkpoint and its signatures/cosignatures;
4. all available consistency proofs and their verification outcomes;
5. authenticated escrow policy versions, quorum/failure-domain requirements and key identifiers;
6. compromise declarations and the evidence/time window that motivated them;
7. archive manifests/object digests and exact retrieval verification outcomes;
8. current database/runtime identities, explicitly marked as untrusted until reconciled;
9. identities of human ceremony participants and the role each is exercising;
10. a unique ceremony identifier and monotonic/global-provenance parent reference.

Absence of evidence is itself recorded. Missing material must not be converted into a positive continuity claim.

## Human roles and separation of duties

V1 defines four logical roles. One person MAY fill more than one role only if the currently authenticated emergency policy explicitly allowed that combination before the disaster; the default is separation.

### 1. Evidence Custodian

Collects and preserves pre-disaster and disaster evidence. Cannot authorize the new root solely by possessing the evidence package.

### 2. Independent Verifier

Recomputes signatures/digests/consistency proofs and classifies surviving anchors as consistent, conflicting, stale, compromised, or unverifiable. Cannot alone generate or activate the new root.

### 3. Re-root Authorizer

Participates in the human authorization threshold. The authorizer signs the exact canonical ceremony payload, including the fact that continuity is lost/disputed and the selected surviving-history boundary. Ordinary admin/provider/worker credentials are not eligible.

### 4. Root Key Custodian

Participates in generation/custody of the new root public verification authority. New private material is generated fresh and is not imported from disaster-supplied storage unless a separate surviving authenticated policy explicitly proves that material remains uncompromised.

The ceremony threshold MUST require at least two independently controlled human/organizational failure domains for production re-root. A single administrator cannot self-authorize a new production trust root.

## Authorization policy

The authorization policy for invoking the ceremony must itself have been committed before the disaster in the global provenance chain. It defines:

- eligible role classes;
- minimum human authorization threshold;
- required independent failure-domain count;
- prohibited role combinations;
- whether any external witness/notary is mandatory;
- canonical payload/version;
- maximum compromise window assumptions;
- mandatory post-ceremony verification/drill gates.

If that policy is unavailable or its authority is itself one of the disputed roots, the system cannot silently invent a weaker replacement. The owner/security governance must perform an explicitly out-of-band organizational decision, and the durable record must classify the event as `POLICY_AUTHORITY_LOST`, not ordinary root rotation.

## Fresh-root generation

Fresh root generation MUST occur only after the evidence package is sealed and the required authorizers have approved the exact ceremony intent.

Requirements:

- generate new private keys using fresh entropy in a controlled environment;
- expose only public verification keys to the durable runtime/history, consistent with LAB-086 public-only historical recovery;
- do not derive the new root from an old HMAC/recovery secret, database secret, provider credential, backup encryption key, or worker credential;
- do not create a reusable symmetric master key for future emergency override;
- record key algorithm, public key bytes/digest, generation ceremony identity and intended role;
- private custody after generation follows the newly authorized threshold policy and remains outside the ordinary runtime durable store.

## Selecting the historical boundary

The ceremony must not pretend that one surviving history is continuous when the evidence cannot prove that.

The Independent Verifier classifies the maximal historical boundary into one of:

- `CONTINUOUS_TO_ANCHOR`: surviving evidence proves append-only continuity up to exact checkpoint X;
- `PREFIX_ONLY`: continuity is proved only up to checkpoint X; later material exists but is untrusted;
- `SPLIT_VIEW`: two or more independently authenticated incompatible successors exist after common checkpoint X;
- `NO_AUTHENTICATED_PREFIX`: no surviving independently authenticated checkpoint can establish a historical prefix.

For `SPLIT_VIEW`, V1 permits the human governance layer to choose a future operational branch only if the canonical authorization payload names all conflicting roots and the last common authenticated prefix. The unchosen branch remains retained evidence. This is an explicit governance decision, not a cryptographic proof that the selected branch was the unique historical truth.

For `NO_AUTHENTICATED_PREFIX`, the new root may establish a new epoch for future operations, but historical idempotency/non-reuse guarantees that depended on the lost history cannot be claimed. Effect admission that could repeat historical external side effects remains disabled until a separate product/security decision establishes a safe migration strategy. This is a hard boundary: human signatures cannot manufacture missing historical non-reuse evidence.

## Canonical re-root payload

All authorizers sign one canonical, versioned payload containing at minimum:

- protocol/version = `dr-reroot-v1`;
- repository/product logical identity;
- ceremony id;
- parent global-provenance transition id/digest;
- trigger condition;
- old authenticated policy/root identifiers, if available;
- complete digest of the sealed evidence package;
- historical-boundary classification and selected checkpoint/common prefix;
- digests of every known conflicting checkpoint;
- explicit list of compromised/unavailable old authorities;
- new public root key set and threshold/failure-domain policy;
- statement that no continuity beyond the selected boundary is being claimed;
- post-ceremony gates required before activation;
- authorization expiry/not-before values if the global policy uses time bounds.

Any semantic change produces a different payload and requires a fresh authorization threshold.

## One-way global provenance transition

The committed transition is not a replacement genesis record. It appends to the existing global provenance chain when the parent chain is available, or to a specifically marked `REROOT_FROM_LOST_PARENT` recovery record when the parent cannot be authenticated.

The durable transition must bind:

- old known root/checkpoint digest(s);
- evidence-package digest;
- human authorization set;
- new public root set;
- selected historical boundary;
- ceremony policy id/version;
- exact reason automated continuity failed.

The verifier MUST distinguish `NORMAL_ROTATION` from `HUMAN_REROOT`. A later verifier, auditor or migration must never normalize the latter into the former.

## Runtime authority boundary

The following actors MUST NOT be able to invoke, approve, or finalize the ceremony through their ordinary credentials or API surface:

- worker;
- provider adapter;
- LAB-080 request/effect path;
- ordinary broker session;
- database writer;
- ordinary system/cloud administrator;
- archive maintenance process;
- DR restore process that only possesses backup bytes.

Runtime code may only enter a fail-closed `CEREMONY_REQUIRED` state and emit/export the evidence package. Final authorization material is imported through a dedicated, offline-oriented, narrowly scoped recovery interface whose accepted objects are the canonical signed ceremony artifacts, not arbitrary shell/admin commands.

## Post-ceremony mandatory gates

Committing the new public root does **not** immediately restore normal operation. Before activation:

1. verify the re-root transition and every human signature against the ceremony policy;
2. re-fetch/re-authenticate all surviving archive objects against the selected historical boundary;
3. rebuild exact archive/index coverage only from authenticated objects;
4. run the complete application-idempotency non-reuse verification for every retained epoch;
5. run broker startup/recovery finite-state verification from a fresh process;
6. execute a DR recovery drill using the new escrow/root policy;
7. confirm ordinary admin/provider/worker credentials cannot perform re-root operations;
8. require a fresh activation transition `REROOT_VERIFIED -> ACTIVE` signed/authorized under the new root policy.

If any gate fails, the system remains fail-closed. There is no "activate anyway" bit in V1.

## Historical idempotency safety after re-root

A human re-root may restore verification authority but cannot recreate exact consumed-key history that has actually been lost.

Therefore:

- if all authority-required consumed-key epochs are restored and authenticated to the selected boundary, ordinary application-idempotency admission can resume after the full gate;
- if any required epoch remains unavailable/unverifiable, lookup is `PENDING_RECONCILIATION`/fail-closed, never `MISS`;
- if an epoch is proven irrecoverably lost, V1 does not permit silent namespace reuse. The affected namespace must remain sealed or move through a separately authorized product/security migration with a new external-effect safety argument.

## Crash and retry semantics

Ceremony artifacts are immutable and identified by digest.

- crash before sealed evidence package: restart collection; no root authority exists;
- crash after sealed package but before authorization quorum: continue collecting signatures over the exact same digest or abandon and create a new ceremony id;
- crash after authorization quorum but before provenance commit: re-verify quorum and commit exactly once using ceremony id/digest uniqueness;
- crash after provenance commit but before post-gates: restart in `FULL_REVERIFY_REQUIRED`;
- duplicate submission of the exact committed ceremony artifact is idempotent;
- same ceremony id with different payload digest is a permanent conflict and fails closed.

## No-secret-recovery rule

There is deliberately no permanent "ceremony secret" whose possession is sufficient to recover the system. Authority is the combination of:

- surviving pre-disaster policy evidence where available;
- explicit multi-party human authorization;
- freshly generated public-root authority;
- an immutable exceptional provenance record;
- successful post-ceremony verification/drill.

This preserves the LAB-086 direction: durable history should be publicly verifiable and must not depend on long-lived symmetric recovery signing material.

## RED-first executable matrix

The implementation must begin with tests. V1 freezes the following 60-case matrix; individual cases may be split into smaller tests but the semantic coverage is mandatory.

### Trigger / entry boundary (1-8)
1. transient archive unavailability does not permit ceremony;
2. satisfiable escrow quorum does not permit ceremony;
3. threshold compromise permits only `CEREMONY_REQUIRED`, not automatic root change;
4. no-surviving-quorum enters ceremony-required state;
5. irreconcilable split view enters ceremony-required state;
6. ordinary admin cannot set ceremony-required state as an authority bypass;
7. worker/provider cannot invoke ceremony interface;
8. backup restore process cannot self-promote to ceremony authority.

### Evidence package (9-16)
9. missing known conflicting checkpoint is detected when referenced evidence exists;
10. evidence package digest changes on any field mutation;
11. surviving witness checkpoint signature is verified;
12. invalid consistency proof is retained as negative evidence, not accepted continuity;
13. missing evidence is recorded as missing, not synthesized;
14. disaster database identity is marked untrusted before reconciliation;
15. evidence package is immutable after sealing;
16. same ceremony id cannot seal two package digests.

### Roles / quorum / failure domains (17-26)
17. single ordinary admin cannot authorize;
18. single eligible authorizer below threshold cannot authorize;
19. threshold satisfied inside one failure domain is rejected when policy requires two;
20. prohibited role combination is rejected;
21. eligible multi-domain quorum authorizes exact payload;
22. signature from unknown role key does not count;
23. revoked/compromised authorizer key does not count;
24. stale ceremony policy cannot lower threshold;
25. new root key custodian alone cannot authorize activation;
26. evidence custodian alone cannot authorize activation.

### Root generation / payload binding (27-34)
27. new public root is bound into canonical payload;
28. replacing one public key invalidates authorization;
29. changing selected historical boundary invalidates authorization;
30. omitting split-view competing root invalidates authorization;
31. old HMAC/recovery secret is never accepted as new root authority;
32. provider/worker/admin credential is never accepted as root key;
33. duplicate exact authorization signatures count once;
34. authorization over one ceremony id cannot be replayed to another.

### Historical-boundary semantics (35-42)
35. continuous prefix is accepted only with valid consistency evidence;
36. stale-but-valid checkpoint cannot silently outrank a newer mutually consistent quorum checkpoint;
37. incompatible authenticated successors classify as split view;
38. split-view chosen branch retains unchosen branch evidence;
39. split-view choice is marked governance decision, not cryptographic continuity;
40. no-authenticated-prefix cannot claim historical non-reuse completeness;
41. lost consumed-key epoch prevents `MISS`;
42. irrecoverable historical epoch keeps namespace sealed absent separate migration.

### Provenance / commit / crash (43-50)
43. re-root transition binds old root/evidence/new root/reason;
44. verifier distinguishes HUMAN_REROOT from NORMAL_ROTATION;
45. crash before quorum leaves no new authority;
46. crash after quorum/before commit can commit exactly once;
47. same ceremony id with different payload after commit fails closed;
48. exact duplicate committed artifact is idempotent;
49. crash after commit enters FULL_REVERIFY_REQUIRED;
50. deleting old contradictory evidence is detected/audit-failing.

### Post-gates / activation (51-60)
51. root commit alone does not enable worker delegation;
52. root commit alone does not enable provider effects;
53. archive re-authentication failure blocks activation;
54. consumed-key coverage gap blocks activation;
55. broker startup verification failure blocks activation;
56. failed DR drill blocks activation;
57. ordinary admin credential cannot skip a failed gate;
58. fresh activation transition under new policy enables only after all gates pass;
59. restart after ACTIVE re-verifies HUMAN_REROOT provenance and selected boundary;
60. historical key previously consumed before disaster never becomes `MISS` solely because a human re-root occurred.

## Implementation shape when executable source becomes available

The first production slice should be deliberately small:

1. add a pure canonical ceremony-payload encoder/verifier with golden vectors;
2. add an immutable evidence-package representation and digest;
3. add policy-driven role/quorum/failure-domain verification;
4. add a durable `CEREMONY_REQUIRED` / `FULL_REVERIFY_REQUIRED` state that has no effect-admission path;
5. add the one-way provenance transition and duplicate/conflict rules;
6. only then integrate offline artifact import and post-ceremony gates.

Do not begin by adding an administrative `force_recover()` method. Such a method would erase the security boundary this contract is intended to define.

## Audit conclusions

1. Human re-root is a governance transition, not a cryptographic proof that missing history was correct.
2. The new root must be fresh and public-only in durable history; no reusable symmetric emergency master secret is introduced.
3. Ordinary runtime/admin/provider/worker authority cannot invoke or approve the transition.
4. Split view remains visible forever in evidence; selecting a branch is explicit and exceptional.
5. Missing historical consumed-key evidence cannot be repaired by human signatures; affected effect namespaces remain fail-closed.
6. Re-root commit is not activation. Full archive/idempotency/startup verification plus a DR drill are mandatory before effects resume.
7. The exceptional transition is one-way and permanently distinguishable from normal root rotation.

## Next distinct evidence task if exact execution remains unavailable

Freeze a **post-re-root trust-epoch / namespace migration contract** for the case where future operation must resume but some historical application-idempotency epoch is provably irrecoverable. The contract must distinguish safe new effect namespaces from unsafe reuse, define external side-effect migration/cutover evidence, require explicit product/security authorization, and prove that a new trust epoch cannot accidentally map an old application key back to `MISS`.
