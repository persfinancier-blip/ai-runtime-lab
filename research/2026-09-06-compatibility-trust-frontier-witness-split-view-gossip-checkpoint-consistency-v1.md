# Compatibility trust-frontier witness, split-view gossip and checkpoint-consistency — V1 frozen contract

Date: 2026-09-06
Status: `COMPATIBILITY_TRUST_FRONTIER_WITNESS_SPLIT_VIEW_GOSSIP_CHECKPOINT_CONSISTENCY_V1_FROZEN`
Scope: LAB-093 design follow-up; no production witness network, verifier, or behavioral compatibility PASS is claimed.

## 1. Why this contract exists

The preceding adjudicator-trust contract froze authenticated trust roots, verifier generations, capability scopes, semantic diversity, revocation, quarantine and equivocation. That is still insufficient if a compromised or partitioned trust service can present **different individually valid trust-frontier histories to different consumers**.

A local verifier that sees one coherent signed sequence cannot, by itself, prove that another verifier was not shown a different coherent signed sequence. The missing property is cross-view consistency.

This contract therefore freezes a witness layer for the compatibility trust frontier. Its purpose is not to decide semantic compatibility. Its purpose is narrower and foundational:

- make every admitted trust-frontier checkpoint globally comparable;
- require cryptographic ancestry/consistency across frontier advances;
- obtain independent witness cosignatures before consequential admission;
- exchange checkpoints over multiple independent channels so split views cannot remain purely local;
- detect forks, rollback, stale-view pinning and withholding;
- preserve fork evidence rather than silently choosing a branch;
- support offline/air-gapped catch-up without granting stale state new authority;
- recover after a detected fork through an explicit higher-authority continuity procedure.

The central rule is:

> A locally valid trust-frontier checkpoint is not sufficient authority for consequential compatibility admission unless it is consistent with the verifier's retained frontier and satisfies the current witness policy.

## 2. Primary donor mechanisms

### 2.1 RFC 9162 — Certificate Transparency v2

RFC 9162 is the donor for Merkle append-only consistency proofs and the split-view threat model. It distinguishes local proof validation from the harder property that all clients are seeing a consistent log view. It explicitly notes that comparing signed tree heads through gossip can reveal inconsistent views, and that failed append-only/consistency checks yield signed evidence of log misbehavior.

Primary source:
- https://www.rfc-editor.org/rfc/rfc9162.html

Adopted mechanisms:
- signed checkpoints/tree heads;
- append-only Merkle consistency proofs between old and new checkpoints;
- conflicting signed checkpoints as durable misbehavior evidence;
- cross-client comparison/gossip as necessary protection against split views.

LAB does not reuse CT certificate semantics. The logged object here is verifier-trust/frontier state and compatibility-admission metadata.

### 2.2 C2SP transparency-log witness protocol

The C2SP witness protocol is the donor for stateful witness cosigning. A witness tracks the latest checkpoint it accepted for a log, verifies the log signature, verifies the consistency proof from the witness's retained checkpoint to the proposed checkpoint, persists the new checkpoint atomically, and only then returns a cosignature. It also specifies the important same-size rule: if old and new tree sizes are equal, root hashes must be identical.

Primary source:
- https://github.com/C2SP/C2SP/blob/main/tlog-witness.md

Adopted mechanisms:
- witness identity as name + public key + configured log/trust-origin scope;
- stateful latest-checkpoint tracking;
- consistency proof verification before cosigning;
- atomic check-and-persist-before-signing;
- rejection of stale or conflicting old-size requests;
- monitor-readable witness checkpoint surface.

LAB strengthens the model with authenticated witness capability generations, diversity domains, revocation/quarantine and explicit trust-frontier recovery semantics.

### 2.3 C2SP checkpoint / cosignature / policy formats

C2SP checkpoint and cosignature specifications are donors for canonical checkpoint commitments and witness quorum policy. A checkpoint binds an origin, tree size and root hash; witness cosignatures can be verified by clients; policy determines which witness subsets are strong enough.

Primary sources:
- https://github.com/C2SP/C2SP/blob/main/tlog-checkpoint.md
- https://github.com/C2SP/C2SP/blob/main/tlog-cosignature.md
- https://github.com/C2SP/C2SP/blob/main/tlog-policy.md

Adopted mechanisms:
- compact signed checkpoint object;
- witness cosignatures as independent statements that consistency was checked;
- quorum policy separate from mere signature validity;
- offline verification of cosigned checkpoints.

