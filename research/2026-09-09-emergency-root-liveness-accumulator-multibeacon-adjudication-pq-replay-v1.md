# LAB-093 follow-up — emergency-root liveness, promise accumulators, multi-beacon fairness, topology adjudication, and PQ replay binding

Date: 2026-09-09

Status: `EMERGENCY_ROOT_LIVENESS_ACCUMULATOR_MULTIBEACON_ADJUDICATION_PQ_REPLAY_V1_FROZEN`

This is a regression-first design freeze. It does **not** substitute for LAB-086 exact executable RED/GREEN evidence.

## Context

LAB-086 remains the active priority. In this run direct exact-source execution was re-probed with:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git
```

and failed before repository execution with `Could not resolve host: github.com` (exit 128). GitHub connector control-plane operations remained available. No new LAB-086 behavioral or compile PASS is claimed.

The next recorded distinct fallback was therefore executed: close five survivability/anti-omission gaps left by the previous emergency-root / promise-frontier / multi-beacon / copy-domain / PQ provenance freezes.

## Primary donors and mechanisms

1. **NIST SP 800-57 Part 1 Rev. 5 / Rev. 6 IPD** — key lifecycle, backup/recovery, compromise, trust-anchor and keying-material storage boundaries. Mechanism reused: recovery availability is distinct from key secrecy; recovery material and its custody need lifecycle state rather than an implicit permanent trust assumption.
2. **RFC 9162 / Certificate Transparency lineage** — signed checkpoints, append-only consistency evidence, inclusion promises and gossip. Mechanism reused: compact historical state must remain independently auditable through authenticated commitments and consistency ancestry; a summary count is not a conservation proof.
3. **NIST IR 8213 / Randomness Beacon v2 and public beacon work** — beacon pulse commitments, source composition and externally verifiable randomness. Mechanism reused: application sampling policy must commit source population/rounds/fallback rules before reveal.
4. **drand threshold-BLS model** — fixed group/round produces a unique aggregate result once threshold participation exists. Mechanism reused: uniqueness removes output-shopping among multiple valid threshold aggregates, but does not remove withholding/timeout/fallback bias.
5. **The Update Framework (TUF)** — monotonically versioned root metadata, expiration and rollback resistance. Mechanism reused: successor trust metadata must advance from an already trusted root and clients must reject lower versions rather than accepting a correctly signed rollback.
6. **Sigstore/Rekor** — transparency checkpoints, sharding/key rotation, trust-root management. Mechanism reused: log/key rotation must retain historical verification material and a stable trust-root lineage; fresh attestation does not make old provenance disappear.
7. **TLS 1.3 transcript binding + RFC 9954 hybrid TLS** — negotiated cryptographic choices are authenticated by the handshake transcript; hybrid selection is an explicit protocol state. Mechanism reused: negotiation offers, selection, retry/fallback and session context must be cryptographically bound so an archived transcript cannot be replayed into another session.

## Frozen contract A — emergency-root liveness without challenge leakage or recovery DoS

### A1. Separate three properties

A dormant emergency root has independent properties:

- `CUSTODY_SECRECY`: required private material is not exposed beyond policy;
- `LIVENESS`: the required quorum can currently produce a policy-valid response;
- `RECOVERY_AUTHORITY`: that quorum is authorized for the current recovery generation.

No one property implies the other two.

### A2. Challenge binding

A liveness challenge MUST bind at least:

```text
challenge_id
nonce
purpose = EMERGENCY_ROOT_LIVENESS
root_generation
membership_generation
policy_digest
issued_at_interval
deadline
verifier_identity
```

A response valid for another challenge, generation, verifier, purpose or deadline is replay evidence, not current liveness.

### A3. Challenge secrecy boundary

Routine liveness MUST NOT require central reconstruction/export of the emergency private key or threshold shares. Challenge material may be public unless revealing the exact challenge before the policy's commitment point enables targeted selective denial.

If challenge secrecy is used, record its objective precisely: it can reduce targeted selective-availability attacks but does not prove share secrecy or honest membership.

### A4. DoS does not equal key loss

`LIVENESS_CHALLENGE_TIMEOUT != ROOT_KEY_LOST`.

Timeout produces a bounded availability state such as `LIVENESS_UNPROVEN` or `PARTIAL_QUORUM_OBSERVED`. Key-loss/disposal requires separate evidence.

Repeated timeout MAY trigger recovery policy, but MUST NOT silently authorize membership/threshold reduction.

### A5. Quorum-member replacement under partial loss

Replacement is a new authenticated membership generation. It MUST bind:

- predecessor membership generation;
- surviving quorum evidence;
- replacement member identity/custody domain;
- threshold before and after;
- emergency-root anti-rollback floor;
- activation effective time/sequence.

Old and new shares/membership are not cross-combinable unless the threshold scheme explicitly proves compatibility.

A partial-loss recovery may restore future availability but does not erase historical exposure/loss evidence.

## Frozen contract B — authenticated accumulator for promise compaction

### B1. Conservation remains the invariant

Every predecessor promise MUST map exactly once to one successor disposition:

```text
FULFILLED
OUTSTANDING_CARRIED
POLICY_VALID_TERMINAL
```

Neither counts nor one aggregate digest alone prove this.

### B2. Promise identity

Each promise has a stable canonical `promise_id` derived from immutable acceptance semantics, not from its current compacted container position.

### B3. Compaction generation

A compaction produces an immutable authenticated generation containing:

```text
predecessor_generation
predecessor_root
successor_root
accumulator_scheme/version
canonicalization_version
population_count
fulfilled_root
carried_root
terminal_root
mapping_commitment
checkpoint/signatures
```

### B4. Proof obligations

A verifier MUST be able to establish both:

1. membership/disposition proof for any known predecessor `promise_id`;
2. global conservation / anti-omission evidence showing the successor partition covers the authenticated predecessor population exactly once.

A Merkle membership proof for selected items is insufficient to prove global non-omission.

### B5. Archive survivability

Compaction does not permit deletion of all verification inputs. At minimum retain enough authenticated material to reproduce/check:

- predecessor population commitment;
- canonicalization/scheme version;
- mapping/conservation proof;
- successor partition commitments;
- checkpoint/consistency ancestry;
- policy-valid terminal-disposition semantics.

`ACCUMULATOR_ROOT_RETAINED != COMPACTION_REPRODUCIBLE`.

### B6. Scheme migration

Accumulator/canonicalization upgrades create successor generations. A new scheme cannot reinterpret predecessor promise identities or deadlines. Cross-scheme migration requires an explicit equivalence/conservation proof.

## Frozen contract C — multi-beacon independence and timeout fairness

### C1. Independence is an evidence claim

`N_BEACONS != N_INDEPENDENT_BEACONS`.

Record independence-relevant dimensions such as operator/control domain, implementation, upstream entropy source where knowable, network/failure domain, signing/custody domain, and governance/recovery authority.

Correlated sources count according to the frozen policy's failure-domain denominator, not UI labels.

### C2. Precommit before reveal

Before any relevant beacon result is available, freeze:

```text
source population
source rounds
minimum source threshold
combiner
normalization/canonicalization
source deadlines
timeout clock/evidence
missing-source rule
fallback rule
retry rule
final sample derivation
```

### C3. Selective-abort boundary

If a participant can observe one or more revealed values and then decide whether to reveal/withhold its own contribution, last-revealer bias exists unless the protocol removes or explicitly bounds that choice.

Threshold-BLS uniqueness for a fixed group/round removes output-shopping among multiple valid threshold aggregates; it does **not** by itself prevent a threshold coalition from withholding the round or force a fair application fallback.

### C4. Timeout fairness

Timeout policy MUST use authenticated/precommitted timing evidence and cannot be changed after observing partial randomness.

Examples of fail-closed states:

- `SOURCE_TIMEOUT_PRECOMMITTED` — frozen rule legitimately excluded a late source;
- `SOURCE_WITHHELD_OR_UNAVAILABLE` — expected source produced no accepted pulse;
- `POST_REVEAL_FALLBACK_REBINDING` — fallback changed after observing randomness;
- `SOURCE_SET_LAUNDERED` — denominator/subset changed after reveal.

### C5. Composition does not prove entropy independence

A deterministic combiner can preserve security if at least one source satisfies its assumed property only when the combiner threat model actually provides that guarantee. The application MUST record the combiner security assumption rather than simply asserting that XOR/hash of multiple sources is unbiased.

## Frozen contract D — copy-domain conflict adjudicator and appeal

### D1. Adjudicator is itself an authority surface

A conflict adjudicator cannot erase authenticated topology-source disagreement merely by choosing a winner. Its decision creates a successor adjudication generation containing:

```text
conflict_id
all source assertions/digests
source authority epochs
scope/time intervals
adjudicator authority generation
policy/version
reason/evidence references
decision
appeal window/status
successor topology generation
```

### D2. Fail closed while unresolved

For destruction/negative-space claims, unresolved `PRESENT` or `POSSIBLE` evidence dominates `ABSENT`.

A lower-priority source can be superseded for future operational topology while remaining preserved as historical evidence.

### D3. Appeal does not rewrite predecessor evidence

Appeal/reversal creates another generation. Historical decisions, inputs and signatures remain auditable.

### D4. Completeness proof for topology sources

A topology generation MUST state which authority classes were required, which were queried, their authenticated scope/interval and which were unavailable.

`ALL_RESPONDING_SOURCES_AGREE != REQUIRED_SOURCE_POPULATION_COMPLETE`.

A positive all-copy-domains-accounted claim is forbidden when a required authority class is omitted without an explicit policy-valid exception recorded before outcome inspection.

### D5. Adjudicator compromise

Compromise/revocation of the adjudicator authority degrades affected decisions according to effective time and policy. A clean successor adjudicator can re-adjudicate from preserved source evidence, but cannot retroactively pretend the compromised decision never existed.

## Frozen contract E — provenance transparency survivability, trust-root rollover, and PQ negotiation replay resistance

### E1. Transparency survivability

Historical provenance verification MUST survive log sharding/key rotation/service retirement by retaining or making recoverable:

- exact entry/bundle or equivalent authenticated payload;
- inclusion proof/commitment;
- signed checkpoint;
- log identity/key epoch;
- consistency/shard lineage where required;
- trust-root metadata needed to authenticate the historical log key.

A live API lookup is not the sole admissible archive strategy.

### E2. TUF-style trust-root rollover

Trust-root successor metadata MUST advance monotonically from already trusted metadata. Correctly signed lower-version metadata is a rollback, not a valid recovery path.

Root rollover MUST preserve enough predecessor key/threshold/version evidence to authenticate the transition independently after old online services disappear.

### E3. Attestation key compromise

A later clean root/key does not make artifacts attested during a compromised interval trustworthy. Re-attestation under a clean key proves only the new statement unless an independent rebuild/reverification re-establishes artifact semantics/provenance.

### E4. Negotiation transcript binding

For PQ/hybrid negotiation record/authenticate at least:

```text
protocol/version
client/initiator offer set
server/responder supported/selected set
selected suite + hybrid combiner semantics
policy epoch
retry/HelloRetry/fallback/error path
session/connection context
nonces/randoms or canonical session identifier
peer identities where available
transcript digest
```

### E5. Replay/cross-session rule

`VALID_ARCHIVED_NEGOTIATION_TRANSCRIPT != AUTHORIZATION_FOR_THIS_SESSION`.

A transcript from session A cannot authorize session B even if peer identities and selected algorithms match. The consequential operation must bind the current session/context nonce or equivalent fresh channel binding.

### E6. Downgrade detection

If authenticated policy requires PQ/hybrid and both authenticated offer/support evidence show a permitted PQ/hybrid suite, a classical-only result is fail-closed unless a policy-authorized fallback condition is itself transcript-bound.

Retry/fallback messages are part of the authenticated negotiation state; dropping them from archives destroys independent downgrade adjudication.

### E7. Multi-implementation verification

Verifier diversity is measured by independently reviewable implementation/build/provenance failure domains, not process count. Divergent results for the same authenticated evidence produce `VERIFIER_DIVERGENCE` and block consequential promotion until adjudicated.

## Cross-cutting monotonicity rules

The following evidence is historical and cannot be erased by a clean successor generation:

- observed emergency-root member/share compromise or loss;
- liveness timeout/partial-quorum evidence;
- promise omission/duplication detected during compaction;
- beacon withholding/selective-abort/fallback rebinding;
- topology-source conflict or adjudicator compromise;
- provenance/attestation key compromise;
- negotiation downgrade/equivocation/replay evidence.

Successor generations restore future eligibility only according to explicit policy.

## RED-first regression matrix (40 cases)

### Emergency root — 1..8
1. Replay valid old liveness response against fresh nonce -> reject.
2. Replay response across root generation -> reject.
3. Replay response across verifier/purpose -> reject.
4. Timeout of one member below quorum -> `LIVENESS_UNPROVEN`, not key loss.
5. Selective DoS of known challenge target -> no automatic threshold lowering.
6. Replace lost member without predecessor quorum/recovery authority -> reject.
7. Activate replacement with stale anti-rollback root generation -> reject.
8. Successful successor liveness after historical compromise -> future eligible but compromise history retained.

### Promise accumulator — 9..16
9. Drop promise A, duplicate B while keeping same count -> conservation proof rejects.
10. Change carried promise deadline during compaction -> reject.
11. Membership proofs all sampled items pass but one unsampled predecessor omitted -> global conservation proof rejects.
12. Retain successor root but delete canonicalization/mapping proof -> `COMPACTION_NOT_REPRODUCIBLE`.
13. Reassign promise ID from container index after compaction -> reject identity drift.
14. Unknown terminal disposition code -> reject.
15. Cross-scheme migration without equivalence/conservation proof -> reject.
16. Valid compaction + full archive package -> independently reverify after predecessor service retirement.

### Multi-beacon — 17..24
17. Two endpoints under same operator/control key claimed as two independent sources -> denominator rejects.
18. Change source subset after seeing first pulse -> `SOURCE_SET_LAUNDERED`.
19. Change timeout after partial reveal -> reject.
20. Change fallback after preferred outcome unavailable -> `POST_REVEAL_FALLBACK_REBINDING`.
21. Last participant withholds after seeing earlier contributions -> record selective-abort exposure; do not claim unbiased output unless protocol proof covers it.
22. Threshold-BLS fixed round yields valid unique aggregate -> accept uniqueness only, not availability/fairness claim.
23. Retry on same decision with a new beacon round after seeing first outcome when retry was not precommitted -> reject.
24. Precommitted source/round/timeout/fallback policy with valid pulses -> deterministic reproducible sample.

### Copy-domain adjudication — 25..32
25. CMDB `ABSENT`, backup authority `PRESENT` -> unresolved fail closed.
26. Snapshot authority unavailable but required by policy -> no completeness claim.
27. Adjudicator drops losing source bytes/digest -> archive completeness failure.
28. Adjudicator changes decision in place after appeal -> reject; require successor generation.
29. Compromised adjudicator signs clean successor decision using compromised epoch -> reject.
30. Clean successor re-adjudicates from preserved sources -> future decision may recover; old decision remains historical.
31. Required source-population list is changed after seeing conflict -> denominator laundering reject.
32. All required source classes respond/authenticate and adjudication resolves conflict -> successor topology may be used with lineage preserved.

### Provenance/PQ negotiation — 33..40
33. Historical Rekor/log service disappears but full checkpoint/inclusion/trust-root archive exists -> historical verification remains possible.
34. Only live lookup URI retained and service disappears -> survivability insufficient.
35. Correctly signed old root metadata below trusted version -> rollback reject.
36. Artifact signed during compromised attestation-key interval then merely re-signed by clean key -> do not mark provenance repaired.
37. Replay valid session-A PQ negotiation transcript into session B -> reject cross-session binding.
38. Omit retry/fallback messages from archived transcript -> downgrade adjudication incomplete.
39. Both sides authenticated as supporting required hybrid, final transcript classical-only without policy-authorized fallback -> downgrade reject.
40. Independent verifier implementations disagree on same archived evidence -> `VERIFIER_DIVERGENCE`, block promotion.

## Implementation guidance for later RED/GREEN work

Prefer typed immutable records for generations and explicit status enums. Keep policy denominator/population data authenticated with the evidence it governs. Avoid mutable `current_*` fields as the sole source for historical interpretation.

Do not implement a general-purpose cryptographic accumulator unless a simpler authenticated Merkle partition + exact conservation manifest satisfies the real scale/performance requirement. The acceptance property is anti-omission/conservation and archival verifyability, not novelty.

For beacon composition, start with the simplest deterministic precommitted combiner and explicit missing-source policy whose security assumption can be audited. Do not claim independence from provider names alone.

For PQ negotiation, reuse transcript-binding patterns rather than inventing an unauthenticated side log. The archive may store a canonical transcript projection, but it must be bound to the authenticated session transcript and policy epoch.

## Decision

Freeze `EMERGENCY_ROOT_LIVENESS_ACCUMULATOR_MULTIBEACON_ADJUDICATION_PQ_REPLAY_V1_FROZEN` as the next LAB-093 capability/evidence design slice. Exact executable implementation remains subordinate to LAB-086 and to RED-first tests on exact repository source.