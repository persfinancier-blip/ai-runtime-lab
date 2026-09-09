# Emergency-root anti-amplification, promise GC, multi-beacon governance, adjudicator confidentiality, and PQ negotiation state-machine v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE; executable RED/GREEN pending
Freeze tag: `EMERGENCY_ROOT_ANTI_AMPLIFICATION_PROMISE_GC_MULTIBEACON_GOVERNANCE_ADJUDICATOR_CONFIDENTIALITY_PQ_STATE_MACHINE_V1_FROZEN`
Parent: LAB-093 / #178 design follow-up. Does not supersede LAB-086 exact executable gate.

## Scope

This evidence slice closes five distinct follow-ups recorded in `state/CURRENT.md`:

1. emergency-root challenge-channel anti-amplification/rate-limit evidence and quorum recovery under simultaneous member compromise;
2. promise-accumulator deletion/GC safety with historical non-membership proofs;
3. multi-beacon source enrollment/removal governance and correlated-outage recovery without outcome-conditioned denominator changes;
4. copy-domain adjudicator quorum/independence and evidence-confidentiality boundaries;
5. transparency mirror/witness independence, trust-root expiry/offline recovery, and PQ/hybrid negotiation downgrade across retry, resumption and 0-RTT.

No executable PASS is claimed here. The exact LAB-086 source path was re-probed first in this run and `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com` (exit 128).

## Primary-source donors

- TLS 1.3 / RFC 8446: 0-RTT replay risk, anti-replay state, and the rule that a failed 0-RTT attempt may retry with 0-RTT disabled without disabling TLS 1.3. https://www.rfc-editor.org/rfc/rfc8446.html
- TLS 1.3 successor text / RFC 9846: explicitly reiterates that 0-RTT has no inherent replay protection and retry behavior can duplicate an application message across connections. https://www.rfc-editor.org/info/rfc9846/
- Sigstore Rekor security model: append-only log verification requires monitoring; a single log operator is not equivalent to an independent monitor/witness. https://docs.sigstore.dev/about/security/
- Sigstore Rekor sharding: old trees may be frozen and signing keys rotated while historical entries remain queryable. https://docs.sigstore.dev/logging/sharding/
- Sigstore Rekor auditing: independent monitors such as omniwitness can audit consistency. https://docs.sigstore.dev/logging/overview/
- TUF metadata model: signed metadata carries expiration and clients reject metadata older than trusted state; expiration is therefore a freshness boundary, not a request to silently accept stale roots offline. https://theupdateframework.io/docs/metadata/
- drand resharing specification: membership/threshold transitions are explicit protocol events; old shares cease to validate in the new group while the public beacon key can remain stable. https://docs.drand.love/docs/specification/
- drand v2 post-mortem: authorization mistakes around DKG control can let an operator force resharing/removal and reduce threshold, demonstrating that membership-transition authority is itself a critical capability boundary. https://docs.drand.love/blog/2025/03/21/drand-v2-0-postmortem/

## 1. Emergency-root challenge anti-amplification and simultaneous compromise recovery

### Frozen boundary

A dormant-root liveness challenge is an externally triggerable cryptographic operation. Therefore challenge authenticity alone is insufficient: a valid but attacker-amplified challenge stream can exhaust HSM/operator/quorum capacity or create a coercion side channel.

`AUTHENTIC_CHALLENGE != SAFE_CHALLENGE_CHANNEL`

Every accepted challenge must bind at least:

- `challenge_id` / nonce;
- root-generation and membership-generation IDs;
- verifier/challenger authority epoch;
- purpose class;
- issue time and deadline;
- cost/rate-limit class;
- previous accepted challenge sequence or monotonic counter where available;
- response disclosure class (proof-of-possession only; never raw share reconstruction).

The receiver enforces a policy-fixed budget before performing expensive threshold/HSM work. Rate-limit state is consequential security state and must not be reset by reconnect, process restart, challenger rotation, or retry unless an authenticated policy explicitly says so.

