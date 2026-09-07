# Freshness Clock Authority / Secure-Time Rollback / Suspend-Resume / Long-Offline Verifier Semantics V1

Date: 2026-09-07
Status: FROZEN DESIGN CONTRACT
Scope: LAB-093 follow-up; composes with the previously frozen witness activation-epoch distribution/freshness contract. This design freeze does **not** substitute for executable RED/GREEN proof.

## Contract name

`FRESHNESS_CLOCK_AUTHORITY_SECURE_TIME_ROLLBACK_SUSPEND_LONG_OFFLINE_V1_FROZEN`

## Problem

The preceding activation-epoch contract requires positive authenticated freshness evidence before a verifier may treat a witness epoch as current authority. That requirement is incomplete unless the verifier can answer a harder question: **what clock is allowed to decide whether the freshness interval is still open?**

A naive implementation that checks `now < next_update` against local wall time is rollbackable. A VM snapshot, RTC reset, filesystem rollback, host clock change, long suspend, restored container image, or deliberate clock rewind can make an already-expired authority object appear fresh again. Conversely, a monotonic process clock is not sufficient across reboot/snapshot boundaries and may or may not include suspend time depending on the clock selected.

The contract below separates authenticated time evidence, local elapsed-time evidence, persisted lower bounds, and historical-only verification.

## Primary sources / donors

1. RFC 8915, Network Time Security for NTP: https://www.rfc-editor.org/rfc/rfc8915.html
   - NTS authenticates NTP time synchronization and provides replay/request-response protections.
   - Section 8.5 explicitly recognizes the bootstrapping problem when the local clock is not correctly set.
   - It recommends persisting the last synchronized system time and refusing certificates whose `notAfter` is earlier than that recorded time; it also recommends multiple time sources.
   - It warns that cryptographic authentication does not eliminate delay attacks; accepted error remains bounded by network-delay policy rather than becoming exact trusted time.

2. RFC 3161, Time-Stamp Protocol: https://www.rfc-editor.org/rfc/rfc3161.html
   - Donor for an externally authenticated statement that a particular digest existed at a trusted time.
   - Useful as durable historical-time evidence, not as a continuously fresh wall clock.

3. The Update Framework specification: https://theupdateframework.github.io/specification/
   - Trusted metadata versions must not roll backward.
   - Expired metadata must not remain trusted; expiration is explicitly used to limit freeze attacks.
   - The client persists trusted metadata to non-volatile storage.
   - Donor for separating monotonic trusted state from expiration/freshness checks.

4. Linux timerfd/clock semantics: https://www.man7.org/linux/man-pages/man2/timerfd_settime.2.html
   - `CLOCK_REALTIME` is settable and can jump discontinuously.
   - `CLOCK_MONOTONIC` is nonsettable after boot but does not include suspend time.
   - `CLOCK_BOOTTIME` is monotonic and includes suspend time.
   - Donor for the rule that suspend-aware lease/freshness accounting must not use a clock that pauses during suspend.

## Core distinction

```text
AUTHENTICATED_TIME_SAMPLE
    != LOCAL_WALL_CLOCK
    != MONOTONIC_ELAPSED_TIME
    != CURRENT_AUTHORITY
```

No single clock source is sufficient for all failure modes.

A current-authority verdict is valid only when the verifier has both:

1. a non-rollbackable lower bound proving time has not moved backwards across durable recovery boundaries; and
2. a bounded upper/liveness argument proving the verifier has not silently remained offline beyond the freshness allowance.

If either side is missing, current authority becomes unknown rather than being inferred from a convenient local timestamp.

## Data model

### `TrustedTimeFloorV1`

Persisted per verifier authority lineage:

```text
lineage_id
floor_utc
floor_source_class
source_identity_digest
source_evidence_digest
activation_frontier
persist_generation
observed_boot_id
observed_snapshot_epoch   # where available
```

Semantics:

- `floor_utc` is a **lower bound**, never an assertion that local wall time equals this value now.
- A verifier MUST NOT move `floor_utc` backwards.
- The durable update that advances this floor MUST be atomic with the trusted activation/publication frontier that relied on that time evidence.
- Missing or rolled-back floor state is a recovery event, not permission to recreate the floor from local wall time.

### `AuthenticatedTimeSampleV1`

