# Recovery-authority compromise, witness resurrection, correlated unlearning, privacy convergence, provider finality revocation, recursive authority discovery — v1

Date: 2026-09-11
Status: FROZEN DESIGN / RED-FIRST CONTRACT; no executable PASS claimed
Contract ID: `RECOVERY_AUTHORITY_COMPROMISE_WITNESS_RESURRECTION_UNLEARNING_CORRELATION_PRIVACY_CONVERGENCE_PROVIDER_REVOCATION_AUTHORITY_RECURSION_V1_FROZEN`

## Why this slice exists

The previous freeze established canonical recovery after provenance-root equivocation, stable witness identity across membership epochs, conservative unlearning-proof composition, monotonic privacy accounting, provider-fork finality boundaries, and recursive authority inventory before epoch GC.

This slice handles the next failure layer: what happens when the evidence that *resolved* an earlier dispute is itself later compromised, when compacted membership history can be replayed to resurrect tombstoned witnesses, when certified-unlearning bounds share correlated residual influence, when privacy resolvers disagree through graph split/merge cycles, when provider finality evidence is later revoked after failover, and when the issuer attesting authority-inventory completeness can itself be reconstructed from predecessor authority.

No production implementation is authorized by this note. Exact RED/GREEN remains required.

## Primary donors / facts

### TUF root continuity and rollback resistance

The Update Framework requires root metadata version N+1 to be signed by a threshold from both trusted root N and new root N+1, and requires sequential version progression. Clients must retrieve intermediate roots rather than jumping directly to an arbitrary latest root. This is an explicit continuity mechanism for changing trust roots and detecting rollback/freeze behavior.

Source: https://theupdateframework.github.io/specification/v1.0.17/ — sections 5.3 and 6.1.

### SLSA provenance trust boundary

SLSA verification authenticates provenance against configured roots of trust, but explicitly does not claim protection against compromise of the trusted build platform itself. A valid signature therefore proves who attested, not that a compromised trusted authority told the truth.

Sources:
- https://slsa.dev/spec/v1.0/verifying-artifacts
- https://slsa.dev/spec/draft/dependency-provenance

### Privacy accounting is cumulative

NIST defines a privacy budget / privacy-loss budget as an upper bound on cumulative privacy loss. Identity-graph disagreement or resolver churn therefore cannot safely create a fresh accounting namespace without a continuity proof.

Sources:
- https://csrc.nist.gov/glossary/term/privacy_budget
- https://csrc.nist.gov/glossary/term/privacy_loss_budget

### Sanitization / authority extinction needs assurance over key reachability

NIST SP 800-88 Rev. 2 emphasizes sanitization assurance/validation and explicitly discusses cryptographic erase and externally managed keys. A local deletion assertion is therefore insufficient when recovery authority can still be reconstructed through external, wrapped, backup, escrow, or predecessor-controlled key material.

Source: https://csrc.nist.gov/pubs/sp/800/88/r2/final

### Certified unlearning is guarantee-specific, not a magic global deletion bit

Recent certified-removal work derives guarantees under explicit model/algorithm assumptions; high-dimensional settings make those guarantees materially non-trivial. A certificate for one component cannot be promoted to an exact global deletion claim when downstream components share correlated state or residual influence unless the composition theorem actually covers that dependency graph.

Source: https://arxiv.org/abs/2505.07640

## Frozen invariants

### 1. Recovery-authority compromise after equivocation resolution

`RECOVERY_PROOF_PREVIOUSLY_ACCEPTED != RECOVERY_AUTHORITY_FOREVER_TRUSTED`.

A recovery resolution R_k is valid only relative to the authority state and evidence cutoff under which it was accepted. If the recovery authority for R_k is later proven compromised over an interval that intersects the issuance interval of R_k, the system MUST NOT silently rewrite history to the old disputed branch and MUST NOT keep treating R_k as unconditionally canonical.

Instead:
- preserve the monotonic rollback/equivocation floor already learned;
- enter `RECOVERY_AUTHORITY_DISPUTED` for affected descendants;
- require a strictly higher recovery generation R_{k+1};
- bind R_{k+1} to the last undisputed predecessor, all known conflicting roots, R_k, compromise evidence/cutoff, and a successor authority that is independently authorized through a continuity chain;
- do not allow the compromised R_k authority alone to nominate its successor;
- never lower the highest known generation/rollback floor merely because compromise evidence is later overturned.

TUF donor mechanism: trust-root transition should be sequential and dual-authorized by predecessor+successor threshold where predecessor remains trustworthy. If predecessor authority itself is disputed, a separate emergency/recovery root with independently established authority is required; no self-healing circular signature chain is accepted.

### 2. Witness tombstone resurrection through compacted membership history

`COMPACT_HISTORY_ACCEPTS_WITNESS_ID != WITNESS_AUTHORIZED_AT_EVENT_EPOCH`.

