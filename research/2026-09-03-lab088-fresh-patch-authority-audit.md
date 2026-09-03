# LAB-088 fresh patch authority audit — 2026-09-03

## Scope

Fresh static audit of draft PR #172 (`lab/088-threshold-signer-noise`) against LAB-088's remaining gate: confirm that the signer-noise fix changes availability/robustness only and does not widen threshold authority semantics.

## Exact diff audited

The production diff changes only four local collector sites:

1. `verify_threshold()` in `experiments/provider_threshold_rotation/protocol.py`;
2. `verify_enablement()` in `experiments/provider_threshold_rotation/enablement.py`;
3. the old/new authority quorum collector inside rotation-authority rotation;
4. persisted authority-transition verification during durable/restart audit.

In every site, the only semantic change is moving `seen.add(sig.signer_id)` from before verification to after successful HMAC verification.

## Authority audit

The patch does **not** change:

- threshold values;
- signer membership or key lookup;
- revocation checks;
- provider/authority identity binding;
- payload construction or digest identity;
- signature comparison primitive (`hmac.compare_digest`);
- duplicate-valid-signature counting (a valid signer is still counted once);
- persistent authority schema or proof identity.

For a clean signature list, accepted quorum semantics are unchanged. For noisy input, revoked, unknown, or cryptographically invalid entries no longer reserve a signer identity before proof. A later valid signature from the same authorized signer can therefore contribute exactly once. This removes the previously reproduced fail-closed availability poison without creating an additional signer or lowering quorum.

The new regression file also explicitly retains two negative invariants: duplicate valid signatures count once, and revoked/unknown noise cannot inflate quorum.

## Result

Fresh patch audit: **PASS — no threshold-authority semantic widening found.**

This satisfies only LAB-088 remaining gate item 3 (fresh patch audit). It does **not** substitute for execution of the existing supported-integration suite or downstream LAB-084/LAB-085/LAB-086 compatibility regressions.

## Execution/capability note

Direct repository execution remains unavailable in this run because `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository access with `Could not resolve host: github.com`.

No branch mutation and no new behavioral PASS are claimed by this note.

## Next action

Keep PR #172 draft. When exact branch execution is available, run the existing LAB-083 `test_supported_integration.py` suite first, then the downstream LAB-084/LAB-085/LAB-086 regressions against the exact PR #172 head. If those are green, LAB-088 can be reconciled for readiness without further authority-design changes.
