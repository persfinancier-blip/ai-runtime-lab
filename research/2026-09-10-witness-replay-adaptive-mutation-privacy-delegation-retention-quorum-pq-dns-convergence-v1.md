# Witness replay, adaptive mutation, privacy delegation, retention quorum, and PQ/DNS convergence — v1

Date: 2026-09-10
Status: `WITNESS_REPLAY_ADAPTIVE_MUTATION_PRIVACY_DELEGATION_RETENTION_QUORUM_PQ_DNS_CONVERGENCE_V1_FROZEN`
Scope: distinct design/evidence fallback while LAB-086 exact local executable gate remains blocked by per-run transport/materialization capability.

## Executive contract

This slice freezes five additional authority boundaries:

1. `VALID_OLD_ACKNOWLEDGEMENT != CURRENT_REOPEN_AUTHORITY`
2. `ADAPTIVE_MUTATION_FINDS_NO_BUG != COVERAGE_COMPLETE`
3. `PRIVACY_BUDGET_DELEGATED != PRIVACY_BUDGET_MULTIPLIED`
4. `N_TIME_SOURCES_AGREE != N_INDEPENDENT_TIME_AUTHORITIES`
5. `DNSSEC_VALID_ROUTE != CURRENT_RESUMPTION_ROUTE_AUTHORITY`

The common rule is conservation of authority across replay, adaptation, delegation, correlated inputs, and eventually-consistent routing state. A credential, proof, clock sample, privacy allowance, or DNS answer that remains syntactically/cryptographically valid is not automatically fresh authority for a new consequential action.

## Primary donors and what is reused

### RFC 9162 — Certificate Transparency v2
Reuse: signed historical tree heads plus consistency proofs as a donor model for append-only lineage and detection of incompatible views. A successor/reopen protocol must authenticate ancestry; a replayed acknowledgement of an older head cannot authorize a different successor head merely because the signature is still valid.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### SLSA reproducibility guidance
Reuse: independence is a security property, not a count. SLSA notes that multiple rebuilders that share vulnerable pipeline software are not truly independent. Apply the same rule to adaptive mutation generators, oracles, corpus builders, and verifier pipelines.

Source: https://slsa.dev/spec/draft/faq

### NIST SP 800-226 — differential privacy evaluation
Reuse: privacy loss composes across repeated releases. Therefore delegation, verifier rotation, subject aliasing, split/merge operations, restore, or retry must not mint new disclosure budget for the same protected subject/purpose/window.

Source: https://csrc.nist.gov/pubs/sp/800/226/final

### NIST Internet Time / authenticated NTP guidance
Reuse: authenticated source identity/health and explicit leap handling. NIST documents that leap-second realization can make civil timestamps locally ambiguous and that implementations may realize the event differently. Consequential expiry/deletion decisions therefore need monotonic epoch/freshness evidence rather than naive wall-clock comparison alone.

Sources:
- https://www.nist.gov/pml/time-and-frequency-division/time-services/nist-authenticated-ntp-service
- https://www.nist.gov/pml/time-and-frequency-division/time-distribution/internet-time-service-its

### RFC 9460, RFC 6781, RFC 9849
Reuse: DNS SVCB/HTTPS downgrade protections, DNSSEC rollover/cache overlap, and ECH retry/config-source scoping. RFC 6781 explicitly requires rollover design to account for old data still living in caches. RFC 9849 requires persisted ECH-related state to remain associated with its ECHConfig source and warns about inconsistent retry configurations. Route convergence therefore cannot be inferred from one valid answer or one successful TLS retry.

Sources:
- https://www.rfc-editor.org/rfc/rfc9460.html
- https://www.rfc-editor.org/rfc/rfc6781.html
- https://www.rfc-editor.org/rfc/rfc9849.html

## 1. Witness reopen quorum: key compromise and acknowledgement replay

### Threat
A predecessor generation G0 is finalized. A legitimate reopen proposal P1 is acknowledged by quorum Q under key generation K1. Before P1 is durably finalized, one or more acknowledgement keys are compromised, rotated, or retired. An attacker replays old acknowledgements against a distinct P2, or reuses a previously valid acknowledgement after the admissible replay window, membership epoch, or predecessor head changed.

