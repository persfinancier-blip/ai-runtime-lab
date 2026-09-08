# Retention-domain attestation, hidden common-control challenge, erasure-coded archive survivability, and long-term omission-proof crypto agility v1

Date: 2026-09-08
Status: FROZEN DESIGN CONTRACT — executable RED/GREEN remains pending
Issue context: LAB-093 / #178; does not supersede LAB-086 exact executable gate
Contract: `RETENTION_DOMAIN_ATTESTATION_CHALLENGE_ERASURE_ARCHIVE_CRYPTO_AGILITY_V1_FROZEN`

## Question

The previous freeze established that `REPLICA_COUNT != INDEPENDENT_DESTRUCTIVE_DOMAIN_COUNT` and that a retention receipt proves a retention fact, not admission existence. This follow-up closes four remaining gaps:

1. who may attest destructive-domain independence when the attester can itself be compromised;
2. what a relying party can and cannot prove by challenging nominally independent stores;
3. whether erasure-coded archival fragments preserve positive exhaustive-prefix omission reproducibility;
4. how archived omission evidence remains verifiable when signatures, hashes, certificates, or keys age, are deprecated, or are later compromised.

## Primary-source donors

1. **RFC 4998 — Evidence Record Syntax (ERS)**, RFC Editor, 2007. Long-term evidence survives algorithm/key ageing through Archive Timestamp renewal and, when the hash tree algorithm becomes weak, Hash-Tree Renewal over the archived data plus prior evidence. It explicitly distinguishes timestamp renewal from hash-tree renewal and requires preservation of verification material.
   - https://www.rfc-editor.org/rfc/rfc4998.html
2. **NIST CSWP 39-upd1 — Considerations for Achieving Crypto Agility: Strategies and Practices**, 2026. Crypto agility is the capability to replace/adapt cryptographic mechanisms while preserving security and ongoing operations.
   - https://doi.org/10.6028/NIST.CSWP.39-upd1
3. **NIST SP 800-131A Rev. 2 — Transitioning the Use of Cryptographic Algorithms and Key Lengths**, 2019. Algorithm/key transitions must be planned; older algorithms may remain needed for verification of previously protected data even after they are no longer allowed for new protection.
   - https://csrc.nist.gov/pubs/sp/800/131/a/r2/final
4. **Tahoe-LAFS immutable-file encoding/configuration**. `k-of-N` erasure coding allows recovery from any `k` shares; ciphertext hashes/Merkle roots verify reconstruction/share integrity. Distinct server count is an availability-placement property, not proof of independent administrative/destructive control.
   - https://tahoe-lafs.org/trac/tahoe-lafs/browser/docs/configuration.rst
   - https://tahoe-lafs.org/trac/tahoe-lafs/browser/docs/specifications/file-encoding.rst

## Frozen boundaries

### 1. Attestation is evidence about control provenance, not a new root of truth

`VALID_DOMAIN_ATTESTATION_SIGNATURE != INDEPENDENT_DESTRUCTIVE_DOMAIN_PROVEN`

A `RetentionDomainAttestationV1` may state observed provenance facts, but an attester must not be able to create independence merely by signing the claim. The relying policy evaluates the claim against independently retained evidence.

Required fields:

- `store_id` and stable logical `retention_domain_id`;
- `attester_lineage`, generation, signing key ID;
- cloud/account/tenant identifiers when available;
- delete-capability principal or role fingerprints;
- KMS/HSM root or key-policy lineage identifiers;
- backup/replication-controller lineage;
- operator/organization/control-domain identifiers;
- software/firmware/control-plane provenance where material;
- upstream storage/provider dependency identifiers;
- evidence references and collection time interval;
- explicit `unknown_fields` rather than silent omission;
- statement digest, signature, transparency receipt(s), and witness policy generation.

No single attester may both define the denominator and self-certify all members as independent.

### 2. Attester compromise is append-only re-appraisal, not history deletion

`ATTESTER_COMPROMISE != HISTORICAL_RECEIPT_ERASURE`

A later compromise of the attestation authority changes current reliance on affected attestations. It does not erase that a signed attestation existed. Re-appraisal records:

`ATTESTED -> COMPROMISE_DISCOVERED -> CURRENT_INDEPENDENCE_REOPENED -> REAPPRAISED`

