# Oracle adjudication threshold, reviewer independence, normative-conflict resolution, and governance capture v1

Status: `ORACLE_ADJUDICATION_THRESHOLD_REVIEWER_INDEPENDENCE_NORMATIVE_CONFLICT_GOVERNANCE_V1_FROZEN`

Date: 2026-09-07

Related: LAB-093 / #178; composes with `CONFORMANCE_CORPUS_ORACLE_INDEPENDENCE_EXPECTED_VERDICT_PROVENANCE_SPEC_AMBIGUITY_V1_FROZEN`.

## Problem

The previous oracle-independence contract makes an expected verdict independently attributable, but it does not yet define who is allowed to adjudicate ambiguity, when multiple reviewers are materially independent, how recusals and compromised keys affect quorum, how adjudication-policy rotation preserves historical trust, or how two genuinely conflicting normative authorities are represented without inventing a single false truth.

A simple `2-of-3 reviewers signed this expected result` is insufficient. Three people can share one implementation, one employer, one parser, one mutable standards mirror, one signing key custody domain, or one decision-maker. A threshold only distributes trust if the threshold members are meaningfully independent along the failure modes that matter to the claim.

## Frozen conclusions

### 1. Reviewer count is not reviewer independence

`n` signers are not automatically `n` independent adjudicators.

Every oracle policy MUST define an `AdjudicatorIndependenceProfileV1` with declared failure domains at least for:

- employer/organization or controlling legal entity;
- direct reporting/managerial chain where relevant;
- implementation/codebase provenance;
- parser/canonicalizer/crypto-library provenance;
- normative-source retrieval/mirror provenance;
- signing-key custody and HSM/account boundary;
- review-artifact preparation path;
- financial or authorship interest in the disputed behavior;
- prior direct participation in the implementation decision being appealed/adjudicated.

Two reviewers sharing a material domain may both provide evidence, but the policy MUST NOT count them as independent threshold units for the failure mode that domain controls.

### 2. Threshold policy is explicit, versioned, and claim-scoped

Introduce `OracleThresholdPolicyV1` with:

- policy generation and immutable digest;
- eligible adjudicator identities and public keys;
- required signature threshold;
- required independence-domain coverage;
- claim classes for which the policy is valid;
- recusal/conflict rules;
- key compromise/revocation semantics;
- supersession/rotation rules;
- emergency behavior, if any;
- expiry/review horizon;
- archival/trust-bundle references.

A valid `t-of-n` cryptographic signature set is necessary but not sufficient. The verifier also evaluates whether the accepted signers satisfy the policy's independence constraints.

Example: a policy may require `3 signatures`, including at least `2 organizational domains`, `2 implementation-provenance domains`, and `2 key-custody domains`. Four signatures from one organization using one shared reference implementation do not satisfy that policy.

### 3. Independence is claim-relative, not absolute

There is no universal scalar `independent=true`.

A reviewer can be independent for one layer but not another. For example:

- two reviewers may use different parser implementations but the same independently validated Ed25519 primitive; this may be acceptable for a JSON grammar dispute but not for a dispute about that crypto primitive;
- two organizations may be administratively independent but consume the same generated expected-output corpus; they are not independent oracle paths for that corpus;
- two human reviewers may be independent of the production verifier but both derive conclusions from one shared unpublished interpretation note; the note is then a common semantic dependency.

`OracleIndependenceProofV1` therefore records the transitive dependency graph relevant to the exact assertion under adjudication.

### 4. Conflicted adjudicators recuse; recusal does not silently lower the threshold

A materially conflicted adjudicator MUST be marked `RECUSED` for that adjudication and contributes neither approval nor rejection to threshold closure.

Conflict includes at minimum:

- author/maintainer of the disputed implementation behavior when the question is whether that behavior is normative;
- direct author of the expected verdict under appeal when independent review is required;
- undisclosed material financial/control interest in the outcome;
- direct involvement in the appealed decision where objective review is required;
- compromised or uncontrolled signing key/custody path.

The required threshold MUST NOT automatically shrink because reviewers recuse or become unavailable. If the frozen policy can no longer be satisfied, the result is `UNKNOWN_INSUFFICIENT_INDEPENDENT_QUORUM` until an authorized policy migration occurs.

This follows the useful governance donor from IETF practice: conflicted decision-makers can recuse, and appeals exist specifically so a prior decision is not self-finalizing. W3C similarly distinguishes consensus, dissent, formal objections, and escalation rather than treating raw majority as truth.

### 5. Abstention, dissent, recusal, and absence are distinct states

Each adjudicator state is explicit:

- `APPROVE` — signs the exact adjudication payload;
- `REJECT` — signs a conflicting conclusion/reason;
- `ABSTAIN` — eligible, reviewed or declined to decide, but declares no conclusion;
- `RECUSED` — ineligible for this case due to a recorded conflict;
- `UNAVAILABLE` — no authenticated participation;
- `KEY_UNTRUSTED` — signature cannot count under historical trust evaluation.

Only `APPROVE` signatures count toward an approval threshold. `REJECT` evidence is retained and may force conflict handling even when the numerical approval threshold is met, according to policy.

### 6. Sustained normative dissent can block high-assurance closure

For authority-relevant semantics, threshold approval is not always enough to erase a reasoned contradictory adjudication.

`OracleThresholdPolicyV1` MUST specify a dissent rule. High-assurance baseline:

- an authenticated `REJECT` that cites a different applicable normative clause/source creates `ADJUDICATION_CONFLICT_OPEN` unless the approval record explicitly resolves that clause/source conflict;
- a purely implementation-preference objection may be recorded without blocking normative closure if it does not dispute the normative proposition;
- unresolved normative dissent yields `UNKNOWN_NORMATIVE_CONFLICT`, not majority victory.

This borrows the useful distinction from W3C Process: consensus is not defined as a fixed percentage, and sustained objections are treated as distinct governance evidence rather than disappearing into a vote count.

### 7. Genuine normative conflicts are first-class objects, not forcibly synthesized

Introduce `NormativeConflictV1` containing:

- conflict id;
- exact immutable normative source revisions;
- exact clauses/assertions in conflict;
- applicability predicates for each source;
- semantic propositions that cannot simultaneously hold;
- jurisdiction/profile/version scope;
- known precedence or supersession rules, if authoritative;
- adjudicator evidence;
- resolution status;
- permitted scoped profiles, if separation is possible.

Resolution order:

1. apply an explicit precedence/supersession rule already present in the frozen normative profile;
2. determine whether the clauses actually apply to different scopes/versions and split the semantic profiles;
3. apply an independently authorized corrigendum/erratum or designated authority decision if the profile explicitly recognizes that authority;
4. otherwise retain both propositions and return `UNKNOWN_NORMATIVE_CONFLICT` for claims requiring one unique answer.

The system MUST NOT invent precedence based on source recency, implementation popularity, reviewer majority, or current maintainer preference.

### 8. Historical oracle governance is immutable and replayable

Every adjudication binds the exact `OracleThresholdPolicyV1` generation used at the time.

Future maintainers cannot invalidate or rewrite historical expected verdicts merely by changing today's reviewer set or threshold. Historical replay evaluates:

`TRUST(adjudication, event_time, oracle_policy_generation, historical_key_status)`.

A later governance policy may supersede future adjudications and may create a new oracle generation for affected cases, but the old signed adjudication remains immutable evidence of what was authorized under the old policy.

### 9. Adjudicator key compromise has an effective-time boundary

A compromised adjudicator key MUST NOT be handled as an timeless boolean.

`AdjudicatorKeyStatusV1` records:

- key identity and policy generations where authorized;
- activation/retirement times;
- authenticated compromise/revocation statement;
- known or bounded effective compromise time when available;
- historical status evidence and trust-bundle digest.

Rules:

- compromise proven before an adjudication signature -> that signature cannot count;
- compromise proven after an authenticated adjudication time may preserve the historical signature if policy permits and the temporal boundary is independently supported;
- compromise discovered later with unknown start time -> high-assurance historical quorum may become `UNKNOWN_HISTORICAL_ADJUDICATOR_TRUST` if removing that signer drops the independent threshold.

This composes with the frozen historical trust/status contract rather than reusing today's key state as historical truth.

### 10. Threshold-policy rotation uses dual authorization; no unilateral current-maintainer rewrite

For `OracleThresholdPolicyV1` generation P -> P+1, require `OraclePolicyRotationProofV1`.

High-assurance baseline:

- P+1 content is signed by the threshold required by P;
- P+1 is also signed by the threshold required by P+1 before it becomes authoritative;
- all added/removed adjudicators, key changes, independence-domain changes, threshold changes, and emergency clauses are explicit;
- rollback to an older policy generation is rejected by monotonic generation/history evidence;
- P remains archived for historical verification.

This mirrors a useful TUF root-rotation principle: trust-root metadata declares keys and thresholds, and rotation is authenticated through the trusted root chain rather than by whichever new key claims authority. Sigstore's TUF-based public root further demonstrates organizationally/geographically distributed threshold root holders and compromise-time-aware key lifecycle.

### 11. Emergency governance cannot mint normative truth silently

If an emergency policy exists, it MUST be predeclared in the prior trusted policy and narrowly scoped.

