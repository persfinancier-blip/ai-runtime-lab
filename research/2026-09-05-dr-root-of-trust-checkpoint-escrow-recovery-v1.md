# DR Root-of-Trust / Checkpoint Escrow Recovery V1

Status: `DR_ROOT_OF_TRUST_CHECKPOINT_ESCROW_RECOVERY_V1_FROZEN`
Date: 2026-09-05
Scope: LAB-093/#178, composed with LAB-086 public-only historical recovery and LAB-097..100 global provenance / activation authority.

## Problem

The prior archive-loss contract assumes the primary domain still possesses an authenticated manifest/provenance checkpoint against which recovered archive bytes can be verified. The harder disaster is simultaneous loss or compromise of that local checkpoint state while archive bytes may still exist in offline or cross-domain backups.

A backup cannot safely solve this by asserting its own head. If the only surviving statement of history is supplied by the same recovery source that supplies the bytes, recovery has become self-authenticating and rollback/substitution resistance is gone.

This note freezes the V1 root-of-trust/checkpoint escrow recovery protocol. It is a design/evidence contract only; production implementation still requires executable RED/GREEN.

## External donors and evidence

1. **TUF root-role recovery.** TUF separates ordinary online roles from high-authority root metadata. If a threshold of root keys is compromised, root metadata must be re-issued out of band. Root metadata also defines key thresholds for other roles. This supports a distinct offline recovery authority rather than allowing the storage plane to mint a replacement trust root.
2. **C2SP transparency-log witness protocol.** Witnesses retain the latest checkpoint they cosigned, require continuity from that size, verify the log signature and consistency proof, and reject inconsistent views. A witness therefore acts as an independently persisted anti-rollback observation, not as a storage mirror.
3. **C2SP transparency-log policy.** Trust policy can require quorum across independently operated witness groups. This is a useful donor for recovery authorization that survives compromise of one administrative domain without trusting any one escrow copy.
4. **RFC 6962 consistency proofs.** A later tree head is acceptable relative to an older trusted head only if append-only consistency can be proved. A root hash alone does not establish continuity.
5. **NIST SP 800-57 Part 1 Rev.5.** Key management guidance treats trust anchors, key backup/recovery, compromise and key lifecycle as distinct managed concerns; this supports separating recovery authorization keys from ordinary runtime/provider keys.

## Non-negotiable invariants

1. **No backup self-authentication.** Archive bytes, a manifest, and a checkpoint recovered from one backup source are evidence candidates, not authority merely because they agree with each other.
2. **Independent pre-disaster escrow is required.** Automatic recovery is allowed only when the system can reconstruct a trusted pre-disaster anchor from one or more independently persisted authorities that existed before the incident.
3. **Escrow records public verification material, not runtime mutation secrets.** LAB-086 history remains public-only after cutoff. Recovery escrow must never reintroduce durable HMAC/private provider authority merely to make DR easier.
4. **Threshold/out-of-band recovery is stronger than ordinary admin authority.** Ordinary storage lifecycle, worker/session, provider, activation, and application-idempotency authorities cannot mint or replace a DR trust anchor.
5. **Highest authenticated checkpoint wins; ambiguity fails closed.** Recovery may advance from the newest mutually consistent authenticated checkpoint. It may not choose an older checkpoint merely because more backups contain it.
6. **Rollback and split-view are first-class failures.** Two validly signed escrow checkpoints that cannot be placed on one authenticated parent/consistency chain are not merged by policy preference; automatic recovery stops.
7. **Recovery restores verification authority only.** It does not reopen worker delegation, provider activation, or effect admission. A full fresh LAB-097..100/LAB-093 startup verification cycle is required afterward.
8. **No independent DR provenance island.** Every accepted DR root/checkpoint restoration must become a parent-linked transition in the same global authenticated provenance chain used by LAB-097..100.

## Escrow package V1

Each independently held escrow package is immutable and contains at minimum:

- logical history / deployment identity;
- canonical encoding version;
- global provenance checkpoint generation/sequence;
- checkpoint digest/root and parent checkpoint identity;
- current archive-manifest generation + digest;
- current provider-generation/history head digest;
- current LAB-090/LAB-100 activation-authority digest/state summary sufficient for restart verification;
- LAB-086 public recovery/root verification key set and thresholds effective at the checkpoint;
- DR policy version/digest;
- escrow-package creation time and monotonic sequence where available;
- signer/witness identity and signature/cosignature over the canonical package;
- optional append-only consistency material to the previous escrow checkpoint.

The escrow package contains no private provider key, no worker token/session secret, no application effect credential, and no durable symmetric break-glass signing secret.

## Independent escrow domains

V1 requires at least two administrative/failure domains for automatic root recovery. A deployment may use more.

Examples:

- offline owner-controlled medium + independent cloud/account witness;
- two organizational custodians plus an online transparency witness;
- geographically separated HSM-backed custodians plus public-only checkpoint mirror.

Independence is a policy property, not a hostname count. Two buckets controlled by the same credential set are one failure domain.

## Recovery quorum

The DR policy defines named escrow groups and a threshold expression. Example semantics:

- owner-custodian group: 2-of-3;
- independent witness group: 1-of-2;
- recovery quorum: both groups.

A package contributes only if:

- its signature verifies under the escrow public key already trusted by the pre-disaster DR policy lineage;
- its logical history identity matches;
- its policy version is not older than the trusted minimum;
- its checkpoint can be ordered consistently with the other accepted packages.

A threshold authorizes selecting a checkpoint; it does not authorize altering checkpoint contents.

## Selecting the recovery checkpoint

Given candidate escrow packages:

1. authenticate each package independently;
2. partition by exact logical history identity;
3. discard packages signed only by unknown/revoked escrow keys;
4. construct the parent/consistency relation between surviving checkpoints;
5. reject any candidate that rolls back below an already independently trusted checkpoint;
6. require the configured cross-domain quorum on the **same checkpoint identity**, or on checkpoints where append-only consistency proves one is a strict successor of the other;
7. select the highest checkpoint for which quorum and continuity both hold;
8. if two quorum-supported candidates are incomparable, stop automatic recovery and classify `DR_SPLIT_VIEW`.

Majority by timestamp, filename, storage generation, or administrator preference is forbidden.

## Recovery of partial key compromise

### One escrow key/domain compromised

If quorum remains satisfiable without that domain, recovery may proceed from an uncompromised quorum. The compromised key is then revoked through a parent-linked DR-policy transition after the original history is restored and verified.

### Threshold not compromised, but stale signed packages exist

Stale packages may verify cryptographically but cannot override a newer quorum-supported checkpoint. They remain audit evidence only.

### Threshold of escrow authority compromised

Automatic recovery stops. V1 does not provide a cryptographic method to distinguish attacker-produced quorum signatures from legitimate ones once the configured recovery threshold itself is compromised.

Recovery then requires an explicit human owner/security ceremony with independent out-of-band evidence. That ceremony may establish a new root only as a new security epoch with documented loss of automated continuity; it must not be represented as ordinary verified continuation.

## Out-of-band owner ceremony boundary

Human recovery is required when any of these hold:

- no configured independent quorum survives;
- quorum-supported checkpoints form an unresolved split view;
- the DR policy/key threshold itself is believed compromised;
- the highest trustworthy checkpoint cannot be ordered against surviving global provenance;
- logical history identity is ambiguous;
- every surviving checkpoint is supplied only by the same domain as the recovered archive bytes and no independent pre-disaster observation exists.

The automated system must not invent a new trust root in these cases.

## Archive-byte recovery after checkpoint restoration

Once an authoritative escrow checkpoint is selected:

1. restore its public verification material into an isolated recovery context;
2. verify the checkpoint package and parent/consistency lineage again;
3. fetch candidate archive/manifest/provenance bytes from backups;
4. verify them against the selected checkpoint identities/digests;
5. reject any backup that is internally valid but older, foreign, or inconsistent with the selected checkpoint;
6. rebuild only missing availability replicas/locators, preserving immutable historical identities;
7. append a canonical `DR_TRUST_ROOT_RESTORED` transition to the existing global provenance chain using the configured DR recovery authority;
8. append/commit ordinary archive locator restoration transitions as required;
9. re-read all state through the production path;
10. run the complete startup/recovery planner; only a `NONE` plan plus all LAB-090/LAB-100/LAB-093 gates permits normal delegation/effects.

## Anti-rollback ordering

Recovery ordering uses four monotonic dimensions together:

1. logical history identity;
2. parent-linked global provenance sequence;
3. archive-manifest generation/digest;
4. independently witnessed/escrowed checkpoint sequence.

A higher timestamp is never sufficient. A higher sequence with broken parent linkage is not accepted. A backup cannot skip an authenticated intermediate transition unless the protocol has a cryptographic consistency proof that commits to the same prefix.

## Crash and UNKNOWN semantics

- Crash before recovery checkpoint selection: no authority change.
- Crash after quorum selection but before durable global transition: selection is recomputed from escrow packages; no local flag is trusted.
- Crash after `DR_TRUST_ROOT_RESTORED` commit but before acknowledgement: restart verifies the committed parent-linked transition and resumes idempotently.
- Timeout while fetching one escrow domain: quorum may proceed only if policy can still be satisfied without it; otherwise remain fail closed.
- Newer escrow package appears during recovery: CAS/parent check invalidates a stale plan; recovery restarts selection from current evidence.
- Restored archive bytes mismatch selected checkpoint: reject bytes; do not weaken checkpoint choice.

## Startup states

V1 distinguishes:

- `DR_ROOT_HEALTHY` — local authenticated checkpoint and required external escrow continuity verified;
- `DR_ROOT_LOCAL_LOST` — local checkpoint unavailable, escrow recovery required;
- `DR_ESCROW_QUORUM_READY` — sufficient independently authenticated checkpoint evidence exists;
- `DR_SPLIT_VIEW` — independently valid but inconsistent quorum candidates exist;
- `DR_ESCROW_INSUFFICIENT` — surviving independent evidence does not meet policy;
- `DR_THRESHOLD_COMPROMISED` — configured recovery authority believed compromised;
- `DR_ROOT_RESTORED_VERIFYING` — checkpoint restored but full global/startup verification incomplete;
- `DR_ROOT_RECOVERED` — full production-path verification completed; normal startup may continue subject to all other gates.

Only the last state can lead to ordinary delegation/effect admission.

## RED-first matrix (60 cases)

### Package authentication
1. valid package from trusted escrow key -> eligible;
2. unknown signer -> ignore/reject contribution;
3. revoked signer -> reject;
4. modified checkpoint digest -> reject;
5. modified manifest digest -> reject;
6. wrong logical history id -> reject;
7. malformed canonical encoding -> reject;
8. package containing forbidden private runtime secret -> audit regression failure.

### Quorum and independence
9. two signatures from same configured domain -> count once per policy;
10. two buckets sharing one credential/domain -> do not satisfy two-domain policy;
11. exact configured quorum -> eligible;
12. one below threshold -> fail closed;
13. owner quorum without required witness group -> fail closed;
14. witness quorum without owner group -> fail closed;
15. duplicate key appears in two groups contrary to policy -> reject policy;
16. stale policy attempts lower threshold -> reject rollback.

### Ordering / rollback
17. older valid checkpoint only -> cannot override independently known newer checkpoint;
18. newer checkpoint with valid parent consistency -> select newer;
19. newer sequence with broken parent -> reject;
20. same sequence, different root -> split view;
21. higher wall-clock time, lower sequence -> rollback reject;
22. archive backup matches stale checkpoint but not selected head -> reject backup;
23. foreign history root with valid signatures -> reject;
24. selected checkpoint omits newer authenticated manifest transition -> reject.