If the compromise onset is bounded rather than exact, every attestation whose issuance interval overlaps that bound is conservatively affected.

Recovery of the attestation authority follows the previously frozen rule: a threshold-compromised authority cannot establish its own trusted successor without a separately trusted recovery root or new-lineage/out-of-band bootstrap.

### 3. Hidden common control is not fully provable away by a remote challenge

`SUCCESSFUL_STORAGE_CHALLENGE != GOVERNANCE_INDEPENDENCE_PROVEN`

A malicious common operator controlling two nominal stores can answer two independent nonce challenges from one backend. Possession/retrievability probes therefore prove bounded facts such as current access to committed bytes, not absence of shared credentials, accounts, operators, KMS roots, deletion APIs, or common upstream infrastructure.

This is a hard boundary, not an implementation deficiency.

### 4. Challenge protocol detects contradictions and correlated control signals

`RetentionDomainChallengeV1` is still useful as positive evidence and fraud detection.

A challenge binds:

- fresh verifier nonce;
- target logical store/domain;
- object/archive manifest digest;
- pseudo-random requested fragment/block indices derived from the nonce;
- expected content/Merkle commitments;
- deadline and authenticated-time evidence;
- attestation generation and retained-domain registry generation.

A valid response binds the same tuple and returns the requested bytes/proof path plus the responder's authenticated identity.

Challenge classes:

- **independent nonce/data challenge** — detects stores that cannot actually serve their committed material;
- **asymmetric fault injection / recovery drill** — intentionally disables one credential/path and verifies another remains readable without using the disabled authority;
- **credential-separation challenge** — requires proofs/actions under independently scoped principals;
- **KMS lineage challenge** — verifies that decrypt/unwrap capability for one domain is not needed to read another domain's independently recoverable material;
- **network/control-path diversity observation** — supporting evidence only, never sufficient independence proof;
- **simultaneous deadline challenge** — exposes hidden serialization/proxying or correlated outage but cannot prove its absence when responses succeed.

Challenge evidence can positively prove contradiction with a prior attestation, e.g. a supposedly independent archive can only recover when another domain's credential is restored. Successful challenges only increase assurance; they do not prove the negative claim that no hidden common control exists.

### 5. Independence assurance is provenance-vector based

Define `DestructiveDomainAssuranceV1` over separately scored dimensions:

- `account_control`;
- `delete_credential_control`;
- `kms_root_control`;
- `operator_control`;
- `replication_or_backup_control`;
- `upstream_storage_control`;
- `software_firmware_control`;
- `billing_or_org_admin_control` where it can terminate/delete the service;
- `attestation_control`;
- `challenge_path_control`.

The effective independence class is the minimum policy-sufficient combination, not a count of endpoints.

`N_ENDPOINTS / ONE_DELETE_PRINCIPAL = ONE_DESTRUCTIVE_DOMAIN`

Unknown provenance is not treated as independent: `INDEPENDENCE_UNKNOWN`, not `INDEPENDENCE_PROVEN`.

## Erasure-coded archive survivability

### 6. Erasure coding can preserve exhaustive-prefix reproducibility

For canonical prefix bytes `P`, create an immutable `ArchiveReconstructionManifestV1` containing:

- canonical prefix checkpoint and tree root;
- exact byte length and chunking parameters;
- erasure-code algorithm/version and `k,n`;
- per-fragment identity and content commitment;
- whole-prefix canonical content digest(s);
- parser/predicate algorithm identifiers and frozen versions;
- source checkpoint/signature evidence;
- domain placement map by stable logical retention-domain ID;
- manifest signature/transparency receipts and long-term evidence record reference.

If any policy-valid set of `k` fragments reconstructs byte-exact `P` and the reconstructed bytes verify against the independently retained checkpoint/root plus manifest digest, exhaustive-prefix omission verification is semantically equivalent to verification from a whole-copy archive.

`ERASURE_CODED_STORAGE != WEAKER_SEMANTIC_PROOF` **when byte-exact reconstruction and independent commitments verify**.

Tahoe-LAFS is the storage donor: any `k` of `N` shares can reconstruct, while ciphertext hashes/Merkle roots verify integrity of the reconstructed object/share pipeline.

