# Provenance recovery, witness tombstoning, unlearning proof budgets, privacy mapping, provider failover, and authority inventory — v1

Status: DESIGN FROZEN / RED-FIRST CONTRACT
Date: 2026-09-11
Primary follow-up: LAB-093/#178 family; does not supersede LAB-086 execution priority.

## Why this slice exists

The preceding freezes established that signed provenance, witness key rotation, unlearning attestations, privacy tombstones, provider receipts, and authority inventories are not self-authenticating merely because individual records verify cryptographically. This slice closes the next ambiguity: how recovery behaves after equivocation, reassignment, expiry, failover, or discovery of previously hidden authority.

## Frozen contract

### 1. Canonical recovery after provenance-root equivocation

`RECOVERY_ROOT_SIGNED != EQUIVOCATION_RESOLVED`.

When two same-generation provenance roots are individually authentic but incompatible, neither may be selected by timestamp, arrival order, signer preference, or local majority alone. Recovery evidence MUST bind:
- the disputed root generation;
- both competing root digests;
- the last non-disputed predecessor digest;
- an explicit recovery generation strictly above the disputed generation;
- the recovery policy/issuer set and its own provenance root;
- the evidence cutoff used to conclude which history is canonical;
- a monotonic rollback floor preventing later resurrection of the rejected branch.

A recovery root is valid only if the recovery authority is independent of the compromised/equivocating authority set according to the configured failure-domain policy. If independence cannot be established, state remains `EQUIVOCATION_UNRESOLVED`.

### 2. Witness reassignment and tombstoning across overlapping membership epochs

`NEW_WITNESS_KEY != NEW_WITNESS_IDENTITY` and `IDENTITY_REASSIGNED != PREDECESSOR_VOTE_ERASED`.

Witness membership is evaluated using stable canonical witness/failure-domain identity over explicit membership epochs. A witness reassignment must carry:
- old canonical witness ID;
- new canonical witness ID;
- predecessor membership epoch;
- successor membership epoch;
- authorization from the membership authority valid at the transition cutoff;
- a tombstone preventing the predecessor identity from being counted again in overlapping epochs.

Overlapping epochs may count a stable failure domain at most once. Cross-signing between predecessor and successor keys cannot manufacture an extra vote. If reassignment evidence is ambiguous or circular, quorum evaluation fails closed.

### 3. Proof-budget composition for certified and approximate unlearning

`MULTIPLE_UNLEARNING_ATTESTATIONS != EXACT_DELETION_PROOF`.

Every component in a derived model/data path carries a deletion-proof class:
1. `EXACT_DELETION_PROOF`
2. `CERTIFIED_BOUND(epsilon_or_other_bound, assumptions)`
3. `EMPIRICAL_APPROXIMATION(test_suite, confidence_scope)`
4. `UNKNOWN`

Composition is monotonic toward weaker evidence. A chain containing an empirical or unknown component cannot be promoted to exact merely because several independent tests pass. Certified bounds compose using their stated mathematical assumptions; if assumptions are incompatible or unverifiable, the composition is `UNKNOWN`.

Derived artifacts — ensemble members, merged checkpoints, distilled students, embeddings, caches, ANN indexes, quantized copies, adapters, sparse shards — inherit the union of relevant holdout/training influence lineage unless a stronger proof explicitly removes that lineage.

### 4. Privacy namespace mapping proof expiry/deletion without accounting loss

`MAPPING_PROOF_EXPIRED != PRIVACY_HISTORY_EXPIRED` and `IDENTIFIER_DELETED != BUDGET_RESET`.

Privacy accounting stores a monotonic subject-accounting lineage independent of the currently usable identity mapping proof. Mapping proofs carry namespace epoch, resolver/model version, evidence cutoff, expiry, and revocation status.

On expiry/deletion:
- the system may lose the ability to assert a positive identity mapping;
- cumulative spend/reservations/unknown-loss floors MUST NOT decrease;
- a later relink may merge accounting lineages conservatively;
- a split may separate future authorization only after proving it cannot undercount historical loss;
- absence of a live mapping proof is not proof of subject disjointness.

### 5. Provider fork finality through failover/recovery

`FAILOVER_PROVIDER_CURRENT != PREDECESSOR_RECEIPT_FORK_FINALIZED`.

Provider failover introduces a new provider epoch but does not settle unresolved receipts from the predecessor epoch. Finality evidence MUST bind provider identity, provider epoch, logical operation identity, canonical payload digest, predecessor sequence/fork set, and an authenticated finality rule.

Arrival time and signing-key freshness do not choose a winner. Sequence gaps, contradictory receipts, timeout-after-send, or restored old signing keys keep the operation unresolved until provider-specific evidence proves one canonical external history or proves no further predecessor effect can occur.

Compensation is a new external effect with its own logical ID and bounded ancestry; it does not delete the original effect from history.

### 6. Recursive authority-inventory completeness under cross-signing/shared recovery roots

