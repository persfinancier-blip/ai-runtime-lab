# Independence Registry / Challenge Anti-Collusion / Repair / Renewal-PQ Migration V1

Status: **FROZEN DESIGN CONTRACT — executable RED/GREEN still required**
Date: 2026-09-08
Issue family: LAB-093/#178 follow-up while LAB-086 exact-source execution remains blocked.

## Contract name

`INDEPENDENCE_REGISTRY_CHALLENGE_REPAIR_RENEWAL_PQ_MIGRATION_V1_FROZEN`

## Scope

This contract closes five unresolved assurance gaps left by the destructive-domain / erasure-archive / long-term-evidence work:

1. lifecycle authority for the registry that defines trusted destructive domains;
2. admission/retirement rules that cannot silently launder failed members out of the denominator;
3. challenge scheduling that remains useful when scheduler/verifier/storage operators may collude;
4. erasure-code repair that preserves the independence denominator rather than merely restoring share count;
5. recursive compromise handling for evidence-renewal authorities and ordered classical -> hybrid/PQ migration.

This is design evidence, not executable proof.

## Primary safety boundaries

- `REGISTRY_MEMBERSHIP != INDEPENDENCE_PROVEN`
- `MEMBER_RETIREMENT != HISTORICAL_DENOMINATOR_ERASURE`
- `RANDOM_LOOKING_CHALLENGE != UNPREDICTABLE_CHALLENGE`
- `SHARE_COUNT_RESTORED != INDEPENDENCE_RESTORED`
- `NEW_RENEWAL_SIGNATURE != OLD_EVIDENCE_REHABILITATED`
- `HYBRID_PRESENT != PQ_ASSURANCE_ESTABLISHED`

## 1. Independence-evidence registry lifecycle

Define `IndependenceRegistryV1` as versioned authenticated state:

- registry lineage + generation;
- member/domain IDs;
- control/provenance vector per domain (operator, cloud/account, deletion authority, KMS/root, replication controller, recovery credential, upstream storage/control dependencies);
- admission evidence digest;
- challenge/recovery-drill evidence digests;
- status: `CANDIDATE`, `ACTIVE`, `QUARANTINED`, `RETIRED`, `COMPROMISED`;
- effective-from generation;
- retirement reason and superseding domain, if any;
- policy generation and authority threshold.

Same lineage + same generation + different authenticated registry digest => `INDEPENDENCE_REGISTRY_EQUIVOCATION_CONFLICT`.

No last-writer-wins, newest timestamp, fastest mirror, or endpoint majority may resolve that conflict.

### Authority separation

Registry lifecycle authority must not be the sole attester of member independence. Prefer separation between:

- domain evidence producer;
- challenge scheduler;
- verifier/auditor;
- registry adjudication authority;
- recovery root.

A threshold-compromised registry authority cannot self-appoint a trusted successor. Recovery must chain through an independently controlled higher/recovery authority or explicit out-of-band/new-lineage bootstrap.

## 2. Admission and retirement without denominator laundering

A new domain becomes `ACTIVE` only after policy-defined evidence shows that it is not merely a new endpoint/key/region under an existing destructive/control domain.

Minimum admission evidence should include:

- provenance/control vector;
- independently retained identity and configuration evidence;
- at least one challenge/retrievability success;
- for high assurance, an asymmetric recovery drill demonstrating restoration while a pre-existing domain/control path is disabled;
- conflict check against known common dependencies.

### Retirement rule

Retiring a failed/compromised domain does **not** retroactively reduce the denominator used to evaluate earlier durability promises.

Example: a policy promised survival across 3 independent destructive domains, one fails, and governance removes it. Historical evaluation remains `3-domain promise with 1 failed member`, not `2-of-2 all healthy`.

Therefore retain:

- `historical_required_denominator`;
- `current_active_denominator`;
- `current_verified_independent_denominator`;
- per-generation member set.

A repair/replacement domain is a new member generation, not a relabeling of the failed member.

## 3. Challenge scheduler anti-collusion / unpredictability

Possession/retrievability challenges remain useful only if the storage side cannot know sufficiently early which object/share/range will be checked.

Define `ChallengeRoundV1`:

- policy generation;
- committed eligible population digest before randomness disclosure;
- challenge epoch;
- randomness source(s) and transcript digest;
- derived target/sample positions;
- nonce;
- response deadline;
- verifier set;
- result/evidence digest.

