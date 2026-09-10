# Attestation transparency, holdout witness recovery, privacy resolver poisoning, retention idempotency, and ticket-key erasure

Date: 2026-09-10
Status: `ATTESTATION_TRANSPARENCY_HOLDOUT_WITNESS_PRIVACY_POISONING_RETENTION_IDEMPOTENCY_TICKET_ERASURE_V1_FROZEN`
Scope: distinct design/evidence fallback while LAB-086 exact byte-local execution remains transport/materialization-blocked.

## Run observation

The preferred LAB-086 path was probed first. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before any repository code executed with `Could not resolve host: github.com`. GitHub connector reads/writes remained available. No LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed in this run.

## Primary donors

- RFC 9162, Certificate Transparency Version 2.0 — authenticated append-only views, consistency proofs, split-view detection through comparison/gossip: https://www.rfc-editor.org/rfc/rfc9162.html
- NIST SP 800-226 privacy-budget definition — cumulative privacy-loss upper bound: https://csrc.nist.gov/glossary/term/privacy_budget
- NIST SP 800-88 Rev. 2 — cryptographic erase, key hierarchy sanitization, externally managed keys, recovery/validation concerns: https://csrc.nist.gov/pubs/sp/800/88/r2/final
- RFC 9846 (TLS 1.3) — ticket lifetime <= 7 days and recommendation to bound total lifetime of keying material across successive tickets: https://www.rfc-editor.org/info/rfc9846/
- RFC 9325 — secure TLS use; old ticket-encryption keys must be destroyed after their validity period: https://www.rfc-editor.org/rfc/rfc9325.html

## Contract A — domain-attestation issuer transparency and compromise recovery

### A1. Authentic signature is not sufficient provenance

`ATTESTATION_SIGNATURE_VALID != DOMAIN_CLAIM_INDEPENDENT`

A domain-independence claim is admissible only when it is bound to an authenticated issuer/root lineage, subject identity, claim generation, validity interval, and predecessor/successor relation. Cross-signing by issuers that share an operator/root/control plane does not manufacture independent failure domains.

### A2. Compromise windows are monotonic evidence

If an issuer/root is later compromised, every attestation whose validity interval intersects the compromise window becomes `PROVENANCE_UNCERTAIN` unless independently re-established by a non-overlapping trusted lineage. Replacing the issuer key or member ID does not erase the historical uncertainty.

### A3. Successor-root admission must be transparent

Recovery requires a successor attestation root that commits to:
- predecessor root(s),
- known compromise interval,
- affected attestations/member generations,
- revoked/fenced issuers,
- replacement issuer/domain lineage,
- minimum independent-domain threshold.

A successor root cannot silently omit an affected predecessor branch. This borrows the CT idea that signed views are useful only when their consistency/lineage can be checked; a new signed root alone is not proof that history was preserved.

### A4. Revocation is authority removal, not evidence deletion

Revoked issuer/domain attestations stop contributing future voting authority, but their historical signed evidence remains retained for reconciliation and equivocation analysis.

## Contract B — holdout compact-root witness quorum and anti-rollback recovery

### B1. Compact root authenticity is distinct from completeness

`COMPACT_ROOT_AUTHENTIC != DISCLOSURE_HISTORY_COMPLETE`

A compact holdout root must commit deterministically to the complete predecessor disclosure/provenance event range, not merely to the latest exposure count. GC is allowed only after a witness quorum acknowledges the exact compact root and covered predecessor range.

### B2. Witness quorum must preserve independent failure domains

Multiple witness signatures from the same storage/operator/root lineage count as one independence domain for anti-rollback purposes.

### B3. Partial witness loss is recoverable only monotonically

If some witnesses are lost, recovery may install a successor witness set only if it carries forward the maximum authenticated exposure/disclosure floor from every surviving predecessor view plus an `UNKNOWN` floor for unresolved predecessor intervals. Missing witnesses never imply zero exposure.

### B4. Rollback detection precedes reuse

A holdout family remains unusable for fresh confirmation whenever observed compact-root generation is below any previously authenticated generation or when predecessor coverage cannot be proven. Recovery must not relabel the dataset or analyst/controller to obtain a fresh exposure budget.

## Contract C — adversarial privacy identity-resolution poisoning

### C1. Resolver output is untrusted accounting input

`RESOLVER_SAYS_DISTINCT != PRIVACY_SUBJECTS_PROVEN_DISJOINT`