`ALL_ENUMERATED_DOMAINS_ACKED != AUTHORITY_UNIVERSE_COMPLETE`.

A ticket/security epoch or equivalent predecessor authority may be garbage-collected only after recursively enumerating every domain capable of restoring, deriving, unwrapping, replaying, or reauthorizing predecessor material. Inventory nodes include at minimum KMS/HSM replicas, wrapped keys, backup/DR sets, escrow, offline recovery credentials, dormant regions, replay-state stores, signing/recovery issuers, and parent/root credentials.

Cross-signing or shared recovery roots collapse nominally separate nodes into one correlated authority domain for independence calculations. Inventory completeness evidence MUST include parent/root dependencies and a closure digest over the reachable authority graph. Discovery of a previously omitted node reopens extinction proof and quarantines affected resumption/recovery paths, but does not lower the already-monotonic security epoch floor.

## RED-first matrix (40 cases)

### Provenance recovery (1-7)
1. Same-generation roots A/B both valid -> unresolved, no automatic winner.
2. Newer local timestamp on A -> still unresolved.
3. Majority of nodes saw A but recovery authority shares compromised root -> unresolved.
4. Independent recovery authority binds A/B + predecessor + higher generation -> recover canonical branch.
5. Recovery root omits losing branch digest -> reject.
6. Replayed rejected branch after recovery -> rollback reject.
7. Recovery evidence cutoff predates equivocation discovery -> reject.

### Witness reassignment (8-14)
8. Key rotation for same witness -> one vote.
9. Cross-signed old/new keys in overlapping epoch -> one vote.
10. Reassignment without predecessor membership authorization -> reject.
11. Authorized reassignment + predecessor tombstone -> successor may vote once.
12. Tombstoned predecessor key reappears -> reject vote.
13. Circular A->B->A reassignment without independent membership root -> reject.
14. Two witness IDs map to same failure domain -> count once.

### Unlearning proof composition (15-21)
15. Exact + exact with compatible lineage -> exact may survive.
16. Exact + certified bound -> certified bound.
17. Certified + certified incompatible assumptions -> unknown.
18. Empirical + empirical independent suites -> empirical, never exact.
19. Exact source deletion but derived embedding unknown -> unknown overall.
20. Distilled student from affected teacher -> inherits influence lineage.
21. Deleted adapter but cached logits remain -> influence not proven absent.

### Privacy mapping/accounting (22-27)
22. Mapping proof expires -> spend floor unchanged.
23. Namespace rotates -> no budget reset.
24. Identifier tombstoned then probabilistically relinked -> conservative merge.
25. Resolver reports no match -> not proof of disjointness.
26. False merge later split -> historical loss remains accounted.
27. Deleted mapping evidence with unresolved reservations -> reservations remain charged/unknown.

### Provider failover/finality (28-34)
28. Old provider timeout-after-send then failover -> unresolved external effect.
29. Contradictory valid receipts -> provider fork.
30. New provider epoch current -> predecessor fork still unresolved.
31. New signing key receipt conflicts with old epoch receipt -> no timestamp winner.
32. Missing sequence number -> cannot infer no effect.
33. Provider-specific authenticated finality covers fork set -> finalize one history.
34. Compensation receipt -> append new effect, retain original ancestry.

### Authority inventory (35-40)
35. All known KMS replicas ack deletion but backup inventory incomplete -> no GC.
36. Wrapped predecessor key found in DR snapshot after GC attempt -> reopen extinction proof.
37. Two escrow services share one recovery root -> correlated domain.
38. Cross-signed recovery issuers counted as independent -> reject independence claim.
39. Inventory closure omits dormant region replay-state store -> no 0-RTT/resumption release.
40. Complete recursively authenticated authority graph + proven extinction -> epoch GC allowed without lowering monotonic floor.

## Donors / evidence

- SLSA v1.1 Threats & mitigations: trusted control planes can be induced to sign false provenance; cache provenance must bind the transitive closure of relevant inputs. https://slsa.dev/spec/v1.1/threats
- Sigstore/Rekor transparency design is a donor for append-only authenticated evidence and split-view monitoring; cryptographic log evidence does not by itself define application-level canonical recovery policy. https://docs.sigstore.dev/logging/overview/
- NIST SP 800-88 Rev. 2: cryptographic erase requires assurance around all relevant key material and explicitly discusses externally managed keys and elimination of dependent/unwrapped copies. https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf
- NIST differential privacy guidance treats privacy loss as cumulative; namespace or identifier lifecycle must not silently recreate budget. https://www.nist.gov/itl/applied-cybersecurity/privacy-engineering/collaboration-space/focus-areas/de-identification-tools

## Implementation consequence

No production refactor is authorized by this document alone. For LAB-093..100, implement regression tests first against exact executable source, preserve current trusted boundaries until RED is demonstrated, then make the smallest change that establishes the frozen invariants. Do not use these design results as evidence that LAB-086's executable gate passed.