An emergency path may permit temporary operational policy such as `CURRENT_POLICY_ACCEPTED=false` or suspend a verifier generation, but MUST NOT silently create `NORMATIVELY_VALID=true` for an ambiguous case with insufficient normal oracle quorum.

Emergency adjudications are explicitly labeled and cannot be used to close scoped semantic equivalence unless the normal policy says they have that authority.

### 12. Governance capture is part of the archival closure

A portable oracle adjudication archive MUST retain:

- exact adjudication payload and signatures;
- threshold-policy bytes/generation;
- reviewer public keys/certificates and historical status evidence;
- reviewer-independence declarations/proofs;
- conflicts/recusals/dissent statements;
- normative-source inventory and exact source artifacts;
- policy-rotation chain;
- timestamps/checkpoints used for historical trust;
- verifier capable of evaluating historical threshold + independence semantics.

A future maintainer list in a live repository is not historical governance evidence.

## Data contracts

### `AdjudicatorIdentityV1`

Fields:
- stable adjudicator id;
- signing public key identity;
- organization/control domain;
- implementation/library provenance declarations;
- key-custody domain;
- roles/claim classes;
- validity interval;
- disclosure digest.

### `AdjudicatorIndependenceProfileV1`

Fields:
- claim/assertion id;
- relevant failure-domain taxonomy;
- adjudicator dependency graph;
- allowed shared dependencies and justification;
- prohibited shared dependencies;
- computed independent-domain coverage;
- evidence digests.

### `OracleThresholdPolicyV1`

Fields:
- policy generation/digest;
- eligible adjudicators/keys;
- threshold number;
- minimum independence-domain coverage;
- dissent handling;
- recusal rules;
- claim scope;
- emergency scope;
- activation/expiry;
- predecessor/successor policy linkage.

### `AdjudicatorDecisionV1`

Fields:
- adjudication/case digest;
- policy generation;
- decision state (`APPROVE|REJECT|ABSTAIN|RECUSED`);
- cited normative assertions;
- rationale digest;
- dependency/conflict disclosure digest;
- signature and time evidence.

### `NormativeConflictV1`

Fields:
- conflict id;
- exact source/section pairs;
- incompatible propositions;
- scope/applicability;
- recognized precedence rules;
- adjudicator decisions;
- resolution or explicit unresolved state;
- derived profile split, if any.

### `OraclePolicyRotationProofV1`

Fields:
- old/new policy digests;
- old-policy threshold signatures;
- new-policy threshold signatures;
- independence coverage under both policies;
- membership/key/domain delta;
- monotonic generation witness;
- historical archive references.

### `OracleGovernanceClosureProofV1`

`GOVERNANCE_CLOSED` only when:

- the exact adjudication payload is immutable;
- approving signatures satisfy cryptographic threshold;
- approving signers satisfy independent-domain threshold;
- no required reviewer is silently counted despite recusal/conflict/untrusted key;
- all material normative dissent/conflicts are resolved or the result is explicitly UNKNOWN;
- exact historical policy/key/source evidence is archived;
- policy lineage is non-rollback and replayable.

## Donor mechanisms and limits

### TUF

TUF root metadata defines trusted keys and a minimum signature threshold for roles. This is a strong donor for explicit versioned threshold authority and trust-root rotation. It does not by itself establish organizational or semantic independence between keys, so this contract adds failure-domain coverage above raw signature counting.

Primary source: `https://theupdateframework.io/docs/metadata/`.

### Sigstore

Sigstore's threat model documents threshold-signed roots, offline root keys, key rotation/revocation, compromise-time semantics, freshness protection, and geographically/organizationally distributed root holders. This is a strong donor for combining threshold cryptography with custody diversity, but Sigstore identity authenticity is not itself normative semantic adjudication.

Primary source: `https://docs.sigstore.dev/about/threat-model/`.

### IETF

RFC 3710 permits recusal/exclusion for serious conflicts of interest in IESG decision-making; RFC 2026 defines escalation/appeals for standards disputes. Current IETF conflict-resolution guidance retains the appeal chain. These are governance donors for avoiding self-finalization and preserving an independent review path, not cryptographic threshold definitions.

Primary sources: RFC 3710, RFC 2026 / current IESG conflict-resolution statement.

### W3C

The 2025 W3C Process treats consensus, sustained objections, formal objections, votes, and escalation as distinct decision evidence. It explicitly does not reduce consensus to a fixed percentage. This is a useful donor for the rule that authenticated normative dissent cannot be erased solely by numerical majority.

Primary source: `https://www.w3.org/policies/process/`.

### NIST threshold cryptography

NIST IR 8214C (published 2026-01-20) treats threshold cryptography as distributed execution of a primitive with secret material shared across parties and explicitly frames the goal as distribution of trust. It is useful support for the cryptographic threshold layer, but it does not define semantic reviewer independence; this contract must model that separately.

