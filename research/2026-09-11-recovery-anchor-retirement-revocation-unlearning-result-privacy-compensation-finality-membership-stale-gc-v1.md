# Recovery-policy anchor loss, reconstructed-retirement revocation, post-close unlearning revocation, privacy compensation forks, finality membership recovery, and stale-old GC attacks — V1

Status: `RECOVERY_ANCHOR_RETIREMENT_REVOCATION_UNLEARNING_RESULT_PRIVACY_COMPENSATION_FINALITY_MEMBERSHIP_STALE_GC_V1_FROZEN`

Date: 2026-09-11

Context: LAB-086 remains the priority executable task. This run re-probed direct exact source materialization first. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but no supported connector-to-executor byte-exact materialization path is exposed. Therefore this note executes the next distinct evidence task from `state/CURRENT.md`; it does **not** claim RED/GREEN, compile, integration, or security-gate PASS.

## Primary donors

- TUF specification: authenticated, versioned trust-root transition; threshold authorization; rollback/mix-and-match resistance. Source: https://theupdateframework.io/spec/
- RFC 9162: an authenticated later log head is not enough to prove append-only continuity; consistency proofs and cross-view checking matter. Source: https://www.rfc-editor.org/rfc/rfc9162.html
- NIST SP 800-226: privacy budget is an upper bound on cumulative privacy loss across analyses; failover or bookkeeping repair cannot mint fresh budget. Sources: https://csrc.nist.gov/pubs/sp/800/226/final and https://csrc.nist.gov/glossary/term/privacy_budget
- Raft joint consensus: direct old->new membership switching is unsafe because disjoint majorities can exist during transition; joint consensus requires overlapping authorization before new-only authority. Sources: https://raft.github.io/ and https://raft.github.io/raft.pdf

## Frozen contracts

### A. Independent registry recovery-policy anchor partially lost or equivocal

The recovery-policy anchor is itself authority-bearing state and must have an authenticated version/generation, predecessor relation, canonical policy digest, root/failure-domain set, threshold, and compromise-evidence cutoff.

A partially lost anchor has three states:

- `RECOVERY_POLICY_ANCHOR_PROVEN`: predecessor and current policy continuity are authenticated;
- `RECOVERY_POLICY_FLOOR_PROVEN_CONTINUITY_UNKNOWN`: a monotonic minimum policy generation is still authenticated, but canonical successor continuity is not;
- `RECOVERY_POLICY_ANCHOR_UNKNOWN`: neither continuity nor monotonic floor can be proven.

Rules:

- loss of some anchor replicas cannot lower the accepted policy generation;
- a surviving self-signed successor policy does not repair predecessor loss;
- same-generation incompatible policy digests are `RECOVERY_POLICY_ANCHOR_EQUIVOCATION`, even when both satisfy their own threshold;
- correlated keys/failure domains do not count as independent votes;
- when only a floor is proven, old policies remain non-resurrectable but new registry recovery is blocked until a higher independently rooted policy generation commits all surviving conflicting anchor heads and the last undisputed predecessor;
- wall-clock freshness, arrival order, replica count, or locally available branch never chooses the canonical policy.

### B. Retirement recovery-bridge revocation after continuity was reconstructed

A reconstructed retirement bridge is not immortal authority. It binds the lost predecessor range, all surviving heads it reconciled, the retirement floor, the bridge issuer/policy generation, evidence cutoff, and resulting canonical checkpoint.

If bridge authority is later revoked or proven compromised for the issuance interval:

- the already authenticated non-resurrection floor remains monotonic unless independent evidence disproves it;
- the bridge-derived canonical-branch claim becomes `RETIREMENT_BRIDGE_AUTHORITY_UNCERTAIN`;
- evidence compacted solely because of that bridge cannot be treated as safely forgotten;
- successor re-signing of the same bridge is not repair;
- repair requires an independently authorized higher bridge generation that commits the revoked bridge, every surviving conflicting checkpoint/head, the last undisputed predecessor/floor, and any retention/compaction boundary crossed under the revoked bridge;
- if required predecessor material was destroyed after the now-revoked bridge authorized compaction, the system must preserve the retirement floor but classify canonical continuity as unknown rather than fabricate proof.

### C. Unlearning worker-result revocation after proof-epoch close

Closing an unlearning proof epoch freezes the accepted result set, but later evidence can invalidate authority that produced one or more results.

Each accepted worker result binds worker identity/failure domain, credential/policy generation, proof epoch, DAG root, theorem/profile digest, deterministic input/output digest, evaluation interval, and result signature/attestation.

