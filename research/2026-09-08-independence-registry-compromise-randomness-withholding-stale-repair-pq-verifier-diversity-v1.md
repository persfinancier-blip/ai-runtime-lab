# Independence registry compromise, randomness withholding, stale-repair races, and PQ verifier diversity — v1

Date: 2026-09-08
Status: DESIGN FROZEN / executable RED→GREEN pending
Parent: LAB-093 / #178
Priority note: this does **not** supersede LAB-086. Exact LAB-086 source execution was attempted first in this run and failed before repository execution because direct git transport could not resolve `github.com`.

## Objective

Close four remaining authority/survivability gaps from the previous independence-registry / anti-collusion / archive-repair / PQ-migration design freezes:

1. what happens when the authority that defines the independence registry is itself compromised;
2. what challenge selection means when committed randomness contributors withhold after the eligible population is frozen;
3. how concurrent archive repairs avoid acting on stale membership/manifests and silently laundering a degraded denominator;
4. how hybrid/PQ evidence avoids verifier monoculture and downgrade when one verifier implementation/family is compromised or unavailable.

The result is a contract for future regression-first implementation, not executable proof.

## Current-run capability evidence

Attempted exact checkout path first:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto11
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

GitHub connector reads/writes remain available. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, and no new LAB-086 behavioral/compile PASS is claimed.

## Primary donors

### Distributed randomness

- drand protocol specification: a beacon round is a threshold BLS signature assembled from at least the configured threshold of partial signatures, with chained mode binding a round to the prior signature. This provides a useful donor for threshold availability and public verification, but threshold beacons can still miss a round when too many contributors withhold. <https://docs.drand.love/docs/specification/>
- drand cryptography overview: threshold cryptography removes a single participant as a correctness authority and requires a threshold of participants to produce the beacon. <https://docs.drand.love/docs/cryptography/>
- RFC 9381 (VRFs): uniqueness and pseudorandomness/unpredictability properties are useful for deterministic per-member contributions, while the RFC also makes clear that key-generation assumptions matter. <https://www.rfc-editor.org/rfc/rfc9381.html>

### Erasure repair / reconstructability

- Tahoe-LAFS architecture: immutable data is erasure-coded into `N` shares and recoverable from `K`; this is a useful donor for separating reconstruction threshold from storage-server count. <https://tahoe-lafs.org/trac/tahoe-lafs/browser/trunk/docs/about-tahoe.rst>
- Tahoe-LAFS performance/repair documentation distinguishes checking/verifying/repairing and explicitly models `K` required shares and `N` total shares. <https://tahoe-lafs.org/trac/tahoe-lafs/browser/docs/performance.rst>

### PQ migration / hybrid anti-downgrade

- NIST PQC guidance: FIPS 203/204/205 are standardized and migration should proceed now; NIST also continues evaluating additional algorithm families, including diversity/backup candidates. <https://www.nist.gov/pqc>
- NIST selected HQC as a backup KEM based on a different mathematical family from ML-KEM, explicitly motivating algorithmic diversity in case weaknesses are found. <https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption>
- August 2026 IETF TLS composite-signature work explicitly warns that accepting a stand-alone component where composite protection is required is a downgrade and that prevention is a relying-party policy obligation. <https://datatracker.ietf.org/doc/draft-reddy-tls-composite-mldsa/11/>
- September 2026 CFRG draft on strong-unforgeability hybrid signatures binds the PQ signature to the message plus traditional signature, illustrating that composition semantics matter and that merely carrying two signatures is not sufficient to define assurance. <https://www.ietf.org/ietf-ftp/internet-drafts/draft-prabel-cfrg-suf-hybrid-sigs-02.html>

## Frozen contract name

`INDEPENDENCE_REGISTRY_AUTHORITY_RECURSION_RANDOMNESS_WITHHOLDING_STALE_REPAIR_PQ_VERIFIER_DIVERSITY_V1_FROZEN`

## 1. Registry authority compromise recursion

### Core boundary

```text
VALID_REGISTRY_SIGNATURE
  != CURRENT_REGISTRY_AUTHORITY_TRUSTWORTHY
  != MEMBER_INDEPENDENCE_TRUE
  != HISTORICAL_REGISTRY_STATE_ERASED
```

A valid registry signature proves that a key authorized under some accepted authority generation signed the statement. It does not prove that the authority was uncompromised at signing time, and it does not make the registry's assertions about destructive-domain independence intrinsically true.