### 2.4 transparency-dev witness implementation/model

The transparency-dev witness project is a donor for the operational model: witnesses retain prior checkpoints, verify consistency proofs, countersign consistent checkpoints, and allow clients to demand witnessed checkpoints to resist split views.

Primary source:
- https://github.com/transparency-dev/witness

Adopted mechanism:
- witnesses are not mirrors of semantic application state; they are independent continuity observers.

## 3. Trust-frontier checkpoint identity

Every frontier advance produces a canonical immutable checkpoint:

```text
TrustFrontierCheckpointV1 {
  origin
  frontier_sequence
  frontier_state_root
  event_tree_size
  event_tree_root
  predecessor_checkpoint_digest
  trust_root_generation
  trust_policy_generation
  witness_policy_generation
  issued_at_logical
  checkpoint_schema_generation
  issuer_generation
  issuer_signature
}
```

### 3.1 `origin`

`origin` is a construction-bound identifier for the logical compatibility trust plane. It prevents a valid checkpoint for one environment/product/history from being replayed into another.

### 3.2 `frontier_sequence`

Strictly monotonic logical sequence. Sequence alone does not prove ancestry; it is an ordering hint checked together with predecessor digest and Merkle consistency.

### 3.3 `frontier_state_root`

Commitment to the complete current trust-plane state required for admission decisions, including at minimum:

- active trust-root generation;
- authorized adjudicator generations/capability scopes;
- revocations and quarantines;
- diversity policy;
- witness policy;
- admitted/revalidation-required compatibility edges where authority-relevant;
- compromise/equivocation/fork markers;
- recovery epochs.

### 3.4 `event_tree_size` / `event_tree_root`

The trust plane retains an append-only canonical event log. The checkpoint commits to the event tree so a verifier can require a consistency proof from its retained checkpoint to the candidate checkpoint.

### 3.5 `predecessor_checkpoint_digest`

Direct parent commitment. This provides simple chain ancestry while the Merkle consistency proof proves that the full event history is append-only.

## 4. Canonical frontier event log

Every authority-relevant transition is represented as a canonical append-only event before it can influence the frontier state root.

Examples:

- trust-root rotation;
- adjudicator authorization/revocation/quarantine;
- witness authorization/revocation/quarantine;
- diversity-policy update;
- proof-bundle admission/revalidation state change;
- equivocation proof registration;
- split-view proof registration;
- recovery epoch start/completion;
- explicit emergency authority transition.

No transition may exist only as a mutable current-state row. Current state is derived from authenticated event history plus canonical reducer generation.

## 5. Witness generation and capability

A witness is not identified only by a public key. Each admitted witness is a content-addressed `witness_generation` committing to:

- signing-key generation;
- source/build identity;
- checkpoint parser/canonicalizer generation;
- consistency-proof verifier implementation/dependency root;
- durable state-store semantics;
- supported checkpoint/proof schema generations;
- configured trust-frontier origin(s);
- capability scope;
- operator/hosting/administrative diversity labels;
- network/distribution dependencies relevant to split-view resistance.

Required capability scopes include:

- `VERIFY_FRONTIER_CHECKPOINT_SIGNATURE`
- `VERIFY_FRONTIER_ANCESTRY`
- `VERIFY_EVENT_TREE_CONSISTENCY`
- `COSIGN_FRONTIER_CHECKPOINT`
- `SERVE_LATEST_COSIGNED_CHECKPOINT`
- optionally `GOSSIP_CHECKPOINTS`

A valid signature from a witness generation lacking the required current capability scope does not satisfy quorum.

## 6. Witness atomicity rule

For each trust-frontier origin, a witness persists one latest accepted checkpoint and its identity.

Acceptance of candidate `C_new` from retained `C_old` is one atomic operation:

1. verify origin and issuer authority;
2. verify checkpoint canonical form/signature;
3. verify current witness trust-policy authorization;
4. require candidate sequence/tree size not less than retained state;
5. if sequence/tree size is equal, require exact same checkpoint/root identity;
6. verify direct predecessor/ancestry rule where applicable;
7. verify Merkle consistency proof `C_old -> C_new`;
8. persist `C_new` durably;
9. only after durable persistence, return witness cosignature.

The witness must never sign first and persist later. Concurrent requests must not allow the witness to move from N to N+K and then back to N.

## 7. Witness diversity

Witness quorum is calculated after diversity collapse.