Membership compaction MUST retain enough authenticated evidence to answer, for every authority-relevant event:
- canonical witness identity;
- failure-domain identity;
- membership epoch interval;
- tombstone/revocation effective cutoff;
- successor mapping, if any;
- threshold policy effective at that event;
- proof that compacted representation has not omitted an intervening tombstone or reassignment.

Rules:
- a tombstoned witness ID cannot be resurrected by replaying an older compact root;
- a successor key that reuses predecessor identity does not restore predecessor authority before/after its authorized interval;
- overlapping old/new keys for the same canonical witness count once;
- if compaction cannot prove interval continuity, quorum status is `UNKNOWN`, not valid;
- GC of detailed membership events is forbidden until the compact representation can reproduce all authority decisions needed by retained checkpoints/recovery roots.

### 3. Certified-unlearning composition under correlated components

`CERTIFIED(A) + CERTIFIED(B) != CERTIFIED(A∪B)` when A and B share correlated residual influence unless the certificate explicitly composes under that dependency model.

Required proof metadata per component:
- deletion subject/version;
- training/state lineage input set;
- certificate theorem/profile identifier;
- assumptions and bound parameters;
- residual influence bound;
- dependency/correlation set;
- downstream artifacts derived after certification;
- expiry or invalidation conditions.

Composition rules:
- exact proof may remain exact only if all relevant descendants are exact and no untracked derived state exists;
- certified numeric/statistical bounds compose using the theorem's valid composition rule, otherwise conservative union/worst-case bound;
- correlated components MUST NOT be multiplied/added as though independent unless independence is itself proven;
- empirical approximation never upgrades to certified or exact by repetition;
- ensemble, distillation, cache, embedding, ANN index, adapter, optimizer state, checkpoint and merged model inherit the union of unresolved influence lineage;
- if dependency provenance is incomplete, result is `UNLEARNING_UNKNOWN`.

### 4. Privacy accounting convergence under resolver disagreement

`RESOLVER_A_SPLIT + RESOLVER_B_MERGE != NEW_BUDGET`.

Maintain a monotonic privacy-accounting floor independent of any one mutable resolver graph.

For each subject/accounting equivalence proof retain:
- resolver identity/model/version;
- input evidence cutoff;
- graph epoch;
- claimed equivalence/disjointness relation;
- confidence/proof class;
- expiry/revocation state;
- cumulative spend/reservation/unknown-loss contributed by every linked namespace.

Convergence rule under disagreement:
- merge candidate sets conservatively for budget accounting;
- do not reveal full identity linkage merely to reconcile accounting;
- false merge may over-constrain budget but MUST NOT disclose unrelated identity histories;
- false split MUST NOT mint fresh budget;
- after later convergence, cumulative accounting floor is max/conservative composition of all histories that may refer to the same subject;
- deletion/tombstone of mapping evidence does not erase already accrued privacy loss.

### 5. Provider finality evidence revocation after failover

`FINALITY_RECEIPT_ACCEPTED_AT_T != FINALITY_IRREVOCABLE_IF_ISSUER_LATER_COMPROMISED`.

Provider effect history needs two separate notions:
- effect-state finality;
- evidence-authority validity.

If a receipt/finality issuer key is later revoked or proven compromised for an interval covering issuance:
- preserve the receipt as historical evidence;
- mark authority status `REVOKED_OR_DISPUTED`;
- do not infer that the effect did or did not happen solely from that receipt;
- if external effect may already have occurred, state becomes `EFFECT_UNKNOWN` until independent reconciliation/finality evidence resolves it;
- do not blind-retry destructive effects;
- failover provider cannot finalize predecessor history merely by issuing a new receipt;
- compensation is a new sequenced effect and cannot erase the original effect/evidence fork;
- sequence gaps/forks remain explicit through compaction.

A replacement finality proof must bind provider identity, operation semantic id, payload digest, predecessor receipts/forks, effect sequence/cutoff, revocation evidence, and independent provider-side state or a higher-trust reconciliation source.

### 6. Recursive authority-inventory discovery when inventory issuers are recoverable from predecessor authority

`INVENTORY_SIGNED_COMPLETE != AUTHORITY_UNIVERSE_COMPLETE`.

The inventory issuer is itself part of the authority graph. Therefore an epoch-GC/extinction proof must recursively close over:
- the issuer's signing/recovery keys;
- predecessor/successor issuer authorities;
- KMS/HSM keys able to restore issuer credentials;
- backup/DR/wrapped/escrow/offline copies;
- cross-signing roots and shared recovery roots;
- dormant regions/tenants;
- replay-state or credentials able to reactivate predecessor authority;
- discovery services whose compromise could omit authority domains.

If an inventory issuer can be reconstructed from an older authority that the inventory claims extinct, the proof is circular and invalid unless the older authority's extinction is independently established.

Required closure algorithm conceptually computes a fixed point over `CAN_RESTORE(authority_x, authority_y)` edges. GC is permitted only if every predecessor authority reachable from retained current authority has one of:
- independently verified destroyed/sanitized evidence;
- expiry that is cryptographically enforced and non-restorable;
- explicitly quarantined state preventing resumption/authorization;
- or a higher-order recovery policy that cannot itself recreate the old authority.

