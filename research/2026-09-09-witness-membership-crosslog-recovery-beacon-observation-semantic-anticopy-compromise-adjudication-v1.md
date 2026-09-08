# Witness membership continuity, cross-log recovery, beacon observation completeness, semantic anti-copy, and compromise-boundary adjudication v1

Date: 2026-09-09

Status: `WITNESS_MEMBERSHIP_CROSSLOG_RECOVERY_BEACON_OBSERVATION_SEMANTIC_ANTICOPY_COMPROMISE_ADJUDICATION_V1_FROZEN`

## Scope

This note advances LAB-093's retained security-evidence architecture while LAB-086 exact source execution remains unavailable. It does **not** substitute for executable RED/GREEN proof.

Questions resolved here:

1. How witness membership changes during a partition preserve the historical denominator and cannot silently discard a dissenting witness.
2. How a cross-log anchor promise survives compromise, retirement, or replacement of the destination log.
3. What positive evidence is sufficient to call a threshold-beacon liveness observation surface complete when collectors disagree or disappear.
4. How semantic attesters can be prevented from merely copying peers while still permitting deterministic independent reproduction.
5. Who may establish or correct an earlier compromise-effective boundary without allowing the compromised provenance authority to self-exonerate or retroactively invalidate arbitrary history.

## Primary donors

- RFC 9162, Certificate Transparency v2: append-only Merkle consistency, signed tree heads, MMD freshness and monitor/auditor model: https://www.rfc-editor.org/rfc/rfc9162.html
- Chrome Certificate Transparency log lifecycle: explicit `Qualified`/`Usable`/`ReadOnly`/`Retired`/`Rejected` states and retirement timestamps; pre-retirement evidence can retain limited historical value: https://googlechrome.github.io/CertificateTransparency/log_states.html
- transparency.dev witness model: witnesses retain the latest checkpoint they observed and cosign only a checkpoint consistent with retained history; witness quorum is split-view resistance, not semantic truth: https://blog.transparency.dev/building-a-transparent-keyserver
- drand protocol and security model: threshold partial signatures, deterministic per-round output, catch-up, resharing, and threshold availability assumptions: https://docs.drand.love/docs/specification/ and https://docs.drand.love/docs/security-model/
- Sigstore threat/security model: transparency + monitors expose misbehavior; TUF distributes/revokes service trust; compromise time can preserve legitimate pre-compromise verification while rejecting later use: https://docs.sigstore.dev/about/threat-model/ and https://docs.sigstore.dev/about/security/
- TUF compromise recovery: if a threshold of Root keys is compromised, trusted Root recovery must be re-issued out of band rather than self-recovered by the compromised threshold: https://theupdateframework.io/docs/faq/
- Sigstore trusted-root time windows and signed timestamp separation: trust material can carry start/end validity intervals and time may be supplied by a separately trusted TSA: https://docs.sigstore.dev/cosign/system_config/custom_components/ and https://docs.sigstore.dev/cosign/verifying/timestamps/

## 1. Witness membership denominator continuity across partition

### Problem

Suppose witness set `W1,W2,W3` protects checkpoint generation `g`. `W3` observes a conflicting checkpoint and then becomes partitioned. While it is unreachable, the registry rotates to `W1,W2,W4`. If current verification simply counts `2-of-3` in the new set, the system can silently erase the only dissenting historical witness by changing the denominator.

### Frozen distinctions

`CURRENT_WITNESS_MEMBERSHIP != HISTORICAL_WITNESS_DENOMINATOR`

`MEMBER_RETIREMENT != HISTORICAL_DISSENT_ERASURE`

`UNREACHABLE_WITNESS != RETIRED_WITNESS`

`NEW_QUORUM_VALID != OLD_CHECKPOINT_RECONCILED`

### Contract

Introduce a versioned `WitnessMembershipEpochV1`:

- `epoch_id`
- ordered/canonical member identities and public keys
- threshold policy
- predecessor epoch digest
- activation condition/time/sequence
- retirement records with reason and authority
- required handoff/reconciliation frontier

Every cosigned checkpoint is bound to the exact membership epoch and threshold policy under which it was accepted.

A membership transition is authoritative only if it preserves an append-only epoch chain and satisfies one of:

