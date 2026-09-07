# Recovery-policy transparency bootstrap / offline-root custody / total-loss governance-root reconstitution v1

Status: `RECOVERY_POLICY_TRANSPARENCY_BOOTSTRAP_OFFLINE_ROOT_CUSTODY_TOTAL_LOSS_RECONSTITUTION_V1_FROZEN`

Date: 2026-09-08

Context: LAB-093 / #178. This is a design fallback only while LAB-086 exact executable validation remains unavailable. It does not substitute for executable RED/GREEN evidence.

## Question

How can `TimeFloorRecoveryAuthorityV1` recover when every ordinary and emergency recovery signer is unavailable, destroyed, or believed compromised, without silently inventing a new root of trust?

## Core conclusion

`TOTAL_SIGNER_LOSS` is not an ordinary key rotation.

If all currently trusted recovery-authority signing keys are lost/compromised **and** there is no independently authenticated continuity evidence capable of authorizing a successor, then the existing trust domain cannot cryptographically prove a unique legitimate successor root.

The only safe authority result inside the old trust domain is:

`RECOVERY_AUTHORITY_UNAVAILABLE_NO_CONTINUITY_PROOF`

A replacement root may still be established through an explicitly external organizational bootstrap, but that is a **new trust bootstrap event**, not a cryptographically continuous rotation. It must be represented as such and must never rewrite the old history into apparent continuity.

This follows the general trust-anchor model: RFC 9718 states that trust in a trust anchor is assumed and established outside the relying protocol; RFC 5011 can securely update anchors only after trust is already established. TUF similarly states that if a threshold of Root keys is compromised, Root metadata must be re-issued out of band.

## Security invariant

`NEW_ROOT_SIGNATURES != CONTINUITY_FROM_OLD_ROOT`

A candidate new root cannot prove its own legitimacy merely by signing a statement that it is the successor. Self-authorization is forbidden after total loss just as it is during ordinary root-policy rotation.

## Three distinct states

### 1. Ordinary rotation

At least one authorization path required by the predecessor policy remains valid. Use the normal predecessor+successor continuity protocol. No reconstitution semantics apply.

### 2. Recoverable disaster with independent continuity evidence

All online/ordinary signing capability may be gone, but a separately governed, previously bootstrapped continuity mechanism still exists, for example:

- offline predecessor root shares/keys that were not part of the failed signer set;
- a previously authenticated offline `RecoveryContinuityRootV1`;
- independently held archival continuity shares;
- a precommitted external governance key set whose digest/policy is already authenticated by the old trust domain;
- an authenticated transparency checkpoint containing a precommitted successor/reconstitution policy.

This remains a continuous recovery only if that mechanism was authenticated **before** the disaster and satisfies its own threshold/control-domain policy.

### 3. Total trust continuity loss

No still-trusted predecessor authorization path and no precommitted independent continuity authority remain.

The old domain must freeze authority-bearing mutation. A new root can be introduced only by an explicitly external bootstrap decision whose trust basis is visible to relying parties. The old domain must report continuity as broken.

## Proposed records

### `RecoveryContinuityRootV1`

Pre-disaster, offline-custodied authority used only for reconstitution, never for routine time-floor recovery.

Fields:

- `lineage_id`
- `continuity_root_generation`
- `public_keys[]`
- `threshold_policy`
- `control_domain_policy`
- `allowed_operations = {RECONSTITUTE_RECOVERY_POLICY}`
- `not_before` / `not_after`
- `predecessor_policy_digest`
- `publication_checkpoint_digest`
- `custody_manifest_digest`
- `ceremony_manifest_digest`

Its public definition must be authenticated by the currently trusted recovery governance before it is needed.

### `RootCustodyManifestV1`

Documents the intended offline custody boundary without storing secrets:

- hardware/token class;
- geographic/control-domain separation requirements;
- minimum number of independent custodians;
- dual-control requirements;
- backup-media policy;
- restore-test cadence;
- destruction/retirement procedure;
- compromise-reporting path;
- ceremony witness requirements.