Different keys, machines or URLs are not necessarily independent. For split-view resistance, common-mode risks include:

- same operator/admin authority;
- same signing service/HSM tenant;
- same witness implementation with an unfixed consistency bug;
- same parser/canonicalizer library;
- same hosting account/control plane;
- same network edge/CDN path where the threat is selective distribution;
- same deployment pipeline/build root;
- same parent organization where policy requires organizational independence.

The witness policy specifies minimum independent domains. Example:

```text
witness_quorum:
  signatures >= 3
  independent_operator_domains >= 2
  independent_consistency_verifier_lineages >= 2
  independent_distribution_domains >= 2
```

Quorum is evaluated only after removing revoked, quarantined, stale, wrong-scope and common-mode-collapsed witnesses.

## 8. Client/verifier admission rule

A consequential compatibility PASS may rely on checkpoint `C` only when all are true:

1. `C` is validly signed by the configured trust-frontier issuer generation;
2. `C.origin` matches the construction-bound trust plane;
3. `C` is not older than the verifier's retained authenticated frontier;
4. the verifier has a valid consistency/ancestry path from retained checkpoint to `C`;
5. `C` satisfies the current witness quorum/diversity policy;
6. no contradictory checkpoint or fork proof exists for `C.origin` at or before the relevant recovery epoch;
7. no required witness is currently revoked/quarantined in a way that invalidates the historical quorum for this checkpoint;
8. the current trust-root/witness-policy frontier authorizes use of `C` for the requested admission scope.

A verifier may cache a valid witnessed checkpoint, but cache age is not itself authority to skip freshness or withholding policy.

## 9. Split-view detection

A split view exists when two authenticated checkpoints for the same origin cannot both belong to one append-only history.

### 9.1 Same sequence/tree size, different root

Immediate cryptographic contradiction:

```text
(origin, size=N, root=A) != (origin, size=N, root=B)
```

Both signed checkpoints are retained as fork evidence.

### 9.2 Different sizes with no valid consistency proof

If `C_small` and `C_large` are individually issuer-valid but no valid append-only consistency proof connects them, they are conflicting views.

### 9.3 Predecessor-chain contradiction

Two checkpoints can also conflict if they claim incompatible predecessor ancestry even when higher-level mutable state superficially matches.

### 9.4 Contradictory witness behavior

A witness equivocates if it validly cosigns incompatible checkpoints for the same origin/recovery epoch. Both cosignatures become durable witness-equivocation evidence and the witness generation is quarantined.

## 10. Gossip channels

The trust-frontier must not depend on a single distribution endpoint for cross-view detection.

Checkpoint gossip uses multiple channels chosen to fail independently where practical:

- direct trust-frontier service response;
- witness monitoring endpoints;
- independent witness-to-witness exchange;
- verifier-to-verifier checkpoint exchange;
- append-only archival/transparency publication;
- offline signed checkpoint transfer for air-gapped environments;
- optional operator-owned out-of-band monitoring channel.

The canonical checkpoint digest is the gossip unit. Full state does not need to be exposed to every channel.

### 10.1 Gossip acceptance

Receiving a newer checkpoint through gossip does not immediately grant authority. The receiver verifies issuer/witness signatures and consistency from its retained checkpoint first.

### 10.2 Gossip contradiction

Receiving an incompatible authenticated checkpoint is sufficient to enter split-view fail-closed state. The receiver must not discard it because it came from a lower-priority channel.

### 10.3 Channel diversity

Multiple URLs behind one CDN/account are one distribution domain unless policy proves otherwise. Witness policy records distribution dependencies where they materially affect split-view detection.

## 11. Freeze and withholding detection

A malicious service may avoid an obvious fork and instead pin selected consumers to an old but internally valid checkpoint.

Therefore availability/freshness policy distinguishes:

- `CONSISTENT_AND_FRESH`
- `CONSISTENT_BUT_STALE`
- `WITHHOLDING_SUSPECTED`
- `PARTITIONED`
- `SPLIT_VIEW_CONFIRMED`

### 11.1 Freshness evidence

Freshness may be established from:

- monotonic logical frontier observed through independent witnesses;
- signed checkpoint logical issuance sequence/time;
- maximum allowed checkpoint age for the deployment;
- external known-frontier commitment where one already exists in the LAB authority graph.

Wall-clock time alone is not sufficient authority because clock control is not equivalent to trust-frontier continuity.

### 11.2 Withholding rule