### Anti-amplification rules

- Duplicate/replayed `challenge_id` is answered from a cached decision/evidence path or rejected; it must not trigger another expensive ceremony.
- Multiple valid challenger identities in one control domain do not multiply the allowed budget unless the policy explicitly assigns separate quotas.
- Timeout is `LIVENESS_UNPROVEN`, not `MEMBER_LOST`, and cannot by itself lower threshold or remove members.
- Emergency recovery must not require revealing enough private material to the liveness verifier to reconstruct the root.
- A challenge failure caused by the verifier exceeding its own allowed request rate is not evidence against the member.

### Simultaneous member compromise

Recovery policy must freeze the recovery denominator before evaluating who responded. If `k` members are simultaneously compromised, a successor membership may activate only through an independently authorized recovery path whose authority is not itself derived solely from those compromised members.

`COMPROMISED_INCUMBENT_QUORUM != AUTHORITY_TO_DECLARE_ITSELF_CLEAN`

Required state:

- immutable predecessor membership generation;
- compromise evidence set and observation time;
- recovery-authority generation and denominator;
- proposed successor member set/threshold;
- proof that the successor still satisfies policy minimum independence domains;
- explicit handling of ambiguous/unreachable members;
- monotonic activation/rollback floor.

Threshold may not be lowered merely to make recovery possible after seeing which members remain available. If the configured independent recovery quorum cannot be reached, the state is `RECOVERY_AUTHORITY_UNAVAILABLE`, requiring owner/security escalation rather than automatic weakening.

## 2. Promise accumulator deletion / GC and historical non-membership

### Frozen boundary

Compaction established conservation of predecessor promises. GC adds a stronger problem: after predecessor records are physically removed, a verifier must still distinguish:

1. a promise that existed and reached a terminal disposition;
2. an outstanding promise carried forward;
3. an identifier that never belonged to the historical population;
4. a promise omitted maliciously before compaction/GC.

A membership proof for retained items is not a proof that a queried historical ID never existed.

`CURRENT_NON_MEMBERSHIP != HISTORICAL_NON_EXISTENCE`

### Required GC generation

Each immutable `PromiseGCGeneration` binds:

- predecessor population commitment/root and canonicalization version;
- predecessor count plus stable ID namespace/version;
- exact compaction-generation root;
- terminal-disposition set commitment;
- carried-outstanding set commitment;
- deleted-object scope and retention policy;
- proof system/accumulator version;
- archive locations sufficient to verify predecessor population and mapping;
- activation checkpoint and witness/quorum evidence.

Historical non-membership is valid only relative to a specific authenticated population root and namespace. A later accumulator that omits an ID cannot retroactively prove the ID never existed.

### GC safety

- Deletion is permitted only after the conservation proof and all required witness/checkpoint evidence are durably archived.
- A GC generation that cannot reproduce its predecessor population commitment after service retirement is `GC_ARCHIVE_INSUFFICIENT`.
- Terminal disposition proofs must remain verifiable after the object body is deleted.
- Reusing a deleted stable promise ID in a successor namespace is forbidden unless the namespace generation changes and verifiers bind that generation.
- An accumulator implementation upgrade creates a successor proof generation; it does not rewrite old proofs.

## 3. Multi-beacon enrollment/removal governance and correlated outage recovery

### Frozen boundary

The source set is part of the randomness security policy, not runtime discovery metadata.

`SOURCE_AVAILABILITY_CHANGE != AUTHORITY_TO_CHANGE_RANDOMNESS_DENOMINATOR`

Every beacon-policy generation binds:

- exact enrolled source identities/keys;
- independence/failure-domain claims;
- source-specific round mapping;
- combiner algorithm/version;
- minimum source denominator/threshold;
- timeout and missing-source rules;
- retry/fallback rules;
- enrollment/removal authority and quorum;
- effective round/time boundary.

