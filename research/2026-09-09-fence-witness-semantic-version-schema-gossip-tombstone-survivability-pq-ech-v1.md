# External fence witness, semantic-version, schema-gossip, tombstone survivability, and PQ/ECH resumption contract v1

Date: 2026-09-09
Status: FROZEN DESIGN EVIDENCE; exact RED/GREEN execution still required
Contract id: `FENCE_WITNESS_SEMANTIC_SCHEMA_GOSSIP_TOMBSTONE_PQ_ECH_V1_FROZEN`

## Scope

This note continues LAB-093/#178 while LAB-086/#163 remains the executable priority. It does **not** substitute for LAB-086's retained exact-source gate.

The current run re-probed direct source transport with:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
```

and observed failure before repository execution:

```text
Could not resolve host: github.com
```

No new LAB-086 behavioral or compile PASS is claimed.

## Primary-source donors

1. etcd disaster recovery: restored clusters are logically new clusters; revision bump plus `--mark-compacted` prevents revision rollback and invalidates stale watches/caches after restore. <https://etcd.io/docs/v3.7/op-guide/recovery/>
2. RFC 8785 JSON Canonicalization Scheme: cryptographic hashing/signing needs invariant representation; duplicate JSON names are forbidden; Unicode string data is preserved as-is; numeric semantics are constrained to I-JSON/IEEE-754 behavior. <https://www.rfc-editor.org/rfc/rfc8785.html>
3. RFC 9162 Certificate Transparency v2: append-only ancestry is proved with Merkle consistency proofs, but a log can still show inconsistent split views to different clients; independent cross-view observation is therefore a separate assurance requirement. <https://www.rfc-editor.org/rfc/rfc9162.html>
4. NIST SP 800-88 Rev.2: sanitization assurance is program-level, includes logical/cloud storage, validation, and trust in vendor implementations; deletion of one live representation is not proof that all restore-capable representations are gone. <https://csrc.nist.gov/pubs/sp/800/88/r2/final>
5. RFC 9849 TLS Encrypted Client Hello: ECH separates public `ClientHelloOuter` from private `ClientHelloInner`; ECH rejection is not authorization to silently downgrade, and retry configurations require consistency across endpoints. <https://www.rfc-editor.org/rfc/rfc9849.html>
6. RFC 9846 / TLS 1.3: resumption PSKs/tickets carry prior-session state but current connection policy still matters; renewed tickets must not extend predecessor authority without bound. <https://www.rfc-editor.org/rfc/rfc9846/>
7. RFC 8446 TLS 1.3: SNI is explicitly supplied on resumption; clients should retain SNI with the PSK; incompatible PSKs are ignored and a full handshake is used when necessary. <https://www.rfc-editor.org/rfc/rfc8446.html>
8. RFC 9813 operational TLS-PSK guidance: authorization decisions whose inputs changed between initial authentication and resumption must be reevaluated; if safe reevaluation is impossible, perform a full handshake. <https://www.rfc-editor.org/rfc/rfc9813.html>

## Frozen boundary A — external monotonic fence-floor witness quorum

`RESTORED_LOCAL_FLOOR != PROOF_OF_GLOBAL_FLOOR_CONTINUITY`

A sink restored from snapshot cannot safely infer that the restored `highest_fence` is still globally authoritative. The durable authority must include an external monotonic witness generation that cannot roll back with the sink snapshot.

Required model:

- `FenceFloorGeneration = {domain_id, generation, floor, predecessor_digest, witness_set_id, quorum_signature, created_at_epoch}`;
- every accepted mutating request carries a fence `f >= floor` and a generation reference;
- the protected sink rejects any request from a generation older than its highest externally witnessed generation;
- after restore, local state is `RESTORE_GAP_UNKNOWN` until the sink proves either exact continuity or a successor floor greater than every still-live predecessor authority;
- witness quorum counts independent failure/custody domains, not process count;
- witness-set rotation is itself an authenticated successor generation and cannot lower the effective floor.

### Restore-gap reconstruction

A restore is safe only when one of these is proved:

1. exact predecessor checkpoint + consistency to the latest witnessed floor; or
2. a successor generation whose floor is strictly above the maximum predecessor authority and whose creation required an independent recovery quorum.

Absence of older records after restore is not evidence that no larger fence was previously issued.

## Frozen boundary B — canonical semantic projection versioning

`CANONICAL_BYTES_V2 != SEMANTIC_EQUIVALENCE_TO_V1`

Changing parser, canonicalizer, serialization library, schema mapping, Unicode handling, number handling, default application, unknown-field policy, or projection algorithm creates a semantic-version transition even when both versions produce deterministic bytes.

Required model:

- every authenticated object binds `projection_version`, `schema_generation`, and `canonicalizer_id`;
- migration H1 -> H2 signs a bridge over both the predecessor semantic digest and successor semantic digest;
- during a dual-verifier window, both implementations must produce the same normalized **meaning**, not merely accept the same bytes;
- unknown mandatory/critical fields fail closed;
- parser/library retirement does not delete the predecessor verifier specification or its test corpus until the historical verification horizon closes;
- a hash migration cannot be used to erase ambiguity discovered in predecessor semantics.

RFC 8785 is a donor for invariant JSON bytes, not proof that application-level semantic projection is identical across parser/library generations.

## Frozen boundary C — schema-registry witness/gossip and root rollover

`SIGNED_SCHEMA != GLOBALLY_UNIQUE_SCHEMA_VIEW`

A registry can equivocate by signing two individually valid schemas for the same logical generation. Therefore a single signature proves authenticity of one view, not non-equivocation.

Required model:

- schema generations form authenticated append-only lineage;
- each generation has a signed head `{registry_id, epoch, version, schema_digest, predecessor_digest}`;
- independent witnesses retain observed heads and consistency evidence;
- conflicting heads for the same epoch/version are permanent split-view evidence and are never garbage-collected merely because one view later wins adjudication;
- root rollover requires predecessor-root authorization plus successor-root proof, except for a separately precommitted break-glass recovery root;
- a compromised predecessor root marks affected history `ROOT_COMPROMISE_AFFECTED`; successor signatures do not retroactively repair it;
- gossip retention survives normal registry retirement and root rotation.

RFC 9162 is the donor for append-only consistency and the explicit limitation that inconsistent client views require cross-view detection outside a single log's normal proof path.

## Frozen boundary D — tombstone-GC proof survivability after backup-provider retirement

`BACKUP_PROVIDER_RETIRED != RESTORE_PATH_PROVEN_DEAD`

A deletion tombstone may be garbage-collected only after evidence covers the full restore/replay-capable copy-domain universe for the tombstone's lifetime. Provider retirement can remove the live query API while old snapshots, exports, escrow copies, customer-managed replicas, legal holds, or offline archives still exist.

Required deletion proof set:

- immutable copy-domain inventory generation;
- per-domain deletion/sanitization disposition;
- authenticated provider-retirement statement identifying which restore paths became impossible and which remain externally controlled;
- independent witness over the final coverage root;
- retention of enough proof material to verify the GC decision after the original provider/API disappears;
- explicit `UNVERIFIABLE_AFTER_PROVIDER_RETIREMENT` if historical proof depends only on an unavailable provider control plane.

NIST SP 800-88r2 is the donor for program-level sanitization validation and logical/cloud scope. It does not justify treating control-plane disappearance as sanitization evidence.

## Frozen boundary E — TLS/PQ resumption across ECH, virtual hosts, ALPN, and service meshes

`TICKET_DECRYPTS_AT_EDGE != AUTHORITY_FOR_INNER_SERVICE`

With ECH and service meshes, ticket decryption can happen at a shared client-facing edge while authorization belongs to the inner virtual host/backend. A shared ticket key is operational key distribution, not proof that all virtual hosts share the same application authority or crypto-policy floor.

Required current-connection binding:

- ECH acceptance state and `ECHConfig` generation when relevant;
- authenticated `ClientHelloInner` server identity / inner SNI;
- selected ALPN and application protocol policy;
- backend/service identity after mesh routing;
- current certificate/server-identity generation;
- current PQ/hybrid minimum policy epoch;
- ticket issue policy epoch and original authentication class;
- 0-RTT replay/spend authority owner.

Rules:

- ECH rejection/retry is not authority to disable a stricter PQ/hybrid policy;
- a ticket accepted by a shared edge is rejected for application use if the selected inner service would not authorize that predecessor session;
- cross-service ticket-key sharing cannot imply cross-service authorization;
- ALPN change requires current authorization reevaluation; consequential early data is rejected when semantics differ;
- a ticket issued before a PQ/hybrid policy escalation may remain historical evidence but cannot bypass the new floor;
- when safe reevaluation is impossible, fall back to a fresh full compliant handshake rather than weakening policy.

RFC 9849 explicitly separates outer and inner ClientHello semantics and requires secure handling of rejection/retry. RFC 8446 and RFC 9813 support re-evaluating current connection and authorization inputs rather than treating resumption as timeless authority.

## Cross-cutting invariants

1. `AUTHENTIC_PREDECESSOR != CURRENT_AUTHORITY`.
2. `VALID_SIGNATURE != UNIQUE_GLOBAL_VIEW`.
3. `DETERMINISTIC_SERIALIZATION != STABLE_APPLICATION_SEMANTICS`.
4. `RESTORE_SUCCESS != AUTHORITY_CONTINUITY`.
5. `PROVIDER_RETIREMENT != DATA_DESTRUCTION`.
6. `SHARED_TLS_KEY != SHARED_APPLICATION_AUTHORITY`.
7. `ECH_RETRY != CRYPTO_POLICY_DOWNGRADE_PERMISSION`.
8. `HISTORICAL_VERIFIABILITY` must survive ordinary key/root/provider/parser retirement or explicitly degrade instead of silently claiming equivalent assurance.

## RED-first matrix (40 cases)

### Fence witness / restore (1-8)
1. restore snapshot with local floor 40 while external witness remembers 57 -> reject stale floor;
2. restore snapshot and present fence 41 under predecessor generation -> reject;
3. exact checkpoint proves floor 57 -> resume at >=57;
4. successor recovery generation floor 58 with independent quorum -> accept;
5. successor generation floor 50 below witnessed 57 -> reject;
6. two witness processes in one custody domain pretending to be quorum -> reject independence claim;
7. witness-set rollover drops one old witness and lowers floor -> reject;
8. compromised predecessor witness root followed by clean successor -> preserve predecessor degradation marker.

### Semantic projection/versioning (9-16)
9. V1 and V2 accept same JSON but map large integer differently -> divergence fail closed;
10. duplicate JSON property accepted by one parser -> reject object;
11. Unicode normalization applied only by V2 -> semantic mismatch;
12. V2 applies a default that V1 treated absent -> mismatch unless explicit migration rule;
13. unknown critical field ignored by old verifier -> reject downgrade;
14. H2 bridge signs only successor digest -> insufficient migration evidence;
15. H1/H2 bridge binds both semantic digests and schema generations -> accept migration;
16. predecessor canonicalizer retired but historical spec/test corpus retained -> historical verification remains supported.

### Schema gossip/root rollover (17-24)
17. same epoch/version, two valid signatures over different schema digests -> split-view fail closed;
18. witnesses observe identical head -> no equivocation evidence;
19. later winner attempts to delete losing signed head -> reject GC;
20. root rollover lacks predecessor authorization and no precommitted recovery root -> reject;
21. precommitted recovery root performs successor rollover under policy -> accept with recovery marker;
22. compromised old root signs fresh schema after compromise cutoff -> reject current authority;
23. two witnesses share same storage/administrative domain -> do not count as independent quorum;
24. registry retirement without archived heads/consistency proofs -> mark history unverifiable.

### Tombstone GC/provider retirement (25-32)
25. live DB deleted, retired backup provider still has offline export -> no tombstone GC;
26. provider API gone but signed retirement record enumerates surviving customer archive -> no GC;
27. every versioned copy domain covered by independent proof -> GC eligible;
28. new backup domain appeared after original inventory generation -> require successor inventory;
29. provider control plane unavailable and no archived proof -> `UNVERIFIABLE_AFTER_PROVIDER_RETIREMENT`;
30. deletion proof retained only in provider being retired -> insufficient survivability;
31. legal-hold archive remains -> deletion incomplete regardless of primary-key destruction;
32. independent archive retains final coverage root after provider retirement -> historical GC decision remains verifiable.

### TLS/PQ ECH/mesh resumption (33-40)
33. shared edge decrypts ticket, inner SNI maps to different service authority -> reject resumption authorization;
34. ECH retry config changes but current PQ floor unchanged -> retry without weakening floor;
35. ECH rejected and client attempts silent classical fallback below policy -> reject;
36. same ticket key shared by services A/B, ticket issued by A used for B -> require B authorization, default reject;
37. same inner SNI but ALPN changes from idempotent protocol to consequential protocol -> reject 0-RTT / reevaluate resumption;
38. ticket issued under classical-only epoch, server now requires hybrid PQ -> fresh compliant handshake;
39. backend identity rotated while edge still decrypts old ticket -> current backend identity/policy decides, not ticket decryption;
40. authorization metadata unavailable during resumption -> full handshake, not permissive acceptance.

## Audit

No production-code change is justified from this design note alone. Exact RED/GREEN tests must precede implementation. The contracts deliberately separate authenticity, freshness, uniqueness/non-equivocation, semantic equivalence, survivability, and current authorization so one proof cannot be silently reused as evidence for another property.

## Exact next distinct evidence task if LAB-086 remains blocked

Investigate and freeze:

**external witness quorum recovery under witness loss/compromise + semantic projection test-corpus attestation and verifier-build provenance + schema gossip privacy/selective disclosure + deletion-proof legal-hold/retention-policy conflict resolution + PQ/ECH resumption ticket authority during ECH key rotation, backend migration and split client-facing/inner termination.**
