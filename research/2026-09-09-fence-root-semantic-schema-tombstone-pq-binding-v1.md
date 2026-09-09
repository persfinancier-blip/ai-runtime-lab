# Fence-floor recovery, semantic verifier migration, schema split-view, tombstone GC, and PQ resumption binding

Date: 2026-09-09
Status: FROZEN DESIGN / RED-FIRST CONTRACT

Contract id: `FENCE_ROOT_SEMANTIC_SCHEMA_TOMBSTONE_PQ_BINDING_V1_FROZEN`

## Scope and run observation

LAB-086 remains priority #1. Direct exact-source execution was re-probed in this run with:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
```

The failure occurred before repository code executed. No new LAB-086 behavioral or compile PASS is claimed.

This note freezes the next distinct evidence slice recorded in `state/CURRENT.md`; it does not substitute for executable RED/GREEN proof.

## Primary donors

1. etcd disaster recovery: restoring a snapshot creates a new logical cluster identity; `--bump-revision` prevents revision decrease and `--mark-compacted` invalidates stale watches/caches after restore.
   - https://etcd.io/docs/v3.7/op-guide/recovery/
2. RFC 8785 JSON Canonicalization Scheme: duplicate object names are forbidden; canonicalization depends on stable I-JSON number/string semantics and preserving Unicode strings as-is.
   - https://www.rfc-editor.org/rfc/rfc8785.html
3. RFC 8949 CBOR: deterministic encodings and decoder behavior are security-relevant; duplicate map keys are a known interoperability/security boundary.
   - https://www.rfc-editor.org/rfc/rfc8949.html
4. RFC 9162 Certificate Transparency v2: signed tree heads plus consistency proofs bind append-only ancestry between historical roots rather than merely accepting a current root.
   - https://www.rfc-editor.org/rfc/rfc9162.html
5. NIST SP 800-88 Rev. 2: sanitization is a program-level completeness claim over target data/media and includes logical/cloud environments and validation of the sanitization result.
   - https://csrc.nist.gov/pubs/sp/800/88/r2/final
6. RFC 9846 / TLS 1.3: resumed sessions remain subject to current handshake context. Clients must validate the new SNI against the original certificate and normally should preserve SNI; 0-RTT acceptance requires the same TLS version, cipher-suite properties, and ALPN protocol associated with the selected PSK. A safer decision can always fall back to a full handshake.
   - https://www.rfc-editor.org/rfc/rfc9846.html
7. RFC 7301 ALPN: ALPN selection is a property of the connection; on resumption the values in the new handshake are authoritative for the new connection.
   - https://www.rfc-editor.org/rfc/rfc7301.html

## 1. Fence-floor authority compromise and recovery

### Boundary

`RESTORED_STORAGE != RESTORED_WRITE_AUTHORITY`

A sink that accepts monotonic fencing generations must not derive its post-restore minimum accepted generation only from a potentially stale restored snapshot. Snapshot integrity proves fidelity to the snapshot; it does not prove freshness relative to writes accepted after that snapshot.

The durable authority model needs two concepts:

- `sink_state_generation`: application/storage state restored from backup;
- `fence_floor_generation`: highest generation that the sink must reject below.

The latter must either survive restore in an independently freshness-protected authority domain or be re-established through an authenticated successor-generation protocol whose predecessor floor is proven.

### Compromise/recovery rule

If the authority storing the fence floor is compromised, recovery creates a successor authority generation. A clean successor cannot retroactively certify that predecessor writes below an unknown/compromised floor were impossible.

`SUCCESSOR_FLOOR_ESTABLISHED != PREDECESSOR_HISTORY_REPAIRED`

Historical intervals whose floor cannot be reconstructed remain degraded evidence.

### RED-first regressions

1. restore pre-fence snapshot after sink accepted a higher fence -> stale owner write must fail;
2. restore both app DB and same-age local fence metadata -> fail closed until independent floor evidence arrives;
3. independent floor store ahead of snapshot -> sink adopts higher floor before consequential writes;
4. compromised floor authority signs lower floor -> rejected by monotonic predecessor lineage;
5. successor authority with correct higher floor -> new writes allowed, predecessor uncertainty retained;
6. authority rollback to valid older signed state -> rejected;
7. restore into new logical cluster identity without predecessor linkage -> no inherited write authority;
8. crash between floor adoption and app-state recovery -> restart must preserve max floor, not minimum observed state.

## 2. Semantic-projection hash migration and verifier-quorum independence

### Boundary

`VERIFIER_A_ACCEPTS && VERIFIER_B_ACCEPTS != SAME_SEMANTICS`

During parser/canonicalizer/hash migration, quorum is meaningful only if independent implementations attest to the same canonical semantic projection. Two verifiers accepting different parsed objects under the same source bytes is divergence, not redundancy.

Each proof generation should bind at least:

- source-format version;
- parser/canonicalizer implementation identity or audited profile;
- canonical semantic projection hash;
- hash algorithm identifier;
- critical-field set/schema generation;
- predecessor proof-generation identifier.

### Migration rule

A hash migration `H1 -> H2` requires an authenticated bridge committing to the same semantic projection under both algorithms during a transition window. Re-hashing bytes under H2 without proving semantic identity does not migrate historical meaning.

`NEW_HASH_MATCHES_BYTES != OLD_SEMANTICS_PRESERVED`

Verifier-quorum independence is counted by distinct parser/canonicalizer/failure domains, not process count. Two processes using the same library/build are one implementation domain for differential-parser assurance.

### RED-first regressions

9. duplicate JSON key accepted differently by two parsers -> fail closed;
10. CBOR duplicate map key first-wins vs last-wins -> fail closed;
11. integer/float coercion changes authority field -> fail closed;
12. Unicode normalization changes projection -> fail closed;
13. H1/H2 dual bridge over same semantic projection -> accepted successor generation;
14. H2 digest computed over different projection -> rejected despite valid signatures;
15. two verifier processes sharing one parser build -> do not count as two independent implementations;
16. independent verifiers disagree on critical-field presence/default -> fail closed and preserve evidence.

## 3. Schema-registry equivocation and split-view

### Boundary

`SIGNED_SCHEMA != UNIQUE_SCHEMA_VIEW`

A signed schema registry can equivocate by presenting two individually valid schema generations for the same `(registry, epoch/version)` to different verifiers. Signature validity alone therefore does not prove a single global security interpretation.

Security-critical schema generations need authenticated append-only lineage with a consistency mechanism or witness/gossip-equivalent cross-view comparison. RFC 9162 is the donor pattern: historical signed heads plus consistency proofs establish ancestry; conflicting signed heads must remain retained as equivocation evidence.

Critical security fields are monotonic semantics: an older verifier that does not understand a newly mandatory field is unsupported for that generation.

`UNKNOWN_CRITICAL_FIELD != OPTIONAL_FIELD`

### RED-first regressions

17. two different signed schemas at same generation -> `SCHEMA_EQUIVOCATION`;
18. verifier A sees branch X, verifier B branch Y -> no quorum green;
19. valid newer schema without predecessor consistency -> reject migration;
20. valid consistency bridge X->X2 -> accept successor;
21. old parser ignores new critical dependency edge -> unsupported, not green;
22. registry root rotation without binding old/new root and current schema head -> reject;
23. later adjudication selects one view -> preserve both conflicting historical signed views;
24. offline verifier missing required schema generation -> fail closed rather than apply nearest-known older schema.

## 4. Tombstone GC witness and backup-discovery completeness

### Boundary

`TOMBSTONE_GCED != REINTRODUCTION_IMPOSSIBLE`

A deletion tombstone may be safely compacted only after proving that every restore/replay-capable domain capable of reintroducing a predecessor object is beyond the tombstone generation or is permanently retired/sanitized under authenticated evidence.

Required copy-domain universe includes, as applicable:

- primary replicas;
- delayed replicas/change streams;
- derived indexes/materialized views/caches;
- queues and retry/dead-letter stores;
- snapshots/backups/archives;
- exports and offline restore media;
- disaster-recovery images;
- search/vector/feature derivatives that can recreate authority-bearing state.

GC witnesses must commit to the exact tombstone generation and the versioned copy-domain universe used for completeness. A source saying `ABSENT` only proves absence in its authenticated scope.

`ALL_RESPONDING_DOMAINS_ABSENT != REQUIRED_DOMAIN_UNIVERSE_COMPLETE`

NIST SP 800-88r2 supports the broader program-level principle: sanitization claims require defined scope and validation, including logical/cloud environments.

### RED-first regressions

25. tombstone GC while an old backup remains restorable -> reject GC;
26. later restore from undiscovered backup -> successor system must retain external tombstone floor and suppress object;
27. all current replicas absent but backup inventory incomplete -> `NEGATIVE_SPACE_UNCOVERED`;
28. backup retired with authenticated sanitization evidence -> may close that domain interval;
29. new backup domain added after prior completeness proof -> successor CopyDomainUniverse generation required;
30. witness quorum all from one backup operator/control plane -> insufficient independence;
31. tombstone and discovery evidence GC together -> historical deletion no longer re-auditable, reject;
32. derived cache can recreate primary object after deletion -> deletion incomplete until derivative is revoked/expired/sanitized.

## 5. PQ/TLS ticket policy with client caching, server identity rollover, and SNI/ALPN rebinding

### Boundary

`TICKET_DECRYPTS != CURRENT_CONNECTION_AUTHORIZED`

A TLS resumption ticket is a credential derived under predecessor connection and policy state. Decryptability or valid PSK binder does not authorize bypassing current identity, application-protocol, or crypto-policy checks.

RFC 9846 requires clients to validate the new SNI against the original certificate and normally preserve the original SNI. TLS 1.3 0-RTT acceptance is stricter: the selected ALPN must match the protocol associated with the PSK; if not, early data is rejected and the connection can fall back to a non-0-RTT handshake. RFC 7301 likewise makes the current connection's ALPN negotiation authoritative.

For a PQ/hybrid deployment this implies:

- cached tickets carry predecessor crypto-policy epoch and original authenticated identity context;
- server identity/certificate rollover is re-evaluated at resumption;
- SNI rebinding across services is not permission to reuse application authorization learned under another service;
- ALPN change invalidates consequential 0-RTT assumptions even when 1-RTT resumption might otherwise be cryptographically possible;
- current PQ/hybrid minimum policy overrides a classical predecessor ticket;
- when authorization context cannot be safely reconstructed/revalidated, perform a fresh full compliant handshake.

### Cross-service rule

`CERT_COVERS_BOTH_NAMES != RESUMPTION_AUTHORITY_SHARED`

A certificate valid for multiple names does not by itself prove that ticket-key custody, application authorization, tenant boundary, ALPN semantics, or PQ policy are shared between those services.

### RED-first regressions

33. client caches classical ticket, server policy upgrades to PQ/hybrid-required -> ticket cannot lower current floor;
34. ticket valid cryptographically after server certificate/identity rollover but new SNI not valid for predecessor certificate context -> reject resumption;
35. certificate covers A and B, ticket from A offered to B without explicit shared resumption authority -> reject/fresh handshake;
36. same ticket offered with different ALPN for 0-RTT -> reject early data;
37. ALPN unchanged but application authorization epoch advanced -> re-evaluate authorization before consequential operation;
38. server ticket-key cluster shared across services but policy authority not shared -> decryptability does not confer cross-service authorization;
39. mixed client/server rollout where client lacks PQ and current server requires PQ -> no ticket fallback below floor;
40. unknown/expired policy metadata for cached ticket -> fail closed for consequential resumption, permit fresh compliant handshake path.

## Frozen invariants

1. `RESTORED_STORAGE != RESTORED_WRITE_AUTHORITY`.
2. `SUCCESSOR_FLOOR_ESTABLISHED != PREDECESSOR_HISTORY_REPAIRED`.
3. `VERIFIER_A_ACCEPTS && VERIFIER_B_ACCEPTS != SAME_SEMANTICS`.
4. `NEW_HASH_MATCHES_BYTES != OLD_SEMANTICS_PRESERVED`.
5. `SIGNED_SCHEMA != UNIQUE_SCHEMA_VIEW`.
6. `UNKNOWN_CRITICAL_FIELD != OPTIONAL_FIELD`.
7. `TOMBSTONE_GCED != REINTRODUCTION_IMPOSSIBLE`.
8. `ALL_RESPONDING_DOMAINS_ABSENT != REQUIRED_DOMAIN_UNIVERSE_COMPLETE`.
9. `TICKET_DECRYPTS != CURRENT_CONNECTION_AUTHORIZED`.
10. `CERT_COVERS_BOTH_NAMES != RESUMPTION_AUTHORITY_SHARED`.

## Implementation order when exact source is executable

1. LAB-086 exact retained gate remains first.
2. Implement RED tests for the frozen contracts before production refactors.
3. Prefer explicit generation/lineage objects over mutable booleans or self-asserted current-state markers.
4. Preserve conflicting predecessor evidence instead of repairing history in place.
5. Count independent failure domains, not object/process copies.
6. For TLS/PQ resumption, route uncertainty to a fresh compliant handshake rather than weakening current policy.