### Required registry object

Conceptual `IndependenceRegistryGenerationV1`:

```text
registry_lineage_id
registry_generation
predecessor_digest
membership_generation
member_records[]
independence_policy_digest
challenge_policy_digest
repair_policy_digest
crypto_policy_digest
issued_at_evidence
signing_authority_generation
recovery_authority_generation
transparency_receipt_set
witness_quorum_evidence
```

Each `member_record` must retain stable provenance identity and control-domain claims rather than only endpoints:

```text
member_id
storage_identity
operator_domain
administrative_domain
credential_domain
kms_or_key_domain
delete_authority_domain
billing/control-account domain
network/control-plane domain
software/firmware family
upstream service dependencies
admission_generation
retirement_generation?
```

### Compromise semantics

If compromise evidence reaches the registry-signing authority:

- existing registry generations remain historical signed artifacts;
- **current reliance** on assertions issued inside the affected compromise interval is re-appraised;
- registry statements are not silently rewritten or deleted;
- member independence cannot be restored merely by re-signing identical claims with a new key;
- a successor registry authority requires separately authorized continuity/recovery evidence;
- if the recovery root is also within the compromised control domain and no independent higher/out-of-band anchor exists, same-lineage recovery is `UNPROVEN` and must fail closed or rebootstrap into a new lineage according to the previously frozen recovery contract.

### Historical denominator rule

```text
REGISTRY_AUTHORITY_COMPROMISE != HISTORICAL_DENOMINATOR_SHRINK
```

If a generation required 4 independently controlled destructive domains, later compromise of the registry authority does not convert that historical requirement into 3-of-3. It may make the assurance of the recorded independence claims uncertain, but it does not alter the denominator that was required when the evidence was created.

### Re-admission after compromise

Members admitted only under the compromised interval require fresh re-admission evidence under the recovered authority. The fresh generation must preserve the old member identity/history and record whether the member is:

- `REVALIDATED_INDEPENDENT`;
- `REVALIDATED_DEPENDENT`;
- `REVALIDATION_UNKNOWN`;
- `RETIRED_WITH_HISTORY_RETAINED`.

No member inherits `independent=true` merely because its endpoint/key is unchanged.

## 2. Randomness withholding after population commitment

Previous freeze required `commit(population) -> reveal randomness -> select challenge`. This closes target-selection bias by a scheduler that sees randomness before freezing the eligible population. It does **not** by itself guarantee progress when randomness contributors withhold.

### Core boundaries

```text
POPULATION_COMMITTED != RANDOMNESS_AVAILABLE
RANDOMNESS_CONTRIBUTOR_COUNT != INDEPENDENT_RANDOMNESS_DOMAINS
WITHHOLDING != PERMISSION_TO_RECOMMIT_POPULATION
```

If contributors can force a recommit after learning who would be challenged, withholding becomes a selection-bias primitive.

### Round object

Conceptual `ChallengeRandomnessRoundV1`:

```text
round_id
epoch
population_commitment
population_generation
randomness_policy_generation
contributor_set_generation
commit_deadline
reveal/beacon_deadline
contributions_or_beacon_proof
final_randomness?
outcome
```

Outcomes:

- `RANDOMNESS_COMPLETE`;
- `RANDOMNESS_PARTIAL_POLICY_SATISFIED`;
- `RANDOMNESS_WITHHELD_QUORUM_LOST`;
- `RANDOMNESS_EQUIVOCATION_CONFLICT`;
- `ROUND_EXPIRED_WITHOUT_SELECTION`.

### Preferred policy

For consequential challenge rounds, prefer a threshold public randomness beacon or a combine-after-commit construction whose output remains unbiased provided at least one required contribution is unknown/uncontrolled before commitment.

A practical composition can be:

```text
R = H(
  domain_separator ||
  epoch ||
  population_commitment ||
  external_threshold_beacon ||
  optional independent local commitments/reveals
)
```

The external threshold beacon supplies publicly verifiable round identity. Optional committed local entropy can reduce reliance on one beacon family, but only if local contributions cannot be selectively omitted after their value becomes known.

### Withholding rule

If the policy-required randomness threshold is not reached after population commitment:

1. do not choose a substitute population for the same round;
2. do not use scheduler-local fallback randomness unless that fallback was frozen in the policy **before** the round;
3. record the round as failed/withheld;
4. keep the same eligible population commitment as historical evidence;
5. start a new round only under a monotonically new `round_id/epoch`, with a new commitment and explicit reason;
6. count repeated contributor withholding as availability/compromise evidence against the contributor/control domain.

This trades liveness for anti-bias rather than silently laundering a targeted avoidance attack into a valid challenge.

### Deterministic fallback caveat

A hash of already public data is reproducible but not unpredictable. It is acceptable only where unpredictability is not required. It must not be described as anti-collusion randomness merely because it “looks random.”

## 3. Concurrent repair and stale-manifest race safety

### Core boundary

```text
VALID_OLD_MANIFEST != AUTHORITY_TO_REPAIR_CURRENT_GENERATION
K_VALID_SHARES != CURRENT_POLICY_DENOMINATOR_SATISFIED
```

A repair job that begins under membership generation `g` must not publish a “healthy” result after registry/provenance state has advanced to `g+1` unless it revalidates the exact assumptions that authorize placement.

### Repair lease / compare-and-swap contract

Conceptual `RepairPlanV1` must bind:

```text
archive_id
source_manifest_digest
source_checkpoint/root
required_k
required_n
required_independent_domain_count
registry_generation
member_set_digest
independence_evidence_frontier
crypto_policy_generation
repair_policy_generation
plan_nonce
created_at_evidence
```

Before **placement**, and again before **commit**, the repair coordinator must compare the authoritative current state to the plan.

Commit is allowed only if:

- the source manifest/checkpoint still matches the archive lineage;
- registry generation and relevant member/control-domain facts remain compatible;
- no selected target has become retired/compromised/dependent;
- the resulting share set independently satisfies `>=k` reconstruction and the required destructive-domain denominator;
- encryption/key/manifest dependencies remain available and policy-valid;
- no concurrent repair has already committed a newer manifest generation.

### Stale-plan outcomes

- `REPAIR_PLAN_STALE_REPLAN_REQUIRED` — relevant state changed before write.
- `REPAIR_RACE_LOST_SUPERSEDED` — another valid repair committed first.
- `RECONSTRUCTABLE_BUT_INDEPENDENCE_DEGRADED` — bytes can be reconstructed but denominator cannot be proven.
- `REPAIR_COMMITTED_POLICY_SATISFIED` — both reconstruction and independence gates pass.

### Manifest commit rule

Use a monotonic manifest generation and exact predecessor digest. A repair commit conceptually behaves like CAS:

```text
commit(new_manifest)
  only if current_manifest_digest == source_manifest_digest
  and current_registry/provenance frontier satisfies plan predicates
```

If CAS fails, the job must re-read and re-plan; it must not “merge” target placements by counting shares from incompatible stale plans without full re-evaluation.

### Orphaned writes

Shares written by a plan that loses the commit race are untrusted/orphan candidates until a later current plan explicitly validates and adopts them. Physical presence does not imply membership in the authoritative archive manifest.

## 4. PQ verifier diversity and hybrid downgrade resistance

### Core boundaries

```text
TWO_SIGNATURE_COMPONENTS != TWO_INDEPENDENT_VERIFIERS
TWO_VERIFIER_PROCESSES != TWO_IMPLEMENTATION_FAMILIES
HYBRID_PARSE_SUCCESS != HYBRID_POLICY_SUCCESS
COMPONENT_UNAVAILABLE != PERMISSION_TO_DOWNGRADE
```

A system that verifies both classical and PQ signatures in the same library/build/runtime/control domain can still have a common parser/implementation fault. Cryptographic algorithm diversity and implementation diversity are separate dimensions.

### Assurance vector

Every consequential hybrid verification result should retain at least:

```text
classical_algorithm
classical_key_generation
classical_verifier_implementation_id
classical_verifier_version/build digest
pq_algorithm
pq_parameter_set
pq_key_generation
pq_verifier_implementation_id
pq_verifier_version/build digest
parsing/canonicalization implementation id
policy_generation
composition_mode
component_results
cross-check result
```

### Composition policy

The policy must be explicit:

- `AND`: both classical and PQ components must verify;
- `OR`: either may verify;
- `TRANSITIONAL`: a versioned rule with exact dates/generations/authority for changing requirements.

For evidence created specifically to survive uncertainty in either family, **AND-style creation and renewal is the default frozen high-assurance profile**. The verifier must not silently reinterpret AND evidence as OR because one implementation is unavailable.