Unknown/unreachable inventory domains keep the epoch quarantined; they do not count as absent.

## RED-first matrix (40 cases)

### Recovery authority (1-7)
1. Recovery R2 resolves roots A/B; later R2 signing authority compromised before issuance -> affected state disputed.
2. Compromise begins after R2 issuance with trusted timestamp -> R2 retained if timestamp/authority interval proof is sound.
3. Compromised R2 authority self-signs R3 successor -> reject circular recovery.
4. Independent emergency authority binds A/B/R2/compromise cutoff into R3 -> eligible.
5. Later evidence overturns compromise allegation -> do not lower rollback/generation floor.
6. R3 omits one previously known conflicting root -> reject incomplete recovery.
7. Recovery chain skips R2 without proving continuity from last undisputed predecessor -> reject.

### Witness resurrection / compaction (8-14)
8. Tombstoned witness appears in replayed old compact root -> reject.
9. New key reuses tombstoned canonical witness ID -> no authority until explicit successor epoch.
10. Old/new overlapping keys of same canonical witness -> count once.
11. Compacted membership omits an intervening tombstone -> quorum UNKNOWN/fail closed.
12. Threshold policy changes across compacted epochs -> evaluate event against event-time policy.
13. GC detailed events but compact proof reconstructs identity/tombstone/threshold history -> accept.
14. Reassignment to a genuinely independent witness with authenticated predecessor transition -> count according to new epoch only.

### Correlated unlearning (15-21)
15. Two independently certified shards with no shared descendants and theorem permits composition -> compose per theorem.
16. Certified shards share optimizer state -> no independence assumption; conservative/unknown.
17. Adapter deleted but distilled model remains -> influence lineage remains.
18. Exact retrain of one component while shared embedding cache survives -> global result not exact.
19. Repeated empirical membership tests all pass -> still empirical, not certified.
20. Certificate missing theorem/profile version -> UNKNOWN.
21. Component certificate invalidated by later model merge -> downstream proof re-evaluation required.

### Privacy resolver convergence (22-28)
22. Resolver A says subject X/Y same; B says disjoint -> budget uses conservative merged accounting without exposing identity details.
23. Later B converges to merge -> no budget reset.
24. Graph split after earlier merge -> no fresh budget.
25. False merge discovered -> future mapping may split, historical spend floor retained.
26. Mapping proof expires -> spend floor retained.
27. Resolver model rollback to older graph version -> reject lowering accounting state.
28. Tombstone collision between unrelated namespaces -> isolate identity disclosure while conservatively protecting budget.

### Provider finality revocation (29-34)
29. Accepted receipt issuer compromised over issuance interval -> receipt authority disputed.
30. Effect is known independently from provider state -> retain effect finality despite revoked receipt authority.
31. Effect known only from revoked receipt -> EFFECT_UNKNOWN, no blind retry.
32. Failover provider issues contradictory predecessor-finality claim -> fork, not automatic replacement.
33. Compensation after disputed effect -> new sequenced effect, original remains in history.
34. Receipt compaction drops revoked fork/gap -> reject compact proof.

### Recursive authority inventory (35-40)
35. All enumerated KMS domains ack deletion but issuer can be restored from escrow -> no GC.
36. Inventory issuer recovery key lives under predecessor KMS key claimed extinct -> circular proof, reject.
37. External KMS domain discovered after earlier GC candidate -> reopen extinction proof, keep monotonic epoch floor.
38. Cross-signed inventory issuers share same recovery root -> one failure domain, not independent quorum.
39. Fixed-point closure finds no restorable predecessor authority and sanitization evidence validates -> GC eligible.
40. One dormant region cannot be enumerated/queried -> authority universe incomplete; quarantine, no GC.

## Implementation implications for future executable work

When exact source is available, prefer explicit typed states over booleans:
- `TRUSTED / DISPUTED / REVOKED / UNKNOWN` authority states;
- stable IDs plus epoch intervals instead of current-key identity;
- proof objects that include theorem/profile/dependency lineage;
- privacy accounting records separate from mutable identity graph storage;
- provider effect state separate from receipt-authority state;
- recursive authority inventory represented as an authenticated graph with monotonic generation/cutoff.

Do not implement automatic repair that destroys disputed evidence. Preserve forks/tombstones/revocations until a higher-authority proof resolves them.

## Audit conclusion

The common pattern is that **evidence authority is itself mutable, recoverable, and compromisable**. Therefore every retained security decision needs both content lineage and authority lineage. Compaction, deletion, failover, unlearning, namespace rotation, and key recovery are safe only when they preserve a monotonic uncertainty/rollback/accounting floor and cannot manufacture fresh independence or erase an unresolved predecessor.

Frozen verdict: `RECOVERY_AUTHORITY_COMPROMISE_WITNESS_RESURRECTION_UNLEARNING_CORRELATION_PRIVACY_CONVERGENCE_PROVIDER_REVOCATION_AUTHORITY_RECURSION_V1_FROZEN`.
