# Publication witness key lifecycle / policy rotation / history archival / bootstrap v1

Status: `PUBLICATION_WITNESS_KEY_LIFECYCLE_POLICY_ROTATION_HISTORY_ARCHIVAL_BOOTSTRAP_V1_FROZEN`

Date: 2026-09-07

## Scope

This note extends the frozen oracle-publication contract. It answers four questions that the prior anti-equivocation design deliberately left open:

1. how a new or offline verifier acquires an initial trusted publication frontier without silently upgrading TOFU into externally established trust;
2. how witness key expiry, retirement and compromise affect historical checkpoint trust;
3. how witness-set/policy rotation preserves anti-fork guarantees across the old/new boundary;
4. what must survive log/witness decommission so historical publication evidence remains independently replayable and rollback/fork laundering is detectable.

This is a design/evidence freeze, not an implementation PASS.

## Core distinction

`VALID_COSIGNATURE != TRUSTED_WITNESS_HISTORY != CURRENT_PUBLICATION_FINALITY`.

A cryptographically valid witness cosignature proves only that a particular key signed a checkpoint. Authority additionally depends on the historical witness policy, the key's trust interval, the accepted bootstrap root/frontier, and absence of an unresolved conflicting witnessed branch within the policy's safety model.

## 1. Bootstrap semantics

Define `PublicationBootstrapV1`:

- `log_origin` and exact log public-key generation;
- `checkpoint_bytes` and checkpoint digest;
- tree size/root;
- exact `PublicationWitnessPolicyV1` generation and digest;
- witness public keys and identity/failure-domain metadata;
- accepted witness cosignatures;
- optional predecessor/root-migration evidence;
- bootstrap method;
- verifier-local acceptance time;
- provenance/evidence digest.

Allowed bootstrap classes:

### B0 — unauthenticated discovery

A checkpoint fetched from the network with no previously trusted binding is discovery only. Verdict: `UNTRUSTED_DISCOVERY`.

### B1 — TOFU

The verifier locally pins a first observed log/policy/checkpoint. This creates a local trust anchor only. It MUST be labelled `TOFU_LOCAL`, scoped to that verifier/trust domain, and MUST NOT be reported as globally or independently established non-equivocation.

A later conflict with another independently established history is not resolved in favour of the older local pin merely because it was first-seen.

### B2 — out-of-band authenticated bootstrap

A checkpoint/policy root distributed through an already trusted authenticated channel may establish `AUTHENTICATED_BOOTSTRAP`, but the claim is only as strong as that channel's authority and scope.

### B3 — continuity bootstrap

A new checkpoint/policy is accepted through a previously trusted publication frontier plus valid append-only consistency and an authorized policy/key migration. This is the preferred normal path.

### B4 — multi-anchor recovery bootstrap

If ordinary continuity is unavailable, recovery requires an explicit out-of-band governance event whose authority is independent of the potentially compromised publication/witness path. Recovery evidence must preserve the abandoned/conflicting history; it cannot reset the log namespace.

## 2. Witness state and key lifecycle

Define `WitnessKeyHistoryV1` with:

- witness identity;
- key generation/id and exact public key bytes;
- policy generations in which it was authorized;
- `valid_from` / planned `retire_after`;
- signed retirement/revocation/compromise statements;
- effective invalidity time when known;
- discovery/publication time of the status statement;
- archival trust-material digest.

Historical verdict is evaluated at checkpoint/cosignature event time, not by blindly applying today's active-key set.

### Planned retirement / ordinary expiry

Retirement after a checkpoint does not retroactively invalidate a historically authorized cosignature. The old public key and policy generation remain archived for historical verification.

### Compromise with known effective time

If independently authenticated evidence establishes compromise effective at `T_compromise`, cosignatures at or after that boundary are not counted for authority. Earlier signatures may remain historically acceptable if policy says the evidence is sufficient to establish that boundary.

### Compromise with unknown effective time

If only discovery time is known and actual compromise start is unknown, affected historical signatures cannot be treated as safely pre-compromise merely because they predate discovery. High-assurance result is `UNKNOWN_WITNESS_HISTORICAL_TRUST` for claims whose quorum safety depends on that witness.

### Key loss without compromise evidence

Loss of a private key affects future availability, not historical authenticity. Historical verification depends on preserved public material and policy history.

## 3. Witness-policy rotation

Define `WitnessPolicyRotationV1`:

- old policy generation/digest;
- new policy generation/digest;
- activation frontier `(log_origin, tree_size, root)`;
- old-policy authorization over the rotation statement;
- new-policy acceptance/authorization over the same canonical statement;
- append-only consistency from the last old-policy checkpoint to the activation checkpoint;
- explicit old/new witness-set overlap and failure-domain mapping;
- anti-fork safety proof for the transition;
- archival receipt/checkpoint set.

### Rotation rule

A new policy MUST NOT become authoritative solely because the new witness set signs itself into existence. Normal rotation requires continuity authorization from the previous trusted policy and acceptance by the new policy.