1. **ordinary rotation** — old policy authorizes the successor and all reachable old witnesses are reconciled through a checkpoint frontier consistent with their retained frontier;
2. **partitioned rotation** — old policy cannot fully reconcile every member, so the transition records unresolved members/frontiers explicitly and requires a higher/out-of-band recovery authority; unresolved historical dissent remains a live conflict obligation;
3. **compromise recovery** — follows the separately trusted recovery root; a compromised witness-registry threshold cannot authorize its own clean successor.

A verifier evaluating a historical checkpoint uses the denominator and threshold frozen at that checkpoint's epoch, not today's membership.

A newly activated epoch cannot make an old same-size/different-root conflict disappear. If an old witness later reconnects with a conflicting retained frontier, that conflict is evaluated against the historical epoch and may taint descendant current reliance.

### CT lifecycle donor

Chrome's CT log lifecycle separates current usability from historical treatment: a `Retired` log stops being relied on for new SCTs, while some SCTs issued before its retirement timestamp can retain historical compliance value. The important donor mechanism is the explicit retirement boundary rather than deleting the log from history.

## 2. Cross-log destination compromise, retirement, and recovery

### Problem

A source log may have promised to anchor checkpoint `S_g` into destination log `D`. Later `D` is compromised, retired, or replaced by `D2`. Treating `D2` as if it had always been the promised destination launders a missed anchor and destroys omission evidence.

### Frozen distinctions

`DESTINATION_SUCCESSOR != RETROACTIVE_PROMISE_TARGET`

`DESTINATION_COMPROMISE != SOURCE_PROMISE_CANCELLATION`

`DESTINATION_UNAVAILABLE != ANCHOR_OMISSION_PROVEN`

`VALID_OLD_ANCHOR != CURRENT_DESTINATION_TRUST`

### Contract

Every `CrossLogAnchorPromiseV1` binds:

- source checkpoint digest/generation;
- exact destination log identity + key/trust generation;
- deadline/MMD-like publication bound;
- canonical anchor statement identity/predicate;
- destination membership/trust epoch;
- recovery/successor policy identifier.

If the destination is replaced before the deadline, the original promise remains outstanding unless a separately authorized `AnchorPromiseSupersessionV1` is issued **before** the old deadline and is itself independently retained. Supersession must bind both old and new destinations and cannot erase already accrued lateness.

If the original destination is compromised after a valid anchor was independently retained, current reliance on that destination is re-appraised, but the historical anchor receipt/checkpoint is not deleted. Independent cross-anchors, monitors, witnesses or archives may preserve its historical existence.

If compromise makes semantic verification of the old destination impossible and no independent retained proof remains, state becomes `HISTORICAL_ANCHOR_EXISTENCE_NONREPRODUCIBLE`, not `ANCHOR_NEVER_EXISTED`.

Positive omission remains strict: retained promise + proven elapsed deadline + authenticated complete destination state after deadline + canonical non-inclusion evidence. `404`, timeout, retired endpoint or unavailable archive remains `UNKNOWN`.

## 3. Threshold-beacon observation-quorum completeness and collector equivocation

### Problem

A drand-style round fails to produce a threshold output. One collector reports that member `M3` never sent a partial; another claims it did. The final output's absence proves insufficient valid partials reached an aggregator, but not which member withheld or whether the observation surface was complete.

### Frozen distinctions

`ROUND_FAILURE != MEMBER_WITHHOLDING_PROVEN`

`COLLECTOR_COUNT != INDEPENDENT_OBSERVATION_DOMAINS`

`NO_PARTIAL_OBSERVED != NO_PARTIAL_EMITTED`

`COLLECTOR_SIGNATURE != COMPLETE_OBSERVATION_SURFACE`

### Observation model

Define `BeaconObservationEpochV1` before the round:

- beacon/group epoch and threshold;
- expected member set;
- canonical round identifier/message;
- registered collectors and independent control domains;
- collection window;
- required observation threshold;
- canonical per-member evidence format;
- collector transparency/publication obligation.

A collector can make a positive claim `PARTIAL_OBSERVED(member, round, digest)` only with a cryptographically valid partial bound to the exact round/group.

A positive negative claim `PARTIAL_NONPARTICIPATION_PROVEN(member, round)` requires stronger evidence:

1. a prior participation obligation for that member/round;
2. an authenticated post-window statement from the required collector observation quorum;
3. no valid partial for that member in the complete committed observation set;
4. proof that the collector set itself satisfied the frozen denominator/control-domain policy;
5. no unresolved collector equivocation for that round.

If collectors disagree, the disagreement is evidence. Same collector identity signing incompatible complete-observation commitments for the same round is `COLLECTOR_EQUIVOCATION_PROVEN`.

Collector disappearance before its required final commitment degrades attribution to `OBSERVATION_COMPLETENESS_UNKNOWN`; it must not shrink the denominator after the fact.

### drand donor boundary

drand defines final randomness once any party obtains at least the threshold of valid partial signatures and validates partials before aggregation. Its threshold failure is therefore directly useful as an availability fact. It does not by itself provide a complete forensic attribution layer for which member failed to emit versus whose message was lost or withheld by the network/collector; that layer must be additional.

## 4. Semantic-attester anti-copy challenge timing

### Problem

A semantic quorum is useless if several nominally independent attesters wait for the first answer and copy its result. Yet deterministic reproduction is desirable: honest implementations should converge on the same result from the same immutable evidence.

### Frozen distinctions

`SAME_RESULT != INDEPENDENT_REPRODUCTION`

`SIGNATURE_DIVERSITY != COMPUTATION_DIVERSITY`

`COMMITMENT_MATCH != SEMANTIC_CORRECTNESS`

`DETERMINISTIC_CONVERGENCE != COPY-FREEDOM`

### Commit-before-reveal protocol

For a high-assurance semantic decision, freeze `SemanticChallengeV1` with exact evidence/input digest, verifier-policy generation, canonical parser/algorithm versions, attester denominator, deadline and nonce/challenge epoch.

Phase A — **commit**:

Each attester independently computes and publishes/signs a commitment over at least:

`H(challenge_id || input_digest || verdict || canonical_output_digest || evidence_digest || implementation_provenance_digest || salt)`

The commitment deadline closes before any attester may reveal the underlying verdict/output/salt.

Phase B — **reveal**:

After the committed set is frozen, attesters reveal verdict/output/evidence/provenance/salt. The verifier checks every reveal against its pre-existing commitment and independently re-runs all deterministic verification possible.

An attester that does not commit before reveal cannot join the denominator for that challenge. A revealed peer result cannot be used to retroactively create an eligible commitment.

This prevents straightforward wait-and-copy while preserving deterministic equality as a desirable post-reveal property. It does **not** prove organizational independence or prevent pre-commit collusion; provenance/control-domain policy and challenge sampling remain separate layers.

For especially consequential audits, challenge inputs may include independently selected hidden samples revealed to each attester only after eligibility is frozen, but all such sampling rules must be committed before randomness/output values are visible to the scheduler.

## 5. Compromise-effective boundary adjudication authority

### Problem

A provenance authority is discovered compromised on day T. It claims compromise began only at T, preserving prior statements. An investigator has evidence the key was stolen at T-30. Conversely, an attacker may try to declare an absurdly early compromise boundary to invalidate inconvenient valid history.

The compromised authority cannot be the sole judge of its own effective compromise boundary.

### Frozen distinctions

`REVOCATION_PUBLICATION_TIME != COMPROMISE_EFFECTIVE_TIME`

`AUTHORITY_SELF_REPORT != FINAL_ADJUDICATION`

`EARLIER_BOUNDARY_CLAIM != EARLIER_BOUNDARY_PROVEN`

`BOUNDARY_CORRECTION != HISTORICAL_EVIDENCE_ERASURE`

### Authority model

Define independent roles:

- `ProvenanceAuthority` — emits ordinary provenance attestations.
- `RevocationAuthority` — can stop future/current acceptance.
- `CompromiseBoundaryAdjudicationAuthority` — threshold/higher authority allowed to set or correct `effective_from` using evidence.
- `Transparency/Witness layer` — makes revocation/boundary statements non-equivocating and discoverable.
- `RecoveryRoot` — out-of-band/higher root used if the ordinary adjudication threshold itself is compromised.

A `CompromiseBoundaryDecisionV1` contains:

- affected authority/key generation;
- decision sequence/version;
- `effective_from` interval or lower/upper bound, not necessarily a falsely precise instant;
- evidence digests and their authenticated times/sequences;
- adjudication policy generation;
- threshold signatures;
- predecessor decision digest;
- explicit supersession semantics.

