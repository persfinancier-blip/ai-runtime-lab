# LAB-054 — Causal gossip ordering and observer credibility

## Result
Cross-observer wall-clock comparison is not required for freeze attribution. Each observer instead maintains an authenticated sequence/predecessor chain. A local freeze suspicion exists only when the same verified observer chain contains a newer peer view and a later causal successor contains an older prefix. Consequential corroboration requires distinct observer identities.

## Donors
- RFC 9162: consistency of the log view across query sources is a distributed auditing problem and requires sharing authenticated log responses; failure can yield signed evidence of misbehavior.
- C2SP Transparency Log Witness Protocol: a witness persists its latest verified checkpoint, requires the submitted old state to match that durable predecessor, verifies consistency, and atomically advances its record. This is the transferable sequence/predecessor mechanism.
- C2SP tlog proof/cosignature: witness identity/quorum is application policy; authenticated timestamps exist but proof verification does not make them a universal cross-observer ordering oracle.

## Experiment
The reference model signs observer sequence number, predecessor observation ID, peer view identity/content, and an intentionally untrusted `claimed_time`. Classification never compares claimed wall clocks.

Covered: newer→older causal regression, older→newer progression, malicious timestamps, replay/rollback, same-sequence observer fork/equivocation, distinct-observer corroboration, duplicate quorum inflation, partition/silence, restart watermarks, persisted-head tampering, and authenticated peer split views.

## Boundary
This is evidence detection/attribution after observations are exchanged. It is not reliable gossip delivery, Byzantine consensus, global total ordering, or fork prevention. Silence remains unknowable availability state.
