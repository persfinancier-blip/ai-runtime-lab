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

The supported API keeps two roles separate:

- **publication authority**: only the current root may authorize a never-before-published registry entry;
- **historical verification authority**: an already-published entry must resolve to its exact durable historical authority binding, with no fallback to current authority if that binding is missing or corrupt.

That separation is necessary. Reusing one generic verifier would either make old entries unreadable after key rotation or, worse, let old authority sign new registry successors / let missing history be silently reinterpreted.

## Audit findings fixed before integration

### Durable recovery material, not an ambient object

The first slice stored only a digest of `RecoveryAuthority` while `recover()` still used the caller-owned in-memory object. Although the dataclass is frozen, its `keys` mapping is mutable. The corrected design persists the exact recovery descriptor by content ID and always loads recovery authority from SQL.

### Publication authority is not historical verification authority

Already-published rows are verified against their exact historical root. Never-before-published candidates must still satisfy the current authority at publication time. A standalone lifecycle binding is not equivalent to registry publication.

### Missing historical binding must fail closed

The compatibility adapter initially fell back from `HistoricalAuthorityMissing` to current publication verification. That could hide deletion/corruption of `registry_authorized_entries`, especially before the first root rotation. The supported surface now uses a strict historical-only adapter for inherited read/resume/durable-verification paths.

### Strict historical reads must not break first publication

LAB-075 `reserve()` verifies authority before calling `observe()`. Replacing that verifier with historical-only logic initially made a legitimate first publication impossible. The supported LAB-076 journal now performs the atomic LAB-076 `observe()` first; inherited reserve then sees an exact historical binding. A dedicated regression covers this path.

### Durable verification needs one stable SQLite window

The raw lifecycle verifier makes multiple SQL reads. In autocommit mode a concurrent rotation/recovery could change state between those reads. The supported lifecycle verifier holds a `BEGIN IMMEDIATE` guard while the raw verifier executes, and the cross-layer journal verifier holds the same kind of write-excluding guard while lifecycle + LAB-075 durable checks run. A concurrency regression delays the verifier and proves a competing rotation cannot commit until the audit window exits.

## Atomic integration boundary

`DurableRegistryAuthority` and the transactional broker journal use the same SQLite database. New registry publication executes under one `BEGIN IMMEDIATE` transaction that:

1. reads the exact current authority head;
2. verifies a never-before-published candidate with the current authority;
3. binds the candidate to that exact authority ID/version;
4. verifies LAB-075 registry generation/predecessor continuity;
5. inserts/verifies the exact content-addressed registry row;
6. CAS-advances the registry head.

This makes authority rotation and new registry publication serialize on the same local write boundary. If rotation wins first, an old-signer candidate becomes stale. If publication wins first, it becomes durable historical state and remains verifiable after rotation.

## Failure matrix covered

- ambient/static authority substitution;
- normal rotation below threshold;
- same-generation different authority;
- stale signer after rotation/revocation;
- historical entry verification after rotation;
- missing/corrupt historical authority or historical entry binding;
- restart with wrong recovery authority;
- mutation of caller-owned recovery keys after bootstrap;
- separate break-glass recovery quorum;
- registry publication racing authority rotation;
- pre-authorized-but-unpublished stale entry after rotation;
- confirmed durable receipt after root + registry rotation without adapter re-execution;
- current-root successor of a historical registry head;
- mixed-snapshot durable verification under concurrent rotation;
- strict historical verification without breaking legitimate first publication;
- unsafe caller-controlled key replacement.

## Exact-source evidence

The final executable/test files used in the validation run were reconstructed through the GitHub connector and checked with `git hash-object` against GitHub blob identities. The final executable blobs were unchanged by the documentation-only update that recorded this evidence.

Observed validation:

- LAB-076 protocol + real integration + integration audit + supported audit: **21/21 passed**;
- LAB-075 audited registry regressions: included in the backward-regression run;
- LAB-074 capability-bound journal regressions: included in the backward-regression run;
- LAB-073 sink-capability regressions: included in the backward-regression run;
- LAB-072 transactional broker regressions: included in the backward-regression run;
- combined LAB-075/074/073/072 backward-regression run: **80/80 passed**;
- total corrected tests observed in the final gate: **101/101 passed**;
- LAB-076 unsafe self-swap seed: **failed as expected** because caller-controlled authority replacement is accepted by the deliberately unsafe baseline;
- `python -m compileall -q experiments`: **passed**.

A fresh remote patch audit was then performed with focus on publication-vs-history authority, missing historical bindings, SQLite guard/nested-connection behavior, restart reconstruction, and exact-type supported surfaces.

## Boundary

This model does not detect rollback of an entire internally consistent database snapshot. Whole-store freshness remains delegated to the external monotonic-anchor work from LAB-034–037. It does not create distributed PKI, consensus, service discovery or transport security. Recovery-authority rotation remains owned by LAB-057 rather than being duplicated here.