### 7. Erasure coding does not manufacture domain independence

`N_FRAGMENTS != N_INDEPENDENT_DESTRUCTIVE_DOMAINS`

Fragments placed on many endpoints under one destructive principal remain one failure domain. `k-of-n` durability math must therefore be evaluated over destructive domains, not storage-node count.

For omission-proof survivability, policy must require that after any allowed destructive-domain failure set there remain at least `k` retrievable fragments **and** independently retained reconstruction metadata/checkpoint/evidence.

### 8. No single reconstruction root

A system fails the survivability claim if all fragments are distributed but the only copy of any indispensable item remains in one domain, including:

- the reconstruction manifest;
- erasure-code parameters;
- encryption/decryption material required to recover canonical bytes;
- source checkpoint/tree root;
- canonical parser/predicate definition;
- algorithm identifiers;
- signature certificates/revocation evidence;
- archive-timestamp chain.

The archive object and the evidence needed to interpret/verify it have separate survivability denominators.

### 9. Reconstruction is deterministic and proof-producing

A reconstruction attempt emits `ArchiveReconstructionReceiptV1` with:

- fragment IDs and domains actually used;
- fragment commitment checks;
- decoder implementation/version;
- reconstructed whole-prefix digest;
- verification against source checkpoint/root;
- parser/predicate version and exhaustive scan result;
- time/quorum evidence and verifier identity;
- success/failure/unknown status.

A decode success without root/content verification is not admissible positive evidence.

## Long-term cryptographic agility for omission evidence

### 10. Historical evidence must carry an algorithm timeline

`CURRENTLY_DEPRECATED_ALGORITHM != HISTORICAL_EVIDENCE_AUTOMATICALLY_FALSE`

Long-term verification asks whether the evidence was already fixed before the relevant algorithm/key became unsafe, and whether subsequent preservation evidence renewed that fact while still trustworthy. This follows RFC 4998's archive-timestamp-chain model.

### 11. Two different renewal operations are required

Following RFC 4998:

- **signature/timestamp/public-key ageing or TSA key compromise**: renew the timestamp/evidence chain so the older evidence is covered by a new trusted timestamp before the old mechanism ceases to be relied upon;
- **hash-tree/content-commitment algorithm ageing**: mere timestamp renewal is insufficient; access the archived data/evidence, recompute under the new secure hash, and create a new hash-tree/evidence chain while the old binding is still reliable.

Frozen rule:

`SIGNATURE_RENEWAL != HASH_BINDING_RENEWAL`

### 12. ArchiveCryptoPolicyV1 is versioned and non-retroactive

Required policy data:

- algorithm identifiers and parameter sets;
- policy generation and effective interval;
- statuses: `approved_for_new`, `legacy_verify_only`, `deprecated`, `disallowed_for_new`, `compromised_or_broken`;
- earliest known unsafe/compromise interval when applicable;
- required renewal lead time;
- acceptable successor algorithms;
- required independent timestamp/recovery authorities;
- PQ/hybrid migration policy where required.

NIST SP 800-131A is the donor for planned algorithm transitions; NIST CSWP 39-upd1 is the donor for operational crypto-agility as an explicit system capability.

### 13. Dual/multi-algorithm commitments prevent cliff-edge migration

For newly produced archive manifests/evidence, policy may require algorithm suites such as:

`content_digest = {H1, H2}` and/or `evidence_signature = {S1, S2}`

where independence assumptions are documented. During a migration window, at least one suite must remain currently acceptable. Adding a second algorithm after the first is already broken cannot retroactively repair the missing historical binding.

### 14. Renewal must occur before trust is lost

`REHASH_AFTER_HASH_BREAK_WITHOUT_PRIOR_TRUSTED_BINDING != RECOVERY`

If all prior content-binding hashes are already practically forgeable and no independent pre-break evidence fixes the original bytes, rehashing the bytes now only authenticates the bytes currently presented. It cannot prove they are the historical bytes.

Likewise, post-compromise signatures from the compromised lineage cannot by themselves rehabilitate old evidence.

### 15. Algorithm compromise causes scoped current-reliance re-appraisal

Historical receipts remain append-only. Current verdicts transition, for example:

`OMISSION_PROVEN(g7)`
`-> HASH_RISK_DISCOVERED(g8)`
`-> CURRENT_RELIANCE_UNKNOWN_OR_INVALID(g9)`
`-> HASH_TREE_RENEWED_FROM_STILL_TRUSTED_BINDING(g10)`
`-> OMISSION_PROVEN_CURRENTLY_RELIABLE(g11)`

No evidence record is silently rewritten.

## Fraud / contradiction classes

1. attester self-certifies its own exclusive denominator;
2. same attestation generation, different provenance digest;
3. omitted shared delete principal;
4. hidden shared KMS root;
5. hidden shared cloud/account admin;
6. hidden common replication controller;
7. hidden common backup root;
8. hidden common upstream storage provider/control account;
9. successful dual challenge served from one undisclosed backend;
10. challenge nonce replay;
11. cached challenge response outside deadline;
12. domain identity rotation presented as new independence;
13. fragment endpoint rotation presented as new destructive domain;
14. `n` fragments but fewer than `k` surviving destructive domains;
15. enough fragments survive but manifest/checkpoint is lost;
16. decoder returns bytes that fail the source root;
17. decoder/version ambiguity changes canonical bytes;
18. parser/predicate version drift changes semantic absence;
19. old signature algorithm expires without renewal;
20. hash tree algorithm weakens but only timestamp is renewed;
21. rehash occurs after old hash binding is already untrustworthy;
22. post-compromise attester certifies its own recovery lineage;
23. late attester compromise overlaps historical attestations;
24. crypto policy downgrade makes old weak suite newly acceptable;
25. algorithm alias/canonicalization collision;
26. one physical archive is counted multiple times through gateway aliases;
27. erasure fragments are independently addressed but encrypted under one lost key;
28. all evidence-record renewal material is retained by one archive domain;
29. timestamp authority and archive authority share hidden compromise root;
30. challenge verifier and attester are same compromised control domain.

## 48-case RED-first executable matrix

| # | Case | Expected frozen result |
|---|---|---|
| 1 | one signed attestation, no corroborating provenance | `INDEPENDENCE_UNKNOWN` |
| 2 | two endpoints, same delete credential | one destructive domain |
| 3 | two regions, same cloud root account | one destructive domain |
| 4 | distinct accounts, same global operator credential | independence not proven |
| 5 | distinct operators, same KMS root | independence not proven |
| 6 | distinct KMS roots, same destructive backup controller | independence not proven |
| 7 | complete independent vectors from separate attestations | policy may mark independent |
| 8 | required provenance field omitted | fail closed/unknown |
| 9 | same attestation generation, two digests | equivocation conflict |
| 10 | lower attestation generation replay | rollback reject |
| 11 | attester compromise after issuance, outside proven onset | historical receipt retained; unaffected interval may remain usable |
| 12 | attester compromise onset overlaps issuance | current independence reopened |
| 13 | compromised attester self-rotates successor | reject continuity |
| 14 | fresh nonce challenge, correct requested blocks | possession/retrievability evidence only |
| 15 | challenge response replays old nonce | reject |
| 16 | correct bytes after deadline | stale/late response; not fresh proof |
| 17 | two nominal stores answer through same disclosed backend | common-control evidence |
| 18 | two stores answer independently | does not prove absence of hidden common control |
| 19 | disabling A credential makes B unreadable | contradiction: shared destructive/control dependency |
| 20 | disabling A leaves B independently reconstructible | increases assurance only |
| 21 | endpoint/key rotation claimed as new domain | reject denominator inflation |
| 22 | common account discovered late | reopen current survivability |
| 23 | 3-of-10 fragments, 3 valid fragments available | reconstruct candidate bytes |
| 24 | reconstructed bytes match whole-prefix digest/root | archive bytes verified |
| 25 | decode succeeds but root mismatches | reject |
| 26 | 3 fragments all in one destructive domain | no 3-domain survivability claim |
| 27 | >=k fragments across policy-valid domains | reconstructibility satisfied |
| 28 | >=k fragments but reconstruction manifest lost | `CURRENTLY_NONREPRODUCIBLE` |
| 29 | manifest survives but source checkpoint lost | positive omission proof incomplete |
| 30 | checkpoint survives but canonical parser missing | semantic proof incomplete |
| 31 | one fragment corrupt, enough alternatives remain | recover and record failed fragment |
| 32 | n-k+1 destructive-domain losses leave <k | unavailable/unknown, never absence-proven |
| 33 | ciphertext fragments survive but sole decryption key lost | canonical-byte reconstruction unavailable |
| 34 | independent manifest/evidence copies survive archive loss | proof remains reconstructible if >=k fragments remain |
| 35 | old signature still allowed for legacy verification | verify under historical policy, not for new protection |
| 36 | signature/TSA key nearing end of trust | timestamp/evidence renewal required |
| 37 | timestamp renewed before signature algorithm loses trust | chain may preserve evidence |
| 38 | content hash weakens but only timestamp renewed | insufficient; require hash-tree renewal |
| 39 | hash-tree renewal while old hash still trustworthy | migrate binding to new hash |
| 40 | hash-tree renewal after old binding already broken, no independent pre-break anchor | historical identity unproven |
| 41 | dual hash H1/H2, H1 deprecated, H2 still accepted | current verification may continue per policy |
| 42 | dual signatures S1/S2, S1 compromised, S2 independently valid | scoped re-appraisal; S2 may preserve assurance if policy/dependency independence holds |
| 43 | both algorithms share one compromised implementation/key root | no artificial dual-algorithm independence |
| 44 | crypto policy version rollback | reject |
| 45 | late hash compromise predates omission proof | reopen current omission reliance |
| 46 | renewed evidence chain itself only stored in failed domain | long-term proof currently nonreproducible |
| 47 | recovery reconstructs bytes and full evidence chain after archive/operator loss | current reproducibility restored without rewriting history |
| 48 | crash after producing renewal but before durable independent receipt | old evidence remains; new renewal not relied on until independently retained |

