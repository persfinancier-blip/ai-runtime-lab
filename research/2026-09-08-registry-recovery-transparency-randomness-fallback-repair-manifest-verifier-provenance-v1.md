# Registry/recovery transparency, beacon fallback, repair-manifest witnessing, and verifier provenance v1

Date: 2026-09-08
Status: design contract / RED-first freeze; **no production implementation or behavioral PASS claimed**
Parent: LAB-093 / #178
Priority note: LAB-086 remains priority #1; this work is the recorded fallback because exact source execution is unavailable in this run.

## Frozen contract

`REGISTRY_RECOVERY_TRANSPARENCY_RANDOMNESS_FALLBACK_REPAIR_MANIFEST_VERIFIER_PROVENANCE_V1_FROZEN`

## Problem statement

Prior freezes established that a valid registry signature is not proof of factual destructive-domain independence, that a compromised registry authority cannot self-install a trusted successor, that challenge populations must be fixed before randomness, that withholding cannot authorize same-epoch reselection, that archive repair must preserve both reconstructability and independence, and that nominally multiple PQ verifier processes do not necessarily represent independent implementations.

Four residual authority gaps remain:

1. How does a relying party learn that a registry/recovery authority generation has been superseded or compromised without trusting only that same authority?
2. How can challenge selection survive randomness-beacon withholding or beacon compromise without enabling fallback-driven bias/downgrade?
3. How are repair-manifest generations made non-repudiable and globally auditable so a compromised repair coordinator cannot hide a stale/losing manifest?
4. What evidence is sufficient to count two PQ verifier implementations as genuinely independent rather than two wrappers around one parser/library/build chain?

## Primary donor mechanisms

### TUF root continuity and freeze boundary

TUF requires clients to retrieve intermediate root metadata generations and verify each N+1 root with thresholds from both the trusted predecessor and the new root. TUF also explicitly notes that repository control alone can freeze clients by withholding newer root metadata, bounded by trusted metadata expiration. This is a useful donor for continuity but also proves that a signed authority chain alone does not solve latestness/dissemination.

Source: https://theupdateframework.github.io/specification/draft/

### RFC 9162 append-only transparency

Certificate Transparency defines signed tree heads, inclusion/consistency proofs and monitor/auditor behavior. A monitor can fetch entries, reconstruct the tree, verify signed heads and retain signed evidence of log misbehavior. Consistency across query sources requires sharing/observing views rather than trusting one endpoint. This is the donor for independently witnessed authority/manifest publication.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### drand threshold beacon and resharing

drand group configuration binds node set, threshold and transition parameters; its group hash identifies configuration for resharing. Randomness is threshold-produced. Resharing changes participants while preserving the public-facing distributed key, and requires old/new threshold participation during transition. The chain root of trust is separate from the current network composition. This is useful for membership rotation, but a threshold beacon that cannot reach threshold still has an availability failure and does not justify silent local fallback.

Sources:
- https://docs.drand.love/docs/specification/
- https://docs.drand.love/docs/security-model/

### SLSA + Reproducible Builds independence warning

SLSA's verified reproducible-build guidance explicitly requires independent build platforms; multiple reproducers using the same vulnerable pipeline software can share one compromise mode. Reproducible Builds provides the byte-for-byte/hash comparison mechanism across environments. These are direct donors for verifier implementation/build provenance: equal outputs can corroborate one artifact, but independence must be demonstrated separately from output equality.

Sources:
- https://slsa.dev/spec/draft/faq
- https://reproducible-builds.org/docs/checksums/
- https://reproducible-builds.org/docs/adding-build-variance/

## Frozen semantic boundaries

### 1. Authority transparency

Hard rule:

`VALID_AUTHORITY_GENERATION != GLOBALLY_OBSERVED_CURRENT_AUTHORITY`

and:

`AUTHORITY_SELF_PUBLICATION != INDEPENDENT_SUPERSESSION_EVIDENCE`