Enrollment/removal takes effect only in a successor generation at a precommitted future boundary. Results already revealed under generation `G` cannot trigger membership changes for the same decision.

### Correlated outage

If several sources fail because they share a network/cloud/operator dependency, they count as one correlated failure for independence analysis even when their cryptographic keys differ.

Recovery choices must be predeclared. Valid examples:

- fail closed if fewer than policy-minimum independent domains respond;
- delay to a later predeclared round;
- use a predeclared emergency source set whose membership was committed before the outage.

Invalid:

- drop unavailable sources after observing the available outputs;
- retry only because the combined value is undesirable;
- enroll a convenient new beacon after reveal and recompute the same decision;
- classify correlation only after observing which sources failed.

The drand v2 post-mortem is a direct donor for treating membership-transition control as a high-risk authority: permissive DKG controls could let a rogue operator iteratively remove peers and reduce threshold.

## 4. Copy-domain adjudicator quorum, independence, and evidence confidentiality

### Frozen boundary

The adjudicator resolves conflicting evidence about whether a destructive/copy domain exists or contained material. Therefore the adjudicator is itself a consequential authority and cannot be modeled as one opaque signer.

`N_ADJUDICATOR_SIGNATURES != N_INDEPENDENT_ADJUDICATORS`

Each adjudication generation binds:

- fixed adjudicator population/denominator before evidence review;
- independence/control-domain metadata;
- conflicts and source snapshots under review;
- applicable evidence-access policy;
- verdict and confidence/coverage class;
- dissent/minority statements where policy requires;
- appeal successor linkage.

### Independence

Two adjudicators sharing the same employer/operator, credentials, evidence backend, or build/LLM pipeline may constitute one correlated decision domain. Policy defines which correlations are disqualifying rather than inferring independence from distinct public keys.

### Confidentiality

Full evidence disclosure can itself leak secrets, backup topology, customer data, key locations or destructive capabilities. Therefore adjudication separates:

- public commitment/root;
- least-privilege evidence excerpts;
- sealed/confidential evidence payloads;
- auditor-specific disclosure receipts;
- final public verdict and coverage statement.

A commitment to hidden evidence proves binding, not correctness or completeness. Adjudicators must prove they evaluated the complete policy-required evidence population without requiring public disclosure of all sensitive material. If confidentiality prevents a required independent adjudicator from inspecting necessary evidence, assurance becomes `ADJUDICATION_EVIDENCE_INSUFFICIENT`, not a silent lower threshold.

Appeals create a new generation. They preserve the predecessor verdict, evidence commitments, denominator and dissent instead of replacing them.

## 5. Transparency mirror/witness independence, trust-root expiry/offline recovery, and PQ retry/resumption/0-RTT downgrade

### Transparency independence

Rekor's model explicitly requires monitoring of the append-only log. A mirror that merely copies bytes from the primary does not provide independent split-view detection unless it independently verifies consistency/checkpoints and has an independent observation/custody path.

`MIRROR_COUNT != WITNESS_INDEPENDENCE`

Required historical verification package:

- entry bytes/digest;
- inclusion proof;
- signed checkpoint/tree head;
- consistency ancestry across relevant shard/key transitions;
- historical trust-root metadata;
- witness/monitor observations according to the historical denominator;
- enough archived material to verify after a shard is frozen or service retires.

Sigstore sharding is a donor: old trees can be frozen and keys rotated while historical entry lookup remains supported. Retirement must not erase the verification lineage.

### Trust-root expiry and offline recovery

TUF metadata expiration is a deliberate freeze-attack defense. Therefore:

`OFFLINE != PERMISSION_TO_IGNORE_EXPIRY`

An offline verifier may preserve historical verification with archived metadata that was valid for the historical event, but it must not use expired metadata to authorize a new consequential update unless an explicit offline-recovery policy allows it.

Offline root recovery must bind:

