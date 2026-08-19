# LAB-038 — Threshold trust-root rotation and authenticated break-glass recovery

Date: 2026-08-19
Issue: #73
Branch: `lab/038-threshold-root`

## Question

How can verifier trust-root rotation and compromise recovery remain safe when one signer is compromised, without letting the currently compromised provider self-authorize its own replacement?

## Primary-source donor comparison

### The Update Framework (TUF)

Primary sources:
- https://theupdateframework.github.io/specification/v1.0.26/
- https://github.com/theupdateframework/specification/blob/master/tuf-spec.md

Transferable mechanisms:
- every role has an explicit key set and signature threshold;
- root update `N -> N+1` must be signed by a threshold from the currently trusted root **and** a threshold from the candidate root;
- each key identity contributes at most once to threshold counting;
- root versions advance incrementally, creating an auditable chain of trust;
- keys removed/revoked by a new trusted root cease to authorize subsequent metadata.

This dual-threshold rule prevents a candidate root from becoming trusted merely because it can sign itself, while also proving that the new root is internally usable before activation.

### HashiCorp Vault recovery/unseal quorum

Primary sources:
- https://developer.hashicorp.com/vault/docs/concepts/seal
- https://developer.hashicorp.com/vault/docs/commands/operator/rekey

Transferable mechanisms:
- sensitive recovery/rekey authority can be split across independent shares;
- privileged recovery/rekey operations require a configured threshold/quorum rather than one operator secret;
- with auto-unseal/HSM/KMS deployments, recovery keys are conceptually separate from the seal provider key and are used for privileged recovery operations;
- rekey operations themselves require the existing quorum before changing shares/threshold.

The lab does not implement Shamir Secret Sharing. It transfers the authority principle: break-glass recovery must be controlled by a separately pinned quorum whose authority is not supplied by the compromised provider/root being replaced.

## Synthesized protocol

### Normal rotation

For current root `R_n` and candidate `R_(n+1)`:

1. provider identity must remain bound;
2. candidate version must be exactly `n+1`;
3. authority epoch must remain unchanged;
4. build one canonical rotation payload containing the candidate root descriptor;
5. verify unique, non-revoked signatures satisfying the old-root threshold;
6. independently verify unique, non-revoked signatures satisfying the new-root threshold;
7. atomically persist exactly the candidate root, then activate it in memory.

### Break-glass recovery

Recovery is deliberately a different authority path:

1. candidate root is still bound to the same provider identity;
2. root version advances exactly one;
3. `authority_epoch` advances exactly one;
4. recovery payload binds old version/epoch, candidate root, and pinned recovery-authority generation;
5. signatures must satisfy the separately pinned recovery quorum;
6. current provider/root keys do not count toward that quorum unless independently configured as recovery identities (the reference configuration keeps them separate);
7. after activation, receipts/rotation records from the previous authority epoch are non-current.

## Failure experiment

Unsafe reference: `UnsafeSingleSignerRecovery` accepts a self-asserted key supplied by the candidate root itself.

Observed unsafe result:

```text
AssertionError: True is not false : unsafe self-authorized one-signer recovery was accepted
FAILED (failures=1)
```

This demonstrates the bootstrap flaw: cryptographic validity under an attacker-selected key is not authorization.

## Corrected experiment

Prototype: `experiments/anchor_threshold_root/`.

Observed corrected result:

```text
Ran 15 tests
OK
```

Covered scenarios include old/new thresholds, single-compromise rejection, duplicate signer rejection, revocation, provider/version/epoch binding, separate recovery quorum, provider-key recovery rejection, recovery replay rejection, durable-write failure, single-root restart state, and evidence without private signing material.

`python -m compileall -q experiments` also passed.

## Audit findings

The first passing suite covered the required matrix but did not explicitly prove two failure semantics. The audit added:

1. **recovery replay after epoch advance** — the same recovery transition must fail once the authority epoch has advanced;
2. **durable-write failure** — if persistence fails, the candidate root must not become active in memory.

Both are now regression tests.

## Integration with earlier LABs

- **LAB-034/035 freshness:** threshold signatures authenticate authority but do not independently defeat whole-storage rollback. Root/recovery version and epoch must still be anchored to the trusted replay-watermark/external monotonic-anchor layer.
- **LAB-036 authenticated anchor observations:** threshold-root state determines which provider verification identities are authorized; observation freshness/challenge binding remains separate.
- **LAB-037 key authorization:** LAB-038 generalizes the single trusted key into a threshold root set and replaces unauthenticated `recover()` control input with a separately pinned recovery quorum.

## Authority separation

Normal rotation and compromise recovery are intentionally not interchangeable. Normal rotation proves continuity from the currently trusted root and usability of the new root; break-glass recovery assumes normal continuity may be compromised, so it requires an independent pinned authority and advances the authority epoch.

A signature is evidence of key possession. It is not, by itself, evidence that the signer is authorized for the current operation.

## Non-goals

- no general certificate authority;
- no transparency log;
- no real HSM/KMS deployment;
- no Shamir implementation;
- no production public-key cryptography claim;
- no claim that local atomic file replacement provides rollback resistance.

## Stop-condition assessment

The required threshold/recovery matrix is covered, the unsafe single-signer/self-authorized design demonstrably fails, the corrected deterministic model passes, and the authority/freshness boundary is explicit. Remaining work is remote publication/audit/integration.
