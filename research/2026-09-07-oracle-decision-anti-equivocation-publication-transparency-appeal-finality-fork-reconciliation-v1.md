# Oracle decision anti-equivocation, publication transparency, appeal finality, and fork reconciliation v1

Status: `ORACLE_DECISION_ANTI_EQUIVOCATION_PUBLICATION_TRANSPARENCY_APPEAL_FINALITY_FORK_RECONCILIATION_V1_FROZEN`

Date: 2026-09-07

Related: LAB-093 / #178; composes with `ORACLE_ADJUDICATION_THRESHOLD_REVIEWER_INDEPENDENCE_NORMATIVE_CONFLICT_GOVERNANCE_V1_FROZEN`.

## Problem

The frozen oracle-governance contract defines who may adjudicate and how threshold/reviewer independence works, but it still allows a dangerous gap: an adjudicator or threshold group can produce two individually valid but conflicting signed decisions for the same semantic case and show different decisions to different relying parties. A mutable database can also rewrite publication order, erase an appealed decision, or serve a stale pre-appeal view.

A signature proves attribution. It does not prove that the signer signed only one decision, that every verifier saw the same decision history, that a later appeal superseded rather than erased the original, or that an offline verifier has the latest authoritative state.

This contract separates four claims:

1. decision authenticity;
2. decision non-equivocation;
3. append-only publication/order;
4. current/final policy status.

None implies the others automatically.

## Frozen conclusions

### 1. Same-key conflicting adjudications are first-class fraud proofs

Every normative decision has a stable `DecisionSlotV1`:

`(case_digest, semantic_profile_digest, oracle_generation, adjudication_generation)`.

Within one slot, one adjudicator identity/key may authorize at most one semantic decision payload. Two signature-valid, payload-different decisions from the same adjudicator for the same slot form `ADJUDICATOR_EQUIVOCATION_PROVEN`.

The system MUST retain both conflicting signed payloads. It MUST NOT resolve the contradiction by timestamp, last-write-wins, database order, signer explanation, or whichever object appears in the current repository.

A threshold group can equivocate even if no single member does, by producing two distinct threshold-valid signer sets. Therefore a second fraud class exists: `THRESHOLD_DECISION_EQUIVOCATION_PROVEN` when two incompatible decisions for the same slot each independently satisfy the applicable historical threshold and independence policy.

### 2. Appeals never reuse the original decision slot

An appeal is not an edit of the challenged decision.

Introduce `OracleAppealV1` containing:

- appeal id;
- challenged decision digest and publication receipt;
- appellant identity/authority class where relevant;
- exact grounds and evidence digests;
- appeal-policy generation;
- opened-at authenticated publication position;
- procedural state;
- resulting adjudication generation when resolved.

A successful or unsuccessful appeal creates a new `adjudication_generation` linked to its predecessor. The challenged signed decision remains immutable historical evidence.

Reusing the old slot for a new result would make a legitimate supersession indistinguishable from equivocation and is forbidden.

### 3. Publication is an append-only authority layer, not a convenience index

Introduce an `OraclePublicationLogV1` that records, in one append-only ordered namespace:

- adjudicator decisions;
- threshold closure proofs;
- dissent/conflict objects;
- appeal openings;
- appeal decisions;
- oracle-policy rotations;
- adjudicator-key-status/compromise statements;
- contradiction/fraud proofs;
- supersession edges.

Each accepted object receives an inclusion receipt bound to an immutable log checkpoint/tree root. The publication layer MUST make deletion, reorder, and replacement detectable.

This follows the transparency security model in RFC 9943: a suitable VDS is append-only, non-equivocating, and replayable; RFC 9942 defines signed receipts and consistency proofs that can demonstrate append-only evolution. RFC 9162 similarly requires auditing both append-only evolution and consistency of the view presented to all query sources.

### 4. A Merkle root alone does not prevent split views

A malicious log can sign two different internally valid roots and present them to separate populations. Inclusion in one signed tree is therefore insufficient for global non-equivocation.

The publication checkpoint must be externally witnessed.

Introduce `OraclePublicationCheckpointV1`:

- log/origin identity;
- tree size / monotonic sequence frontier;
- root hash;
- previous accepted checkpoint reference where the VDS supports it;
- log signature;
- witness-policy generation;
- witness cosignatures;
- issuance/time evidence;
- optional consistency proof references.

The transparency-dev/C2SP witness mechanism is the direct donor: a witness retains its previous checkpoint, verifies consistency to the next checkpoint, refuses to cosign a non-append-only evolution, and cosigns consistent checkpoints. This converts a witness's retained state into an anti-fork anchor.

### 5. Witness count is not enough; acceptance quorums need fork intersection

A generic `m-of-n` witness policy can still admit disjoint acceptance quorums.