```text
source_class                 # e.g. NTS quorum, trusted timestamp, signed publication checkpoint
source_identity
sample_utc
uncertainty_before
uncertainty_after
request_nonce_or_binding
sample_evidence_digest
received_activation_frontier
```

A sample defines an interval, not a mathematically exact instant:

```text
[sample_utc - uncertainty_before,
 sample_utc + uncertainty_after]
```

Network time is not promoted to zero-error trusted time merely because packets are authenticated.

### `LocalElapsedGuardV1`

```text
boot_identity
clock_class                  # suspend-aware required for freshness expiry
start_tick
max_elapsed
associated_time_floor_digest
```

For a process that remains in one non-rolled-back boot domain, suspend-aware monotonic elapsed time may safely prove that **at least** a duration has elapsed or that a bounded freshness window has expired.

It MUST NOT be used to bridge reboot, VM snapshot restore, container checkpoint restore, or rollback of the durable trusted-state store unless an external recovery proof re-establishes continuity.

### `FreshnessClockDecisionV1`

Possible outcomes:

- `CURRENT_FRESH`
- `CURRENT_EXPIRED`
- `HISTORICAL_ONLY`
- `TIME_ROLLBACK_DETECTED`
- `TIME_CONTINUITY_UNKNOWN_AFTER_RESTORE`
- `CURRENT_TIME_UNKNOWN_OFFLINE`
- `SOURCE_DISAGREEMENT_NO_AUTHORITY`
- `RECOVERY_REQUIRED_NO_AUTHORITY`

## Source classes and authority

### Class A — durable monotonic authority frontier

Highest-value evidence is not ordinary wall time but a previously authenticated and durably persisted lower bound tied to the same authority lineage.

Examples:

- a witnessed publication checkpoint that itself commits an authenticated issuance time;
- an RFC 3161-style trusted timestamp over a checkpoint digest;
- an externally monotonic generation/epoch whose transition includes an authenticated time interval.

This evidence survives local clock reset because it is verified from durable signed history.

### Class B — authenticated network time

NTS-protected NTP is acceptable as a **fresh time sample** if:

- server identity authentication succeeds;
- request/response freshness/replay checks succeed;
- the source is permitted by policy;
- measured uncertainty and network-delay bounds are retained;
- where policy requires it, enough administratively independent sources agree within a configured envelope.

NTS is not a rollback-resistant durable state store. A fresh NTS sample may advance `TrustedTimeFloorV1`; it does not permit a stale persisted verifier state to be silently accepted.

### Class C — local wall clock / RTC

Local `CLOCK_REALTIME`/RTC is advisory unless independently protected by a platform-specific anti-rollback primitive that the verifier actually validates.

A wall-clock reading lower than the durable trusted floor is a rollback signal. A reading higher than the floor may help availability, but cannot alone establish authority after durable-state continuity has been lost.

### Class D — local monotonic elapsed time

Within a known-live boot/runtime continuity domain:

- use a suspend-aware monotonic clock for authority freshness (`CLOCK_BOOTTIME`-class semantics on Linux);
- do not use `CLOCK_MONOTONIC` alone if suspend time must count against expiry;
- do not translate monotonic ticks into historical UTC without an authenticated anchor.

## Freshness decision rule

Let a freshness object authorize an operation only during signed interval `[this_update, next_update]`, subject to uncertainty.

The verifier computes conservative bounds:

```text
trusted_lower_bound = max(
    durable TrustedTimeFloorV1,
    lower edge of newly authenticated time samples,
    prior bound + proven suspend-aware elapsed time
)

trusted_upper_bound = min(
    upper edges of currently authenticated time samples
)   # when available
```

Then:

1. If `trusted_lower_bound > next_update`, return `CURRENT_EXPIRED`.
2. If a clock/state rollback is observed, return `TIME_ROLLBACK_DETECTED` and fail closed for consequential current-authority operations.
3. `CURRENT_FRESH` requires a positive argument that current real time is inside the permitted interval under policy uncertainty. A merely low local wall clock is not such an argument.
4. If only historical evidence remains, return `HISTORICAL_ONLY` or `CURRENT_TIME_UNKNOWN_OFFLINE`.
5. Unknown current time MUST NOT revive an expired or superseded witness epoch.

## Secure-time rollback rules

### Wall-clock rewind

If local wall time `W` is lower than persisted trusted floor `F` beyond tolerated measurement uncertainty:

```text
W < F - tolerance  -> TIME_ROLLBACK_DETECTED
```

Consequential current-authority mutation is blocked until a new authenticated time source re-establishes a current interval at or above `F`.

The verifier MUST NOT lower `F` to match `W`.

### VM / filesystem snapshot rollback

Restoring an old VM snapshot may roll back all of these together:

- wall clock configuration;
- monotonic process state;
- cached freshness metadata;
- trusted activation frontier;
- persisted `TrustedTimeFloorV1`.

Therefore local consistency among those values is **not** evidence of freshness after snapshot rollback.

If the platform cannot supply an independent non-rollbackable snapshot/boot epoch, recovery requires at least one external authenticated source whose state is strictly newer than the restored verifier's retained frontier. Until then:

`TIME_CONTINUITY_UNKNOWN_AFTER_RESTORE`.

### Durable-store rollback

If an external publication/witness frontier known from any independent durable source is greater than the verifier's local retained frontier, the local store is rolled back even if its signatures are internally valid.

This is an authority rollback first and a clock problem second. Current authority stays blocked until frontier and time-floor recovery both close.

## Suspend / resume

Freshness windows continue to age while the verifier is suspended.

Therefore:

- a suspend-aware monotonic clock is required for local elapsed-time enforcement;
- a clock that stops during suspend cannot extend an authority lease/freshness interval;
- after resume, if the suspend-aware elapsed time places the lower bound past `next_update`, expiry is immediate;
- if suspend duration cannot be reconstructed reliably, return `CURRENT_TIME_UNKNOWN_OFFLINE` and refresh externally before consequential mutation.

A device does not get a fresh lease merely because no CPU instructions executed while asleep.

## Reboot

Ordinary reboot destroys process-local monotonic continuity. On restart:

1. load durable trusted frontier + `TrustedTimeFloorV1`;
2. reject local wall clock below the floor;
3. obtain authenticated current-time evidence when current authority is required;
4. only then establish a new boot-local `LocalElapsedGuardV1`.

If the system was offline longer than the signed freshness interval, a correct implementation naturally fails closed until refresh.

## Years-long offline operation

A self-contained archive may still prove that a signature/checkpoint/epoch was valid **historically** at a recorded frontier. It cannot prove that the same epoch is the current authority years later.

After a long offline period:

```text
historical verification: MAY continue
current authority-bearing mutation: MUST NOT continue
```

unless the verifier obtains fresh authenticated publication/time evidence and proves monotonic continuation from its retained frontier.

The verifier MUST NOT "catch up" by setting the local clock backwards into an old `next_update` interval.

The verifier MUST NOT treat lack of network access as extension of the prior authority period.

## RTC loss / unknown wall time

If RTC state is lost and local real time is unknown:

- retain the durable trusted lower bound;
- do not invent a current time;
- use historical verification only;
- obtain authenticated current-time evidence before returning `CURRENT_FRESH` for consequential operations.

RFC 8915's recommendation to persist previously synchronized time is a direct donor for this lower-bound behavior.

## Time-source disagreement

Authenticated sources can disagree because of compromise, delay attacks, bad upstream reference clocks, or network asymmetry.

Policy MUST define:

- maximum accepted uncertainty;
- administrative independence requirements;
- maximum pairwise disagreement;
- quorum/selection method;
- which operation classes may proceed under degraded time confidence.

If independent sources form incompatible intervals and no policy-authorized interval can be derived, return `SOURCE_DISAGREEMENT_NO_AUTHORITY`.

Do not majority-vote an arbitrary UTC value and call it normative truth.

## Delay attacks

NTS authenticates the responder and packets but does not make packet delay impossible. RFC 8915 explicitly notes that asymmetric delay can bias computed time and that cryptography alone does not eliminate this attack.

Therefore every network-derived sample carries uncertainty / accepted round-trip bound. Authority freshness uses the conservative edge of that interval.

A sample whose uncertainty is wider than the remaining freshness window is insufficient for `CURRENT_FRESH`.

## Composition with activation epochs

For witness activation epoch `E`:

1. epoch/signature validity proves historical authenticity;
2. `TrustedActivationFrontierV1` proves the verifier has not accepted an older epoch than one already known;
3. `TrustedTimeFloorV1` prevents clock rollback from reopening old freshness intervals;
4. authenticated current-time evidence proves the epoch's freshness object is still inside policy interval;
5. if E+1 has ever been authenticated, E is permanently stale regardless of clock state.