NIST SP 800-57 is the donor for explicit cryptographic key lifecycle, backup, archival, compromise and recovery controls. Sigstore's root-signing repository is a production donor for distributed human keyholders and explicit signing events rather than one opaque administrator root.

### `GovernanceReconstitutionEvidenceV1`

For external rebootstrap after true continuity loss. It must not masquerade as cryptographic predecessor authorization.

Possible evidence classes, depending on the deployment's previously published charter:

- independently authenticated organizational charter/bylaws or constitutional authority;
- multi-party board/trustee/custodian decision;
- legal/court order where that legal authority is explicitly part of the system's governance model;
- signed decision from a predeclared external supervisory body;
- independently archived historical identity and policy records;
- public transparency notices and challenge window;
- relying-party/operator manual acceptance where no stronger root exists.

None of these classes is universally authoritative by itself. The accepted set must be declared in a pre-existing governance charter where possible. Otherwise the event is an explicit new bootstrap.

### `TrustDomainRebootstrapV1`

Represents a non-continuous replacement when the original authority cannot authenticate a successor.

Fields:

- `old_lineage_id`
- `new_lineage_id`
- `old_terminal_frontier_digest`
- `reason = TOTAL_CONTINUITY_LOSS`
- `governance_evidence_digests[]`
- `new_root_digest`
- `publication_checkpoint_digest`
- `effective_time_interval`
- `challenge_window`
- `manual_acceptance_required`

Crucial invariant: `new_lineage_id != old_lineage_id` unless there is authentic predecessor continuity. Reusing the old lineage identifier after total continuity loss would launder a new root into false historical continuity.

## Offline-root custody rules

1. Routine recovery signers and total-loss continuity roots must not share a single failure/control domain.
2. Offline continuity material should be inaccessible to normal runtime processes and ordinary recovery operators.
3. A threshold must require multiple independently controlled custodians; simple key replication is not independence.
4. Custody backup must itself preserve threshold separation. A single encrypted backup file containing every share recreates a one-object catastrophic failure.
5. Restore exercises must prove recoverability without exposing production private material to routine systems.
6. Every ceremony must produce a public/auditable manifest containing participant roles, key/public-share digests, policy generation, predecessor digest and resulting root digest.
7. Secret material is never stored in the transparency log; only commitments, public keys, policy and evidence hashes are published.

## Transparency bootstrap

A reconstitution event is not trusted merely because it appears on the same publication server that lost its root authority.

For continuous recovery, publication must chain from a checkpoint already trusted before the incident or from independent witnesses/archives that can prove that checkpoint.

For non-continuous rebootstrap, publication must explicitly say that continuity is broken and expose the new bootstrap package through multiple independent channels. RFC 9718 is the key donor: initial DNSSEC trust-anchor acceptance is an operator policy/out-of-band decision; in-band RFC 5011 succession only works once an anchor is already trusted.

## External-channel diversity

When true rebootstrap is unavoidable, relying parties should compare the candidate bootstrap package across independent channels such as:

- separately administered transparency mirrors;
- pre-existing public archives;
- organizational website and signed governance publication where that web PKI root is independently trusted;
- package/distribution channels under different operators;
- direct administrator/custodian distribution;
- physical/offline media for high-assurance deployments.

Channel count alone is not sufficient; channels sharing the same DNS, hosting, account recovery, signing key or operator may be one failure domain.

## Why TOFU is insufficient

A verifier that has lost every old trust anchor and simply accepts the first new root it sees is performing TOFU. That may be an explicit local operator policy, but it must be represented as `LOCAL_REBOOTSTRAP_TOFU`, not global continuity.

No protocol can recover the missing historical authentication fact from the new root itself.

## Compromise versus destruction

Total destruction and total compromise require different historical conclusions:

- if keys are proven destroyed without prior compromise, historical signatures before destruction may remain valid;
- if compromise onset is known, signatures before the safe boundary may remain valid;
- if compromise onset is unknown and all historical authority depends on those keys, historical trust becomes `UNKNOWN_HISTORICAL_RECOVERY_AUTHORITY` for the affected interval;
- a new bootstrap does not retroactively repair that uncertainty.

## Governance capture resistance

Emergency governance is dangerous because the incident itself creates pressure to lower thresholds. Therefore:

- thresholds cannot be lowered by the same failed/current root after total compromise;
- a new candidate root cannot authorize its own emergency policy;
- one administrator, one cloud account, one legal entity identity credential, or one current publication endpoint is insufficient unless the deployment explicitly chose that single point of trust beforehand;
- conflicting independently credible reconstitution packages produce `REBOOTSTRAP_GOVERNANCE_DISPUTE_NO_AUTOMATIC_ACCEPT`;
- min/max timestamp, first-seen, newest, longest-log or majority-of-current-endpoints rules must not resolve a root-governance fork.

## Acceptance model for relying verifiers

A verifier must distinguish:

- `CONTINUOUS_RECOVERY_VALID` — predecessor-authenticated continuity path exists;
- `CONTINUITY_RECOVERY_UNKNOWN` — evidence incomplete or disputed;
- `RECOVERY_AUTHORITY_UNAVAILABLE_NO_CONTINUITY_PROOF` — old domain cannot authorize mutation;
- `EXTERNAL_REBOOTSTRAP_PROPOSED` — new trust domain offered through governance bootstrap;
- `EXTERNAL_REBOOTSTRAP_ACCEPTED_LOCAL_POLICY` — this relying party explicitly accepted it;
- `REBOOTSTRAP_GOVERNANCE_DISPUTE_NO_AUTOMATIC_ACCEPT` — competing plausible roots exist.

The system must never collapse the final four states into `VALID_ROTATION`.

## RED-first matrix

1. all routine keys lost, offline continuity threshold intact -> continuous recovery allowed;
2. all routine keys compromised, offline continuity root independently intact -> continuous recovery only under precommitted policy;
3. offline continuity root was never authenticated before incident -> cannot authorize continuity;
4. candidate new root self-signs succession -> reject;
5. same cloud account controls routine and purported offline root -> independence failure;
6. all threshold shares stored in one backup archive -> independence failure;
7. predecessor public metadata exists but no private/authorized continuity signer -> metadata alone cannot authorize successor;
8. current publication server announces a new root after total compromise -> insufficient;
9. independent archive proves old checkpoint plus precommitted continuity root -> eligible continuity evidence;
10. archive proves history but contains no precommitted reconstitution authority -> cannot sign continuity;
11. two mutually incompatible continuity-root quorums both satisfy policy -> dispute/no automatic mutation;
12. true total continuity loss followed by same `lineage_id` reuse -> reject lineage laundering;
13. true total continuity loss followed by new lineage + explicit external bootstrap -> representable, local acceptance required;
14. TOFU new root presented as global continuity -> reject claim;
15. old compromised root countersigns new root after compromise onset -> insufficient;
16. compromise onset known after historical signature -> historical pre-boundary validation can survive;
17. compromise onset unknown -> dependent historical authority unknown;
18. one custodian unilaterally lowers reconstitution threshold -> reject;
19. governance charter was itself introduced only after incident -> cannot prove old-domain continuity;
20. pre-incident charter digest authenticated by old root and independently archived -> valid supporting evidence;
21. court/order evidence not declared as governing authority and conflicts with authenticated charter -> no automatic crypto continuity;
22. two legal/governance packages conflict -> dispute state;
23. rebootstrap package published through five URLs under one account/DNS operator -> one correlated channel;
24. rebootstrap package observed through independent archive + governance registry + separate operator channel -> stronger bootstrap evidence;
25. old root loss with surviving superior trust anchor -> recover through superior authority, not total-loss path;
26. all anchors revoked/deleted and no superior anchor -> fail closed inside old domain;
27. restore drill reconstructs threshold from separated custodians -> operational readiness evidence only, not a production rotation;
28. restore drill exposes all private shares to one runtime host -> custody violation;
29. ceremony transcript omits resulting public-root digest -> audit failure;
30. ceremony transcript contains secrets -> security failure;
31. new bootstrap retroactively labels old ambiguous signatures valid -> reject historical rewrite;
32. new bootstrap supersedes future authority while preserving old uncertainty -> allowed;
33. external rebootstrap package expires before local acceptance -> reject stale bootstrap;
34. local verifier accepts rebootstrap while another does not -> expected local-policy divergence, not protocol equivocation;
35. deployment claims universal acceptance based only on one verifier's local acceptance -> reject;
36. non-continuous rebootstrap later gains broad operator adoption -> adoption does not convert it into cryptographic historical continuity;
37. precommitted continuity root expired before incident -> reject unless policy explicitly permits an authenticated emergency grace path;
38. expired root signs itself a validity extension -> reject;
39. offline continuity root key destroyed but another threshold quorum survives -> continue with surviving quorum;
40. total destruction of every continuity signer with intact public archive -> archive preserves evidence but cannot mint successor authority by itself.

