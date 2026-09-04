# LAB-092 — bind migration provenance to the retained authority graph

Date: 2026-09-04
Status: source/design contract frozen; exact RED/GREEN pending
Related: #176 LAB-092, #169 LAB-090, #179..#181 LAB-094..096, #182..#184 LAB-097..099, #185 LAB-100

## Question

How must the LAB-092 activation-schema migration certificate compose with the newly frozen construction-bound database/bootstrap/history/activation authority graph so that migration cannot become an authority-rebinding or implementation-upgrade bypass?

## Fresh source observations

On PR #177 (`lab-092-activation-schema-provenance`, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`), migration provenance is currently represented by one deterministic shared-anchor intent:

```text
component_id = provider-generation-activation-schema
intent_id = migration:provider-generation-activation-schema:v1
intent_type = migration
payload = {schema: provider-generation-activation, version: 1}
```

The migration helper `_reservation_surface(path, attested, bootstrap)` reconstructs a partial ledger by directly assigning mutable `path`, `attested`, `provider_history.path`, and `provider_history.bootstrap`. `migrate_activation_schema_v1(path, attested, bootstrap)` classifies local DDL/marker state, installs exact DDL + PREPARED marker atomically, verifies current durable/runtime generation, executes the marker to CONFIRMED, and then constructs the normal ledger.

This was a coherent LAB-092 slice when authored, but its completion intent commits only to schema name/version. It does **not** commit to:

- the canonical logical database identity selected by LAB-094..096;
- the retained bootstrap-root identity;
- the provider-history strategy/protocol identity;
- the LAB-100 activation-authority implementation/version/protocol descriptor;
- the pre-migration authority/provenance state from which this migration is authorized;
- a canonical digest of the exact installed table+trigger definition.

Therefore the current marker can prove that *some* migration intent was externally anchored, but not that the migration belongs to the exact authority graph reconstructed at startup.

## Threat / bypass to freeze

Migration must not become a generic ceremony that blesses a differently bound runtime.

Example schedule:

1. DB A was initialized under canonical database identity A, bootstrap root R1, audited history strategy H1, activation authority F1.
2. An attacker/operator presents the same SQLite bytes through a different supported construction context, or rebinds one of the authority descriptors before migration.
3. Current LAB-092 code can build `_reservation_surface(path, attested, bootstrap)` from caller-supplied values and confirm the deterministic migration marker whose payload contains only schema/version.
4. The same marker identity is therefore not sufficient evidence that R1/A/H1/F1 authorized this schema transition.

The same gap applies to legitimate future activation-authority upgrades: a schema migration must not silently imply that a different implementation/version/protocol is now trusted.

## Frozen decision — migration is an authenticated transition of construction provenance

LAB-092 migration is not a free-standing boolean `migration complete` marker. It is an authenticated transition from one exact retained-authority/provenance state to another.

Define a conceptual canonical certificate/transition:

```text
ActivationSchemaMigrationCertificateV1(
  domain,
  certificate_version,
  logical_database_identity_digest,
  bootstrap_root_digest,
  provider_history_descriptor_digest,
  old_construction_provenance_digest,
  old_activation_authority_descriptor_digest,
  new_activation_authority_descriptor_digest,
  migration_schema_id,
  migration_schema_version,
  activation_table_definition_digest,
  activation_trigger_definition_digest,
  provider_generation_head_digest,
  migration_nonce_or_epoch,
)
```

For a pure LAB-092 v1 schema installation with no authority implementation change:

`old_activation_authority_descriptor_digest == new_activation_authority_descriptor_digest`.

If activation authority implementation/version/protocol changes at the same maintenance boundary, that is additionally a LAB-100 authenticated authority transition and MUST be explicitly linked rather than implied by the schema migration.

## Which fields must be committed

### Construction identity

The certificate must bind the exact LAB-094..096 construction graph used to authorize the migration:

- canonical logical DB identity;
- bootstrap root / bootstrap generation descriptor digest;
- provider-history strategy identity + protocol/schema semantics version.

The certificate verifier consumes these values from the already reconstructed private retained-authority graph. They are not taken from mutable public `path`, `bootstrap`, or `provider_history` aliases.

### Activation authority

The certificate binds the LAB-100 `ActivationAuthorityDescriptor`:

```text
implementation_id
implementation_version
protocol_version
provider_id
provider_generation
provider_verification_key_id
```

A migration certificate issued under F1 does not authorize ordinary restart under F2. Changing F1 -> F2 requires a separately authenticated authority transition with the LAB-100 state-handoff proof.

### Exact schema semantics

Commit to canonical digests of the exact activation table and trigger definitions, not merely `schema=... version=1`.

The canonicalization must be the same serialization-bound/domain-separated family required by the retained LAB-092 redesign and LAB-097..099; no Python/SQLite formatting-dependent hash and no self-hash stored only beside the mutable DDL.

### Provider-generation position

The migration certificate binds the authenticated provider-generation head under which the migration was authorized. This prevents replaying the same certificate across a different generation/authority state.

A future design may authorize migration at a broader explicit epoch, but V1 should choose the smallest exact head binding already available.

## Legacy DB entry rule

A legacy DB may enter the new graph only through an explicit migration constructor/operation whose preconditions are fully verified before mutation.

Required order:

1. Resolve canonical DB identity under LAB-087 broker confinement.
2. Bind/validate the expected bootstrap root and audited provider-history strategy.
3. Classify the DB as legacy-for-LAB-092 **without** interpreting absence as pristine product initialization. LAB-097 initialization provenance remains authoritative.
4. Verify the existing provider-generation chain against the retained bootstrap root.
5. Verify runtime provider/head compatibility.
6. Reconstruct and verify the exact LAB-100 activation authority descriptor/state that will remain authoritative through this migration.
7. Verify there is no incompatible pending authority replacement/activation handoff.
8. Construct the canonical migration certificate from the retained graph + exact schema definitions + current authenticated generation head.
9. Install DDL and reserve PREPARED certificate/intent atomically in SQLite as operational state.
10. Externally authenticate/confirm that exact certificate through the shared-anchor authority.
11. Re-read and verify the exact local DDL and confirmed certificate against the still-bound authority graph.
12. Only then allow ordinary LAB-090 recovery or LAB-093 worker delegation.

Any failure before step 10 must not externally bless a partial migration. Any failure after external confirmation is a recoverable/ambiguous completion state only when the exact certificate and exact DDL can be reverified; it must never permit construction under a different authority graph.

## Restart order after migration

Supported restart for a migrated DB is fail-closed in this order:

1. reconstruct LAB-094..096 retained graph;
2. reconstruct exact registered LAB-100 activation authority;
3. authenticate LAB-097 initialization/construction provenance;
4. authenticate LAB-092 migration certificate against the reconstructed graph and exact DDL;
5. verify provider-generation chain + LAB-097..099 activation-ticket provenance;
6. verify runtime/current-head compatibility;
7. only then reconcile pending activation or mutate provider/SQLite state;
8. only after successful durable verification open LAB-093 endpoints.

This order prevents migration code from being an alternate constructor that selects its own `path/bootstrap/history/activation` authority.

## Migration vs authority upgrade ordering

### Pure schema migration

Use the same activation authority descriptor before and after migration. The migration certificate explicitly proves descriptor equality.

### Authority upgrade before schema migration

First complete and authenticate the LAB-100 authority transition and state handoff. Then issue the LAB-092 migration certificate under the new retained authority descriptor. Restart verifies both transitions in order.

### Schema migration before authority upgrade

First complete LAB-092 under the old descriptor. Then complete a separate LAB-100 authority transition referring to the post-migration construction provenance state.

### Simultaneous operation

If a future maintenance command combines them operationally, durable evidence still contains two domain-separated linked transitions with explicit old/new digests and deterministic ordering. One generic `migration` marker must never authorize both.

## RED-first regression additions

Freeze these before production implementation:

1. valid legacy DB + exact retained graph -> explicit migration succeeds;
2. same DB/DDL but different canonical database identity -> certificate verification fails before recovery/delegation;
3. same DB + rebound bootstrap root -> fail before migration confirmation;
4. same DB + substituted provider-history strategy/version -> fail;
5. same provider head + different unrecorded activation implementation id -> fail;
6. same implementation id + version/protocol drift -> fail;
7. migration marker copied from DB A to DB B -> fail through logical DB identity binding;
8. migration marker replayed at another provider generation -> fail through head binding;
9. table definition changed after confirmation -> fail before provider mutation;
10. trigger definition changed after confirmation -> fail before provider mutation;
11. old deterministic `{schema,version}` marker without bound certificate on an already migrated/new-protocol DB -> migration-required/corruption classification, never silently trusted;
12. interrupted DDL+PREPARED state under exact graph -> explicit migration recovery can continue safely;
13. same interrupted state presented under a different authority graph -> fail, do not reuse PREPARED evidence;
14. external confirmation succeeds, local response lost -> restart accepts only exact certificate + exact DDL + exact retained graph;
15. externally confirmed certificate with missing/mismatched DDL -> fail closed, no reinstall;
16. pure schema migration proves old activation descriptor == new activation descriptor;
17. activation authority upgrade without separate authenticated LAB-100 transition -> migration does not authorize it;
18. legitimate LAB-100 upgrade then LAB-092 migration -> succeeds in explicit order;
19. legitimate LAB-092 migration then LAB-100 upgrade -> succeeds in explicit order;
20. combined maintenance path with swapped transition order/digest linkage -> fail;
21. LAB-097 initialized DB cannot be reclassified as legacy/pristine by deleting migration evidence;
22. LAB-098/099 activation provenance verification remains required after migration;
23. no migration helper constructs authority by assigning public `path/bootstrap/provider_history/attested.provider` aliases;
24. LAB-093 restricted worker cannot invoke migration, authority upgrade, factory/registry, or receive certificate signing/authentication capability.

## Implementation constraint when exact execution returns

Do not patch the current `_MIGRATION_PAYLOAD` alone while continuing to construct `_reservation_surface()` from caller-controlled aliases. The coherent implementation slice is:

1. first introduce/consume the construction-bound retained graph + activation authority descriptor at the migration entrypoint;
2. write the above RED cases against the real PR stack;
3. replace the generic schema/version marker payload with one canonical domain-separated migration certificate digest;
4. ensure DDL classifier and migration recovery verify against that exact certificate;
5. run LAB-090, LAB-092, LAB-097..100 and restricted-worker composition gates.

Production code remains blocked on exact executable RED/GREEN availability.

## Runtime observation

A fresh direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` in this run failed before repository access with `Could not resolve host: github.com`. No exact branch test or behavioral PASS is claimed.

## Verdict

`LAB092_MIGRATION_AUTHORITY_GRAPH_BINDING_FROZEN`

LAB-092 migration provenance is now explicitly subordinate to, and cryptographically bound to, the same construction-time authority graph used by normal restart. Migration cannot be used as an alternate authority constructor or as an implicit LAB-100 implementation upgrade.