### Frozen boundary
`SIGNATURE_VALID != ACKNOWLEDGEMENT_FRESH_FOR_THIS_TRANSITION`.

Every acknowledgement MUST bind at least:
- predecessor finalized head/digest;
- successor proposal digest;
- witness membership/quorum epoch;
- acknowledgement key generation;
- monotonic reopen nonce or transition id;
- not-before / expiry or equivalent freshness generation;
- policy generation;
- role (`ack`, `finalize`, `revoke`, `recover`) so signatures are non-interchangeable.

A replay cache MAY optimize detection but MUST NOT be the sole authority. Durable transition identity and predecessor/successor binding are authoritative.

Compromise handling is asymmetric:
- compromise discovered before successor finalization: affected acknowledgements are degraded/rejected according to authenticated compromise time and policy;
- compromise discovered after finalization: historical evidence remains, but assurance for the affected interval is marked degraded; successor keys do not retroactively repair predecessor assurance;
- a newly assembled quorum cannot reuse acknowledgements from a prior membership/policy epoch unless an explicit bridge authorizes that exact reuse.

`QUORUM_COUNT_MET != QUORUM_INDEPENDENCE_MET`: multiple witness keys under one operator/KMS/admin recovery path are one correlated failure domain for security-threshold purposes unless policy explicitly models otherwise.

## 2. Adaptive mutation search and semantic coverage

### Threat
A mutation system dynamically learns which transformations evade current tests. A clean adaptive run may still miss semantic classes because generator/oracle bias, shared implementation defects, search-budget exhaustion, seed censorship, or reward shaping systematically excludes them.

### Frozen boundary
`NO_COUNTEREXAMPLE_FOUND != SEMANTIC_COVERAGE_PROVEN`.

The authenticated test claim MUST separate:
- deterministic corpus root;
- mutation operator set + versions;
- adaptive search algorithm/version;
- seed/root RNG commitments when randomness matters;
- search budget and stopping rule;
- oracle implementation/provenance;
- semantic coverage floor required by policy;
- excluded/unsupported mutation families;
- independently reproduced counterexample/minimization artifacts.

Adaptive discovery can raise coverage but cannot silently lower the frozen coverage floor. Retirement of an operator or semantic class requires an authenticated policy transition with evidence explaining why the class is obsolete or subsumed.

A verifier build and its mutation generator/oracle do not count as independent if they share a compromise-capable builder/pipeline/control plane. Reproducibility is evidence of consistency, not proof that the shared semantics are correct.

## 3. Privacy budget delegation, transfer, and subject split/merge

### Threat
A privacy authority delegates budget to multiple verifier domains; identities rotate; one subject is split into several pseudonyms; several subjects are merged; or budget state is restored from backup. Naive per-credential accounting can multiply the effective privacy loss allowance.

### Frozen boundary
`DELEGATION != MINT`.

Budget is a conserved quantity across parent/child grants. A child allocation reduces available parent authority; transfer moves remaining authority but does not duplicate it. Every grant/transfer/revoke/spend event binds:
- canonical protected-subject set or authenticated equivalence class;
- purpose/policy generation;
- accounting window/epoch;
- parent budget lineage;
- allocated epsilon/delta or scheme-specific privacy-loss units;
- already-spent amount/commitment;
- delegation id and anti-replay generation.

`SUBJECT_SPLIT != FRESH_BUDGET`: splitting aliases/pseudonyms inherits the parent subject's composed spend unless policy proves disjoint protected populations.

`SUBJECT_MERGE != FORGET_PRIOR_SPEND`: merging identities conservatively composes prior relevant spend until a sound accounting rule proves otherwise.

Unknown lineage, ambiguous subject equivalence, conflicting restored ledgers, or partitioned global spend state MUST fail closed for consequential disclosure as `PRIVACY_BUDGET_STATE_UNKNOWN`; they must not reset to zero.

## 4. Retention time-source quorum, common-mode failure, leap/epoch handling