Post-close revocation rules:

- revocation/compromise covering the evaluation interval marks the contribution invalid even after certificate issuance;
- if the remaining independent valid contributions still satisfy the exact original quorum/profile, the certificate may remain valid with a durable revalidation record;
- otherwise the certificate becomes `UNLEARNING_CERTIFICATE_AUTHORITY_UNCERTAIN` and all dependent descendants are blocked from claiming the stronger guarantee until re-proof;
- a newly added worker cannot retroactively vote in the closed epoch; repair occurs in a successor proof epoch referencing the closed epoch and exact DAG/theorem state, or a newer DAG state if dependencies changed;
- deterministic sub-results may be reused only when their own authority is unaffected and their content/profile binding is exact;
- revocation of a shared worker/issuer ancestor invalidates every dependent certificate branch until each is independently re-established.

### D. Privacy compensating-accounting fork and reconciliation after late attestation revocation

A compensating accounting generation is append-only correction, not history rewrite. It binds predecessor accounting head, analysis id, participant-set digest, revoked/uncertain attestation set, conservative delta, cumulative-loss floor, reservations, and coordinator/accounting generation.

If two successors produce incompatible compensation generations from the same predecessor, state is `PRIVACY_COMPENSATION_FORK`.

Rules:

- never choose a compensation branch because it is smaller, newer, or locally committed first;
- cumulative consumed loss floor is the conservative maximum implied by all still-plausible branches until reconciliation;
- unresolved reservations stay reserved unless independently proven unused;
- reconciliation uses a higher accounting generation that commits every fork head and derives one conservative cumulative floor from authenticated evidence;
- coordinator failover does not change `analysis_id`, participant identity lineage, or budget namespace;
- compensation can increase the charged floor or preserve it, but cannot refund already consumed privacy loss merely because an attestation was revoked or a participant disappeared;
- if exact contribution is unknowable, policy-defined upper bound replaces the unknown contribution rather than zero.

### E. Finality-checkpoint replica-set membership transition during recovery

Finality evidence recovery and replica membership change are distinct state transitions. Each checkpoint binds replica-set generation/digest; each membership transition binds predecessor configuration, joint configuration, successor configuration, checkpoint generation/root, and exact catch-up evidence for joining replicas.

Rules:

- a replacement/new replica cannot vote until it has the exact accepted checkpoint plus required consistency/invalidation provenance;
- direct `R_old -> R_new` switch is forbidden during recovery; use joint authority requiring old and new quorums over the same checkpoint transition;
- a failed old replica does not permit lowering old-threshold requirements unless an authenticated membership transition explicitly changes them;
- same checkpoint value copied into new replicas is not equivalent to authenticated catch-up;
- incompatible joint-transition records from the same predecessor are `FINALITY_MEMBERSHIP_FORK`;
- if source-evidence loss leaves only a monotonic quarantine/finality floor, membership can recover storage redundancy but cannot upgrade `UNKNOWN` effects to final/destructive-safe;
- membership finality does not imply effect finality, and effect finality does not imply membership-transition finality.

### F. Stale-old-configuration attacks and audit-evidence retention after `GC_NEW_CONFIG_COMMITTED`

After a valid joint-consensus transition commits `C_new`, `C_old` loses voting authority for future GC epochs. It does **not** become irrelevant evidence.

Rules:

- any post-transition message/vote from `C_old` must bind the committed configuration generation; stale old-generation votes cannot open, advance, close, or roll back a future GC epoch;
- a stale `C_old` quorum cannot resurrect a pre-transition snapshot, even if every old member agrees;
- old nodes returning after partition/restart must catch up through the committed membership transition before participating;
- replayed `GC_PREPARE`, `GC_PROOF_COMMITTED`, or destructive receipts from an older membership generation are evidence-only and cannot authorize a new side effect;
- audit/reconciliation evidence from retired members must be retained according to explicit evidence-retention floor because it may be needed to prove destructive-effect history, compromise intervals, or configuration continuity;
- deleting old-member evidence immediately after `GC_NEW_CONFIG_COMMITTED` is unsafe when any unresolved destructive-effect reconciliation or audit dependency still references it;
- evidence retention does not restore voting authority: retained old signatures prove history only under their original configuration generation;
- a stale-old attack that conflicts with the committed new-config chain is recorded as `GC_STALE_CONFIGURATION_REPLAY` and must not mutate current epoch state.

## RED-first matrix (42 cases)