Every consequential registry/recovery authority generation SHOULD have a canonical immutable `AuthorityGenerationStatementV1` containing at least:

- lineage ID;
- generation number;
- predecessor generation + digest;
- authority role and policy generation;
- signer/key set and threshold;
- activation/not-before frontier;
- supersedes/revokes references if applicable;
- compromise/recovery state;
- canonical statement digest.

Publication becomes a separate event recorded in one or more append-only transparency services. A relying party classifies evidence distinctly:

- `AUTHORITY_VALID_LOCALLY` — chain verifies against retained trust;
- `AUTHORITY_TRANSPARENTLY_PUBLISHED` — inclusion under an authenticated log checkpoint is proven;
- `AUTHORITY_WITNESS_QUORUM_OBSERVED` — policy-defined independent witnesses/cosigners observed a consistent checkpoint;
- `AUTHORITY_CURRENT_WITHIN_LATESTNESS_BOUND` — freshness/latestness policy is additionally satisfied.

No lower class implies a higher one.

### 2. Compromise/supersession discovery

A compromised authority cannot be the sole source declaring its own compromise or successor. `AuthorityStatusStatementV1` may originate from separately scoped compromise/recovery authorities and be transparency-published.

Hard rule:

`SAME_AUTHORITY_SELF_REVOCATION_ONLY != INDEPENDENT_COMPROMISE_PROOF`

A relying party that has evidence of a later independently authorized + transparently published generation MUST reject an older generation as stale even if that old generation still validates cryptographically.

If competing same-lineage/same-generation authenticated digests are observed, state is `AUTHORITY_EQUIVOCATION_CONFLICT`; do not apply last-writer-wins, newest timestamp, fastest mirror or majority-of-endpoints.

If compromise reaches the recovery-root threshold and no separately retained higher/out-of-band recovery anchor exists, same-lineage recovery remains unproven and requires the already frozen new-lineage/external rebootstrap path.

### 3. Beacon-set registry

Challenge randomness policy is versioned and independently authenticated as `RandomnessBeaconPolicyV1`:

- eligible beacon identities and immutable chain/root identifiers;
- threshold/fallback rule;
- independence/control-domain provenance;
- epoch and activation frontier;
- allowed delay/window;
- combination function and canonical transcript;
- predecessor policy digest.

Hard rules:

`BEACON_ENDPOINT_COUNT != INDEPENDENT_BEACON_COUNT`

`BEACON_KEY_ROTATION != NEW_INDEPENDENT_BEACON`

`BEACON_WITHHOLDING != AUTHORITY_TO_RESELECT_TARGETS`

### 4. Commit-before-randomness and fallback

Challenge epoch processing is:

1. commit canonical eligible population and policy generation;
2. publish/retain `ChallengePopulationCommitmentV1`;
3. only then observe randomness inputs;
4. derive the target set from the canonical transcript;
5. publish selection proof/transcript.

Fallback must be predeclared before the population commitment. It may not be invented after observing a bad/unavailable primary beacon.

Safe multi-beacon profiles:

- `B0_SINGLE`: one beacon; withholding => round unavailable.
- `B1_ORDERED_PREDECLARED`: fixed ordered list and fixed deadlines; first beacon satisfying its predeclared slot is used. This improves availability but exposes whichever eligible beacon owns the selected slot to bias if it can choose withholding after learning its value.
- `B2_COMBINE_ALL_REQUIRED`: cryptographic combination of all required beacon outputs; strongest anti-single-source bias but any missing input can halt the round.
- `B3_THRESHOLD_CONTRIBUTIONS`: combine a predeclared threshold of independent contributions under a frozen subset rule that cannot choose the "best" subset after values are known.

No policy may permit arbitrary post-value subset selection.

If withholding changes which value is used, the transcript MUST record the missing/late inputs and exact predeclared fallback rule. Repeated withholding is compromise/availability evidence and may trigger a later policy-generation rotation, never same-epoch reselection.

