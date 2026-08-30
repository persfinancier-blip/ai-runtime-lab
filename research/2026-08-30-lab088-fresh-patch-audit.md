# LAB-088 fresh patch audit

Date: 2026-08-30
Issue: #167
PR: #172
Branch: `lab/088-threshold-signer-noise`

## Scope

Perform the remaining fresh semantic patch audit for LAB-088 without promoting unexecuted downstream compatibility work to evidence.

## Exact diff reviewed

PR #172 changes only the threshold signer-collection rule in two runtime files plus adds the dedicated regression/research artifacts:

- `experiments/provider_threshold_rotation/protocol.py`
- `experiments/provider_threshold_rotation/enablement.py`
- `experiments/provider_threshold_rotation/tests/test_signer_noise.py`

The runtime delta is uniform across all four collectors:

1. do **not** add `sig.signer_id` to `seen` before cryptographic verification;
2. continue rejecting revoked and unknown signer identities exactly as before;
3. compute/compare the same HMAC over the same payload as before;
4. add the signer identity to `seen` only after the MAC comparison succeeds;
5. append/count the signer only after that same successful comparison.

Reviewed collectors:

- live provider threshold proof (`verify_threshold`);
- threshold enablement (`verify_enablement`);
- old/new authority-rotation quorum helper;
- persisted authority-transition verification in `verify_durable_locked`.

## Semantic audit

No authority-model widening was found in the patch.

- Threshold values are unchanged.
- Signer membership lookup is unchanged.
- Revocation filtering is unchanged.
- Payload construction/binding is unchanged.
- HMAC algorithm/key material/comparison is unchanged.
- A duplicate **valid** signature still counts once because the first valid signature adds the signer to `seen`.
- Invalid, unknown, or revoked noise cannot contribute to quorum.
- The only behavior intentionally changed is that an invalid signature naming a real, non-revoked signer no longer suppresses a later valid signature from that same signer.

This matches the issue objective: availability/robustness correction without authority-semantic change.

## Evidence boundary

This note is a source/diff audit, not a new execution claim. Retained exact-source evidence remains 22/22 focused/core PASS + compileall as already recorded on #167/#172.

The remaining readiness gate is unchanged:

1. execute the existing LAB-083 supported-integration suite on PR #172;
2. execute downstream LAB-084/LAB-085/LAB-086 compatibility regressions on the changed collectors;
3. keep PR #172 draft until those executions are observed clean.

Current runtime transport still does not provide a complete branch checkout/file bridge into the executable filesystem, so those downstream gates were not fabricated or inferred from this audit.

## Decision

Fresh patch audit: **CLEAN** for threshold-authority semantics.

PR #172 remains DRAFT because execution compatibility, not source-audit uncertainty, is now the remaining blocker.