### Recovery-policy anchor loss/equivocation (1-7)
1. One anchor replica lost; predecessor+current continuity still proven by independent retained evidence -> remain `ANCHOR_PROVEN`.
2. Current policy survives self-signed but predecessor continuity is lost -> reject as proof of canonical succession.
3. Monotonic policy floor survives while successor branch continuity is unknown -> forbid rollback, block new recovery.
4. Same-generation two valid policy digests -> `RECOVERY_POLICY_ANCHOR_EQUIVOCATION`.
5. Threshold met only by keys in one canonical failure domain -> reject independence.
6. Operator chooses newest-timestamp anchor branch -> reject branch selection.
7. Higher independently rooted generation commits all fork heads + last undisputed predecessor and meets post-compromise threshold -> accept repair.

### Retirement bridge revocation (8-14)
8. Reconstructed bridge later revoked for issuance interval -> canonical branch becomes authority-uncertain.
9. Retirement floor independently authenticated below revoked bridge -> keep non-resurrection floor.
10. Successor authority merely re-signs revoked bridge -> still uncertain.
11. Higher bridge omits one surviving conflicting checkpoint -> reject.
12. Evidence compacted under revoked bridge and predecessor proof no longer exists -> keep floor, classify continuity unknown.
13. Revoked bridge had authorized deletion but deletion not yet executed -> block deletion.
14. Independent higher bridge commits revoked bridge + all surviving heads + compaction boundary -> accept repaired continuity.

### Post-close unlearning result revocation (15-21)
15. Worker credential revoked for interval after epoch close -> invalidate contribution.
16. Remaining original-membership independent results still satisfy exact quorum/profile -> allow durable revalidation.
17. Remaining results fall below quorum -> certificate becomes authority-uncertain.
18. Newly added worker signs old closed epoch to restore quorum -> reject retroactive vote.
19. Successor proof epoch reuses unaffected deterministic content-addressed sub-result -> allowed.
20. Shared issuer ancestor revoked -> invalidate every dependent worker result/certificate branch.
21. Descendant certificate attempts to remain strong while ancestor certificate is uncertain -> reject inherited guarantee.

### Privacy compensation fork/reconciliation (22-28)
22. Late revocation creates compensation generation increasing cumulative floor -> accept append-only correction.
23. Two coordinators produce different compensation heads from same predecessor -> `PRIVACY_COMPENSATION_FORK`.
24. System chooses smaller compensation branch -> reject.
25. Reconciliation omits one fork head -> reject.
26. Higher reconciliation commits all heads and takes conservative cumulative bound -> accept.
27. Revoked participant had unresolved reservation -> reservation remains held absent independent unused proof.
28. Compensation tries to refund consumed loss because participant attestation disappeared -> reject.

### Finality replica membership during recovery (29-35)
29. New replica votes before exact checkpoint/evidence catch-up -> reject.
30. Direct old->new replica-set switch during recovery -> reject.
31. Joint transition requires both old and new quorum over same checkpoint -> accept when both satisfied.
32. Missing old replica is silently removed to make quorum -> reject absent authenticated transition.
33. Same-generation incompatible joint membership records -> `FINALITY_MEMBERSHIP_FORK`.
34. New replicas copy resolved value but lack invalidation/source provenance -> cannot authorize destructive/retry effect.
35. Membership transition commits while effect remains `UNKNOWN` -> membership may complete; effect stays `UNKNOWN`.

### Stale-old configuration after GC new-config commit (36-42)
36. `C_old` quorum attempts to open next GC epoch after committed `C_new` -> reject stale authority.
37. Replayed old `GC_PREPARE` targets current resources -> evidence-only, no mutation.
38. Old node rejoins and votes before catch-up to committed membership chain -> reject.
39. Old destructive receipt is needed for unresolved audit -> retain as historical evidence, not authority.
40. Retention job deletes old-member evidence while unresolved effect reconciliation references it -> block deletion.
41. Old signatures are replayed under new configuration generation -> reject generation mismatch and record stale replay.
42. `C_new` chain remains canonical while stale-old replay is durably recorded for audit -> no state rollback or side effect.

## Audit

- No contract promotes availability evidence into authority.
- Monotonic safety floors survive loss/revocation where independently authenticated, but uncertain continuity blocks destructive progress.
- Revocation is interval-scoped and never repaired by mere successor re-signing.
- Closed epochs/configurations are immutable historical authority domains; later members cannot retroactively vote.
- Privacy corrections are append-only and conservatively cumulative.
- Membership recovery is separate from effect finality.
- Retained historical evidence never regains mutation/voting capability.
- This is architecture/evidence only; exact executable RED/GREEN remains pending behind the current materialization blocker.
