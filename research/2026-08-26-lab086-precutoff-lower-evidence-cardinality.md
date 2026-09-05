# LAB-086 — Pre-cutoff lower-evidence cardinality

## Finding

The LAB-082/LAB-083 durable verifiers are reference-driven: they verify the transition/proof row required by each known provider/root successor. They do not make the reverse statement that every durable lower-layer row is referenced by authenticated history.

At the LAB-086 migration boundary that asymmetry matters. The cutoff claims to verify inherited state before signing a canonical public-only projection and scrubbing HMAC recovery material. An unexplained `asymmetric_provider_transitions` or `provider_rotation_threshold_proofs` row is not represented in the migration projection, yet the current pre-boundary verifier can ignore it.

A focused SQLite counterexample reproduced both cases: the current join/reference walk sees zero controlled transitions while orphan transition/proof rows remain present. Exact set/cardinality comparison detects both.

## Required invariant before cutoff

Before `payload()` or `establish()` may succeed:

1. root successor IDs in normal + recovery transition tables must be disjoint and exactly equal all non-bootstrap root authority IDs;
2. asymmetric provider transition successor IDs must exactly equal all non-bootstrap provider generation IDs;
3. provider threshold-proof keys must exactly equal provider transitions after the threshold-enablement generation.

This check is additional to cryptographic verification. It does not weaken or replace LAB-082/LAB-083 signature verification; it closes the reverse/cardinality side of the history relation at the consequential migration boundary.

## Security/correctness impact

This is primarily durable integrity / fail-closed availability. An invalid orphan row does not by itself obtain authority, but if migration freezes it into post-cutoff state it becomes unexplained durable evidence and may collide with a future successor ID or survive outside the signed migration projection. LAB-086 should reject such state before creating the cutoff.

## Evidence and implementation state

- Real-ledger red regression added as `tests/test_pre_cutoff_lower_evidence_cardinality.py`.
- Minimal runtime patch staged as `research/2026-08-26-lab086-precutoff-lower-evidence-cardinality.patch`.
- Focused SQL diagnostic confirmed the reference-driven loop ignores orphan rows and the proposed exact set comparisons reject them.
- The runtime `migration_guard.py` is intentionally not yet changed in this step; the real-ledger regression must be executed in the exact connector-reconstructed closure before the patch is counted as a fix.
