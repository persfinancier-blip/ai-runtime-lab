# Witness activation-epoch distribution, verifier freshness, and stale-policy cache invalidation v1

Status: `WITNESS_ACTIVATION_EPOCH_DISTRIBUTION_VERIFIER_FRESHNESS_STALE_POLICY_CACHE_INVALIDATION_V1_FROZEN`

Date: 2026-09-07

## Scope

This follow-up closes the relying-verifier side of the witness recovery/anti-cloning contract. The prior contract requires a strictly monotonic `WitnessActivationEpochV1` so a recovered instance at E+1 can fence a stale clone at E. That is insufficient unless relying verifiers learn E+1 through an authenticated anti-rollback channel and can distinguish an old-but-authentic signature from a currently-authoritative signature.

This is a design freeze, not executable proof for LAB-093. Exact RED/GREEN remains required before production integration.

## Primary-source donors

1. TUF specification v1.0.26: trusted metadata versions must not roll backward; expired metadata must not be trusted; timestamp/snapshot/root update rules explicitly detect rollback/freeze attacks and persist trusted versions. Mechanism reused: monotonic trusted metadata + bounded freshness, not cache TTL as authority. Source: https://theupdateframework.github.io/specification/v1.0.26/
2. RFC 6960 OCSP: `thisUpdate` is the most recent time the status is known correct, `nextUpdate` bounds when newer information will be available, and responses past `nextUpdate` should be considered unreliable. Mechanism reused: signed freshness interval distinct from object signature validity. Source: https://www.rfc-editor.org/rfc/rfc6960.html
3. RFC 9162 CT: consistency of views presented to all query sources is a separate property; sharing log responses is required to detect split views. Mechanism reused: anti-rollback publication alone does not eliminate partition/split-view risk. Source: https://www.rfc-editor.org/rfc/rfc9162.html
4. C2SP tlog-witness/tlog-cosignature: witnesses maintain monotonic checkpoint state; witness cosignatures let clients require quorum-observed checkpoints; monitor retrieval should expose recent checkpoints. Mechanism reused: self-contained observed frontier plus independent witnesses. Sources: https://github.com/C2SP/C2SP/blob/main/tlog-witness.md and https://github.com/C2SP/C2SP/blob/main/tlog-cosignature.md

## Core invariants

### 1. Signature validity is not current authority

`VALID_WITNESS_SIGNATURE(E) != CURRENT_WITNESS_AUTHORITY(E)`.

A signature from epoch E remains cryptographically valid after E+1 activates, but it must no longer authorize new relying-party decisions once the verifier has authenticated E+1 or a later epoch.

### 2. Cache TTL is not revocation

HTTP/CDN/application cache expiry controls refetch behavior only. It cannot define when E loses authority. Authority revocation is an authenticated state transition in the publication lineage.

A verifier that has authenticated E+1 MUST reject E immediately even if a cached E policy has hours remaining on its TTL.

### 3. Trusted epoch is monotonic

Each verifier persists:

`TrustedActivationFrontierV1 = (witness_identity, lineage_id, epoch, publication_checkpoint, policy_digest, observed_at, freshness_deadline)`.

The persisted epoch MUST NOT decrease. A response carrying epoch < persisted epoch is `STALE_EPOCH_ROLLBACK` even if every signature is valid.

### 4. Epoch transition publication is authority data

`WitnessActivationEpochPublicationV1` binds at minimum:
- witness identity and authority lineage;
- new epoch E+1;
- predecessor epoch E;
- recovery/rotation authorization digest;
- activation frontier/checkpoint;
- new signing-key/policy digest if changed;
- activation effective sequence/time semantics;
- publication-log checkpoint and required witness quorum;
- freshness/next-refresh bound;
- explicit status of E (`FENCED_FOR_NEW_AUTHORITY`).

It is append-only and anti-rollback protected by the already-frozen oracle/publication witness layer.

### 5. Freshness is positive evidence

Online current-authority verdict requires either:
- a sufficiently fresh authenticated activation publication/checkpoint at epoch >= signature epoch; or
- an application-defined stronger current-status oracle that itself chains to the same monotonic lineage.

Wall-clock age without authenticated `thisUpdate`/`nextUpdate`-style semantics is not freshness evidence.

### 6. Offline verification has a different claim

A self-contained bundle can prove:
- the signature was authority-valid relative to a witnessed historical frontier; and
- no superseding epoch was known within that bundled frontier.

It cannot prove there is no E+1 after disconnection. Therefore offline verdicts distinguish:
- `HISTORICALLY_AUTHORITY_VALID_AT_FRONTIER`;
- `CURRENT_AUTHORITY_VALID` only when the application explicitly accepts a still-live signed freshness interval;
- otherwise `CURRENT_AUTHORITY_UNKNOWN_OFFLINE`.

### 7. Partition is not permission to silently extend authority

If verifier A has authenticated E+1 and verifier B is partitioned with only E, A rejects E. B may continue only while a signed, policy-bounded freshness lease for E is still valid and the operation is permitted under the declared partition policy.

After that bound expires, B becomes `CURRENT_AUTHORITY_UNKNOWN_PARTITIONED` and must fail closed for consequential mutations.

This intentionally allows temporary availability loss rather than undetectable split authority.

### 8. Freshness windows are operation-class policy

Read-only historical verification may tolerate old frontiers. New authority-bearing mutations require the strongest freshness class. Define, at minimum:
- `HISTORICAL_VERIFY`: no current-status claim;
- `LOW_CONSEQUENCE_ONLINE_READ`: bounded stale frontier may be allowed;
- `AUTHORITY_MUTATION`: fresh epoch proof required;
- `RECOVERY/KEY/POLICY_CHANGE`: freshest available quorum-witnessed frontier required, no stale-grace fallback.