`PublicationWitnessPolicyV1` MUST define a declared fault model and prove that any two accepted witness sets intersect in enough non-faulty stateful witnesses to prevent both forks from being accepted under that model.

For a simple homogeneous Byzantine threshold policy, if there are `n` witnesses and an accepted checkpoint requires `q` signatures, any two quorums intersect in at least `2q-n` witnesses. The policy is acceptable only when that guaranteed intersection exceeds the number of witnesses the threat model allows to equivocate/collude in the relevant failure domains.

Example baseline: `n=3f+1`, `q=2f+1` gives an intersection of at least `f+1`; if at most `f` witnesses are Byzantine, at least one intersecting witness is non-equivocating and cannot cosign both inconsistent histories.

This mathematical quorum property is necessary but still not sufficient when witnesses share one administrative/key/storage failure domain. The existing reviewer/custody independence model therefore also applies to publication witnesses.

### 6. Conflicting witnessed checkpoints are portable fork evidence

Two signature-valid checkpoints for the same publication origin that cannot be connected by a valid append-only consistency relation form `PUBLICATION_FORK_PROVEN`.

If both checkpoints satisfy the historical witness acceptance policy, the incident escalates to `WITNESS_QUORUM_SAFETY_FAILURE_PROVEN`; normal oracle finality is suspended for the affected frontier until reconciliation under an explicitly authorized recovery policy.

A verifier MUST preserve both forks, signatures, consistency-proof attempts, witness sets, policy generations, and first-observed publication evidence. It MUST NOT silently choose the larger tree, newer timestamp, or currently reachable endpoint.

### 7. Offline verification proves a historical prefix, not currentness

A self-contained inclusion receipt plus witnessed checkpoint can prove that an adjudication was included in a non-rollback history up to that checkpoint.

It cannot, while fully offline, prove that no later appeal, compromise statement, contradiction proof, or policy rotation exists.

Therefore verdicts are explicitly split:

- `HISTORICALLY_PUBLISHED_VALID` — inclusion and historical publication safety proven up to checkpoint C;
- `CURRENT_STATUS_UNKNOWN_OFFLINE` — no evidence of a fresher authoritative frontier;
- `CURRENT_POLICY_VALID` — requires a freshness mechanism/policy that demonstrates the verifier has an acceptably recent frontier;
- `SUPERSEDED` / `APPEAL_OPEN` / `CONTESTED` — derived only when corresponding later authenticated publication objects are visible.

Offline archives MUST NOT label an old valid decision `CURRENT_FINAL` merely because its old checkpoint verifies.

### 8. Rollback is evaluated against the verifier's retained/witnessed frontier

A verifier or archive stores a monotonic `PublicationFrontierV1` containing the highest accepted checkpoint under each relevant publication/witness policy generation.

Receiving an authentic older checkpoint is not proof of corruption by itself, but it MUST NOT roll the retained frontier backward. If a source claims an older checkpoint is current without an authorized recovery/epoch transition, classify `PUBLICATION_ROLLBACK_ATTEMPT`.

A fresh verifier with no prior checkpoint has only bootstrap/TOFU-level anti-rollback assurance unless it also obtains a trusted externally witnessed checkpoint or archived trust anchor. The first observation cannot prove that an earlier split view never existed.

### 9. Appeal state and semantic validity are separate

The historical challenged decision remains `HISTORICALLY_AUTHORIZED` if it was valid under its then-policy, even after a later appeal overturns it.

Operational/current status is derived by replaying the append-only supersession graph:

- decision published, appeal window open -> `PROVISIONAL_APPEALABLE`;
- authenticated appeal open -> `APPEAL_OPEN`;
- appeal denied/final under policy -> challenged decision may become `FINAL_FOR_POLICY_GENERATION`;
- appeal sustained -> predecessor becomes `SUPERSEDED_BY_APPEAL`; successor becomes the current candidate;
- new contradiction/compromise evidence -> may move the current claim to `CONTESTED` or historical trust to `UNKNOWN/INVALID` without deleting prior evidence.

IETF RFC 2026 is a governance donor for explicit escalation and the idea that an appeal may annul a prior decision while retaining a public appeal record. The cryptographic publication model here is stricter: supersession is always additive and machine-replayable.

### 10. Finality is multidimensional and never means evidence erasure

Introduce four finality dimensions:

1. `PUBLICATION_FINALITY` — object is included in a checkpoint satisfying historical witness policy and is below the accepted non-rollback frontier;
2. `PROCEDURAL_FINALITY` — no appeal is open and the applicable appeal window/path is exhausted according to the frozen governance policy;
3. `SEMANTIC_FINALITY` — no unresolved normative conflict/dissent blocks the claim under that oracle generation;
4. `TRUST_FINALITY` — historical signer/key/witness trust remains sufficient under known compromise evidence.