### Commit-before-randomness

The eligible archive/member population must be committed before challenge randomness is revealed. Otherwise a colluding scheduler can adaptively choose only healthy objects/members.

### Randomness independence

Scheduler-local PRNG output alone is insufficient when scheduler compromise is in scope. High-assurance profiles should derive target selection from multiple independently controlled contributions or a public/unbiasable-after-commit randomness source, binding the final seed to the precommitted population and epoch.

At least one contribution must remain unknown to the storage operator until after population commitment; otherwise unpredictability assurance degrades to `CHALLENGE_COLLUSION_RESISTANCE_UNKNOWN`.

### Verifier separation

A verifier may check response correctness but must not be allowed to redefine the eligible population after seeing failures. Failed/timed-out members remain in the round record.

Repeated suspiciously perfect outcomes with correlated scheduler/operator control are risk evidence, not proof of independence.

## 4. Archive repair without denominator laundering

Erasure-code repair has two separate objectives:

1. restore reconstructability (`>= k` valid shares);
2. restore policy-required independent destructive-domain coverage.

These must be evaluated separately.

Define `ArchiveRepairPlanV1` with:

- source archive root/checkpoint;
- coding parameters `k,n`;
- damaged/missing shares;
- source domains used for reconstruction;
- proposed destination domain;
- destination provenance vector;
- independence-policy generation;
- pre/post verified independent-domain counts;
- byte-exact reconstruction verification result;
- new share commitments and archive manifest generation.

### Forbidden repair patterns

- replacing a failed domain with a new bucket under the same cloud account and counting it as independent;
- copying two lost shares onto one surviving destructive domain and counting `n` shares as `n` independent domains;
- silently shrinking the policy denominator to the currently surviving set;
- repairing from bytes that do not verify against the retained canonical archive root/checkpoint;
- overwriting the only historical manifest rather than append-only supersession.

If reconstructability is restored but independence is not, state must be explicit, e.g. `RECONSTRUCTABLE_BUT_INDEPENDENCE_DEGRADED`.

## 5. Renewal-authority compromise recursion

RFC 4998 distinguishes timestamp renewal from hash-tree renewal and requires renewal before the old mechanism becomes untrustworthy. The same recursion applies to the authority issuing long-term preservation evidence.

Define `EvidenceRenewalAuthorityV1` with versioned keys, algorithm suite, validity/acceptability interval, recovery authority, and provenance/control domain.

### Rules

- compromise of a renewal TSA/authority after issuance reopens **current reliance** on evidence whose validity depends on that authority;
- historical receipts remain append-only facts;
- a compromised renewal authority cannot self-declare all its earlier renewals sound nor self-bootstrap its trusted successor;
- if an older evidence chain was renewed while both old and new mechanisms were still acceptable, the later independent renewal can preserve continuity;
- if the only prior binding was already broken before renewal, a new signature/hash merely authenticates the bytes presented now and cannot recreate historical authenticity.

## 6. Classical -> hybrid/PQ migration ordering

Current NIST guidance says organizations should begin migrating to standardized PQC now; FIPS 203/204/205 are available, and NIST IR 8547 defines transition states such as acceptable/deprecated/disallowed/legacy-use for quantum-vulnerable algorithms.

For long-lived archive evidence, migration must be **overlapping**, not cliff-edge.

Recommended ordering:

1. inventory all classical signature/hash/time-stamp dependencies and their acceptable-through windows;
2. introduce PQ-capable verification/signing support before classical evidence exits its acceptable window;
3. issue a **hybrid renewal** that binds the complete prior evidence chain + protected data/root while the classical binding is still trustworthy;
4. independently verify both classical and PQ components and persist algorithm/policy generations;
5. keep classical verification for historical/legacy validation as policy permits, but do not use a disallowed classical component as the sole basis for current authenticity;
6. after the overlap period and successful re-appraisal, permit PQ-only future renewals only when the governing policy explicitly authorizes them;
7. preserve the prior hybrid/classical chain append-only for auditability.

### Hybrid semantics

`HYBRID` must have explicit policy semantics. Two common modes differ materially:

- `AND`: both classical and PQ signatures/evidence must verify;
- `OR/transition`: either component can carry acceptance during a staged rollout.

