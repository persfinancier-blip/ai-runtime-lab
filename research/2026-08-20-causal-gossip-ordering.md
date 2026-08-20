# LAB-054 — Causal gossip ordering and observer credibility

## Result
Cross-observer wall-clock comparison is not required for freeze attribution. Each observer instead maintains an authenticated sequence/predecessor chain. A local freeze suspicion exists only when the same verified observer chain contains a newer peer view and a later causal successor contains an older prefix. Consequential corroboration requires distinct observer identities.

## Donors
- RFC 9162: consistency of the log view across query sources is a distributed auditing problem and requires sharing authenticated log responses; failure can yield signed evidence of misbehavior.
- C2SP Transparency Log Witness Protocol: a witness persists its latest verified checkpoint, requires the submitted old state to match that durable predecessor, verifies consistency, and atomically advances its record. This is the transferable sequence/predecessor mechanism.
- C2SP tlog proof/cosignature: witness identity/quorum is application policy; authenticated timestamps exist but proof verification does not make them a universal cross-observer ordering oracle.

## Experiment
The reference model signs observer sequence number, predecessor observation ID, exact peer-authenticated view identity/content/signature, and an intentionally untrusted `claimed_time`. Classification never compares claimed wall clocks.

The observer is authoritative only for causal ordering/receipt. Peer-view content remains authoritative only if the original peer signature verifies and the reconstructed signed view hashes to the exact `view_id` carried by the observation. This prevents a compromised observer from inventing plausible peer events and then laundering them into authenticated gossip evidence with its own signature.

Covered: newer→older causal regression, older→newer progression, malicious timestamps, replay/rollback, same-sequence observer fork/equivocation, distinct-observer corroboration, duplicate quorum inflation, partition/silence, restart watermarks, persisted-head tampering, authenticated peer split views, fabricated observer content without a peer signature, and view-id substitution.

## Validation
- Corrected exact-source suite: 13/13 tests passed.
- Unsafe wall-clock seed: failed as expected because attacker-chosen times alone produced `FREEZE_SUSPECTED`.
- `python -m compileall -q experiments/ctv2_bundle_causal_gossip` passed.
- Local Git blob SHA for `protocol.py` and corrected tests matched the GitHub branch blob SHA after publication.

## Audit finding and correction
The first implementation signed `peer/view_id/events` with the observer key but did not preserve or re-verify the peer signature at `accept()`. That allowed observer narrative bytes to masquerade as peer-authenticated evidence. The corrected observation carries the exact peer signature; `accept()` reconstructs the peer view, verifies it against the pinned peer key, then checks exact `view_id` binding before any causal classification.

## Boundary
This is evidence detection/attribution after observations are exchanged. It is not reliable gossip delivery, Byzantine consensus, global total ordering, or fork prevention. Silence remains unknowable availability state, and a compromised peer can still sign its own false view; LAB-054 only prevents observers from fabricating peer-authenticated content.