No clock manipulation can make E current again after E+1 is known.

## Crash atomicity

When a verifier accepts a new authenticated time/frontier sample that advances authority, the following durable values must commit atomically or under a recoverable journal protocol:

```text
TrustedActivationFrontierV1
TrustedTimeFloorV1
sample evidence digest
publication checkpoint digest
```

Crash after accepting the newer authority but before persisting the new floor must not allow restart into an older freshness interval.

If atomicity cannot be proven after crash, transition to `RECOVERY_REQUIRED_NO_AUTHORITY`.

## Forbidden shortcuts

The following are explicitly invalid:

- `time.time() < next_update` as the sole authority check;
- accepting a local wall clock below the last authenticated time floor;
- treating process monotonic time as durable across reboot/snapshot restore;
- using a monotonic clock that pauses during suspend for an expiry interval that must age during suspend;
- extending freshness because the verifier was offline;
- resetting trusted time/frontier state when caches are cleared;
- trusting unauthenticated NTP after authenticated time was previously required;
- silently falling back from NTS to plain NTP for authority decisions;
- choosing the largest reported network time without uncertainty checks;
- reviving E after E+1 because a restored snapshot forgot E+1;
- replacing current-authority proof with historical RFC 3161 timestamp evidence.

## Fraud / contradiction proofs

1. `TIME_FLOOR_ROLLBACK_PROOF` — local persisted floor lower than independently retained predecessor floor.
2. `WALL_CLOCK_REWIND_PROOF` — local wall time below authenticated durable floor beyond tolerance.
3. `SNAPSHOT_FRONTIER_ROLLBACK_PROOF` — restored verifier frontier lower than external monotonic frontier.
4. `SUSPEND_EXCLUDED_FROM_EXPIRY_PROOF` — implementation used a clock class that pauses during suspend.
5. `OFFLINE_FRESHNESS_EXTENSION_PROOF` — freshness accepted after `next_update` solely because no refresh occurred.
6. `STALE_EPOCH_REVIVAL_PROOF` — E accepted after authenticated observation of E+1.
7. `UNAUTHENTICATED_TIME_DOWNGRADE_PROOF` — authority decision uses plain/unauthenticated time after secure-time requirement.
8. `TIME_SAMPLE_UNCERTAINTY_OMISSION_PROOF` — network time treated as exact despite recorded delay/uncertainty.
9. `FRONTIER_TIME_NONATOMIC_CRASH_PROOF` — post-crash state combines newer authority with older time floor or vice versa.
10. `LONG_OFFLINE_CURRENT_AUTHORITY_PROOF` — current authority asserted without fresh authenticated continuation after freshness interval elapsed/unknown.

## RED-first executable matrix

At minimum, implementation work must create failing tests for these cases before production refactor:

1. wall clock advances normally inside interval -> fresh;
2. wall clock rewound below trusted floor -> fail closed;
3. wall clock jumps forward beyond expiry -> expired;
4. wall clock restored into old interval after expiry -> remains expired;
5. persisted floor survives normal reboot;
6. floor storage rollback detected by newer external frontier;
7. VM snapshot restores old epoch E after verifier once saw E+1 -> E rejected;
8. snapshot restores matching old wall+floor+cache -> external newer frontier still detects rollback;
9. no external continuity after snapshot restore -> unknown, not fresh;
10. authenticated NTS sample above floor advances floor;
11. unauthenticated NTP cannot advance authority floor;
12. NTS downgrade failure does not fall back to plain NTP;
13. two independent authenticated sources agree -> accepted interval;
14. independent sources disagree beyond policy -> unknown;
15. one source delayed enough that uncertainty exceeds remaining freshness -> not fresh;
16. network sample lower than durable floor -> rejected/rollback signal;
17. RFC3161 historical timestamp proves past existence but not current freshness;
18. `CLOCK_MONOTONIC`-style suspend pause cannot extend freshness;
19. `CLOCK_BOOTTIME`-style suspend-aware elapsed time expires during suspend;
20. unknown suspend duration -> refresh required;
21. short suspend inside interval -> remains fresh when bounds prove it;
22. long suspend past `next_update` -> expired immediately on resume;
23. RTC lost at reboot -> historical only until authenticated refresh;
24. local RTC below floor -> rollback signal;
25. local RTC above floor but no authenticated current proof after long outage -> current unknown;
26. one-hour offline within explicitly allowed fresh interval with safe elapsed proof -> accepted;
27. offline past interval -> blocked;
28. years offline -> historical verification only;
29. manually setting clock back into old interval does not restore current authority;
30. manually setting clock forward cannot roll trusted frontier back;
31. E+1 known then clock rolled back -> E still stale;
32. E+1 unknown locally but external publication proves it -> E stale after sync;
33. current time fresh but publication frontier stale -> not current authority;
34. publication frontier current but time unknown -> not current authority;
35. current time and frontier both valid -> current authority;
36. crash after accepting new frontier before floor persistence -> recovery required;
37. crash after floor persistence before frontier persistence -> recovery required;
38. atomic frontier+floor commit -> restart valid;
39. cache deletion cannot reset floor;
40. cache restore cannot override durable floor;
41. restored application data with newer external anti-rollback store -> detected;
42. restored anti-rollback store itself without external continuity -> unknown;
43. signed time sample replayed with old request binding -> rejected;
44. same authenticated sample reused only within explicit validity semantics -> deterministic outcome;
45. malformed uncertainty bounds -> reject;
46. negative uncertainty -> reject;
47. integer/time overflow near representational limits -> fail closed;
48. leap/clock-format parsing edge cannot lower trusted floor;
49. source identity rotation requires authenticated continuity policy;
50. compromised time-source removal cannot rewrite historical samples;
51. policy lowering freshness window causes immediate conservative re-evaluation;
52. policy expansion cannot resurrect already expired/superseded epoch without explicit authorized transition semantics;
53. operation class with zero bounded-staleness allowance blocks immediately offline;
54. read-only historical operation can continue offline;
55. authority mutation cannot continue on historical-only proof;
56. stale clone possessing old time cache cannot override newer floor;
57. stale clone with old activation epoch cannot gain authority by clock rewind;
58. duplicated VM clones diverge in wall time -> neither bypasses shared external frontier;
59. suspend/resume plus network partition after expiry -> blocked;
60. resume with fresh authenticated source -> may recover after monotonic checks;
61. delay attack within configured uncertainty -> conservative interval used;
62. delay attack outside bound -> source rejected;
63. source quorum loses independence -> insufficient authority;
64. authenticated time source unavailable -> no insecure downgrade;
65. TLS/NTS bootstrap with unreliable clock obeys explicit bootstrap policy and retained floor;
66. certificate expired before retained floor -> reject per retained-time logic;
67. newly authenticated source reports current time consistent with retained floor -> recover;
68. source reports time far future causing DoS -> policy bounds and independent confirmation required;
69. far-future accepted by authorized quorum advances floor irreversibly; later lower time cannot undo it;
70. operator clears application cache after far-future event -> floor remains;
71. timestamp evidence binds wrong activation lineage -> reject;
72. timestamp evidence binds wrong checkpoint digest -> reject;
73. correct time but wrong oracle/publication generation -> reject;
74. time-floor record with invalid signature/provenance -> reject;
75. local boot identity unexpectedly repeats after snapshot -> not sufficient continuity proof;
76. process restart within same boot uses durable floor plus new elapsed guard;
77. forked publication branches with conflicting times -> fork handling precedes clock selection;
78. unknown publication fork + apparently fresh local time -> authority remains unknown;
79. verifier replay drill after simulated 5-year offline returns historical-only until refresh;
80. full recovery drill proves restored verifier cannot revive superseded E through any wall/monotonic/RTC rollback combination.

## Decision

Freeze this contract as:

`FRESHNESS_CLOCK_AUTHORITY_SECURE_TIME_ROLLBACK_SUSPEND_LONG_OFFLINE_V1_FROZEN`.

The production implementation must model time as authenticated, bounded evidence plus monotonic durable history. **Wall-clock freshness alone is not authority.** Long-offline or restored verifiers fail closed for current consequential authority while retaining historical verification capability.

## Next research boundary

The next distinct unresolved boundary is **secure-time source key lifecycle / time-source quorum independence / far-future poisoning recovery semantics**: define how authenticated time sources rotate keys and policies; how to avoid correlated clock authorities; how an accidentally or maliciously accepted far-future time floor can be recovered without making rollback attacks possible; and whether recovery requires an explicit higher-order governance/appeal artifact rather than ordinary time samples.
