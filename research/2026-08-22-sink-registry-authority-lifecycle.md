# LAB-076 — Sink-registry authority lifecycle

## Question

How can LAB-075 rotate or recover its registry signing authority without letting a stale/revoked key authorize new sink mappings, while still allowing already-bound historical entries to be verified after restart?

## Donor mechanisms

1. **TUF root update continuity.** TUF root metadata is versioned and persists the trusted root. Updating root N→N+1 requires threshold signatures from keys authorized by both the previously trusted root and the new root. This is the reusable normal-rotation mechanism already implemented in `experiments/anchor_threshold_root/`.
2. **Separate recovery quorum.** The lab's existing threshold-root primitive models break-glass recovery separately from normal rotation. Vault independently demonstrates the operational pattern that recovery-key operations use an explicit recovery threshold rather than ordinary runtime authority.
3. **LAB-075 exact entry binding.** A sink mapping is content-addressed and binds `sink_id`, generation, adapter digest, endpoint, operation profile and predecessor. LAB-076 adds the exact historical authority identity/version that authenticated that entry.

Primary references:
- https://theupdateframework.github.io/specification/v1.0.26/#update-the-root-role
- https://developer.hashicorp.com/vault/docs/concepts/seal#recovery-key

## Protocol decision

Persist an append-only local authority history plus one current head. Normal rotation requires old+new threshold proof; break-glass recovery requires the pinned recovery quorum and advances the authority epoch. Each accepted registry entry is durably bound to an exact authority content ID and authority version.

The API separates:

- `verify_for_publication(entry)`: current authority only;
- `verify_historical_entry(entry_digest)`: exact previously bound authority snapshot.

That separation is necessary. Reusing one generic verifier would either make old entries unreadable after key rotation or, worse, let old authority sign new registry successors.

## Failure matrix covered in the first slice

- ambient/static authority substitution;
- normal rotation below threshold;
- same-generation different authority;
- stale signer after rotation/revocation;
- historical entry verification after rotation;
- missing/corrupt historical authority;
- restart with wrong recovery authority;
- separate break-glass recovery quorum;
- registry publication racing authority rotation;
- unsafe caller-controlled key replacement.

## Boundary

This model does not detect rollback of an entire internally consistent database snapshot. Whole-store freshness remains delegated to the external monotonic-anchor work from LAB-034–037. It also does not create distributed PKI or consensus.

## Next integration step

Wire this lifecycle into the merged LAB-075 `RegistryBoundJournal` supported surface so current registry-head reads use historical verification while new publication uses current-authority verification, then rerun LAB-075/074/073/072 regressions.