### Threat
Three nominal time sources agree because all depend on one upstream GNSS/NTP/cloud time authority; an attacker or fault shifts the common source. Separately, leap-second realization or clock rollback creates ambiguous/duplicate wall-clock labels around a destructive retention boundary.

### Frozen boundary
`N_MATCHING_CLOCKS != N_INDEPENDENT_TIME_AUTHORITIES`.

Time quorum policy MUST model transitive dependencies: upstream reference, network path, operator/admin domain, signing/KMS, host clock discipline, and recovery authority. Sources sharing a critical dependency count as one failure domain where that dependency can produce correlated false time.

Destructive retention authorization MUST bind:
- monotonic policy epoch/generation;
- trusted time-source set and dependency-class generation;
- source health/authentication evidence;
- uncertainty interval;
- leap-second/epoch realization policy;
- last accepted monotonic expiry/freshness floor.

Civil timestamp equality/ordering around a leap event is not sufficient. Where time cannot be ordered unambiguously inside the required safety margin, deletion/expiry remains pending rather than guessing.

A rollback in local clock, VM snapshot, database snapshot, or time configuration MUST NOT roll back an already observed monotonic authorization floor.

## 5. PQ/ECH/SVCB: multi-resolver disagreement, DNSSEC rollover, route-policy convergence

### Threat
Resolver A returns current DNSSEC-valid SVCB/ECH policy; resolver B serves an older still-valid cached RRset during DNSSEC/ECH rollover. A client possesses a resumable TLS ticket from the old route/service generation. A failover or retry reaches an endpoint that can decrypt the ticket but is not yet converged on the new PQ/ECH/service policy.

### Frozen boundary
`DNSSEC_VALID != ROUTE_POLICY_CURRENT`.

A valid old RRset is authenticated historical routing information, not automatic current resumption authority. The runtime must bind resumption authorization to a route-policy generation that includes, as applicable:
- origin/inner service identity;
- ECHConfig source and config generation;
- SVCB/HTTPS policy digest/generation;
- ALPN;
- server/backend identity generation;
- current PQ/hybrid minimum;
- ticket-key generation;
- replay/spend authority generation.

Resolver disagreement is explicit state. Security-critical capability stripping cannot be resolved by choosing the weakest answer, first response, or reachable endpoint. If the current policy generation cannot be established within configured freshness/rollover rules, consequential 0-RTT/resumption fails closed and a fresh compliant handshake is required or the connection fails.

DNSSEC rollover must respect cache overlap: old and new validation material can coexist. A route-policy epoch therefore cannot advance merely because one resolver sees the new key/RRset. Conversely, an old cached answer cannot indefinitely pin the client to a weaker crypto floor after authenticated policy advancement.

ECH retry does not bridge unrelated DNS discoveries. Persisted ECH state remains scoped to its authenticated ECHConfig source; retry configuration cannot be used as generic authority for a newly discovered route with a different source/public-name/service context.

`ROUTE_CONVERGED != OLD_TICKET_REAUTHORIZED`: once convergence is established, old tickets still require explicit compatibility with the new service/PQ/replay policy. Decryptability alone is insufficient.

## RED-first regression matrix (40 cases)

### Witness replay / compromise
1. Replay valid G0→P1 acknowledgement against P2 => reject.
2. Replay P1 acknowledgement after membership epoch change => reject absent exact bridge.
3. Replay acknowledgement after policy generation change => reject.
4. Reuse `ack` signature as `finalize` => reject by domain separation.
5. Compromise discovered before finalization and acknowledgement lies in compromised interval => fail/degrade per policy; never silently accept.
6. Compromise discovered after finalization => preserve history, mark affected assurance degraded; do not rewrite finalization.
7. Two keys in same KMS/admin domain satisfy numeric threshold but not independence threshold => reject.
8. Competing successor proposals each gather replayed subsets of one old quorum => split-view evidence retained; neither auto-wins.