### 5. Beacon membership/threshold rotation

A new beacon policy generation requires predecessor continuity. For high-assurance rotations, donor semantics mirror TUF/drand:

- predecessor policy threshold authorizes the successor policy;
- successor policy threshold also authorizes itself when a new authority/key set is introduced;
- generation is monotonic;
- activation epoch is explicit;
- old and new policies cannot both silently govern the same epoch.

A drand resharing that preserves the same public key does not by itself prove unchanged administrative independence; network-composition provenance remains separately versioned.

### 6. Repair-manifest transparency

`RepairManifestV1` is canonical and immutable. At minimum it binds:

- archive/object identity;
- exact predecessor manifest digest/generation;
- source checkpoint/frontier;
- source erasure parameters and fragment digests;
- target placements/domain IDs;
- independence-evidence generation;
- registry generation;
- crypto-policy generation;
- repair plan and recovered/replaced shares;
- reconstructability result;
- independence result;
- coordinator identity;
- resulting manifest digest.

Repair commit is CAS-like against the exact predecessor manifest. A coordinator cannot publish two different successors for the same predecessor generation without producing an equivocation conflict.

Hard rule:

`REPAIR_SQL/OBJECT_COMMIT != AUTHORITATIVE_REPAIR_HISTORY_PUBLICATION`

A repair may be locally complete but remains `REPAIR_COMMITTED_NOT_TRANSPARENTLY_FINAL` until the manifest is included in the configured transparency/witness profile.

### 7. Stale/losing repair manifests

For a given archive lineage + manifest generation, two authenticated different digests are `REPAIR_MANIFEST_EQUIVOCATION_CONFLICT`. Do not select newest timestamp or "manifest currently returned by storage".

A later valid successor must name the exact predecessor digest, so a hidden losing branch cannot be merged away without explicit adjudication/recovery evidence.

Relying parties retain a `TrustedRepairFrontierV1` with last accepted manifest generation/digest and transparency checkpoint. Offline catch-up must prove continuity from that frontier; a fresh latest manifest alone is insufficient.

### 8. Witnessing repair manifests

Witnesses verify append-only checkpoint consistency and policy-defined publication conditions. They do **not** independently prove that the repair's claimed domain independence or reconstructability is semantically correct unless the witness role explicitly includes reproducible semantic verification.

Boundary:

`WITNESSED_REPAIR_MANIFEST != SEMANTICALLY_CORRECT_REPAIR`

Semantic validation remains separately reproducible from fragment hashes, checkpoints, registry/provenance evidence and frozen algorithms.

### 9. PQ verifier provenance

`VERIFIER_PROCESS_COUNT != VERIFIER_IMPLEMENTATION_DIVERSITY`

`DIFFERENT_BINARY_HASH != INDEPENDENT_IMPLEMENTATION`

`REPRODUCIBLE_EQUAL_OUTPUT != INDEPENDENT_CONTROL_DOMAIN`

Each verifier family admitted into a diversity threshold SHOULD carry `VerifierImplementationAttestationV1` covering:

- source repository + immutable revision/tree digest;
- parser/canonicalization implementation identity;
- cryptographic library implementation and version;
- compiler/toolchain identity;
- build recipe/environment digest;
- build platform/operator/control domain;
- dependency closure/SBOM digest;
- produced binary hash;
- reproducibility observations and independent reproducer identities;
- implementation-family declaration and evidence;
- known shared components with other admitted verifier families.

### 10. Counting verifier independence

Independence is vector-valued, not boolean. At minimum track:

- `I_SOURCE`: independently authored source lineage;
- `I_PARSER`: independent parsing/canonicalization implementation;
- `I_CRYPTO_IMPL`: independent crypto implementation/library;
- `I_TOOLCHAIN`: independent compiler/build toolchain lineage;
- `I_BUILD_CONTROL`: independently controlled build platform/operator;
- `I_RUNTIME`: independently controlled runtime/host domain.