`OracleFinalityProofV1` may state `FINAL_FOR_POLICY_GENERATION` only when all required dimensions close.

This is not eternal immutability of meaning. Later authenticated evidence can supersede current status or reveal that a historical trust assumption was false. Such later evidence adds a new state transition; it never rewrites the previously published record.

### 11. Publication policy rotations are themselves in the publication history

Changing log keys, witness keys, witness quorum, log implementation, or publication origin is authority-relevant.

`PublicationPolicyRotationV1` MUST bind:

- old/new log identity and key sets;
- old/new witness-policy generations;
- final checkpoint under the old generation;
- first checkpoint under the new generation;
- cross-generation continuity proof or explicit authorized reset semantics;
- old-policy authorization and new-policy acceptance;
- archival references for both verifier generations.

A rotation cannot erase a fork or reset an inconvenient frontier. An unresolved pre-rotation fork remains durable contradiction evidence.

### 12. Fork reconciliation requires explicit governance, not longest-chain selection

If publication forks are detected, ordinary automatic finalization stops.

`PublicationForkReconciliationV1` requires:

- all known fork checkpoints and signed objects;
- affected decision/publication ranges;
- witness/key compromise assessment;
- independently authorized reconciliation policy;
- explicit canonical successor frontier, if one can be justified;
- treatment of objects unique to losing forks;
- notifications/contradiction artifacts for relying parties;
- fresh publication generation if required.

Objects from a losing fork are not automatically false. They remain signed evidence and may require separate adjudication. `largest tree`, `newest timestamp`, `most currently reachable replicas`, and `operator says this branch is canonical` are forbidden automatic reconciliation rules.

## Data contracts

### `DecisionSlotV1`
Fields: case digest; semantic-profile digest; oracle generation; adjudication generation.

### `OracleAppealV1`
Fields: appeal id; challenged decision digest; challenged publication receipt; appeal policy generation; grounds/evidence digests; state; opening publication position; resolution link.

### `OraclePublicationEntryV1`
Fields: entry type; canonical payload digest; predecessor/supersession references; oracle/policy generations; issuer identity; registration sequence/index.

### `OraclePublicationCheckpointV1`
Fields: publication origin; tree size/frontier; root; log signature; witness-policy generation; witness cosignatures; consistency evidence; time evidence.

### `PublicationWitnessPolicyV1`
Fields: witness identities/keys; quorum rule; independence domains; fault budget; quorum-intersection proof/parameters; key lifecycle; policy generation; rotation rules.

### `PublicationFrontierV1`
Fields: origin; policy generation; highest accepted checkpoint; checkpoint digest; witness set; local/archive observation evidence; predecessor frontier.

### `OracleFinalityProofV1`
Fields: decision digest; publication finality evidence; procedural appeal state/window evidence; semantic-conflict closure; historical signer/witness trust status; current/superseding decision link; verdict.

### `PublicationForkReconciliationV1`
Fields: fork ids/checkpoints; affected range; fraud proofs; compromise analysis; reconciliation authority/policy; chosen successor frontier if authorized; non-canonical branch retention; new generation linkage.

## Primary donor mechanisms and limits

### RFC 9162 Certificate Transparency

CT v2 explicitly requires auditing append-only behavior and consistency of the log view presented to all query sources, and notes that view consistency requires sharing log responses across entities. It is a strong donor for compact signed-checkpoint/consistency evidence and the split-view threat. It does not define oracle appeal semantics.

Primary source: https://www.rfc-editor.org/rfc/rfc9162.html

### RFC 9942 / RFC 9943 SCITT

RFC 9943 requires a suitable VDS to provide append-only history, non-equivocation and replayability. RFC 9942 provides signed receipts and consistency-proof structures that can be verified independently/offline. These are strong donors for publication receipts and auditable ordering; application-specific oracle governance remains outside their scope.

Primary sources:
- https://www.rfc-editor.org/rfc/rfc9942.html
- https://www.rfc-editor.org/rfc/rfc9943.html

### transparency-dev / C2SP witnesses

A witness retains a previous checkpoint, verifies consistency to a proposed checkpoint, and cosigns only consistent evolution. C2SP transparency-log cosignatures allow clients to require a witness quorum before trusting a checkpoint/inclusion proof. This is the direct anti-split-view donor. A witness quorum must still be designed for independence and quorum intersection; arbitrary `m-of-n` is not magically safe.

Primary sources:
- https://github.com/transparency-dev/witness
- https://c2sp.org/tlog-witness
- https://c2sp.org/tlog-cosignature

### RFC 2026 appeals