Identity resolution can be poisoned by malicious or faulty linkage features. Administrative IDs, confidence scores, and new resolver versions do not by themselves create independent privacy capacity.

### C2. Spend floors attach to semantic subject equivalence classes

When two scopes may refer to the same subject, cumulative spend/reservations/unknown transfers compose conservatively until disjointness is independently proved. A later resolver split cannot retroactively refund already-accounted privacy loss.

### C3. Merge/split reconciliation is irreversible with respect to known spend

For a merge, successor spend floor >= max(sum of spend that could overlap, any authenticated prior combined floor). For a split, each child inherits enough predecessor history to prevent the predecessor budget from being cloned across children.

### C4. Resolver compromise triggers quarantine, not reset

A compromised resolver generation fences new privacy-budget grants for affected identity domains until a successor resolver plus continuity witness establishes the inherited spend floor. Historical disclosure evidence remains charged/uncertain rather than being discarded.

## Contract D — retention idempotency-token collisions and external side effects

### D1. Token equality is not operation identity

`IDEMPOTENCY_TOKEN_EQUAL != LOGICAL_OPERATION_EQUAL`

A destructive operation identity must bind at least tenant/resource, action, normalized parameters, policy/delegation generation, membership epoch, and operation nonce/digest. A token collision across distinct logical operations is fail-closed.

### D2. External effect may outlive membership/state

If a destructive call may have reached an external system and acknowledgement is lost, membership removal, lease expiry, or coordinator failover does not make blind retry safe. State is `EFFECT_UNKNOWN` until effect-specific reconciliation proves applied/not-applied or predecessor authority is fenced against further execution.

### D3. Partial multi-replica success remains one unresolved operation

Per-replica receipts must be associated with the same canonical operation digest. Reissuing with a different token/digest while any predecessor replica is unresolved is prohibited unless the external API provides a stronger native idempotency key that is itself collision/freshness bound.

### D4. Recovery cannot reinterpret old tokens

Changing token format/version creates a successor namespace; it cannot reinterpret historical ambiguous tokens as fresh operations. Ambiguous historical collisions remain fenced and require explicit reconciliation.

## Contract E — ticket-key erasure attestation, KMS restore, and ancestry floors

### E1. Deletion from active config is not cryptographic erasure

`KEY_REMOVED_FROM_ACTIVE_KMS != KEY_UNRECOVERABLE`

Erasure evidence must cover every recovery-capable key domain: active KMS/HSM, wrapped copies, backups, DR replicas, exported/wrapped descendants, caches/registers/volatile copies when relevant, and external recovery authorities. NIST SP 800-88r2 explicitly requires attention to key hierarchies and recovered/unwrapped copies.

### E2. Erasure attestation itself is rollback-sensitive

An erasure receipt must bind key id/version, key hierarchy, sanitization method/validation result, time/generation, issuer lineage, and covered recovery domains. Restoring an older KMS snapshot that predates the erasure receipt places the region in `RESUMPTION_QUARANTINED` until it proves that the restored material cannot spend retired ticket authority.

### E3. Disaster recovery never lowers ticket ancestry floors

A restored region must load current minimum floors for ticket-key generation, certificate/DC identity generation, PQ/ECH policy generation, revocation generation, backend/service-equivalence generation, and replay-state generation before accepting resumption. If any floor is unknown, allow only the explicitly safer full-auth path; PSK resumption and especially 0-RTT remain disabled.

### E4. Successor tickets cannot reset total ancestry lifetime

TLS 1.3 limits an individual ticket to <= 7 days and warns that issuing successor tickets can otherwise extend the lifetime of initial keying material indefinitely. Runtime policy therefore carries an `ancestry_started_at`/equivalent authenticated floor across re-encryption and successor-ticket issuance and caps total ancestry lifetime independently of each ticket's local lifetime.

### E5. Retirement acknowledgement must survive region churn

Current-region quorum is insufficient if a removed/rejoining region or DR snapshot can still recover an old ticket key. Retirement completes only after all predecessor spend-authority domains are either (a) attested erased/unrecoverable, or (b) cryptographically fenced by a current admission floor that rejects all tickets descending from the retired key generation.

## 40-case RED-first matrix