Primary source: NIST IR 8214C.

## Fraud / contradiction proofs

The implementation must eventually support durable contradiction evidence for at least:

1. `PSEUDO_INDEPENDENT_QUORUM_PROVEN` — numeric threshold met only by signers sharing a prohibited material failure domain.
2. `CONFLICTED_SIGNER_COUNTED_PROVEN` — recused/conflicted signer counted toward closure.
3. `SILENT_THRESHOLD_LOWERING_PROVEN` — unavailable/recused reviewers caused an unapproved threshold reduction.
4. `KEY_COMPROMISE_BOUNDARY_IGNORED_PROVEN` — signature counted despite historical compromise semantics invalidating it.
5. `CURRENT_GOVERNANCE_REWRITE_PROVEN` — current reviewer/policy state substituted for the historical policy generation.
6. `UNILATERAL_POLICY_ROTATION_PROVEN` — P+1 became authoritative without required old/new policy authorization.
7. `NORMATIVE_DISSENT_ERASURE_PROVEN` — material authenticated normative rejection omitted from closure evidence.
8. `FALSE_CONFLICT_SYNTHESIS_PROVEN` — incompatible normative sources collapsed into one truth without recognized precedence/scope rule.
9. `IMPLEMENTATION_MAJORITY_PRECEDENCE_PROVEN` — implementation popularity used to resolve normative conflict.
10. `HIDDEN_SHARED_ORACLE_DEPENDENCY_PROVEN` — reviewer independence claim omits shared semantic machinery material to the result.

## RED-first matrix (80 cases)

Freeze 80 cases before production integration, grouped 10 each:

A. numeric threshold vs independence — exact 3-of-5 independent, same-org quorum, same-library quorum, same-key-custody quorum, mixed domains sufficient, hidden subsidiary/control relation, shared expected-output generator, allowed low-level shared primitive, prohibited claim-relevant shared primitive, false independence declaration;

B. conflict/recusal — author conflict, manager/subordinate conflict where policy marks material, financial conflict, prior appealed decision-maker, explicit recusal, recused signature present but excluded, unavailable reviewer, abstention, disclosed non-material relationship, undisclosed material conflict discovered later;

C. decision states/dissent — unanimous approval, approval threshold with abstention, approval threshold plus implementation-preference rejection, approval threshold plus unresolved normative rejection, two contradictory normative rejections, insufficient approval quorum, duplicate signer, unknown signer, stale-policy signer, rejection evidence omitted from bundle;

D. key lifecycle — valid current key, retired-after-event key, compromised-before-event key, compromise-after-authenticated-event key, unknown compromise start, revoked signer drops quorum, replacement key under same identity without authorized rotation, shared HSM compromise affecting multiple signers, trust-bundle rollback, current key status substituted for historical;

E. policy rotation — valid old+new dual threshold, old threshold missing, new threshold missing, threshold increase, threshold decrease, membership removal, independence-domain weakening, monotonic generation rollback, emergency clause introduced only by new policy, archived old policy replay;

F. normative conflicts — explicit precedence resolves, version scope split resolves, jurisdiction/profile split resolves, verified corrigendum resolves, two applicable MUST clauses conflict, normative vs informative conflict, current-vs-historical snapshot conflict, recency falsely used as precedence, implementation majority falsely used as precedence, unresolved conflict returns UNKNOWN;

G. appeals/governance capture — original adjudicator appealed, independent appeal panel, same panel self-reviews, appeal changes oracle generation, appeal leaves old generation immutable, missing rationale, missing conflict disclosure, missing policy bytes, missing normative source artifact, offline historical replay succeeds;

H. emergency/fraud — predeclared suspension path, emergency rejects current policy acceptance, emergency tries to mint normative validity, compromised emergency key, emergency threshold unmet, pseudo-independent quorum fraud proof, silent threshold lowering proof, dissent erasure proof, unilateral rotation proof, false conflict synthesis proof.

## Decision

`ORACLE_GOVERNANCE_CLOSED` requires both cryptographic quorum and material independence quorum under an immutable claim-scoped policy generation. Recusal never silently lowers the threshold. Authenticated normative dissent and conflicting applicable normative sources remain explicit evidence; if recognized precedence/scope rules cannot resolve them, the verdict is `UNKNOWN_NORMATIVE_CONFLICT`. Threshold-policy evolution is additive and dual-authorized, with historical policy/key/conflict evidence retained for replay. Current maintainers are not omnipotent over historical expected verdicts.

This contract is design-frozen only. Exact executable RED/GREEN remains pending behind the current LAB-086 source-execution blocker.