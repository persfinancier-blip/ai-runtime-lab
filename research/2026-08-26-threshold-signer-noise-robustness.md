# LAB-088 — Threshold signer-noise robustness

## Finding

The LAB-083 HMAC threshold collectors originally added a `signer_id` to the local `seen` set before cryptographic verification. An untrusted signature list could therefore place an invalid signature naming a real signer before that signer's valid signature. The invalid item consumed the identity, the later valid item was skipped, and an otherwise valid threshold quorum was rejected.

Exact current-main reproduction covered four paths:

1. live provider transition threshold verification;
2. threshold-enablement verification;
3. old/new quorum collection during rotation-authority rotation;
4. persisted authority-transition verification during restart/durable audit.

For threshold 2, the sequence `invalid(signer0), valid(signer0), valid(signer1)` was rejected by the old code even though two distinct valid signers were present.

## Corrected rule

A signer is considered used only after its signature has successfully verified. Revoked, unknown, malformed or cryptographically invalid items do not reserve a signer identity. A second valid signature from an already accepted signer is still ignored, so duplicate valid signatures never inflate quorum.

This changes availability/robustness only. It does not change threshold values, signer membership, revocation semantics, payload identity or authority boundaries.

## Evidence

Published branch `lab/088-threshold-signer-noise`:

- `provider_threshold_rotation/protocol.py` Git blob `c596310401007e8c99374d638811cd72397d2d2f`;
- `provider_threshold_rotation/enablement.py` Git blob `a894d85274f7987cbcae7dcf5bacd6a6984e9ef9`;
- `tests/test_signer_noise.py` Git blob `1835991225820497660402dfc41581837c8380e6`.

Observed execution on those exact source bytes:

- new signer-noise regressions: 6/6 PASS;
- pre-existing LAB-083 protocol tests: 10/10 PASS;
- pre-existing enablement tests: 3/3 PASS;
- pre-existing strict enablement-type tests: 3/3 PASS;
- combined focused/core gate: 22/22 PASS;
- compileall: PASS.

A first published version of the new regression test contained a syntax error. Byte-exact reconstruction caught it before it was counted as evidence; it was replaced by the blob listed above and the corrected published file was executed successfully.

## Remaining integration gate

Draft PR #172 must remain draft until the existing LAB-083 supported-integration tests and downstream LAB-084/LAB-085/LAB-086 regressions are run against the corrected collectors. The change is deliberately isolated from the large in-progress LAB-086 branch.
