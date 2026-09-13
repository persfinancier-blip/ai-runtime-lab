# LAB-095 — database/history identity RED-intent

Date: 2026-09-13
Issue: #180
Draft PR: #187
Branch: `lab-095-database-identity-red-intent`

## Why this slice exists

LAB-095 was opened because supported shared-anchor/provider-history objects retain mutable public database-path state. Reassigning `ledger.path` or `history.path` after construction can redirect later supported operations to a different SQLite database without repeating the original construction-time durable-history verification.

LAB-099 subsequently made the requirement stronger: a mere private/canonical path fixes runtime rebinding but does not provide a construction-bound logical database/history identity suitable for authenticated provenance.

This slice therefore freezes two separate properties instead of conflating them:

1. **Runtime physical binding** — a constructed supported history/ledger object must not be redirected from DB A to DB B through mutable retained path state. A fresh construction/rebind protocol must be required.
2. **Logical lineage identity** — durable provenance must use a path-independent identity authenticated by the existing external shared-anchor mechanism. It must not be `hash(path)`, a SQLite self-hash, a caller-supplied digest, or a plain UUID stored only inside the same mutable DB.

## Source observations

Current `SharedAnchorLedger.__init__()` assigns `self.path = str(path)` and `_con()` subsequently opens `sqlite3.connect(self.path)`. Current `DurableProviderHistory` does the same independently. `HistoricalSharedAnchorLedger` additionally retains a public `provider_history` object whose locked helpers operate on the ledger's already-open connection.

LAB-092's `_classify(self.path)` is an activation-schema provenance classifier, not a durable provider-history trust verification. A superficially compatible DB B can therefore be selected after construction if public path state is rebound.

LAB-092's completion marker is externally confirmed through the shared-anchor ledger, which demonstrates that the existing system already has the primitive needed to authenticate a new identity marker. However, its current deterministic migration payload is not unique per logical database and therefore is not itself a sufficient database identity.

## Frozen test-only contract

PR #187 adds two test-only files only:

- `experiments/provider_generation_history/tests/lab095_database_identity_reference.py`
- `experiments/provider_generation_history/tests/red_intent_lab095_database_identity.py`

Published Git blobs:

- reference: `9f02ddf64cff5b245cfa7a58e188ff9792b3eb18`
- RED intent: `b1499243e8452daadf97fdb9ff97e29a9ce82e28`

Both exact local authored files passed `py_compile` before publication and their local `git hash-object` values match the published blobs.

The branch intentionally contains no production authority implementation yet.

## Logical identity proposal frozen by the reference

A v1 identity migration intent has stable semantic identity:

- intent id: `migration:logical-database-identity:v1`
- component: `provider-history-logical-database`
- intent type: `migration`
- payload schema/version: `provider-history-logical-database` / `1`
- payload includes a fresh 32-byte nonce and the authenticated bootstrap generation id.

The nonce alone is **not** authority. The logical database identity digest is derived only from the exact externally CONFIRMED shared-anchor row and receipt evidence: payload digest, provider id/generation, shared-anchor position, request id, and receipt binding.

This gives the intended semantics:

- changing a filesystem path does not change logical identity;
- copying a database after identity confirmation preserves the same logical lineage, which is appropriate for backup/restore;
- two independently initialized databases using the same provider bootstrap receive distinct nonces and therefore distinct externally confirmed identities;
- deleting/substituting the identity row is already constrained by contiguous shared-anchor history and receipt verification;
- a caller cannot choose a trusted identity merely by passing a digest to a constructor.

## Parent-chain-link proposal

The reference also freezes deterministic domain-separated links:

- genesis link = hash(`logical_database_identity_digest`, `bootstrap_generation_id`);
- transition link = hash(`logical_database_identity_digest`, previous parent link, exact provider transition proof fields).

This provides LAB-099 with a deterministic `parent_chain_link_digest` prerequisite without pretending that the activation ticket itself is authenticated by LAB-095. LAB-099 must separately bind its authority-relevant activation ticket fields into authenticated handoff/provenance evidence.

## Deliberately unresolved implementation questions

These are not safe to guess in the first RED-intent slice:

- where the fresh nonce is generated and how migration retry/crash semantics retain the same nonce without allowing caller substitution;
- exact ordering between identity PREPARED reservation, external confirmation, and provider-generation/activation migrations;
- how legacy databases are migrated without allowing deletion to masquerade as first installation;
- whether runtime physical binding should use only a private canonical path, a captured file identity (`stat` device/inode), an open connection/capability, or a composition of these;
- how Windows/Unix path and file-replacement semantics affect a file-identity guard;
- exact integration order with LAB-094 bootstrap immutability, LAB-096 provider-history strategy immutability, and LAB-097 deletion provenance.

## Validation and limits

A fresh LAB-086 direct clone probe was performed first in this run and again failed before repository execution with `Could not resolve host: github.com` (exit 128). The connector can read exact source but there is still no supported programmatic connector-to-filesystem byte stream for the complete dependency closure in this runtime.

Therefore no exact repository behavioral RED is claimed for LAB-095 yet. The expected pre-fix failures are visible in source:

- production module `experiments.provider_generation_history.database_identity` does not exist;
- `DurableProviderHistory.path` remains publicly assignable and later consumed by `_con()`.

Do not count the two `py_compile` passes as behavioral execution of the repository stack.

## Next action

LAB-086 remains first on each run. If byte-exact materialization remains unavailable, continue LAB-095 by source-auditing migration/crash ordering and freezing a test-only identity installation/recovery state machine. Only then implement the smallest production identity primitive and private runtime binding, followed by LAB-080/081/090/092 downstream execution when exact materialization is available.