### Adaptive mutation / coverage
9. Adaptive search finds zero bugs but omits frozen mutation family => coverage FAIL.
10. Search budget exhausted before required family reached => incomplete, not PASS.
11. Generator and oracle share compromised dependency => independence claim FAIL.
12. Reproducible poisoned generator on two identical pipelines => reproducibility PASS, independence/security FAIL.
13. Operator silently removed between corpus versions => reject policy transition.
14. New operator subsumes old class with authenticated equivalence evidence => allow retirement only after explicit transition.
15. Adaptive seed/result censorship removes known counterexample => corpus/provenance mismatch FAIL.
16. Minimized counterexample cannot be reproduced by independent verifier => retain as unresolved failure, not discard.

### Privacy delegation / split-merge
17. Parent delegates 60% to A and 60% to B => conservation rejects over-allocation.
18. Parent delegates to A, then rotates credential and delegates same remainder again => replay/lineage rejects duplication.
19. Budget transfer A→B leaves spendable authority at A => reject inconsistent lineage.
20. Subject X split into X1/X2 to obtain two budgets => compose inherited spend; no reset.
21. X1/X2 merge after separate spends => conservative composition retained.
22. Backup restores pre-spend ledger while durable spend witness is newer => fail closed, no budget rollback.
23. Two partitions accept spends beyond global budget => reconciliation marks violation; no further consequential disclosure.
24. Subject equivalence unknown after identity migration => `PRIVACY_BUDGET_STATE_UNKNOWN`, no fresh allowance.

### Retention time quorum
25. Three clocks share one compromised upstream => independence threshold FAIL.
26. Two independent authenticated sources disagree outside uncertainty margin => deletion pending.
27. Local wall clock rolls back after expiry previously established => monotonic expiry floor remains.
28. VM snapshot restores pre-expiry local state => cannot resurrect retention authority.
29. Positive leap second produces duplicate civil labels at boundary => use monotonic/epoch evidence; ambiguous deletion blocked.
30. Sources realize leap differently but remain within declared uncertainty => deterministic policy handles without double expiry.
31. Time signing/KMS shared across nominal sources is compromised => correlated domain degradation applied.
32. Time-source dependency graph unavailable => destructive retention fails closed rather than assuming independence.

### PQ/ECH/SVCB/DNS convergence
33. Resolver A new PQ-required RRset, resolver B old weaker cached RRset => do not choose weaker for compatibility.
34. Old RRset DNSSEC-valid during rollover but policy epoch already advanced => old ticket cannot bypass new floor.
35. New DNSKEY visible but old cached DS/RRset causes validation mismatch => treat as rollover/transient failure, not downgrade.
36. ECH retry config is valid but DNS requery discovers different ECHConfig source/public_name => retry authority not transferable.
37. Old route endpoint decrypts ticket after backend migration => require current service/route authorization, else fresh handshake/fail.
38. Two resolvers disagree on SVCB capability; attacker selectively strips SVCB on one path => no weakest-answer fallback for required capability.
39. Route convergence proven, but ticket ALPN/backend/PQ generation incompatible => reject resumption despite convergence.
40. Ticket decrypts and certificate is valid, but replay/spend authority generation is partitioned/unknown => consequential 0-RTT disabled.

## Implementation implications for later RED/GREEN work

No production code is authorized by this design freeze alone. When exact source execution is available, tests should introduce explicit types/fields for transition generation, freshness, dependency-domain identity, budget lineage, monotonic time floor, and route-policy generation only where the existing architecture lacks an equivalent owner. Avoid parallel subsystems.

Security state must distinguish at least `VALID`, `DEGRADED_HISTORY`, `SPLIT_VIEW`, `FRESHNESS_UNKNOWN`, `PRIVACY_BUDGET_STATE_UNKNOWN`, `TIME_AUTHORITY_UNKNOWN`, and `ROUTE_POLICY_UNCONVERGED` where those states are consequential. Do not collapse them into generic retryable errors that downstream code can accidentally treat as authorization.

## Decision

Freeze `WITNESS_REPLAY_ADAPTIVE_MUTATION_PRIVACY_DELEGATION_RETENTION_QUORUM_PQ_DNS_CONVERGENCE_V1_FROZEN` as an extension of LAB-093/#178 architecture evidence. This does not substitute for LAB-086 exact executable proof and does not change any draft/merge status.