RFC 2026 defines an explicit appeals chain, requires detailed/publicly known challenged decisions, and allows an appellate body to annul an earlier decision. It is a governance donor for non-self-finalizing decisions and explicit procedural finality. This contract adds immutable cryptographic supersession instead of mutable administrative state.

Primary source: https://datatracker.ietf.org/doc/html/rfc2026

## Fraud / contradiction proofs

Implementation must eventually persist at least:

1. `ADJUDICATOR_EQUIVOCATION_PROVEN` — same signer, same decision slot, conflicting payloads.
2. `THRESHOLD_DECISION_EQUIVOCATION_PROVEN` — two incompatible decisions for one slot each satisfy threshold/independence policy.
3. `PUBLICATION_FORK_PROVEN` — signature-valid publication checkpoints cannot be connected by valid append-only consistency.
4. `WITNESS_QUORUM_SAFETY_FAILURE_PROVEN` — conflicting forks each satisfy witness acceptance policy.
5. `APPEAL_ERASURE_PROVEN` — challenged decision or appeal record removed/replaced rather than superseded.
6. `SLOT_REUSE_AS_SUPERSESSION_PROVEN` — later appeal decision illegally reuses the predecessor adjudication generation.
7. `PUBLICATION_ROLLBACK_ATTEMPT` — source attempts to move an established frontier backward.
8. `FALSE_OFFLINE_CURRENTNESS_PROVEN` — verifier labels a historical checkpoint current without freshness evidence.
9. `NON_INTERSECTING_WITNESS_POLICY_PROVEN` — accepted quorum policy admits disjoint/fault-only intersections under its declared threat model.
10. `FORK_LONGEST_CHAIN_AUTORECONCILIATION_PROVEN` — fork resolved by size/time/operator preference without authorized reconciliation.

## RED-first matrix (80 cases)

Freeze 80 cases before production integration, 10 per group:

A. signer/threshold equivocation — identical duplicate, same signer conflicting verdict, same signer conflicting rationale only when rationale is authority-bound, two threshold-valid disjoint signer sets, overlapping threshold conflicting decisions, invalid signature noise, stale policy signer, compromised signer, same case different profile, legitimate new adjudication generation after appeal;

B. publication inclusion/order — valid inclusion, missing inclusion, wrong leaf digest, reordered entries, deleted prior entry, duplicate registration semantics, policy rotation ordering, appeal-before-challenged impossible order, supersession edge to unknown object, replay full ordered history;

C. checkpoint consistency — monotonic valid checkpoint, valid consistency proof, invalid proof, same-size different root, larger incompatible root, signed stale root, wrong origin, wrong tree size, corrupted root, first-observation bootstrap;

D. witness safety — valid intersecting quorum, insufficient quorum, unknown witness, retired witness, compromised witness, shared custody-domain threshold, two forks with one honest intersecting refusal, two forks satisfying unsafe disjoint quorums, witness rollback, witness-policy rotation;

E. offline/currentness — valid historical offline receipt, old but authentic checkpoint, archived higher frontier rejects rollback, no freshness evidence, bounded freshness policy met, freshness expired, later appeal unavailable offline, later compromise unavailable offline, portable witnessed checkpoint, TOFU-only verifier;

F. appeal lifecycle — appeal window open, appeal opened, duplicate appeal id, appeal references wrong digest, denied appeal, sustained appeal, successor generation, challenged history retained, nested authorized appeal, appeal authority unavailable/UNKNOWN;

G. finality — publication-only closure, procedural-only closure, semantic conflict open, signer trust unknown, witness trust unknown, fully final-for-policy, later contradiction proof, later key compromise before event, later supersession, current policy rotation without rewriting old finality evidence;

H. fork/recovery — detect fork, preserve both branches, longest-chain forbidden, newest-time forbidden, operator-choice forbidden, authorized reconciliation, losing-fork unique signed object retained, witness compromise changes reconciliation trust, publication generation reset with explicit proof, unresolved fork keeps current status UNKNOWN.

## Integration consequence for LAB-093

LAB-093 implementation must not let a raw threshold signature or an unwitnessed database row become `oracle_final=true`.

The future supported verifier should conceptually require:

`decision authenticity -> oracle threshold/independence -> append-only publication inclusion -> witnessed non-equivocating frontier -> appeal/supersession replay -> historical trust -> finality verdict`.

A break at any step yields the corresponding `UNKNOWN`/contradiction state rather than silent success.

## Exact next research seam if execution remains blocked

Define **publication witness key lifecycle / witness-policy rotation / witness-history archival and bootstrap semantics**: how an offline or newly initialized verifier safely acquires an initial trusted publication frontier, how witness key compromise with uncertain effective time affects historical checkpoints, how old/new witness sets overlap across rotations, and how witness history remains independently replayable after witness/log infrastructure decommission.