Rules:

1. The affected provenance authority may submit evidence/self-report but cannot alone finalize its own boundary.
2. A later adjudication may move the boundary earlier only with newly authenticated evidence and append-only supersession; the old decision remains historical.
3. Moving the boundary later is more dangerous because it rehabilitates previously rejected evidence; require a stricter recovery/higher-root policy than ordinary revocation and positive proof that the earlier boundary was erroneous.
4. Unknown/contested boundary fails closed for consequential **current** decisions whose evidence falls in the disputed interval.
5. Provably pre-boundary evidence may remain historically usable under the frozen policy if its timestamp/order evidence is independently trustworthy.
6. Post-boundary evidence is rejected for authority purposes even if the signature is mathematically valid.
7. A compromised adjudication threshold cannot self-recover; follow TUF's out-of-band recovery pattern.

### Sigstore/TUF donor boundary

Sigstore explicitly treats compromise time as useful for retaining verification of legitimate signatures from before compromise while revoking later trust material, and uses TUF for threshold/root recovery. This is a donor for time-bounded trust and independent recovery, not a claim that Sigstore's exact policy directly implements this proposed adjudication schema.

## Cross-cutting invariants

1. `TODAYS_DENOMINATOR != HISTORICAL_DENOMINATOR`.
2. `RETIREMENT != ERASURE`.
3. `SUCCESSOR != RETROACTIVE_PREDECESSOR`.
4. `ABSENCE_OF_OBSERVATION != POSITIVE_NEGATIVE_EVIDENCE`.
5. `ROUND_FAILURE != ATTRIBUTABLE_WITHHOLDING`.
6. `MULTIPLE_SIGNATURES != MULTIPLE_INDEPENDENT_COMPUTATIONS`.
7. `COMMIT_BEFORE_REVEAL` is necessary against opportunistic copying but insufficient against pre-commit collusion.
8. `REVOCATION_TIME != COMPROMISE_TIME`.
9. The compromised authority cannot be sole adjudicator of its own compromise boundary.
10. Late compromise, hidden common control, or conflicting historical witness evidence re-appraises **current reliance** without deleting immutable historical evidence.

## RED-first executable matrix (64 cases)

The future LAB-093+ executable gate should instantiate all cases below before production refactors.

### A. Witness membership continuity — 16

A1 old epoch ordinary rotation with all frontiers consistent -> accept successor.
A2 partitioned dissenting witness omitted from new membership -> historical unresolved flag persists.
A3 same-size/different-root from retired old witness after reconnect -> equivocation remains detectable.
A4 larger checkpoint without consistency proof -> UNKNOWN.
A5 old witness unreachable only -> cannot mark retired automatically.
A6 retirement signed only by new epoch -> reject if old/higher policy required.
A7 old denominator 2-of-3, new denominator 2-of-2 -> historical 2-of-3 remains unchanged.
A8 remove dissenting member then recalculate old quorum -> reject denominator laundering.
A9 ordinary rotation predecessor digest mismatch -> reject.
A10 skipped membership epoch -> reject unless recovery policy explicitly authorizes gap.
A11 compromise of registry threshold then self-authorized successor -> reject.
A12 out-of-band recovery root successor -> accept only under frozen recovery policy.
A13 stale membership epoch replay -> fail current latestness.
A14 old cosignature remains historically verifiable after retirement boundary.
A15 post-retirement new checkpoint signed by retired witness -> does not count for current quorum.
A16 descendant checkpoint whose ancestry includes unresolved old conflict -> current consequential reliance fails closed.

### B. Cross-log destination recovery — 12

B1 promised anchor appears before deadline in exact destination -> accept.
B2 destination timeout after deadline -> UNKNOWN, not omission proven.
B3 complete post-deadline destination prefix + zero canonical matches -> omission proven.
B4 destination retired before deadline without supersession -> original promise remains outstanding.
B5 successor destination named after old deadline -> cannot erase prior omission.
B6 pre-deadline valid supersession retained independently -> evaluate new destination under new promise.
B7 old destination later compromised but independent anchor receipt survives -> historical existence retained, current reliance re-appraised.
B8 old destination archive lost -> historical proof nonreproducible, not never-existed.
B9 replacement log reuses friendly display name but different key/lineage -> distinct destination.
B10 destination presents same-size different-root checkpoint -> destination equivocation conflict.
B11 cross-anchor exists but source checkpoint digest differs -> not satisfaction of promise.
B12 successor log claims imported history without independently verifiable predecessor binding -> no retroactive satisfaction.