This mirrors the useful TUF root-rotation mechanism: a successor root is verified against both its predecessor's threshold and its own threshold, with intermediate versions retained. The mechanism is a donor, not a claim that TUF itself supplies transparency-witness semantics.

### Cross-policy quorum-intersection safety

Within one homogeneous q-of-n policy, quorum intersection can be reasoned about numerically. Rotation is harder: old and new signer populations may be disjoint.

Therefore the transition must prove that **any old-policy accepted frontier and any new-policy accepted frontier that can be authoritative across the activation boundary cannot both be conflicting without exceeding the declared cross-policy fault budget**.

Acceptable mechanisms include:

- sufficient old/new witness overlap with claim-relevant independence;
- a joint transition epoch requiring both old and new quorums;
- an independent higher-level monotonic authority that binds the exact activation frontier and both policy digests.

Simple `old q-of-n` then immediately `new q-of-n` with no overlap/joint epoch/external continuity is `UNSAFE_POLICY_ROTATION`: it permits fork laundering by retiring the witnesses that remember the inconvenient branch.

## 4. Atomic witness state

C2SP's witness protocol requires a witness to remember its latest cosigned checkpoint, verify consistency from that state, and atomically persist the new checkpoint before returning a cosignature. This is fundamental: a witness key without durable monotonic state is only a signer and cannot provide the intended fork-detection property.

Therefore `WitnessDurableStateV1` must bind:

- log origin/key generation;
- latest checkpoint bytes/digest;
- tree size/root;
- policy generation;
- witness key generation;
- monotonic local generation;
- durable-state seal/digest.

A restored witness MUST recover this state before signing again. If state is missing or rolled back, it must enter `RECOVERY_REQUIRED_NO_COSIGN`, not resume from size zero.

## 5. Rollback and fork laundering across rotation

Forbidden automatic behaviours:

- accept a lower tree size because witness keys changed;
- accept a conflicting root at the same size because the old policy expired;
- discard old checkpoints after policy rotation;
- bootstrap a new witness from only the current log endpoint when prior witness state is unavailable;
- treat a log/witness rebrand, account move, new URL or new key as a new authority namespace unless governance explicitly creates a distinct namespace;
- use current majority/latest timestamp/longest tree to erase a prior witnessed fork.

If old and new valid histories conflict and neither has a valid authorized reconciliation, verdict remains `PUBLICATION_FORK_PROVEN` or `WITNESS_POLICY_TRANSITION_SAFETY_FAILURE`, depending on evidence.

## 6. Decommission and archival survivability

Before decommissioning any witness/log infrastructure, freeze an independently replayable `WitnessHistoryArchiveV1` containing at minimum:

- all policy generations and canonical policy bytes;
- all historical witness public keys and authenticated key-status statements;
- bootstrap roots/frontiers and their provenance;
- policy-rotation statements and old/new authorization evidence;
- witnessed checkpoints required to establish retained frontiers;
- append-only consistency proofs or sufficient log material to recompute them;
- known fork/equivocation/fraud evidence, including losing branches;
- witness durable-state terminal checkpoints;
- trust-bundle/schema/verifier versions needed for offline replay;
- archive completeness/seal/durability/verifier-durability proofs from the previously frozen archive contracts.

`SERVICE_DECOMMISSIONED` is never equivalent to `HISTORY_FINAL`. Historical trust remains derivable only from archived evidence.

A decommission that destroys old witness keys/policies/checkpoints before archival closure is `DECOMMISSION_EVIDENCE_LOSS`; any finalization depending on missing history becomes `UNKNOWN_PUBLICATION_HISTORY`.

## 7. Offline verifier semantics

An offline verifier starts from an explicit trusted bootstrap object and replays policy/key/checkpoint history forward. It must never fetch today's mutable witness list and apply it retroactively.

Offline proof can establish `FINAL_AT_WITNESSED_FRONTIER(F)` when all required historical authority is self-contained. Without a freshness statement anchored after F, it cannot claim no later appeal, compromise, policy rotation or supersession exists. Current-state verdict stays `CURRENT_STATUS_UNKNOWN_OFFLINE`.

## 8. Fraud / contradiction proofs

Freeze the following evidence classes:

1. `WITNESS_KEY_EQUIVOCATION_PROOF` — same witness key cosigns incompatible checkpoints not connected by valid consistency.
2. `WITNESS_STATE_ROLLBACK_PROOF` — later witness state/cosignature regresses below an authenticated prior state.
3. `POLICY_ROTATION_SELF_AUTHORIZATION_PROOF` — new policy installed without predecessor continuity or approved recovery authority.
4. `POLICY_ROTATION_FORK_LAUNDERING_PROOF` — rotation accepts a branch conflicting with retained old-policy evidence.
5. `HISTORICAL_KEY_STATUS_REWRITE_PROOF` — current metadata contradicts archived signed key-status history without authorized supersession.
6. `BOOTSTRAP_SCOPE_INFLATION_PROOF` — TOFU/local bootstrap represented as independently established global trust.
7. `DECOMMISSION_EVIDENCE_LOSS_PROOF` — required old policy/key/checkpoint evidence destroyed before archival closure.
8. `WITNESS_RECOVERY_FROM_ZERO_PROOF` — witness resumes signing without recovering prior monotonic state.
9. `CROSS_POLICY_QUORUM_SAFETY_FAILURE_PROOF` — conflicting frontiers each satisfy their respective policy across a transition.
10. `PUBLICATION_NAMESPACE_RESET_PROOF` — same authority lineage reintroduced as a fresh namespace to evade old fork/rollback history.