### Split view
25. quorum A supports root X and quorum B supports incomparable root Y -> `DR_SPLIT_VIEW`;
26. one compromised witness signs both roots -> does not resolve split;
27. operator chooses preferred root manually through ordinary admin API -> forbidden;
28. one root has more replicas -> no authority preference;
29. one root has newer timestamp only -> no authority preference;
30. consistency proof later shows Y extends X -> recompute, Y may become eligible;
31. consistency proof invalid -> remain split/fail closed;
32. split survives restart -> state remains fail closed.

### Key compromise
33. one escrow key compromised but quorum survives without it -> proceed excluding key;
34. compromised key signs stale root -> no rollback;
35. compromised domain plus honest threshold still selects same root -> eligible;
36. configured threshold believed compromised -> no automatic recovery;
37. emergency reduction of threshold through lost local state -> forbidden;
38. restored old policy resurrects revoked escrow key -> reject;
39. post-recovery key rotation parent-linked -> allowed after full verify;
40. worker/provider key cannot sign DR checkpoint -> reject authority class.

### Backup composition
41. exact archive bytes + no independent checkpoint -> insufficient for automatic recovery;
42. checkpoint + no archive bytes -> root may recover but normal startup still unavailable;
43. backup manifest self-signs matching archive -> not authority;
44. archive matches selected checkpoint digest -> eligible for normal DR byte restore;
45. semantically equivalent reserialization -> reject exact identity;
46. encrypted backup lacks decryption authority -> remain unavailable;
47. cross-domain bytes match selected digest -> location irrelevant;
48. copied escrow signature without package body -> reject.

### Crash / restart
49. crash before quorum selection -> recompute;
50. crash after selection before provenance commit -> recompute;
51. crash after provenance commit before ack -> detect exact committed transition;
52. stale recovery planner races with newer checkpoint -> CAS reject/replan;
53. partial local checkpoint reconstruction -> never treated as trusted;
54. restart while `DR_ROOT_RESTORED_VERIFYING` -> repeat full verification.

### Final admission
55. root restored but archive epoch missing -> no delegation/effects;
56. root+archive restored but LAB-090 activation unresolved -> no delegation/effects;
57. root+archive restored but stale worker session exists -> re-entry required;
58. full global verification succeeds -> recovery planner `NONE` required;
59. successful recovery creates independent DR-only provenance table -> regression failure;
60. historically consumed application key remains non-`MISS` across complete DR cycle.

## Audit conclusions

- The minimum safe automatic DR root recovery requires an independent pre-disaster observation of authority; backup bytes alone are insufficient.
- Witness/escrow quorum protects against one storage/admin domain lying about which checkpoint was current.
- Threshold recovery authority cannot solve compromise of its own threshold. At that boundary automation must stop and a human security ceremony must create a new explicitly documented epoch.
- Escrow should preserve public verification/checkpoint material and signatures, not private runtime mutation secrets.
- Recovery must rejoin the existing global provenance chain and then pass the ordinary full startup/delegation gates; DR is not a parallel authority system.

## Sources

- TUF FAQ — root-key compromise / out-of-band recovery: https://theupdateframework.io/docs/faq/
- TUF roles and metadata — root role and signature thresholds: https://theupdateframework.io/docs/metadata/
- C2SP Transparency Log Witness Protocol: https://c2sp.org/tlog-witness@main
- C2SP Transparency Log Trust Policy: https://c2sp.org/tlog-policy
- C2SP Transparency Log Checkpoints: https://c2sp.org/tlog-checkpoint@main
- RFC 6962 — Merkle consistency proofs: https://www.rfc-editor.org/rfc/rfc6962
- NIST SP 800-57 Part 1 Rev.5 — Recommendation for Key Management: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
