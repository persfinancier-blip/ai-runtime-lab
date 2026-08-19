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

Normal rotation requires exact provider/version/epoch binding, one canonical rotation payload, a threshold of unique valid signatures from the old root, a threshold of unique valid signatures from the candidate root, and atomic persistence before in-memory activation.

Break-glass recovery is a different authority path: root version and authority epoch each advance exactly one; the recovery payload binds old version/epoch, candidate root and recovery-authority generation; signatures must satisfy the separately pinned recovery quorum. Current provider/root keys do not self-authorize this path.

## Failure experiment

Unsafe `UnsafeSingleSignerRecovery` accepts an attacker-selected key supplied by the candidate itself.

Observed unsafe result:

```text
AssertionError: True is not false : unsafe self-authorized one-signer recovery was accepted
FAILED (failures=1)
```

Cryptographic validity under an attacker-selected key is not authorization.

## Corrected experiment

Prototype: `experiments/anchor_threshold_root/`.

Observed corrected result:

```text
Ran 16 tests
OK
```

`python -m compileall -q experiments` also passed.

Covered scenarios include old/new thresholds, single-compromise rejection, duplicate signer non-counting, revocation, provider/version/epoch binding, separate recovery quorum, provider-key recovery rejection, recovery replay rejection, durable-write failure, single-root restart state, evidence without private signing material, and tolerance of junk/unknown/duplicate signatures when a sufficient valid quorum remains.

## Audit findings

The audit added or corrected three semantics before merge:

1. **recovery replay after epoch advance** — the same recovery transition fails once the authority epoch advances;
2. **durable-write failure** — persistence failure cannot activate the candidate in memory;
3. **threshold robustness** — revoked, duplicate, unknown or invalid signatures do not count toward quorum but also cannot turn an otherwise sufficient valid quorum into a denial-of-service failure. Threshold validation also requires enough non-revoked configured keys to make the threshold achievable.

## Integration with earlier LABs

- **LAB-034/035 freshness:** threshold signatures authenticate authority but do not independently defeat whole-storage rollback; root/recovery version and epoch still depend on trusted replay-watermark/external monotonic-anchor freshness.
- **LAB-036 authenticated anchor observations:** threshold-root state determines authorized provider verification identities; observation freshness/challenge binding remains separate.
- **LAB-037 key authorization:** LAB-038 generalizes a single trusted key into a threshold root set and replaces unauthenticated recovery control with a separately pinned recovery quorum.

## Authority separation

Normal rotation proves continuity from the currently trusted root and usability of the new root. Break-glass recovery assumes normal continuity may be compromised, so it requires an independent pinned authority and advances the authority epoch. A signature proves key possession, not authorization for the operation.

## Non-goals

No general CA, transparency log, real HSM/KMS deployment, Shamir implementation, production public-key cryptography claim, or claim that local atomic file replacement supplies rollback resistance.

## Stop-condition assessment

The threshold/recovery matrix passes, the unsafe self-authorized design demonstrably fails, the remote audit finding is corrected and re-tested, and the authority/freshness boundary is explicit. Remaining work is integration.