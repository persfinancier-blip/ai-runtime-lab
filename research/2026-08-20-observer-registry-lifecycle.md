# LAB-055 — Authenticated observer registry lifecycle

## Donor mechanisms

- C2SP Transparency Log Witness Protocol defines a witness by name and public key; witness cosignatures are independent evidence.
- transparency-dev witness implementations persist the last verified checkpoint per log, making witness identity/key configuration a security boundary rather than data asserted by the observed log.
- TUF root metadata supplies transferable lifecycle mechanisms: authenticated/versioned trust metadata, explicit key replacement/revocation, threshold/unique-key semantics, and rollback rejection.

## Protocol

Observer membership is carried by an authenticated `RegistrySnapshot` with stable `registry_id`, monotonic `version` and `generation`, threshold, observer key generations/status, and a digest link to the previous snapshot. New quorum decisions accept evidence only when signed by a distinct ACTIVE observer under the exact current snapshot and observer-key generation. Historical replay resolves the exact recorded snapshot identity instead of reinterpreting old evidence under current membership.

## Experiment

The corrected deterministic suite covers authenticated bootstrap, sybil/duplicate resistance, key rotation, revocation, rollback rejection, predecessor tamper, exact-snapshot historical replay, restart persistence, persisted-state tamper detection, and before/after transition evidence. A deliberately unsafe baseline simply counts self-asserted observer identities and therefore lets two sybils satisfy threshold=2.

## Boundary

Observer authorization says *which observer may contribute*. LAB-054 separately authenticates the peer view the observer reports. Neither layer provides Byzantine consensus, reliable broadcast/delivery, global total ordering, or truthful wall clocks.