## 9. RED-first executable matrix

Implementation should begin with failing tests. Minimum matrix: 80 cases, grouped 10×8.

A. Bootstrap (8): unauthenticated discovery; TOFU label; TOFU scope inflation; authenticated OOB pin; continuity bootstrap; stale bootstrap; conflicting bootstrap anchors; recovery bootstrap preserves old fork.

B. Witness key lifecycle (8): planned retirement; expiry; known pre-event compromise; known post-event compromise; unknown compromise time; key loss; key-id collision; historical key-material omission.

C. Witness durable state (8): monotonic advance; same-size/same-root replay; same-size/different-root reject; lower-size reject; crash before persist; crash after persist/before reply; restored-current state; restored-rolled-back state refuses signing.

D. Policy rotation (8): dual-authorized rotation; new-only self-authorization reject; old-only incomplete activation; skipped generation; activation-frontier mismatch; policy-digest mismatch; rollback to old policy; conflicting concurrent rotations.

E. Cross-policy safety (8): safe overlap; insufficient overlap; joint epoch; external monotonic bridge; disjoint immediate cutover reject; compromised overlap domain; independence-domain collapse; conflicting old/new accepted frontiers.

F. Publication history (8): append-only consistency; missing consistency; stale witnessed frontier; checkpoint omission; losing-fork retention; namespace rename; log-key rotation continuity; log-key self-rotation reject.

G. Archival/decommission (8): complete history archive; missing old key; missing old policy; missing rotation statement; missing losing branch; verifier replay success; decommission before archive closure reject; archive rollback detection.

H. Offline/freshness (8): valid historical offline prefix; no-currentness claim; fresh external frontier; expired freshness; future policy unknown; later compromise unknown offline; appeal after archive frontier; locally pinned stale view.

I. Recovery/governance (8): authorized recovery; unauthorized reset; compromised governance key; preserved conflicting branches; root migration continuity; unknown predecessor; recovery policy version mismatch; recovery after witness-state loss.

J. Fraud/adversarial (8): witness equivocation; state rollback; self-authorized rotation; fork laundering; historical status rewrite; TOFU inflation; decommission evidence loss; namespace reset.

## 10. Mechanism donors and evidence

- C2SP `tlog-witness` v1.0.0: a witness is bound to a name/public key, tracks the latest checkpoint per log, verifies consistency from the stored checkpoint, returns conflict on mismatched old state/root, and MUST persist the new checkpoint before responding. This directly supports stateful anti-rollback witness semantics.
- RFC 9162 / CT lineage: global split-view detection requires comparing observed tree heads/views; a signed tree head alone does not establish global non-equivocation.
- TUF root migration: successor root metadata is verified incrementally and is signed by thresholds from both predecessor and successor root definitions. This is the donor for old+new continuity authorization during witness-policy rotation.
- Sigstore uses TUF-distributed trust roots and documents bootstrapping from a pinned historical root followed by a chain to the latest root; this is a practical example that bootstrap material is explicit and versioned, not magically learned from the current endpoint.

## 11. Frozen decisions

1. First-use network discovery is never silently trusted.
2. TOFU is allowed only as an explicit local bootstrap class and cannot be promoted to global independent trust by wording.
3. Witness historical trust is time-indexed; ordinary retirement is not retroactive invalidation.
4. Unknown compromise start yields `UNKNOWN_WITNESS_HISTORICAL_TRUST` when quorum safety depends on that key.
5. Witness anti-equivocation requires durable monotonic state, not only a signing key.
6. Normal policy rotation requires predecessor continuity + successor acceptance over one canonical transition.
7. Rotation must prove cross-policy anti-fork safety; disjoint instantaneous cutover without a joint/external bridge is unsafe.
8. Old policy/key/checkpoint/fork evidence is append-only historical material and must survive rotation and decommission.
9. Offline verification proves only up to an authenticated witnessed frontier unless freshness evidence is present.
10. No key/log/policy migration may reset the authority namespace or erase a previously proven fork.

## 12. Next distinct evidence task

`publication witness recovery quorum / lost-state disaster recovery / anti-cloning and simultaneous-active-witness semantics`:

Define how a witness recovers after durable state loss without accepting size zero, how recovery state is authorized from independent archives/peer witnesses/log consistency evidence, how restored clones are prevented from both becoming active signers, how lease/fencing applies to witness identity, and how recovery behaves when historical terminal state is itself disputed.