A policy may require different levels for different threats. Example:

- protection against build-server compromise may accept same source/parser/crypto implementation but require independent build control + reproducible byte equality;
- protection against implementation bugs requires independent parser/crypto implementation families, so identical rebuilt binaries do not add diversity;
- protection against algorithm failure is impossible through implementation diversity alone and requires a distinct cryptographic algorithm/family per the already frozen hybrid/PQ policy.

### 11. Common-mode disclosure and re-appraisal

If two verifier families later prove to share an unrecorded common parser/library/build dependency, current diversity must be recomputed. Historical signatures/receipts remain evidence of what was observed; they are not erased. Current assurance can downgrade to `VERIFIER_DIVERSITY_INSUFFICIENT_POST_DISCLOSURE` until policy quorum is restored.

Late discovery of common provenance does not permit rewriting historical policy generations.

### 12. Reproducible-build evidence

Byte-for-byte reproducibility across independently controlled builders is valuable evidence that distributed binaries correspond to the declared build inputs. It does **not** prove source correctness, parser correctness, dependency correctness, or implementation independence.

Hard rule:

`REPRODUCIBLE_BUILD_VERIFIED != VERIFIER_SEMANTICS_VERIFIED`

For genuinely different implementations, cross-verification uses a shared canonical corpus + adversarial vectors and requires agreement on the exact canonical payload/result semantics, while retaining implementation provenance separately.

### 13. Fail-closed states

At minimum preserve these states rather than collapsing to generic failure:

- `AUTHORITY_LATESTNESS_UNKNOWN`
- `AUTHORITY_EQUIVOCATION_CONFLICT`
- `AUTHORITY_RECOVERY_CONTINUITY_UNPROVEN`
- `RANDOMNESS_ROUND_UNAVAILABLE`
- `RANDOMNESS_POLICY_EQUIVOCATION_CONFLICT`
- `RANDOMNESS_FALLBACK_TRANSCRIPT_INVALID`
- `REPAIR_COMMITTED_NOT_TRANSPARENTLY_FINAL`
- `REPAIR_MANIFEST_EQUIVOCATION_CONFLICT`
- `REPAIR_HISTORY_CATCHUP_INCOMPLETE`
- `VERIFIER_DIVERSITY_PROVEN`
- `VERIFIER_DIVERSITY_INSUFFICIENT`
- `VERIFIER_DIVERSITY_INSUFFICIENT_POST_DISCLOSURE`
- `VERIFIER_PROVENANCE_CONFLICT`

Unknown must never be silently promoted to current/independent/safe.

## RED-first regression matrix (64 cases)

### Authority transparency / recovery (1-16)
1. valid locally signed generation absent from transparency => not globally current;
2. independently witnessed later generation makes retained older generation stale;
3. same generation/different digest => equivocation;
4. old authority self-claims "no successor" while recovery log proves successor => reject old view;
5. compromised authority self-installs successor without recovery continuity => fail;
6. predecessor + successor thresholds valid => continuity accepted;
7. missing intermediate generation during offline catch-up => unknown;
8. mirror withholds later authority generation => latestness unknown/stale when independent evidence exists;
9. transparency inclusion without witness profile => publication class only;
10. witness quorum over inconsistent checkpoints => conflict;
11. witness key rotation under same operator does not increase independence;
12. late witness compromise re-appraises current assurance;
13. recovery-root threshold compromise without higher anchor => same-lineage recovery unproven;
14. new-lineage rebootstrap preserves prior bad lineage evidence;
15. stale-but-unexpired authority cannot override proven later generation;
16. authority transparency outage does not authorize self-latestness assertion.