### 9. Roll-forward proof survives cache/provider substitution

Epoch/policy objects are content-addressed and versioned. Mutable URL, CDN object, DNS target, or cache key cannot replace an already trusted generation with lower/different content under the same identity/version.

Same `(lineage, epoch)` with different authenticated content is `ACTIVATION_EPOCH_EQUIVOCATION_PROVEN`.

### 10. Recovery completion requires relying-party rejection proof

A recovered witness must not resume normal service merely because E+1 exists. Recovery closure includes probes proving representative verification boundaries reject E after receiving E+1, including stale-cache and replay paths. This is evidence of distribution behavior, not a claim that every disconnected verifier is instantaneously updated.

## Data contracts

### `WitnessActivationEpochPublicationV1`
Canonical epoch transition statement described above.

### `TrustedActivationFrontierV1`
Verifier-persisted monotonic trusted epoch/checkpoint state.

### `ActivationFreshnessProofV1`
Binds publication/checkpoint, `thisUpdate` equivalent, `nextUpdate`/expiry, verifier policy class, and source/quorum evidence.

### `VerifierEpochDecisionV1`
Records signature epoch, trusted epoch, freshness class, publication frontier and one of:
- `ACCEPT_CURRENT`;
- `ACCEPT_HISTORICAL_ONLY`;
- `REJECT_STALE_EPOCH`;
- `UNKNOWN_CURRENT_OFFLINE`;
- `UNKNOWN_CURRENT_PARTITIONED`;
- `REJECT_ROLLBACK`;
- `REJECT_EQUIVOCATION`.

### `EpochDistributionAuditV1`
Samples relying boundaries after activation and proves they reject the predecessor epoch; records unreachable/partitioned boundaries separately instead of fabricating universal propagation.

## Failure/attack semantics

- Cache serves E after verifier persisted E+1 -> reject E; do not wait for TTL.
- Attacker deletes local frontier then serves E -> local-state-loss recovery required; never bootstrap from E as fresh.
- Same epoch, different policy/key digest -> equivocation, fail closed.
- E+1 observed from one untrusted endpoint without required publication quorum -> discovery only, not authority transition.
- Verifier clock moves backward -> cannot extend signed freshness beyond monotonic/local secure-time policy; if safe time cannot be established, current-status verdict becomes unknown.
- Verifier clock jumps forward -> may cause availability failure but must not restore E authority.
- CDN 304/ETag replay -> accepted only if the underlying signed freshness proof remains valid and epoch is not below persisted frontier.
- Network partition beyond freshness deadline -> consequential writes fail closed.
- Offline bundle whose freshness expired -> historical-only verdict.
- Old witness process signs E after E+1 -> cryptographically valid but authority-rejected by E+1-aware verifier; retained as stale-clone/fraud evidence.

## RED-first executable matrix (40 cases)

1. fresh E accepted before transition; 2. E+1 accepted; 3. E rejected immediately after E+1; 4. cached E TTL cannot override E+1; 5. lower epoch rollback rejected; 6. same-epoch different digest rejected; 7. exact duplicate publication idempotent; 8. skipped predecessor without authorized bridge rejected; 9. forged E+1 rejected; 10. E+1 without publication quorum discovery-only.

11. signed freshness before expiry accepted for allowed class; 12. expired freshness rejected/unknown; 13. missing next-update under mutation policy rejected; 14. future `thisUpdate` beyond clock policy rejected; 15. backward clock cannot extend E; 16. forward clock cannot restore E; 17. stale CDN 200 rejected; 18. stale 304 rejected; 19. DNS/provider substitution cannot lower epoch; 20. local frontier persistence survives restart.

21. deleted local frontier triggers recovery, not TOFU; 22. corrupt frontier triggers recovery; 23. offline valid bundle yields historical-only after freshness expiry; 24. offline bundle inside explicitly accepted freshness window can satisfy only its declared operation class; 25. offline bundle cannot claim absence of later epoch indefinitely; 26. partitioned E verifier works only inside signed grace when policy allows; 27. partition beyond grace blocks authority mutation; 28. E+1 side rejects E during partition; 29. reconnect advances partitioned verifier monotonically; 30. reconnect cannot roll E+1 side backward.

31. stale clone E signature rejected by E+1-aware verifier; 32. stale clone signature retained as evidence; 33. recovery closure audit detects boundary still accepting E; 34. unreachable boundary is recorded unknown, not PASS; 35. historical read policy differs from mutation freshness policy; 36. recovery/key-change path has no stale grace; 37. same lineage/new epoch binds exact predecessor authorization; 38. new lineage cannot masquerade as epoch increment; 39. publication-log fork blocks current-authority verdict; 40. verifier decision receipt records exact frontier/freshness inputs for audit replay.

## Security conclusion

Activation fencing is only end-to-end when the authority generation is enforced at the relying boundary. A recovered witness at E+1 does not neutralize a stale clone at E merely by changing server-side state or cache entries. Every consequential verifier must carry a monotonic trusted activation frontier and require authenticated freshness appropriate to the operation.

The safe partition rule is deliberately asymmetric: once any verifier knows E+1 it never accepts E again; verifiers that do not yet know E+1 may use E only within an explicitly signed bounded-staleness allowance. After that, current authority becomes unknown and consequential operations fail closed. This converts propagation lag into visible bounded unavailability instead of silent split authority.

## Implementation dependency

When LAB-093 reaches executable work, compose this contract with the frozen publication anti-equivocation, witness key lifecycle, recovery quorum/anti-cloning, archive/historical trust, and LAB-087 isolation contracts. Add tests first. No design freeze substitutes for exact branch-local execution.