- last trusted monotonic root version;
- expiration state;
- successor root chain/version ordering;
- required threshold signatures;
- recovery authority/custody evidence;
- rollback floor.

A freshly signed metadata object with a lower version is still rollback. Clock uncertainty must become explicit `FRESHNESS_UNPROVEN`; it must not silently disable expiration checks.

### PQ/hybrid negotiation retry state machine

TLS 1.3 provides the key donor: 0-RTT is replayable, anti-replay state is required, and a client whose 0-RTT attempt encounters an older protocol may retry with 0-RTT disabled but should not disable TLS 1.3. This generalizes directly to PQ/hybrid negotiation:

`RETRY != AUTHORITY_TO_WEAKEN_CRYPTO_POLICY`

For every logical session/operation, authenticated negotiation evidence binds:

- logical operation ID;
- connection/session attempt ID;
- client offer set;
- server supported/selected suite;
- hybrid combiner policy;
- resumption ticket provenance and issuing policy epoch;
- retry counter/reason;
- 0-RTT vs 1-RTT state;
- effective crypto-policy epoch;
- transcript hash/link to predecessor attempt.

Rules:

- A network failure may trigger a retry, but the successor attempt inherits the minimum crypto strength required by the logical operation unless policy explicitly changed independently of the failure.
- Resumption tickets minted under an older/weaker policy cannot override a stricter current policy.
- 0-RTT is prohibited for non-replay-safe consequential state transitions unless the application has an exact anti-replay/idempotency contract.
- Rejecting 0-RTT may cause retry as 1-RTT, not downgrade from required PQ/hybrid to classical-only.
- If both peers advertised a policy-required PQ/hybrid suite on attempt 1, a retry that silently removes it is `NEGOTIATION_RETRY_DOWNGRADE` unless an authenticated policy transition predating the failure authorizes the change.
- Different frontends must share or conservatively coordinate anti-replay/negotiation-floor state. Otherwise an attacker can route retries across nodes to obtain inconsistent acceptance.
- A resumption/0-RTT transcript is not authorization for another logical operation merely because the ticket or old transcript verifies.

## RED-first matrix (40 cases)

### Emergency-root channel / recovery — ER01..ER08

1. `ER01` same signed challenge replayed 1,000 times -> one expensive ceremony maximum; subsequent requests cached/rejected.
2. `ER02` attacker rotates among challenger aliases in one control domain -> shared policy budget applies.
3. `ER03` rate-limit database restart -> quota/sequence survives; restart does not reset attack budget.
4. `ER04` verifier floods beyond allowed budget then records member timeout -> timeout cannot count as member-loss evidence.
5. `ER05` liveness proof path exposes enough shares to reconstruct root -> fail.
6. `ER06` simultaneous compromise reaches incumbent threshold but not independent recovery threshold -> no self-declared clean successor.
7. `ER07` recovery code lowers threshold after seeing unavailable members -> fail closed as outcome-conditioned recovery.
8. `ER08` valid independent recovery quorum activates successor at monotonic generation; predecessor challenges cannot roll it back.

### Promise accumulator GC — PG01..PG08

9. `PG01` all predecessor promises conserved before deletion -> GC eligible.
10. `PG02` one predecessor ID omitted but counts preserved via duplicated ID -> conservation proof fails.
11. `PG03` queried ID absent from current accumulator but present in historical predecessor -> current non-membership cannot claim historical non-existence.
12. `PG04` terminal object body deleted but disposition proof/archive intact -> historical verification passes.
13. `PG05` predecessor archive unavailable after service retirement -> `GC_ARCHIVE_INSUFFICIENT`.
14. `PG06` deleted stable ID reused without namespace-generation change -> reject.
15. `PG07` accumulator/proof implementation changes -> successor proof generation required; old proofs preserved.
16. `PG08` malicious GC marks OUTSTANDING as terminal without authenticated disposition -> reject.

### Multi-beacon governance — MB01..MB08