### Attestation issuer transparency / revocation (8)
1. valid signature from compromised issuer during known compromise window -> reject as independent domain;
2. cross-signed issuers sharing one root/operator -> count one failure domain;
3. successor issuer key with omitted compromised predecessor root -> reject admission;
4. revoked issuer attempts future quorum vote -> reject;
5. revoked issuer's old conflict evidence -> retain and verify;
6. lineage merge hides shared operator behind new member IDs -> independence unchanged;
7. partial compromise interval overlaps attestation validity -> `PROVENANCE_UNCERTAIN`;
8. successor root carries complete predecessor/compromise set and fresh independent domains -> accept.

### Holdout compact-root witnesses (8)
9. signed compact root missing one disclosure event -> reject completeness;
10. two witness keys same operator -> not two independent witnesses;
11. compact root rollback to earlier generation -> quarantine reuse;
12. witness loss with surviving higher exposure floor -> successor inherits higher floor;
13. all witnesses for one interval missing -> carry `UNKNOWN`, not zero;
14. relabeled dataset/controller after rollback -> exposure ancestry unchanged;
15. deterministic predecessor-range proof + quorum -> GC permitted;
16. successor compact root with incomplete predecessor coverage -> reject.

### Privacy identity poisoning (8)
17. poisoned resolver splits one subject into two IDs -> no budget doubling;
18. poisoned resolver merges unrelated subjects -> conservative composition, not silent refund;
19. resolver version rollback -> reject lower spend view;
20. low match confidence but nonzero plausible overlap -> overlap floor retained;
21. later high-confidence split -> no retroactive refund;
22. compromised resolver key -> fence fresh grants;
23. successor resolver + continuity witness -> carry predecessor spend/unknown floors;
24. scope migration across datasets with shared subject lineage -> cumulative accounting preserved.

### Retention idempotency/external effects (8)
25. same token, different resource -> collision fail-closed;
26. same token, same resource, different action/parameters -> collision fail-closed;
27. timeout after possible destructive effect -> `EFFECT_UNKNOWN`;
28. coordinator failover retries unresolved predecessor with new token -> reject;
29. partial replica success + missing receipt -> reconcile/fence before retry;
30. membership removal of executor with possible effect -> does not clear uncertainty;
31. token format rollover with ambiguous predecessor token -> successor namespace cannot reinterpret;
32. canonical digest match + external native idempotency confirmation -> safe convergence.

### Ticket erasure/KMS restore/ancestry (8)
33. active key deleted but backup wrapped copy survives -> retirement incomplete;
34. key sanitized but unwrapped volatile/register copy can persist -> retirement incomplete;
35. erasure receipt exists then KMS snapshot rollback restores old key -> quarantine;
36. DR region rejoins below ticket-key/revocation floor -> reject PSK resumption;
37. full-auth current identity succeeds while replay floor stale -> allow 1-RTT, deny 0-RTT;
38. successor ticket re-encrypted under new key but old ancestry exceeds total lifetime -> reject resumption;
39. removed region cannot prove erasure but admission floor cryptographically rejects retired ancestry -> retirement may complete for spend authority;
40. all recovery domains attested erased/fenced + current floors converged -> resumption authority may be restored.

## Decisions

1. Treat provenance/recovery state as monotonic evidence: replacement identifiers, keys, roots, scopes, witnesses, tokens, and regions cannot erase predecessor uncertainty.
2. Require independent-domain accounting at every quorum boundary; count lineage, not signatures.
3. Make `UNKNOWN` a first-class state for unresolved disclosure/spend/effect/key-recovery windows; never convert absence of evidence into reclaimed authority.
4. For ticket recovery, separate full-auth admission from PSK and 0-RTT admission; recovery may restore them in that order as stronger convergence evidence becomes available.
5. These are RED-first contracts only. They do not substitute for LAB-086 executable proof or for exact RED/GREEN implementation of LAB-093..100.

## Next exact action

LAB-086 remains first priority. Probe once for a supported byte-exact non-model materialization path for executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available: materialize the manifest closure, verify every blob with `git hash-object`, run all real-schema LAB-086 tests, run the unsafe legacy-promotion expected-failure seed separately, run full compileall, then security/reconciliation and branch/main conflict audit. If unavailable again, continue with the next distinct evidence slice: **attestation transparency-log witness equivocation and recovery-root inclusion proofs + reusable-holdout witness compromise threshold changes + privacy resolver poisoning detection/dual-resolver reconciliation + retention external-system receipt authenticity and exactly-once impossibility boundaries + ticket ancestry cutoff after root CA/DC/PQ-policy emergency rotation and cross-region replay-state loss**.
