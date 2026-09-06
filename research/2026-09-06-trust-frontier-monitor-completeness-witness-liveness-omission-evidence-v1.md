# Trust-frontier monitor completeness / witness liveness / omission evidence — v1 frozen

Status: `TRUST_FRONTIER_MONITOR_COMPLETENESS_WITNESS_LIVENESS_OMISSION_EVIDENCE_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 evidence/trust-frontier follow-up. This is a design/RED contract, not a production implementation or behavioral PASS.

## Problem

The prior trust-frontier witness/gossip contract prevents accepting an authenticated split view when conflicting checkpoints are actually observed. It does not by itself prove that the system is *observing enough of the frontier* to detect selective withholding, silent monitor failure, or a witness that remains internally non-equivocating while serving a stale view to all reachable monitors.

A transparency system can therefore be locally consistent and still unsafe if required monitors silently stop observing, all monitor channels share one common outage/control plane, liveness telemetry is forged by the same component being monitored, or a newer checkpoint is visible only through an archival/mirror channel that the admission path never consults.

This contract freezes the non-vacuous monitoring boundary.

## Primary donor mechanisms

### RFC 9162 — Certificate Transparency v2

RFC 9162 requires a monitor to inspect every new entry in every log it watches and describes repeated polling for new signed tree heads. It identifies MMD, STH frequency, append-only behavior, and consistency of the view presented to all query sources as properties that auditing should check. It also treats failure to incorporate promised entries and conflicting views as log misbehavior.

Donor mechanism: monitoring is an active completeness obligation over advances, not merely signature verification of whatever state happens to be returned.

Reference: https://www.rfc-editor.org/rfc/rfc9162.html

### C2SP tlog-witness

The C2SP witness monitor-retrieval mechanism explicitly states that effective transparency must prevent partitioning clients from monitors, including by serving monitors a stale view. A witness should serve a recent checkpoint that it cosigned; the specification allows some delay but recommends not delaying the monitoring view by more than an hour.

Donor mechanism: a cosigned checkpoint and a monitor-visible recent checkpoint are separate obligations; stale-withholding is security-relevant even without equivocation.

Reference: https://c2sp.org/tlog-witness

### C2SP tlog-mirror

A mirror is a cosigner that additionally stores the log contents and makes them accessible. Its signature therefore carries a stronger storage/availability statement than an ordinary witness cosignature.

Donor mechanism: archival/mirror channels can provide independent evidence that a frontier advanced even when ordinary service paths are stale or withheld.

Reference: https://c2sp.org/tlog-mirror

### Sigstore Rekor monitoring model

Sigstore documents independent Rekor auditors/monitors and notes that long-term transparency trust requires monitoring. Rekor exposes a public event stream as an additional observation path.

Donor mechanism: monitoring should be independently operable and should not depend exclusively on the primary log request path.

References:
- https://docs.sigstore.dev/logging/overview/
- https://docs.sigstore.dev/logging/event_stream/

## Frozen decisions

### 1. Monitor identity is a capability generation, not an endpoint

Each required monitor is represented by a content-addressed `monitor_generation` containing at least:

- monitor identity/public key;
- implementation/toolchain generation;
- operator/control domain;
- network/distribution domain;
- observation-channel class (`origin`, `witness`, `mirror`, `archive`, `event_stream`, `offline_import`);
- log/origin scope;
- maximum observation lag policy;
- checkpoint-validation capability;
- retained-frontier storage semantics;
- liveness-attestation source;
- revocation/quarantine state.

Changing any authority-relevant field creates a new generation. Endpoint aliases do not create new monitors.

### 2. Completeness is an obligation over expected frontier advances

For every admitted frontier checkpoint `C_n`, monitoring policy creates an observation obligation for the next permissible advance window.

A monitor does not satisfy the obligation by saying `healthy=true`. It satisfies it only with authenticated evidence binding:

`monitor_generation || log_origin || observed_checkpoint_digest || observed_size/sequence || predecessor/frontier relation || observation_time || channel || policy_generation`.

The monitor must independently validate checkpoint signature and consistency/ancestry from its retained frontier before recording the observation.

### 3. Coverage cannot be satisfied vacuously

Consequential admission requires a configured minimum set of *eligible* monitors after removing:

- revoked/quarantined generations;
- stale monitors beyond their observation deadline;
- monitors lacking the required log/origin scope;
- monitors whose liveness evidence is missing or unauthenticated;
- monitors collapsed into the same common-mode diversity domain where policy requires independence.

If the eligible set falls below policy threshold, the result is `MONITOR_COVERAGE_DEGRADED`, not PASS.

Zero observed advances cannot prove completeness merely because no monitor reports an advance. At least one independent publication/clock/deadline signal must establish whether an advance was expected or whether the frontier is legitimately unchanged.

### 4. Publication commitments are explicit

Each log/trust-frontier generation binds a publication policy containing:

- maximum checkpoint publication interval or event-triggered publication rule;
- maximum monitor-observation lag;
- allowed clock-skew bound;
- required observation-channel classes;
- witness/mirror freshness constraints;
- escalation state transitions.

Absence of a publication deadline is not interpreted as unlimited staleness.

### 5. Distinguish benign delay from selective omission

Frozen states:

- `CURRENT`: monitor observed the admitted frontier within deadline.
- `DELAY_PENDING`: deadline not yet exceeded; no contradiction observed.
- `STALE`: deadline exceeded but no independent proof of a newer checkpoint exists.
- `OMISSION_SUSPECTED`: another eligible independent channel has authenticated evidence of a newer consistent checkpoint that this monitor should have observed.
- `OMISSION_PROVEN`: monitor/channel served an authenticated older checkpoint after evidence proves it had previously observed/cosigned/stored the newer checkpoint, or an authenticated publication commitment is violated with durable contrary evidence.
- `FORK`: incompatible authenticated checkpoints; governed by the split-view contract, not by stale/omission recovery.

`STALE` is not automatically malicious. It still degrades admission authority.

### 6. Witness liveness is not inferred from old cosignatures

A valid historical witness cosignature proves only that the witness accepted that checkpoint at that time. It does not prove current monitor availability or current observation.

Current liveness requires a fresh authenticated response/checkpoint observation within policy. A health endpoint controlled by the same untrusted serving path is insufficient by itself.

A witness that is non-equivocating but stale beyond policy is removed from the current liveness quorum until it catches up consistently.

### 7. Common-mode monitor failures collapse diversity

Monitors sharing the same effective operator, credentials, storage backend, CDN/cache path, scheduler, telemetry collector, or parser/verifier lineage may occupy one common-mode failure domain for the relevant obligation.

Policy computes coverage only after diversity collapse. Three monitors behind one CDN and one backend cannot satisfy a 3-domain omission-detection threshold.

### 8. Archive/mirror evidence can outrank a uniformly stale reachable view

If a valid mirror/archive/offline checkpoint is newer than all currently reachable service/witness monitor views and has valid ancestry/consistency from the retained frontier, the system records `OMISSION_SUSPECTED` or stronger rather than discarding the archive as "old channel" evidence.

A restore from a stale archive cannot lower the retained frontier. Conversely, an archive that proves a newer historical frontier prevents a fresh process from treating uniformly stale online responses as current.

### 9. Monitor liveness telemetry is itself authenticated evidence

Liveness records are content-addressed and bind monitor generation, target origin, observed frontier, monotonic observation counter/epoch where available, time source, and collector generation.

Unsigned metrics, application logs, dashboard status, or a boolean heartbeat are diagnostic only. They cannot satisfy admission coverage.

A telemetry collector that can fabricate observations without possession of the monitor's observation authority does not count as independent evidence.

### 10. Recovery after omission preserves evidence

Recovery never deletes stale/omission evidence. A monitor can return to eligibility only after:

1. presenting a checkpoint consistent with the retained/global frontier;
2. proving catch-up across the missing interval or adopting a trusted mirror/archive consistency path;
3. advancing to a fresh monitor generation if compromise/common-mode defect was involved;
4. satisfying current diversity and liveness policy.

If omission was proven intentional or involved key/toolchain compromise, explicit re-admission authority is required.

## Minimal evidence schema

A monitoring proof bundle contains at least:

- `policy_generation`;
- `log_origin_generation`;
- retained trusted checkpoint digest;
- expected publication window/deadline;
- required monitor set and diversity domains;
- per-monitor generation and eligibility state;
- authenticated observation records;
- observed checkpoint digests/sizes/sequences;
- consistency/ancestry proof digests;
- observation timestamps/time-source generation;
- channel/control/distribution domain;
- stale/omission/fork classification;
- archive/mirror observations;
- revocation/quarantine events;
- recovery/re-admission event if applicable.

The bundle must be sufficient for an independent verifier to recompute coverage without querying current mutable monitor configuration.

## Fail-closed admission rule

A consequential compatibility/trust-frontier edge is monitor-admissible only when all are true:

1. the candidate checkpoint is valid and consistent with retained frontier;
2. publication timing is within the bound of the exact policy generation;
3. the required number of eligible monitor diversity domains has authenticated current observations;
4. no required monitor is in unresolved `OMISSION_SUSPECTED`, `OMISSION_PROVEN`, or `FORK` state;
5. no independent archive/mirror channel proves a newer frontier that the admission view omits;
6. the monitoring proof bundle is complete and independently reproducible.

Failure is `MONITOR_COVERAGE_DEGRADED`/`OMISSION_*`/`FORK`; thresholds do not auto-relax because monitors are unavailable.

## 80-case RED-first matrix

### A. Identity / scope / generation (1–10)
1. endpoint rename without generation change rejected;
2. monitor key rotation with old generation rejected for current liveness;
3. wrong log origin rejected;
4. wrong policy generation rejected;
5. unsupported observation channel rejected;
6. revoked monitor excluded;
7. quarantined monitor excluded;
8. stale capability descriptor excluded;
9. duplicate identity under two URLs counted once;
10. scope widening without new generation rejected.

### B. Non-vacuous coverage (11–20)
11. zero monitors cannot satisfy positive threshold;
12. all monitors silent -> degraded;
13. only unauthenticated heartbeat -> degraded;
14. no expected-publication rule -> fail closed for consequential admission;
15. unchanged frontier before deadline remains `DELAY_PENDING`;
16. unchanged frontier after deadline becomes `STALE`;
17. one required domain missing -> degraded;
18. optional monitor missing does not fail required threshold;
19. duplicate observations from same monitor count once;
20. historical observation outside freshness window cannot satisfy current coverage.

### C. Liveness authenticity (21–30)
21. forged dashboard green status ignored;
22. signed observation with wrong monitor key rejected;
23. replayed old liveness record rejected as current;
24. timestamp outside skew bound rejected;
25. collector-only signature without monitor authority insufficient;
26. valid old checkpoint cosignature insufficient for current liveness;
27. monitor response binds wrong checkpoint digest rejected;
28. observation counter rollback rejected where monotonic counter is required;
29. malformed consistency proof prevents liveness admission;
30. valid current observation restores freshness only after consistency validation.

### D. Diversity / common mode (31–40)
31. three endpoints/one CDN collapse to one domain;
32. separate CDNs/one backend collapse when backend is consequential common mode;
33. separate operators/shared signing key collapse;
34. separate keys/shared verifier defect lineage collapse for affected obligation;
35. independent mirror plus witness count as distinct only when control/storage domains differ;
36. diversity metadata missing -> conservative collapse;
37. revoked domain cannot be replaced by alias endpoint;
38. threshold never auto-reduces during outage;
39. temporary partition degrades rather than reconfigures policy;
40. recovered independent domain can re-enter after fresh authenticated catch-up.

### E. Delay / omission classification (41–50)
41. no newer evidence + before deadline -> delay pending;
42. no newer evidence + after deadline -> stale;
43. newer witness checkpoint vs stale origin -> omission suspected;
44. newer mirror checkpoint vs stale origin+witness -> omission suspected;
45. monitor previously observed newer then serves older -> omission proven;
46. signed publication promise violated with durable newer evidence -> omission proven;
47. stale but internally consistent monitor is not mislabeled fork;
48. same-size different-root checkpoint is fork, not omission;
49. inconsistent ancestry is fork path;
50. eventual consistent catch-up clears stale but preserves historical stale evidence.

### F. Publication deadlines / clocks (51–60)
51. deadline bound to wrong policy generation rejected;
52. clock rollback cannot extend observation deadline;
53. excessive future timestamp rejected;
54. publication interval violation detected;
55. event-triggered checkpoint missing after committed event detected;
56. MMD-like promise expiration produces audit obligation;
57. boundary exactly at allowed deadline handled deterministically;
58. timezone/locale does not alter deadline arithmetic;
59. monotonic elapsed-time evidence preferred where wall clock is unstable;
60. clock-source generation downgrade triggers revalidation.

### G. Archive / mirror / offline (61–70)
61. newer valid mirror beats uniformly stale online view for omission detection;
62. stale archive cannot lower retained frontier;
63. archive checkpoint with invalid ancestry rejected;
64. archive with incompatible root triggers fork path;
65. offline imported newer checkpoint creates catch-up obligation;
66. restored monitor cannot cosign behind externally retained frontier;
67. mirror signature without stored-content availability semantics cannot claim mirror class;
68. archive authenticity failure ignored for authority but retained diagnostically;
69. independent event stream indicating unseen advance triggers investigation but not checkpoint admission without authenticated checkpoint evidence;
70. archive-only advance remains durable across restart.

### H. Recovery / proof bundle / restart (71–80)
71. restart reloads unresolved stale state;
72. restart reloads omission suspected/proven evidence;
73. omission evidence cannot be garbage-collected before resolution policy permits;
74. recovered monitor must prove consistent catch-up;
75. compromised monitor requires new generation/re-admission;
76. proof bundle missing required monitor list rejected;
77. proof bundle missing diversity mapping rejected;
78. independent verifier recomputes same coverage result;
79. disagreement between monitoring verifiers fails closed;
80. no monitoring design result is reported as production PASS until exact executable RED/GREEN and restart tests run.

## Integration consequences

This contract composes with, rather than replaces:

- trust-frontier checkpoint consistency and split-view detection;
- adjudicator trust-root/verifier-diversity/revocation rules;
- deterministic compatibility proof bundles;
- evidence minimization and retention rules.

Production LAB-093 must not create a monitoring subsystem whose local `healthy` state grants authority independently of the authenticated global trust frontier.

## Current execution evidence

During this run, direct git transport was probed with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` and failed before repository execution with DNS resolution failure (`Could not resolve host: github.com`, exit 128). No source mutation or LAB-086 behavioral PASS is claimed.

## Next distinct evidence task if source execution remains unavailable

Freeze **monitor observation receipt / publication promise / omission challenge-response semantics**: define authenticated publication promises, monitor-issued observation receipts, challenge windows, proof-of-non-observation limits, equivocation-resistant challenge transcripts, and exact rules for escalating `STALE -> OMISSION_SUSPECTED -> OMISSION_PROVEN` without pretending that absence alone is cryptographic proof.
