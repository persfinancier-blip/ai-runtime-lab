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

Current Chromium's `certificate_transparency.proto` models log public key/LogID, lifecycle state and timestamps, operator history, list major/minor versions, compatibility version and a list timestamp intended for freshness checks. Chrome's public CT log-list documentation distinguishes logs included for compliance evaluation from the larger set of known/monitored logs.

Primary sources:
- https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/certificate_transparency/certificate_transparency.proto
- https://googlechrome.github.io/CertificateTransparency/log_lists.html

Transferable mechanisms:
1. operator membership is authoritative metadata, not caller input;
2. lifecycle transitions are timestamped and historically retained;
3. list content has explicit version/freshness metadata;
4. verification identity is bound to a stable LogID/profile.

### TUF / Sigstore trust distribution

TUF signed metadata uses designated roles, versions and expiry to resist rollback/freeze/mix-and-match attacks. Snapshot metadata creates a consistent view, and clients reject older/expired metadata. Sigstore recommends TUF-backed TrustRoot distribution so verification keys/certificates rotate through an authenticated update mechanism rather than being accepted from the object being verified.

Primary sources:
- https://theupdateframework.io/docs/metadata/
- https://theupdateframework.io/docs/security/
- https://docs.sigstore.dev/policy-controller/overview/

Transferable mechanisms:
1. authenticate trust metadata against a pinned authority;
2. bind evaluation to exact authenticated content identity, not only a mutable generation number;
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

## Authority boundary

A critical audit correction changed the evaluator API. It no longer accepts an arbitrary `SignedSnapshot` plus a matching caller-provided `snapshot_id`. Instead it receives a `TrustLifecycle` and an exact snapshot ID, then resolves the snapshot only from lifecycle history populated by successful authentication/acceptance.

This closes a self-assertion path in the first corrected draft: a caller could construct an unauthenticated snapshot containing attacker-selected operators, compute its own deterministic `snapshot_id`, and pass both directly to evaluation. Exact content identity alone is not authority; the content must also have crossed the authenticated lifecycle boundary.

## Lifecycle rules tested

- only an authenticated and accepted snapshot supplies log/operator authority to evaluation;
- unknown logs cannot self-promote;
- duplicate LogID/operator IDs and unknown operator references are malformed;
- stale version/generation/time and expired snapshots fail closed;
- same version/generation/time with different signed content is substitution and fails closed;
- `LogID` verification profile is immutable across generations;
- operator reassignment requires a new authenticated generation and does not alter old snapshots;
- `RETIRED`/`DISTRUSTED` logs stop contributing to future thresholds and cannot silently reactivate;
- evaluation is pinned to exact accepted `snapshot_id`, not only generation;
- an unaccepted self-asserted snapshot cannot drive compliance evaluation even if the caller knows its content hash.

## Experiment

Corrected command executed locally against the branch-equivalent corrected source:

```bash
python -m unittest discover -s experiments/ctv2_log_trust_lifecycle/tests -p 'test_*.py' -v
```

Observed: **18/18 passed**.

Also executed:

```bash
python -m compileall -q experiments/ctv2_log_trust_lifecycle
```

Observed: completed successfully.

### Unsafe seed

`unsafe_self_asserted_expected_failure.py` models the LAB-046 authority gap: the caller supplies `trusted=True` and arbitrary `operator_id` values. Two claims then satisfy a 2-log/2-operator threshold even though no authenticated trust metadata exists.

Observed unsafe result: expected assertion failure because `unsafe_evaluate(...)` returned `True`.

## Audit findings

The first corrected draft covered rollback/substitution and distrust, but freshness/lifecycle validity were under-specified. Prior audit added expiry, `state_since <= issued_at`, and fail-closed no-reactivation for `RETIRED`/`DISTRUSTED` logs.

This run found a second, more fundamental authority bug: evaluator input could bypass `TrustLifecycle.accept()` entirely by presenting arbitrary content and its own matching hash. The API was changed so evaluation resolves only accepted snapshots from lifecycle history, and a dedicated forged/unaccepted-snapshot regression test was added. The corrected suite increased from 17 to 18 passing tests.

## Integration implications

LAB-046-style compliance evaluation should receive an authenticated trust-lifecycle handle (or an equivalently verified reference store) and an exact accepted snapshot ID, then derive:

- trusted LogIDs;
- verification profiles;
- operator grouping;
- current lifecycle eligibility.

The caller may provide evidence, but it must not provide authoritative trust/operator metadata or arbitrary snapshot objects. Decisions should persist the exact accepted `snapshot_id` used so later distrust/operator changes do not rewrite historical interpretation.

## Non-goals

- no browser/vendor-specific SCT-count threshold;
- no live Chrome component-updater implementation;
- no claim that HMAC equals TUF/Chrome production authentication;
- no online log qualification process;
- no witness/gossip/consensus layer.

## Stop condition

Satisfied after audit correction: LAB-046-style evaluation consumes only exact authenticated/accepted trust metadata and no longer trusts caller-supplied log/operator/snapshot authority.
