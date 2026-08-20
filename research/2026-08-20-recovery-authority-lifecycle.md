# LAB-057 — Recovery-quorum lifecycle and compromise boundary

Date: 2026-08-20

## Donors

TUF-style root continuity supplies the old+new threshold pattern. HashiCorp Vault recovery-key rekey requires the threshold of existing recovery shares and supports changing the new share count/threshold; optional verification validates the new shares before activation.

Primary sources:
- https://developer.hashicorp.com/vault/docs/commands/operator/rekey
- https://developer.hashicorp.com/vault/api-docs/system/rekey-recovery-key
- https://developer.hashicorp.com/vault/docs/concepts/seal

## Decision

Planned recovery-authority rotation requires three co-authorizations over one canonical transition: old recovery threshold, new recovery threshold, and current normal root threshold. The root co-authorization is intentionally stricter than Vault's recovery-key rekey: a compromised recovery quorum cannot silently replace itself while normal authority remains healthy.

Recovery authority has registry identity, monotonic version/generation, threshold, revocations, and content-derived authority ID. Transition proof sets persist and are re-verified after restart. Root break-glass records preserve the exact recovery authority ID/version/generation used historically.

## Audit finding

The first corrected implementation persisted the recovery transition but not enough historical root material to re-verify its root co-authorization after a later break-glass root recovery. The final version persists root history and re-verifies the exact co-authorizing root on restart. A restart-after-root-recovery regression test covers this case.

## Final boundary

There is no recovery-of-recovery recursion. If both current root quorum and current recovery quorum are lost or compromised, no in-band transition can establish trustworthy authority. Restoration requires an external bootstrap/ceremony with a new trust anchor; the protocol fails closed.

## Validation

- Corrected deterministic suite: 12/12 passed.
- `python -m compileall -q experiments/recovery_authority_lifecycle`: passed.
- Unsafe self-authorized recovery-quorum swap: failed as expected.

## Non-goals

No HSM orchestration, share custody UI, secret reconstruction, distributed consensus, or operator ceremony implementation.