If a verifier remains at `F_old` while the configured independent witness quorum proves `F_new > F_old`, the old verifier is stale even if its checkpoint remains cryptographically valid.

For consequential operations, stale state fails closed once policy freshness bounds are exceeded.

### 11.3 No single endpoint as oracle

Failure to fetch a newer checkpoint from one service is not proof of withholding. Withholding classification requires evidence from independent channels/witnesses or expiry of a configured freshness bound.

## 12. Partial partitions

During network partition:

- each side may continue verifying already-retained history locally;
- neither side may manufacture a lower witness threshold to maintain availability;
- new consequential admission requires the configured currently satisfiable witness policy;
- if policy allows limited degraded operation, that capability must already be explicit and non-consequential or separately authorized; it is not inferred during outage;
- once connectivity returns, checkpoints are cross-compared before normal admission resumes.

If two partitioned sides advanced onto incompatible authenticated frontiers, reconnection enters `SPLIT_VIEW_CONFIRMED`, not latest-wins reconciliation.

## 13. Witness revocation and quorum degradation

Witness revocation/quarantine follows the same monotonic trust-frontier model as adjudicators.

Reasons include:

- key compromise;
- witness equivocation;
- consistency-verifier defect;
- state rollback;
- deployment/provenance compromise;
- misdeclared diversity/common-mode dependency;
- persistent freshness/monitoring failure where policy requires liveness.

Historical checkpoints are reevaluated according to the reason/effective interval:

- routine key rotation need not invalidate past cosignatures;
- unknown-start key compromise may force historical checkpoints in the affected interval to `REVALIDATION_REQUIRED`;
- consistency-verifier defect invalidates cosignatures whose proof path intersects the defective generation;
- equivocation triggers quarantine and blast-radius analysis.

Threshold is never silently lowered after revocation. A threshold/policy change is itself a high-authority trust-frontier event.

## 14. Offline and air-gapped catch-up

Air-gapped systems may receive a proof bundle containing:

- retained local checkpoint identity;
- target checkpoint;
- complete consistency proof from local checkpoint to target;
- all intermediate trust-root/witness-policy transitions needed for validation;
- required witness cosignatures for target and policy transitions;
- revocation/quarantine/fork records up to target frontier;
- optional archived checkpoint chain for audit.

Rules:

1. offline media is a transport, not a trust root;
2. target must descend consistently from the locally retained checkpoint;
3. target must satisfy witness policy valid at the target frontier;
4. bundle cannot erase a locally known newer frontier;
5. an old but internally valid bundle cannot roll the node backward;
6. if the node has locally retained fork evidence, a normal catch-up bundle cannot clear it;
7. after long disconnection, policy may require a minimum multi-witness freshness proof before consequential operation resumes.

## 15. Archive, backup and restore

Backups store checkpoint/witness history as evidence but cannot reset authority.

On restore:

- compare restored checkpoint with any externally retained/global frontier;
- if restored state is behind, it is archival/stale until caught up;
- if restored state conflicts, enter split-view state;
- missing revocation/fork events are treated as incomplete history, not proof they never occurred;
- restored witness local state must never be permitted to cosign a checkpoint older than a checkpoint it had previously made externally observable.

Where witness rollback cannot be ruled out from local storage alone, witness continuity requires an external monotonic anchor, hardware-backed rollback protection, or a separately witnessed state mechanism. A plain filesystem backup is not sufficient.

## 16. Fork evidence object

A canonical `TrustFrontierForkProofV1` contains:

```text
TrustFrontierForkProofV1 {
  origin
  checkpoint_a
  checkpoint_b
  issuer_verification_evidence_a
  issuer_verification_evidence_b
  witness_cosignatures_a[]
  witness_cosignatures_b[]
  failed_or_impossible_consistency_relation
  first_observed_channels[]
  first_observed_logical_time
  proof_digest
}
```

The proof is append-only evidence. Registering it advances the trust frontier into a forked recovery epoch; it is never deleted merely because recovery later succeeds.

## 17. Recovery after detected fork

Fork recovery is deliberately not automatic.

A confirmed split view means ordinary trust-frontier authority has failed. Recovery requires a separately defined higher-authority continuity action that:

1. freezes consequential admission;
2. preserves both branches and all witness evidence;
3. determines blast radius of decisions made under each branch;
4. identifies the last common authenticated checkpoint;
5. selects or reconstructs a canonical successor only under explicit recovery authority;
6. creates a new `recovery_epoch` bound to the fork proof and last common checkpoint;
7. rotates compromised issuer/witness keys/generations as required;
8. republishes a canonical recovery checkpoint with fresh witness quorum/diversity;
9. forces revalidation of compatibility edges whose authority depended on the abandoned/conflicted branch;
10. never pretends the fork did not occur.

`latest sequence`, `largest tree`, `most signatures`, `majority branch`, or `branch seen by main service` are not sufficient recovery rules.

## 18. Checkpoint withholding versus fork recovery

Do not conflate stale withholding with cryptographic fork.

- If all observed checkpoints are mutually consistent but one client is old: stale/withholding path.
- If authenticated checkpoints are inconsistent: split-view/fork path.

A stale client can usually catch up via consistency proof. A forked client cannot safely choose a branch through ordinary catch-up.

## 19. Required storage/indexes

Durable implementation needs indexes by:

- checkpoint digest;
- origin + frontier sequence;
- origin + event tree size;
- predecessor digest;
- witness generation;
- issuer generation;
- trust-root generation;
- witness-policy generation;
- recovery epoch;
- revocation/quarantine interval;
- fork-proof references;
- compatibility edges admitted under checkpoint.

This enables blast-radius queries after witness or issuer compromise.

## 20. Security boundaries

This contract proves continuity of the trust-frontier history. It does **not** prove:

- semantic correctness of a compatibility verdict;
- absence of collusion by all quorum witnesses + issuer;
- correctness of a shared buggy consistency implementation unless diversity policy catches the common mode;
- global real-time freshness without an explicit freshness policy and independent observation;
- physical availability under partition/DoS.

Witnessing reduces the power of one log/trust service to equivocate silently. It does not turn signatures into semantic truth.

## 21. RED-first executable matrix — 80 cases frozen

No production implementation should claim this contract until the following cases exist as executable RED/GREEN tests at the appropriate abstraction level.

### A. Checkpoint identity and canonicalization (1–8)
1. valid genesis checkpoint accepted;
2. wrong origin rejected;
3. noncanonical checkpoint encoding rejected;
4. bad issuer signature rejected;
5. same sequence + same root accepted idempotently;
6. same sequence + different root rejected as fork;
7. changed predecessor digest without event-tree change rejected;
8. unknown checkpoint schema generation rejected.

### B. Consistency and ancestry (9–16)
9. valid N→N+1 consistency accepted;
10. valid N→N+K consistency accepted;
11. malformed consistency proof rejected;
12. proof for wrong old size rejected;
13. proof for wrong new root rejected;
14. tree-size rollback rejected;
15. sequence increase with inconsistent predecessor rejected;
16. individually valid checkpoints with no consistency path produce fork evidence.

### C. Witness atomicity/state (17–24)
17. witness persists before cosigning;
18. simulated crash before persistence yields no cosignature;
19. simulated crash after persistence permits idempotent retry;
20. concurrent N+1/N+2 requests cannot rollback witness state;
21. stale old-size request rejected with retained size;
22. same-size same-root request idempotent;
23. same-size different-root request rejected/quarantined as appropriate;
24. witness state restore to older local backup cannot silently cosign backward.

### D. Witness authorization/diversity (25–32)
25. unknown witness signature ignored/not counted;
26. revoked witness not counted;
27. quarantined witness not counted;
28. wrong capability scope not counted;
29. three keys from one collapsed operator domain satisfy only one domain;
30. shared critical verifier lineage collapses diversity;
31. independent required domains satisfy quorum;
32. automatic threshold lowering after degradation rejected.

### E. Gossip/split view (33–40)
33. newer consistent checkpoint from alternate channel triggers catch-up;
34. incompatible checkpoint from alternate channel triggers fail-closed fork;
35. lower-priority channel evidence cannot be discarded solely by channel rank;
36. verifier-to-verifier contradictory checkpoints create durable fork proof;
37. witness-monitor endpoint contradiction detected;
38. two URLs behind one configured distribution domain do not satisfy channel diversity;
39. stale gossip older than retained frontier cannot roll back;
40. malformed/untrusted gossip cannot advance authority.

### F. Freeze/withholding/freshness (41–48)
41. old but within freshness bound allowed only where policy says;
42. old beyond bound blocks consequential admission;
43. independent witnesses proving newer frontier mark client stale;
44. one unreachable endpoint alone does not prove withholding;
45. one stale witness cannot pin client when quorum proves newer frontier;
46. wall-clock rollback cannot make stale frontier fresh;
47. logical frontier freshness survives benign clock skew;
48. withholding suspicion never auto-selects an unseen branch.