For long-term evidence migration where either cryptographic family may later fail, a stronger transitional policy is normally `AND` at creation/renewal plus later policy-driven re-appraisal; silently treating hybrid as OR can create downgrade paths.

If PQ validation is unavailable or unsupported, the object must not be labeled PQ-protected merely because a PQ field exists.

## 7. Common-mode provenance and challenge evidence

Independence should be evaluated over destructive/control domains, not endpoint count. Registry evidence should record common dependencies including:

- cloud/provider account;
- operator/admin organization;
- deletion credential/API path;
- KMS/HSM root or recovery authority;
- firmware/storage implementation lineage;
- replication controller;
- billing/tenant suspension domain;
- upstream storage backend;
- network/control plane where its compromise can destroy or suppress all copies.

Unknown provenance remains `INDEPENDENCE_UNKNOWN`; it is not rounded up to independent.

## 8. RED-first matrix (48 cases)

Before production refactor, executable tests should cover at least these classes (expand each with positive + negative controls):

### Registry lifecycle (12)
1. valid new independent member admission;
2. same-account endpoint rejected as new independent member;
3. same-generation conflicting registry digest;
4. unauthorized admission;
5. unauthorized retirement;
6. retirement does not rewrite historical denominator;
7. replacement creates new member generation;
8. compromised registry authority cannot self-recover;
9. stale registry replay;
10. offline catch-up across multiple membership generations;
11. late common-control discovery reopens current assurance;
12. crash-safe registry frontier persistence.

### Challenge anti-collusion (12)
13. population committed before randomness;
14. adaptive post-randomness population change rejected;
15. reused nonce rejected;
16. stale round replay rejected;
17. scheduler-only randomness marked weak when scheduler compromised;
18. independent contribution changes target selection;
19. withheld randomness contribution -> explicit unknown/failure;
20. verifier cannot remove failed member from eligible set;
21. timeout remains durable evidence;
22. colluding scheduler/operator transcript conflict detected;
23. challenge targets bind archive/member generation;
24. restart preserves unfinished round semantics.

### Repair / denominator (12)
25. reconstruct exact bytes from any valid k shares;
26. reconstructed bytes fail root -> repair abort;
27. replacement in independent domain restores denominator;
28. replacement under shared account does not restore denominator;
29. share count restored but independence degraded state;
30. policy denominator cannot silently shrink;
31. failed member remains historical evidence;
32. repair manifest append-only supersession;
33. missing reconstruction manifest -> fail closed;
34. missing retained source checkpoint -> fail closed;
35. repair after late provenance compromise triggers re-appraisal;
36. multi-share placement on one domain counted once.

### Renewal / PQ transition (12)
37. timestamp renewal before TSA/key expiry;
38. hash-tree renewal before content-hash deprecation;
39. renewal after sole old binding is already broken does not restore history;
40. renewal-authority compromise reopens current reliance;
41. compromised renewal authority cannot self-recover;
42. hybrid renewal verifies classical + PQ components under AND policy;
43. missing/invalid PQ component fails AND policy;
44. OR semantics require explicit policy generation;
45. downgrade from AND to OR without authorized policy transition rejected;
46. classical-only current reliance rejected after classical disallowed date;
47. historical classical legacy verification retained where policy permits;
48. offline verifier catches up across algorithm/policy generations without skipping transition evidence.

## 9. Primary donors / evidence

- RFC 4998 Evidence Record Syntax: long-term evidence requires renewal before mechanisms become weak; timestamp renewal and hash-tree renewal are distinct, and hash-tree renewal requires access to archived objects + prior evidence chain.
- NIST Post-Quantum Cryptography project (current as of 2026-09-08): FIPS 203/204/205 are finalized and NIST states organizations should begin migration now.
- NIST IR 8547 (initial public draft): transition terminology includes acceptable, deprecated, disallowed, and legacy-use states; migration planning must account for algorithm lifetimes and staged replacement.
- Tahoe-LAFS architecture/documentation remains a donor for k-of-N erasure survivability and integrity separation, but k-of-N storage does not itself prove administrative/destructive independence.

## Decision

Freeze `INDEPENDENCE_REGISTRY_CHALLENGE_REPAIR_RENEWAL_PQ_MIGRATION_V1_FROZEN` as the next LAB-093 design boundary. It does **not** close LAB-086 or any executable gate. Implementation must be RED-first and compose with the previously frozen authority/freshness/retention/omission contracts.