### Anti-downgrade rule

If a lineage has established `HYBRID_REQUIRED` at generation `g`, a relying party may not later accept classical-only or PQ-only evidence for the same assurance class unless a separately authenticated policy transition explicitly permits it.

The August 2026 TLS composite draft makes this same relying-party point: accepting stand-alone ML-DSA where composite protection is required enables downgrade of the composite assurance. This lab generalizes that to durable evidence verification.

### Verifier monoculture

For high-value archival/recovery evidence, define a verifier-diversity profile. Example:

- PQ algorithm verification succeeds in implementation family A;
- a second independently sourced implementation family B independently parses the canonical payload and verifies the same PQ component;
- classical verification is separately executed;
- all implementations consume a byte-identical canonical payload digest;
- disagreement is a conflict, never majority-by-process-count.

Two containers built from the same library commit do not count as implementation diversity.

### Compromised PQ verifier

If one PQ verifier family is later shown compromised:

- its historical result remains recorded;
- current reliance on evidence that depended only on that verifier family is re-opened;
- if a second independently implemented verifier can reproduce the same canonical verification under a still-accepted algorithm, current reliance may be restored under policy;
- if no independent verifier exists, result is `PQ_VERIFICATION_ASSURANCE_UNKNOWN`, not classical-only success;
- no automatic downgrade from `HYBRID_REQUIRED` to classical-only is permitted.

### Algorithm break vs verifier bug

Keep separate:

```text
ALGORITHM_COMPROMISE
VERIFIER_IMPLEMENTATION_COMPROMISE
PARSER/CANONICALIZATION_COMPROMISE
KEY_COMPROMISE
```

A second implementation can help against implementation bugs; it cannot rescue an algorithm family that is cryptographically broken. Conversely, replacing the algorithm does not automatically repair a compromised canonicalization/parser path.

## 5. Recursion and authority graph

The combined authority graph is deliberately non-circular:

```text
registry authority
  -> defines member/policy generations
independence evidence producers
  -> provide provenance/challenge/recovery facts
randomness authority/contributors
  -> select audit targets after population commitment
repair coordinator
  -> executes only against frozen current generations
archive manifest authority
  -> commits authoritative share membership
crypto-policy authority
  -> defines hybrid/PQ requirements
verifier implementations
  -> produce reproducible verification evidence
recovery root
  -> can replace compromised authorities under separately controlled continuity
transparency/witness layer
  -> preserves append-only publication/equivocation evidence
```

No one role should be able to both redefine its own denominator and certify that the new denominator is independent.

## 6. State machine summary

### Registry

```text
ACTIVE
 -> COMPROMISE_EVIDENCE
 -> QUARANTINED_FOR_CURRENT_RELIANCE
 -> REAPPRAISED
 -> RECOVERED_SAME_LINEAGE
    | NEW_LINEAGE_REBOOTSTRAP
    | UNPROVEN
```

### Challenge randomness

```text
POPULATION_COMMITTED
 -> RANDOMNESS_PENDING
 -> RANDOMNESS_COMPLETE -> SELECTION_FIXED -> CHALLENGE_EXECUTED
 -> WITHHELD -> ROUND_FAILED_RECORDED -> NEW_EPOCH_ONLY
```

### Repair

```text
PLANNED@g
 -> WRITING
 -> PRECOMMIT_REVALIDATE
 -> COMMITTED@g+1
    | STALE_REPLAN
    | RACE_LOST
    | DEGRADED
```

### Hybrid verification

```text
POLICY_REQUIRED
 -> COMPONENT_VERIFY
 -> CROSS_IMPLEMENTATION_CHECK (when profile requires)
 -> ACCEPT
    | CONFLICT
    | UNKNOWN
```

No branch maps component failure/unavailability directly to weaker acceptance.

## 7. Fraud / contradiction classes

