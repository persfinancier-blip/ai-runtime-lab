# LAB-047 — Authenticated CT Log-List Lifecycle and Operator-Identity Binding

Date: 2026-08-20  
Issue: #90  
Branch: `lab/047-ct-log-trust-lifecycle`

## Question

How should LAB-046 obtain authoritative `LogID`, verification-profile, operator-group and lifecycle facts without trusting caller-supplied metadata, while preserving historical attribution after log distrust or operator reassignment?

## Protocol boundary

RFC 9162 defines immutable log parameters and cryptographic artifacts, but explicitly states in §6.2 that client discovery, trust and distrust of logs are handled out of band and are outside the RFC. Therefore operator diversity and trust-list freshness are local-authority inputs, not facts that an SCT/log can self-assert.

Primary source:
- https://www.rfc-editor.org/rfc/rfc9162.html

## Donor mechanisms

### Chromium CT log list

Current Chromium's `certificate_transparency.proto` models:

- log public key / LogID / MMD / URL;
- current and historical lifecycle state (`PENDING`, `QUALIFIED`, `USABLE`, `READ_ONLY`, `RETIRED`, `REJECTED`) with state-start timestamps;
- operator history with operator-start timestamps;
- list major/minor versions, compatibility version and list timestamp for freshness.

Chromium's CT README states that the built-in list is superseded by updates delivered through the PKI Metadata component updater.

Primary sources:
- https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/certificate_transparency/certificate_transparency.proto
- https://chromium.googlesource.com/chromium/src/+/main/components/certificate_transparency/README.md

Transferable mechanisms:
1. operator membership is authoritative metadata, not caller input;
2. lifecycle transitions are timestamped and historically retained;
3. list content has explicit version/freshness metadata;
4. verification identity is bound to a stable LogID/profile.

### TUF / Sigstore trust distribution

TUF signed metadata uses explicit versions, expiry, hashes and signatures to resist rollback/freeze/mix-and-match attacks. Clients must not replace trusted metadata with lower versions and must reject expired metadata. Sigstore distributes trust roots/keys through TUF rather than accepting keys from the object being verified.

Primary sources:
- https://theupdateframework.github.io/specification/v1.0.26/
- https://docs.sigstore.dev/about/security/

Transferable mechanisms:
1. authenticate trust metadata against a pinned root;
2. bind evaluation to exact signed content identity, not only a mutable generation number;
3. reject rollback, stale/expired metadata and same-coordinate substitution;
4. keep historical trusted snapshots for attribution rather than rewriting past decisions.

## Reference schema

`SignedSnapshot` contains:

- schema version;
- monotonic `version` and `generation`;
- `issued_at` and `expires_at`;
- canonical operator table;
- canonical log table: `log_id`, immutable `verification_profile`, authoritative `operator_id`, lifecycle `state`, `state_since`;
- pinned signer identity and authenticator.

`snapshot_id = SHA-256(canonical authenticated content)` is the exact trust-view identity used by decisions.

The HMAC is deliberately a deterministic stand-in; production systems would use an authenticated update mechanism such as a signed/TUF-like metadata chain.

## Lifecycle rules tested

- only an authenticated current snapshot supplies log/operator authority;
- unknown logs cannot self-promote;
- duplicate LogID/operator IDs and unknown operator references are malformed;
- stale version/generation/time and expired snapshots fail closed;
- same version/generation/time with different signed content is substitution and fails closed;
- `LogID` verification profile is immutable across generations;
- operator reassignment requires a new authenticated generation and does not alter old snapshots;
- `RETIRED`/`DISTRUSTED` logs stop contributing to future thresholds and cannot silently reactivate;
- evaluation is pinned to exact `snapshot_id`, not only generation.

## Experiment

Corrected command:

```bash
python -m unittest discover -s experiments/ctv2_log_trust_lifecycle/tests -p 'test_*.py' -v
```

Observed: **17/17 passed**.

Also observed:

```bash
python -m compileall -q experiments/ctv2_log_trust_lifecycle
```

completed successfully.

### Unsafe seed

`unsafe_self_asserted_expected_failure.py` models the LAB-046 authority gap: the caller supplies `trusted=True` and arbitrary `operator_id` values. Two claims then satisfy a 2-log/2-operator threshold even though no authenticated trust metadata exists.

Observed unsafe result: expected assertion failure because `unsafe_evaluate(...)` returned `True`.

## Audit findings

The first corrected draft covered rollback/substitution and distrust, but freshness and lifecycle validity were still under-specified. Audit tightened the model by adding `expires_at`, strict expiry rejection at acceptance, `state_since <= issued_at`, and fail-closed no-reactivation for both `RETIRED` and `DISTRUSTED` logs. The suite increased from 14 to 17 passing tests after these corrections.

## Integration implications

LAB-046-style compliance evaluation should receive an exact authenticated trust snapshot (or a verified reference to one), then derive:

- trusted LogIDs;
- verification profiles;
- operator grouping;
- current lifecycle eligibility.

The caller may provide evidence, but it must not provide authoritative trust/operator metadata. Decisions should persist the exact `snapshot_id` used so later distrust/operator changes do not rewrite historical interpretation.

## Non-goals

- no browser/vendor-specific SCT-count threshold;
- no live Chrome component-updater implementation;
- no claim that HMAC equals TUF/Chrome production authentication;
- no online log qualification process;
- no witness/gossip/consensus layer.

## Stop condition

Satisfied: LAB-046-style evaluation can consume exact authenticated trust metadata and no longer trusts caller-supplied log/operator authority.
