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

Persist an append-only local authority history plus one current head. Normal rotation requires old+new threshold proof; break-glass recovery requires the pinned recovery quorum and advances the authority epoch. Each published registry entry is durably bound to an exact authority content ID and authority version.

The API separates:

- `verify_for_publication(entry)`: current authority only;
- `verify_historical_entry(entry_digest)`: exact previously bound authority snapshot.

That separation is necessary. Reusing one generic verifier would either make old entries unreadable after key rotation or, worse, let old authority sign new registry successors.

## Audit findings fixed before integration

### Durable recovery material, not an ambient object

The first slice stored only a digest of `RecoveryAuthority` while `recover()` still used the caller-owned in-memory object. Although the dataclass is frozen, its `keys` mapping is mutable. A caller could therefore mutate the recovery key map after bootstrap. The corrected design persists the exact recovery descriptor by content ID and always loads the recovery quorum from SQL for recovery and restart verification.

### Publication authority is not historical verification authority

LAB-075's original single `verify()` call cannot be reused unchanged. After root rotation, a registry head already published under the old root can remain authoritative as an already-authenticated mapping, but the old root must not sign a new successor. The integration therefore verifies already-published rows against their exact historical root and requires current-root verification only when a new registry row is first published.

### Pre-authorized orphan is not a published registry entry

A standalone lifecycle binding created before root rotation is not enough to activate a registry entry after rotation. Historical verification is accepted by the LAB-075 integration only when the corresponding registry row already exists. If the row does not exist, publication must still pass the current authority. A published row with a missing historical binding fails closed instead of being silently re-authorized.

## Atomic integration boundary

`DurableRegistryAuthority` and the transactional broker journal use the same SQLite database. New registry publication executes under one `BEGIN IMMEDIATE` transaction that:

1. reads the exact current authority head;
2. verifies a never-before-published candidate with the current authority;
3. binds the candidate to that exact authority ID/version;
4. verifies LAB-075 registry generation/predecessor continuity;
5. inserts/verifies the exact content-addressed registry row;
6. CAS-advances the registry head.

This makes authority rotation and new registry publication serialize on the same local write boundary. If the authority rotation wins first, an old-signer candidate becomes stale. If publication wins first, it is durably historical and remains verifiable after the subsequent root rotation.

## Failure matrix covered by the current branch

- ambient/static authority substitution;
- normal rotation below threshold;
- same-generation different authority;
- stale signer after rotation/revocation;
- historical entry verification after rotation;
- missing/corrupt historical authority;
- restart with wrong recovery authority;
- mutation of caller-owned recovery keys after bootstrap;
- separate break-glass recovery quorum;
- registry publication racing authority rotation;
- pre-authorized-but-unpublished stale entry after rotation;
- confirmed durable receipt after root + registry rotation without adapter re-execution;
- current-root successor of a historical registry head;
- unsafe caller-controlled key replacement.

## Evidence status

The isolated authority-lifecycle prototype passed its corrected local deterministic suite before publication; after the recovery-material audit fix the suite passed 12/12 and compileall passed. The lifecycle-aware LAB-075 integration and its real-journal regressions are now published in draft PR #144, but this run has not yet produced exact-source execution evidence for the integrated PR head. The PR therefore remains draft.

## Boundary

This model does not detect rollback of an entire internally consistent database snapshot. Whole-store freshness remains delegated to the external monotonic-anchor work from LAB-034–037. It also does not create distributed PKI, consensus, service discovery or transport security. The recovery quorum is pinned here; its own rotation lifecycle already exists separately in LAB-057 rather than being duplicated in this layer.

## Exact next gate

Restore the exact published PR #144 head through the GitHub connector if direct clone remains unavailable, verify executable file blob identities, and run:

- LAB-076 protocol + integration suites;
- LAB-075 supported registry regressions;
- LAB-074 capability-bound journal regressions;
- LAB-073 sink-capability regressions;
- LAB-072 transactional broker regressions;
- unsafe LAB-076 self-swap seed (expected failure);
- compileall for the affected experiment modules.

Then perform a fresh remote patch audit. Only a clean exact-source run plus audit should permit draft→ready→merge.