1. `REGISTRY_AUTHORITY_SELF_RECOVERY` — compromised registry signer installs successor without independent recovery authority.
2. `REGISTRY_RETROACTIVE_DENOMINATOR_SHRINK` — retirement/compromise rewrites historical required denominator.
3. `MEMBER_INDEPENDENCE_INHERITANCE` — replacement/re-admitted member inherits independence without proof.
4. `RANDOMNESS_RECOMMIT_AFTER_WITHHOLD` — target population is changed after contributor withholding reveals an unfavorable round.
5. `SCHEDULER_LOCAL_RANDOMNESS_LAUNDERING` — local PRNG is substituted despite collusion being in scope.
6. `WITHHOLDER_REMOVAL_RETRY_BIAS` — withholding member is removed and same epoch re-run until desired selection appears.
7. `STALE_REPAIR_MANIFEST_COMMIT` — repair commits under superseded manifest/registry generation.
8. `REPAIR_SHARE_COUNT_LAUNDERING` — N/K restored under fewer independent destructive domains.
9. `ORPHAN_SHARE_AUTO_ADOPTION` — losing repair's writes counted without current validation.
10. `HYBRID_TO_SINGLE_DOWNGRADE` — required composite evidence silently accepted as one component.
11. `VERIFIER_PROCESS_SYBIL` — multiple processes from same implementation/build counted as diverse verifiers.
12. `ALGORITHM_IMPL_CONFUSION` — implementation diversity treated as protection against algorithm break or vice versa.
13. `PARSER_COMMON_MODE` — multiple crypto backends share one compromised canonicalization path.
14. `POLICY_RETROACTIVITY` — later weaker crypto policy validates evidence that failed the policy in force at creation.
15. `VERIFIER_DISAGREEMENT_MAJORITY_LAUNDERING` — conflicting implementations resolved by process count rather than fail-closed adjudication.
16. `PQ_UNAVAILABLE_CLASSICAL_FALLBACK` — PQ verifier outage treated as permission to accept classical-only evidence.

## 8. RED-first matrix — 48 cases

### A. Registry-authority compromise recursion (A01–A12)

| ID | RED stimulus | Required post-fix result |
|---|---|---|
| A01 | Compromised registry signer issues same-generation different membership | `REGISTRY_EQUIVOCATION_CONFLICT` |
| A02 | Compromised signer shrinks historical denominator | reject; old denominator retained |
| A03 | Signer retires compromised member retroactively before compromise event | reject non-monotonic history |
| A04 | Compromised signer installs successor key alone | `SAME_LINEAGE_RECOVERY_UNPROVEN` |
| A05 | Independent recovery threshold coauthorizes successor | accept new authority generation only |
| A06 | Recovery root shares destructive/control domain with compromised signer | independence insufficient / fail closed |
| A07 | Member admitted only during compromise interval, no revalidation | `REVALIDATION_UNKNOWN` |
| A08 | Same member revalidated with fresh independent provenance | `REVALIDATED_INDEPENDENT` if policy passes |
| A09 | Endpoint/key rotation claimed as new independent member | reject inherited independence |
| A10 | Registry authority compromised after historical challenge success | historical receipt retained; current reliance reappraised |
| A11 | Transparency receipt exists for malicious registry generation | proves publication, not semantic truth |
| A12 | Entire registry + recovery authority threshold compromised | require out-of-band/new-lineage recovery |

### B. Randomness availability / withholding (B01–B12)

| ID | RED stimulus | Required post-fix result |
|---|---|---|
| B01 | Scheduler sees beacon before committing population | invalid round ordering |
| B02 | Population committed, one optional contributor withholds, threshold still satisfied | finalize from policy-permitted contributions |
| B03 | Required threshold lost after commitment | `RANDOMNESS_WITHHELD_QUORUM_LOST` |
| B04 | Scheduler recommits population after B03 in same epoch | reject |
| B05 | New epoch with new commitment after recorded failure | allowed |
| B06 | Withholder removed and same round recomputed | reject retry-bias |
| B07 | Local PRNG used as undeclared fallback | reject |
| B08 | Policy predeclares deterministic fallback that is not unpredictable | allow only for non-unpredictability use class |
| B09 | Beacon proof valid but wrong round/epoch | reject binding mismatch |
| B10 | Same round has two valid-looking different beacon outputs | equivocation/conflict |
| B11 | Contributor set has many keys under one operator domain | count as one independence domain where policy uses independence |
| B12 | Repeated withholding by one domain | retain liveness/compromise evidence; do not bias selection |

### C. Concurrent repair / stale manifests (C01–C12)

