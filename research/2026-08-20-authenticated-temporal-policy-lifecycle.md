# LAB-049 — Authenticated temporal compliance-policy lifecycle

Date: 2026-08-20  
Issue: #94

## Question

How can a long-lived CT compliance decision be reproduced under the exact policy that governed it while preventing a caller from cherry-picking an older/weaker policy for a new decision?

## Primary-source donors

**TUF metadata lifecycle.** The Update Framework makes signed metadata explicitly versioned and expiring; clients reject rollback and expired metadata, while snapshot/timestamp metadata bind versions/hashes to resist rollback, freeze and mix-and-match. Transfer: policy authority needs monotonic version/generation, expiry/freshness, exact content identity, and durable trusted history. Source: https://theupdateframework.github.io/specification/

**Chromium CT metadata/configuration.** Chromium's CT component separates log/config metadata from policy enforcement. CTLogList carries major/minor version, freshness timestamp and compatibility version; PKI Metadata updates supersede built-in data, and older component data is rejected. Transfer: CT policy/trust configuration is versioned update state, not arbitrary caller input. Sources: https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/certificate_transparency/ and `certificate_transparency.proto` / PKI metadata installer in that tree.

**RFC 5280 validity intervals.** Certificate authority validity is represented by explicit notBefore/notAfter times. This is not a CT threshold policy donor, but reinforces the separation between object identity and time-bounded authority. Source: https://www.rfc-editor.org/rfc/rfc5280

## Protocol

`PolicySnapshot` contains stable `policy_id`, monotonic version/generation, issued/expiry times, effective interval, thresholds/mode, compatible LAB-048 trust-generation range, and canonical SHA-256 content digest. Only externally authenticated snapshots may enter `AuthenticatedPolicyHistory`.

For a new evaluation, `policy_time` selects the authoritative effective policy automatically. The selected policy must be compatible with the exact LAB-048 trust snapshot generation. The decision persists exact policy identity/version/generation/digest/effective interval plus exact trust snapshot identity/version/generation and evidence timing.

Historical replay resolves the exact recorded policy identity/digest and original trust snapshot, then re-evaluates the same evidence. A later policy cannot rewrite that historical result, while the older snapshot cannot govern a new later decision.

## Failure injection and validation

Unsafe baseline: caller directly supplies a weak `Policy(required_logs=1, ...)` after a newer authoritative policy requires two logs/operators. The weak caller-selected policy returns success; the expected-failure test therefore fails.

Corrected local deterministic suite: **13/13 passed**. It covers automatic time selection, no stale downgrade, historical replay, exact identity binding, interval continuity, rollback, digest substitution, future-policy rejection, trust/policy generation compatibility, evidence mutation, metadata expiry, and stable policy lineage. `python -m compileall -q experiments/ctv2_temporal_policy_lifecycle` also passed.

## Audit finding

The first corrected draft enforced version/generation/time monotonicity but did not require stable `policy_id` lineage. A successor could therefore substitute a different policy identity. The audit added a fail-closed lineage check and regression test before publication.

## Boundary / non-goals

- Metadata signature verification remains an upstream admission boundary, as in LAB-047/048.
- This is not Chrome/browser CT threshold policy and not a general policy language.
- Adjacent policy intervals are explicitly non-overlapping; rollout orchestration is out of scope.
- Local tests used an interface-compatible LAB-048 shadow after inspecting the exact remote LAB-048 protocol; remote patch audit remains required before integration.

## Decision

Policy is authority state, not caller preference. New decisions derive policy from authenticated time-indexed history. Historical replay is permitted only by exact recorded identities and is reproducibility behavior, not a downgrade path.