### Randomness/fallback (17-32)
17. challenge population committed before randomness => accepted;
18. population recomputed after seeing primary output => reject;
19. primary withholding with undeclared local PRNG fallback => reject;
20. predeclared ordered fallback transcript => accepted only under exact policy;
21. scheduler chooses whichever available beacon yields preferred targets => reject;
22. all-required combination missing one source => unavailable, not reselection;
23. threshold combination uses non-canonical subset after values observed => reject;
24. repeated withholding recorded as evidence, next generation may rotate policy;
25. same-epoch policy rotation after bad randomness => reject;
26. two endpoints under one beacon/control root count as one;
27. beacon key rotation alone adds no independence;
28. drand resharing with same chain key retains chain identity but refreshes composition provenance;
29. old/new beacon policy overlap same epoch ambiguously => fail;
30. fallback transcript omits a late/missing primary => reject;
31. authenticated beacon output from wrong chain/root => reject;
32. replayed prior-epoch randomness under fresh challenge population => reject.

### Repair manifests (33-48)
33. exact predecessor CAS + transparent successor => accepted;
34. two successors from same predecessor/generation => equivocation;
35. storage returns only winning branch while retained checkpoint proves losing branch => conflict retained;
36. locally committed repair absent from required transparency => not final;
37. transparent manifest with false reconstructability claim => semantic verifier rejects;
38. witness quorum alone cannot bless false fragment hashes;
39. offline relying party skips manifest generation => catch-up incomplete;
40. later manifest not naming retained predecessor => reject;
41. stale registry generation used in repair => reject under current policy;
42. repair restores k shares but not independent domains => degraded state;
43. coordinator hides failed attempt then republishes same generation => conflict if prior admitted evidence exists;
44. manifest witness compromise re-appraises current publication assurance;
45. same digest replicated to many mirrors does not increase witness independence;
46. archived old manifest remains reproducible after coordinator loss;
47. missing predecessor manifest bytes but retained digest only => continuity can be authenticated but semantic revalidation may be nonreproducible;
48. recovery preserves equivocation evidence and starts explicit corrected lineage.

### Verifier provenance/diversity (49-64)
49. two processes same binary => one implementation family;
50. two differently hashed builds from same source/parser/crypto library => not independent implementation by hash alone;
51. same source rebuilt byte-identically by independent builders => build provenance corroborated, implementation diversity unchanged;
52. different wrappers around same parser/crypto library => shared family for affected threats;
53. independent parser + same crypto library => parser-diverse but crypto-implementation-common;
54. same parser + independent crypto libraries => crypto-implementation-diverse but parser-common;
55. independent source/parser/crypto/build control => high implementation diversity;
56. two builders under same cloud/admin credential => build-control diversity false;
57. late SBOM evidence reveals common vulnerable parser => current diversity recomputed downward;
58. disagreement between independent verifiers => fail closed, do not majority-vote without explicit adjudication policy;
59. algorithm cryptanalytic break affects all implementations => diversity does not restore assurance;
60. hybrid-required policy loses PQ verifier => no classical-only downgrade;
61. provenance attestation signed by verifier itself only => evidence, not independent provenance authority;
62. reproducible build with wrong source commitment => reject;
63. source/toolchain attestation generation rollback => reject;
64. historical verdicts remain evidence after verifier compromise but current reliance is re-appraised.

## Implementation direction when executable source is available

Do not implement this freeze before higher-priority exact gates. When LAB-093+ execution begins, tests should precede production code. Prefer small typed canonical records plus append-only state transitions rather than a broad mutable manager object. Reuse existing transparency/checkpoint, registry-generation, provenance and durable frontier abstractions rather than creating parallel authority graphs.

## Audit conclusion

The central rule is that **continuity, publication, latestness, semantic correctness, randomness unpredictability, reconstructability, and implementation independence are separate claims**. No signature count, endpoint count, replica count, process count or binary count is allowed to launder one claim into another.

Frozen result: `REGISTRY_RECOVERY_TRANSPARENCY_RANDOMNESS_FALLBACK_REPAIR_MANIFEST_VERIFIER_PROVENANCE_V1_FROZEN`.