17. `MB01` source enrolled after outputs for target decision are visible -> cannot participate in that decision.
18. `MB02` source removed after its output is inconvenient -> denominator laundering detected.
19. `MB03` three keys share one operator/network failure domain -> independence count reflects correlated domain.
20. `MB04` correlated outage drops below precommitted minimum -> fail closed/delay according to prior policy.
21. `MB05` outage triggers precommitted emergency source set at future round -> allowed with generation evidence.
22. `MB06` retry selected because first combined random value is undesirable -> reject selective retry.
23. `MB07` membership/threshold transition authorized by insufficient DKG/governance authority -> reject.
24. `MB08` authenticated successor membership activates at future boundary; old generation remains historical verifier context.

### Adjudicator quorum/confidentiality — AJ01..AJ08

25. `AJ01` three signatures from one operational control domain -> do not count as three independent adjudicators.
26. `AJ02` denominator selected after seeing which adjudicators agree -> reject.
27. `AJ03` hidden evidence commitments differ between adjudicators for same generation -> equivocation.
28. `AJ04` required adjudicator cannot inspect necessary confidential evidence -> assurance insufficient; no silent denominator reduction.
29. `AJ05` public verdict reveals secret backup/key location beyond disclosure policy -> confidentiality failure.
30. `AJ06` least-privilege sealed evidence + complete-population proof permits policy-required independent review -> eligible.
31. `AJ07` appeal overwrites old verdict/evidence root -> reject; must create successor generation.
32. `AJ08` later adjudicator compromise degrades affected generation without deleting predecessor verdict/dissent.

### Transparency / expiry / PQ retry state — TP01..TP08

33. `TP01` three mirrors copy a malicious split view from one primary without independent consistency observation -> no three-witness claim.
34. `TP02` frozen Rekor shard + archived entry/inclusion/checkpoint/root lineage -> historical verification survives shard retirement.
35. `TP03` expired TUF-style metadata used offline to authorize a new update with no recovery policy -> reject.
36. `TP04` successor root has lower version but fresh signatures -> rollback rejected.
37. `TP05` clock unavailable offline -> `FRESHNESS_UNPROVEN`, not automatic expiry bypass.
38. `TP06` failed PQ/hybrid 0-RTT attempt retries 1-RTT while retaining required PQ/hybrid floor -> allowed.
39. `TP07` retry/resumption silently removes policy-required PQ/hybrid after network failure -> `NEGOTIATION_RETRY_DOWNGRADE`.
40. `TP08` replayed 0-RTT consequential operation routed to another frontend -> exact anti-replay/idempotency guard blocks duplicate side effect.

## Audit conclusions

1. Availability recovery and security-policy weakening must remain separate operations. DoS, outage, expiry, retry and partial compromise are never implicit authority to lower a threshold, remove sources, ignore expiration or weaken a cryptographic suite.
2. Historical verification requires population/denominator and trust-root context to survive GC, sharding, membership rotation and retirement.
3. Independence is an evidence claim about failure/control domains, not a count of keys, mirrors, beacon endpoints or signatures.
4. Retry/resumption state is part of the cryptographic authorization surface. A fresh transport connection does not reset the logical operation's minimum-security floor.
5. Confidentiality can constrain evidence disclosure, but cannot be used to pretend the required independent review occurred.

## Exact next distinct fallback

If exact LAB-086 source execution remains unavailable after re-probe, investigate and freeze: **challenge-budget authority rollover and distributed rate-limit consistency under partition + promise-GC archive witness quorum and accumulator parameter compromise/migration + beacon governance emergency-policy abuse and cross-beacon dependency attestation + confidential adjudication threshold-privacy/selective-opening and reviewer revocation + transparency gossip split-view evidence retention and PQ resumption-ticket key/algorithm lifecycle across policy deprecation**.

If exact source becomes available, stop design expansion and immediately return to the retained LAB-086 full real-schema/unsafe-seed/compileall/security-conflict gate.
