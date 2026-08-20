# LAB-045 — CT v2 SCT promise-to-inclusion and MMD conformance

Date: 2026-08-20  
Issue: #86  
Branch: `lab/045-ctv2-sct-promise`

## Question

How can an auditor prove that a CT v2 log's signed promise (SCT) refers to the exact leaf later proven under an authenticated STH, and what evidence is actually sufficient to classify Maximum Merge Delay behavior?

## Primary source

RFC 9162 is authoritative: https://www.rfc-editor.org/rfc/rfc9162.html

Transferable mechanisms:

- §4 says an SCT is the log's promise to append the accepted submission within the configured Maximum Merge Delay (MMD).
- §4.7 defines CT v2 Merkle leaves as the hash of the exact `x509_entry_v2` / `precert_entry_v2` `TransItem` bytes.
- §4.8 defines `x509_sct_v2` / `precert_sct_v2`; its signature is computed over the corresponding entry `TransItem`. SCT timestamp and SCT extensions therefore have to reconstruct the same signed entry data.
- §4.10 authenticates tree heads through `signed_tree_head_v2` and requires the tree-head timestamp to be at least as recent as the most recent SCT timestamp in the tree.
- §8 auditing guidance states that a TLS client can audit an SCT against an STH dated after `SCT timestamp + MMD` by obtaining a Merkle inclusion proof.
- §11.3 lists failure to incorporate an SCT-backed certificate within MMD as log misbehavior.

## Corrected MMD interpretation

The initial issue wording treated "inclusion only observed in an STH after the MMD deadline" as proof of a violation. That is too strong.

A Merkle inclusion proof under a post-deadline STH proves that the leaf is in that tree, but does not identify the exact insertion instant. RFC 9162 expressly describes auditing an SCT against an STH dated after the deadline. Therefore a valid exact inclusion proof under such an STH is evidence of fulfillment for this client-side audit, not evidence of lateness.

Conversely, failure to receive an inclusion proof after the deadline is not a cryptographic non-membership proof. A post-deadline STH alone cannot prove absence.

This experiment therefore emits four states:

- `FULFILLED`: exact SCT→leaf binding plus exact authenticated inclusion, or a complete authenticated tree snapshot containing the leaf;
- `NOT_YET_AUDITABLE`: selected STH predates the deadline and no inclusion is yet proved;
- `INCONCLUSIVE_AFTER_DEADLINE`: deadline passed but no membership or authenticated full-tree absence evidence exists;
- `MMD_VIOLATION`: a complete tree snapshot at/after the deadline reconstructs the authenticated STH root and the exact promised leaf is absent.

The last case is monitor-style evidence, not a compact Merkle non-membership proof (ordinary CT Merkle trees do not provide one).

## Implemented chain

`authenticate_sct_to_exact_leaf()`:

1. strict-decodes SCT v2 `TransItem`;
2. strict-decodes the exact leaf `TransItem` and its timestamp/extensions;
3. binds SCT LogID to the immutable LAB-043 log profile;
4. binds SCT type to leaf type (`x509` vs `precert`);
5. requires exact SCT timestamp and extensions to equal the exact leaf fields;
6. verifies the Ed25519 SCT signature over the exact leaf bytes crossing the verifier boundary.

`audit_sct_promise()` then:

1. authenticates SCT→exact leaf;
2. authenticates the selected STH through LAB-043;
3. if an inclusion proof exists, delegates exact-leaf membership to LAB-044;
4. otherwise applies deadline semantics without inventing non-membership evidence;
5. optionally accepts a complete monitor snapshot only after every leaf strictly parses as a CT v2 entry, leaf count matches STH `tree_size`, and the complete set recomputes the authenticated root.

## Unsafe seed

The unsafe baseline verifies only that some exact leaf is included in an authenticated STH. It never verifies that the presented SCT signed that leaf. A valid SCT for `promised-artifact` can therefore be paired with a valid inclusion proof for `different-artifact` and the unsafe check accepts it.

Observed expected failure:

`AssertionError: True is not false : unsafe inclusion-only check accepted a leaf that the presented SCT never promised`

## Validation

Observed locally before publication:

- initial corrected suite: 17/17 passed;
- audit added independent wrong-root-through-LAB-044 coverage and strict validation of every leaf in complete snapshot evidence;
- corrected suite after audit: 19/19 passed;
- unsafe inclusion-only baseline: expected failure;
- `python -m compileall -q experiments/ctv2_sct_promise`: passed.

## Audit findings

Two conceptual errors were explicitly prevented:

1. **Late STH ≠ late insertion.** A post-deadline authenticated STH containing the exact leaf is not proof of an MMD violation.
2. **Missing proof ≠ proof of absence.** After the deadline, lack of inclusion evidence is `INCONCLUSIVE_AFTER_DEADLINE` unless authenticated complete-tree evidence proves absence.

The implementation audit also strengthened complete-snapshot handling so arbitrary hash preimages cannot masquerade as semantic CT entries; every snapshot element must strictly parse as `x509_entry_v2` or `precert_entry_v2`.

## Non-goals / next gap

This experiment does not evaluate full certificate-chain/SCT compliance or browser policy. The next reusable gap is **SCT presentation/compliance aggregation**: multiple SCTs from multiple logs have per-log MMD/profile/state and should not be collapsed into a single boolean. A future task should model policy over a set of independently authenticated SCT promise audits while keeping log diversity/policy rules explicit and versioned rather than hard-coding browser policy.
