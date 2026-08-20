# LAB-046 multi-SCT policy

Reference policy layer over independently authenticated per-log LAB-045 audit results.

The evaluator is deliberately not a browser/vendor CT policy. It binds a versioned local policy to a trust generation, counts distinct trusted LogIDs, optionally requires distinct operator groups, and preserves `FULFILLED`, `NOT_YET_AUDITABLE`, `INCONCLUSIVE_AFTER_DEADLINE`, and `MMD_VIOLATION` instead of collapsing them into one boolean.

Unknown logs never satisfy thresholds. Exact duplicate evidence collapses by LogID. Conflicting authenticated observations for one LogID fail closed. A misbehavior observation is not masked by enough other fulfilled logs. The reference HMAC is only an experiment stand-in for the already authenticated LAB-045 evidence identity/binding boundary; production aggregation should consume that authoritative evidence rather than minting trust locally.

Validation observed locally: corrected suite 13/13 passed; unsafe duplicate/self-asserted row counter failed as expected; compileall passed.