| ID | RED stimulus | Required post-fix result |
|---|---|---|
| C01 | Registry generation changes before any share write | stale plan; replan |
| C02 | Target member retired after first write, before commit | precommit revalidation fails |
| C03 | Target becomes newly dependent on another chosen domain | denominator fails despite share count |
| C04 | Two repairs start from same manifest; R1 commits first | R2 CAS loses and cannot commit stale manifest |
| C05 | R2 wrote valid shares before losing CAS | shares remain orphan candidates |
| C06 | Current plan later validates/adopts orphan share explicitly | adoption allowed with new evidence |
| C07 | `>=k` shares recover bytes but independence count below policy | `RECONSTRUCTABLE_BUT_INDEPENDENCE_DEGRADED` |
| C08 | `>=k` shares and denominator passes, but manifest key missing | repair not complete/currently usable |
| C09 | Source checkpoint/root changes during repair | stale/source-lineage conflict |
| C10 | Repair uses stale independence evidence frontier after compromise | reappraise/replan |
| C11 | Concurrent repair “merges” share counts from incompatible plans | reject without full current revalidation |
| C12 | Valid current CAS + reconstruction + denominator + crypto policy pass | commit next manifest generation |

### D. PQ verifier diversity / downgrade (D01–D12)

| ID | RED stimulus | Required post-fix result |
|---|---|---|
| D01 | Hybrid-required evidence; classical valid, PQ invalid | reject |
| D02 | Hybrid-required evidence; PQ valid, classical invalid | reject under AND profile |
| D03 | PQ verifier unavailable | `PQ_VERIFICATION_ASSURANCE_UNKNOWN`, no classical fallback |
| D04 | Two verifier processes use byte-identical same library/build | one implementation family, not diversity |
| D05 | Two independent PQ implementations agree on exact payload | diversity requirement satisfied if policy accepts both |
| D06 | Independent implementations disagree | conflict/fail closed |
| D07 | Both crypto implementations share compromised canonical parser | parser common-mode reopens reliance |
| D08 | PQ implementation later compromised, independent second implementation re-verifies | current reliance may be restored under policy |
| D09 | PQ algorithm itself broken but two implementations agree | algorithm assurance fails; diversity cannot rescue |
| D10 | Policy established HYBRID_REQUIRED at g; later endpoint offers PQ-only | reject downgrade absent authenticated transition |
| D11 | Later weaker policy is applied retroactively to old failed evidence | reject policy retroactivity |
| D12 | Authenticated policy transition explicitly moves to PQ-only after migration criteria | accept only at/after transition generation |

## 9. Minimal implementation guidance for future RED→GREEN

When exact source execution becomes available, implement this contract incrementally rather than as one subsystem:

1. freeze typed generation/provenance objects and pure validators first;
2. add RED tests for same-generation registry equivocation and retroactive denominator shrink;
3. add pure challenge-round state tests for commit-before-randomness and withholding/no-recommit;
4. add repair-plan CAS tests against a file-backed SQLite manifest/registry fixture;
5. add a crypto-policy verifier harness using two deliberately distinct verifier adapters, including disagreement/unavailable states;
6. only then wire these validators into durable ledger/archive flows;
7. run downstream/restart/crash tests and unsafe expected-failure seeds.

Do not claim implementation diversity merely by spawning more processes. Tests should carry explicit implementation/build identities.

## 10. Audit conclusions

### Security

The design closes the most important silent-fallback paths:

- a compromised registry authority cannot erase its own historical denominator or self-recover;
- randomness withholding cannot cause hidden population reselection in the same round;
- stale repair jobs cannot convert old membership assumptions into a current “healthy” archive;
- unavailable/compromised PQ verification cannot silently downgrade hybrid-required evidence to classical-only.

### Availability

The contract intentionally allows fail-closed/UNKNOWN states. This is necessary because anti-bias, anti-downgrade, and authority-recursion guarantees cannot be preserved by inventing a weaker fallback after the failure occurs. Liveness must come from predeclared redundant contributors/verifiers/recovery authorities, not runtime policy relaxation.

### Remaining uncertainty

The exact production choice of randomness beacon(s), independent verifier implementations, and operational destructive-domain evidence providers remains implementation-specific. The contract defines what their outputs must prove and how failures compose; it does not designate vendors or services.

## Frozen result

`INDEPENDENCE_REGISTRY_AUTHORITY_RECURSION_RANDOMNESS_WITHHOLDING_STALE_REPAIR_PQ_VERIFIER_DIVERSITY_V1_FROZEN`

This design is ready for regression-first implementation after higher-priority exact executable gates are available. It is not a substitute for LAB-086/088/090/091/092 exact branch-local execution.