### C. Beacon observation completeness — 12

C1 threshold valid partials collected -> round success.
C2 threshold not reached -> availability failure only.
C3 one collector saw M3 partial, another did not -> nonparticipation not proven.
C4 invalid M3 partial -> positive malformed/invalid evidence, not valid participation.
C5 all required independent collectors commit complete sets with no M3 valid partial -> attributable nonparticipation if prior obligation exists.
C6 collector disappears before final commitment -> completeness UNKNOWN.
C7 denominator shrunk after collector disappearance -> reject.
C8 same collector signs incompatible complete sets -> collector equivocation proven.
C9 two collectors under same control domain counted as independent -> reject policy.
C10 valid late partial after observation window -> does not retroactively satisfy punctual-liveness obligation but is historical participation evidence.
C11 replayed partial from different round/group -> reject.
C12 collector-only assertion without retained canonical evidence set -> insufficient for positive negative claim.

### D. Semantic anti-copy — 12

D1 independent attesters commit same deterministic verdict then reveal -> eligible convergence.
D2 B commits only after seeing A reveal -> B excluded.
D3 B copies A before commit through collusion -> commitment protocol alone cannot detect; provenance challenge remains required.
D4 reveal does not open commitment -> reject attestation.
D5 commitment binds wrong input digest -> reject.
D6 same verdict but different canonical output where policy requires exact deterministic output -> divergence fail closed.
D7 same output produced by same implementation/control domain under two identities -> one independence domain.
D8 commitment lacks provenance digest where policy requires it -> reject.
D9 scheduler changes challenge input after commitments -> reject challenge.
D10 hidden sample chosen after scheduler sees preferred attester output -> reject adaptive sampling.
D11 attester misses commit deadline but reveals correct result -> correctness may be informative but does not count toward anti-copy quorum.
D12 deterministic reproduction by later auditor matches original -> supports semantic reproducibility, not historical compute independence.

### E. Compromise-boundary adjudication — 12

E1 authority self-reports compromise at T, independent adjudicator confirms -> boundary accepted.
E2 affected authority alone signs T -> provisional only, not final.
E3 authenticated evidence proves compromise before T -> append-only earlier supersession.
E4 attempt to move boundary later using ordinary revocation authority -> reject rehabilitation.
E5 higher/recovery policy positively proves earlier decision erroneous -> later boundary may supersede under stricter rule.
E6 evidence timestamp lies clearly before effective boundary -> historically usable if all other policy passes.
E7 evidence lies clearly after boundary -> reject authority use.
E8 evidence lies inside disputed interval -> consequential current use UNKNOWN/fail closed.
E9 revocation publication happens after effective compromise -> do not conflate the two times.
E10 adjudication threshold compromised -> self-successor rejected; out-of-band recovery required.
E11 replay older adjudication generation to rehabilitate key -> latestness failure.
E12 corrected boundary deletes prior decisions instead of append-only supersession -> reject history erasure.

## Implementation implications

No production refactor is justified until exact executable source returns. When it does, prefer value objects with canonical encodings and append-only generation chains rather than mutable current-state rows whose denominator/authority history can be rewritten.

The executable implementation should keep the five authorities separate where practical: membership/recovery, destination-log trust, beacon observation registry, semantic-attester independence policy, and compromise-boundary adjudication. Combining all five under one signer would collapse the independence assumptions this design is meant to preserve.

## Verdict

`WITNESS_MEMBERSHIP_CROSSLOG_RECOVERY_BEACON_OBSERVATION_SEMANTIC_ANTICOPY_COMPROMISE_ADJUDICATION_V1_FROZEN`

The next distinct evidence frontier, if exact execution is still unavailable, is: **historical policy snapshot availability and garbage-collection safety + witness/collector identity-key rollover without continuity laundering + cross-log proof survivability under hash/key algorithm migration + challenge/result confidentiality before semantic-attester reveal + appeal/finality semantics for compromise-boundary adjudication**.