## Design decisions

1. `RetentionDomainAttestationV1` is evidence, not denominator sovereignty.
2. Destructive-domain independence is evaluated from a provenance vector and independently retained evidence; endpoint count is never sufficient.
3. Remote challenges can prove possession, liveness, and contradictions, but cannot cryptographically prove the absence of hidden governance/common control.
4. Deliberate asymmetric recovery drills are stronger evidence than passive endpoint diversity because they can positively expose shared credentials/control dependencies.
5. Erasure-coded storage preserves exhaustive-prefix omission semantics only after deterministic byte-exact reconstruction and independent verification against the canonical source commitment.
6. `k-of-n` must be computed over independently destructive domains for the survivability claim; node/share count alone is insufficient.
7. Reconstruction metadata, source checkpoints, parser/predicate definitions, keys, and long-term evidence have their own survivability requirements; fragments alone are not enough.
8. Long-term archived omission evidence uses append-only evidence renewal. Signature/timestamp renewal and content-hash renewal are distinct operations.
9. Crypto transitions are versioned, auditable, and begun before old mechanisms lose trust. Post-break rehashing without a still-trusted prior binding cannot recreate historical authenticity.
10. Late compromise/deprecation reopens current reliance without deleting historical receipts.

## Non-claims

- This contract does not claim that hidden common administrative ownership can be disproven purely cryptographically.
- It does not claim Tahoe-LAFS itself supplies destructive-domain governance independence; it is only a donor for `k-of-n` encoding plus integrity commitments.
- It does not claim RFC 4998 alone decides modern algorithm acceptability; algorithm policy is external/versioned.
- It does not substitute for executable RED/GREEN tests.
- It does not unblock LAB-086 or justify changing PR #165 draft/merge state.

## Exact next research fallback if source execution is still unavailable

**independence-evidence registry lifecycle / destructive-domain membership admission-retirement / challenge scheduler anti-collusion and unpredictability / archive repair without denominator laundering / evidence-renewal authority compromise and PQ/hybrid migration ordering**.

Questions to close next:

- who may add/remove a destructive domain from the trusted denominator and how retirement is prevented from laundering a failed domain;
- how random challenge scheduling remains unpredictable when scheduler/verifier can collude with storage operators;
- how automated erasure-code repair chooses replacement domains without silently collapsing independence;
- how evidence-renewal TSA/authority compromise is handled recursively;
- how PQ/hybrid evidence migration is ordered so a classical signature or hash is not trusted beyond its acceptable window.