## Donors / primary sources

- RFC 9718, DNSSEC Trust Anchor Publication for the Root Zone (2025): trust anchor trust is established outside DNSSEC; RFC 5011 provides in-band succession only after initial trust exists. https://www.rfc-editor.org/rfc/rfc9718.html
- RFC 5011, Automated Updates of DNSSEC Trust Anchors: existing trust anchors authenticate new anchors; if all anchors are revoked/deleted and no superior trust point exists, the subtree is treated as insecure rather than silently acquiring a new anchor. https://www.rfc-editor.org/rfc/rfc5011.html
- TUF FAQ/spec guidance: if a threshold of Root keys is compromised, Root metadata must be re-issued out of band. https://theupdateframework.io/docs/faq/
- Sigstore root-signing: distributed hardware keyholders and explicit collaborative signing events are a production donor for offline/multi-party root custody. https://github.com/sigstore/root-signing
- NIST SP 800-57 Part 1 Rev. 5: lifecycle, protection, backup, compromise, archival and recovery of cryptographic keying material. https://doi.org/10.6028/NIST.SP.800-57pt1r5

## Frozen decision

`RECOVERY_POLICY_TRANSPARENCY_BOOTSTRAP_OFFLINE_ROOT_CUSTODY_TOTAL_LOSS_RECONSTITUTION_V1_FROZEN`

1. Total signer/root loss without independently authenticated continuity evidence is not recoverable as an in-domain cryptographic rotation.
2. The old authority must fail closed with `RECOVERY_AUTHORITY_UNAVAILABLE_NO_CONTINUITY_PROOF`.
3. Continuous disaster recovery is permitted only through a pre-disaster authenticated, independently controlled continuity root/policy.
4. If that too is lost, restoration requires an explicit external rebootstrap and a new trust lineage; relying parties must opt into that new bootstrap according to local/governance policy.
5. Rebootstrap cannot retroactively erase compromise uncertainty or fabricate continuity.
6. Offline-root custody must preserve threshold/control-domain separation in both primary and backup material.
7. All ceremonies, policies, root digests, terminal old frontiers, disputes and supersession decisions are append-only/publication evidence.
8. Conflicting fully credible reconstitution packages remain a governance dispute and block automatic authority mutation.

## Exact next research edge if execution remains blocked

Freeze **rebootstrap relying-party convergence / ecosystem split-brain / legacy-client quarantine and migration semantics**: define how a non-continuous new trust lineage propagates to heterogeneous verifiers without silently accepting it on stale clients; how old-lineage and new-lineage operations coexist or are quarantined; and what evidence is required before declaring ecosystem migration complete.