### G. Partitions and reconnection (49–56)
49. partition with no new consequential admission preserves local read-only verification;
50. partition cannot lower witness threshold;
51. reconnect with consistent advancement catches up;
52. reconnect with incompatible advancement enters fork state;
53. largest tree does not auto-win;
54. latest timestamp does not auto-win;
55. majority endpoint count does not auto-win;
56. previously known fork evidence prevents ordinary admission after reconnect.

### H. Revocation/compromise (57–64)
57. routine witness key rotation preserves valid historical cosignatures per policy;
58. compromised witness key with bounded interval marks affected checkpoints for revalidation;
59. unknown-start compromise widens revalidation interval conservatively;
60. witness consistency-verifier defect invalidates intersecting proof paths;
61. witness equivocation quarantines generation;
62. issuer compromise transitions to recovery rather than ordinary rotation when old authority is insufficient;
63. revoked witness generation cannot be “unrevoked” under same identity;
64. fixed witness implementation requires new generation/diversity evaluation.

### I. Offline/archive/restore (65–72)
65. valid offline consistency bundle advances from retained frontier;
66. offline bundle missing intermediate trust-policy transitions rejected;
67. offline bundle older than retained frontier rejected as authority;
68. offline bundle conflicting with retained fork evidence rejected;
69. restored stale server state cannot lower external/global frontier;
70. archive missing revocation segment is incomplete, not clean history;
71. restored witness cannot cosign behind externally observed prior state;
72. air-gapped catch-up after long gap enforces configured witness-freshness policy.

### J. Fork recovery (73–80)
73. fork proof preserves both authenticated branches;
74. ordinary catch-up cannot clear fork state;
75. recovery requires explicit recovery authority generation;
76. recovery binds last common checkpoint and fork proof;
77. recovery rotates compromised issuer/witness generations when required;
78. compatibility edges admitted solely under abandoned/conflicted branch become `REVALIDATION_REQUIRED`;
79. recovered checkpoint requires fresh witness quorum/diversity;
80. historical fork evidence remains queryable after successful recovery.

## 22. Implementation order

When exact executable source becomes available, implement in this order:

1. canonical checkpoint/event schemas and digest fixtures;
2. retained checkpoint store + consistency verifier;
3. witness atomic state machine;
4. witness policy/diversity evaluator;
5. verifier-side witnessed checkpoint admission;
6. gossip ingestion + fork-proof builder;
7. freshness/withholding classifier;
8. offline catch-up bundle verifier;
9. revocation/blast-radius integration;
10. explicit fork-recovery executor;
11. execute the full 80-case matrix RED→GREEN;
12. run composition tests with the previously frozen adjudicator-trust/proof-bundle contracts.

Do not build network-facing witness automation before the local deterministic checkpoint/consistency/recovery semantics are executable and audited.

## 23. Frozen decisions

The following are frozen for V1:

- trust-frontier authority is checkpointed over an append-only canonical event history;
- consequential admission requires retained-frontier consistency plus current witness policy, not merely issuer signature validity;
- witnesses are stateful, persist-before-cosign continuity observers;
- witness identity includes capability and implementation/dependency generation, not only key identity;
- quorum is evaluated after revocation/quarantine/scope/diversity collapse;
- same-size different-root authenticated checkpoints are immediate fork evidence;
- inconsistent authenticated checkpoints from any valid observation channel cause fail-closed split-view state;
- gossip uses multiple independent channels; no one distribution endpoint is globally authoritative;
- stale/withholding and fork are distinct states;
- partitions never implicitly weaken witness threshold;
- backups/offline media cannot roll back a newer retained/global frontier;
- confirmed fork recovery requires separate explicit recovery authority and preserves evidence permanently;
- no production behavioral PASS is claimed by this research note.

## 24. Next distinct research task

After this contract, the next unblocked design question is a **trust-frontier monitor completeness / witness-liveness / omission-evidence contract**: define what evidence proves that witnesses and monitors are actually observing required frontier advances; how to distinguish benign delay from selective omission; how checkpoint publication deadlines and monitor coverage are committed; how stale-but-non-equivocating witnesses are degraded; how a malicious issuer can be detected when it withholds updates from all currently reachable clients but not from archival channels; and what RED cases prove non-vacuous monitoring coverage without turning availability telemetry into authority.