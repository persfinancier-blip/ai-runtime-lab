# LAB-099 activation reservation precursor authenticator / identity contract

Date: 2026-09-12
Status: source-composed design contract frozen; exact RED/GREEN pending
Related: LAB-090/#169, LAB-097/#182, LAB-099/#184, LAB-100/#185

## Objective

Pin the minimum authenticator and runtime-identity rules for the already-frozen `ytim.provider-activation-reservation.v1` precursor.

The precursor exists because the final LAB-099 V2 transition event must authenticate the exact activation ticket, including provider-assigned `fence`, but `fence` does not exist until `prepare_activation()` mutates provider-owned state. A crash after provider prepare therefore needs independently authenticated local evidence proving that exactly one same-id reservation was authorized before the first provider mutation.

This note does not add production code. Exact repository RED/GREEN remains unavailable in this run because direct git transport failed before repository execution with `Could not resolve host: github.com`.

## Source facts used

1. Current provider-generation history already treats a generation handoff as **dual-authority**: `TransitionProof` authenticates the same transition body with both the old generation key and the new generation key, and verification recomputes both tags from the durable old/new descriptors. A successor does not self-authorize merely by presenting its own key.
2. `AttestedCatchup` contains separate `provider` and `verifier` references and performs no constructor pairing check. Its `authenticated_read()` obtains a live provider observation and asks the verifier to validate provider id, generation, challenge, kind and MAC.
3. PR #175 `rotate_provider()` checks the descriptor derived from the successor verifier before calling provider prepare, but the provider object is separately supplied and `prepare_activation()` is the first provider-side mutation. Prior LAB-100 audit showed that descriptor-only verifier validation therefore does not prove provider/verifier pairing.
4. PR #175 `FencedActivationProvider.prepare_activation()` is deterministic/idempotent for the same `(activation_id, expected_position)` while the exact reservation remains pending/committed, and allocates `fence` only inside the provider mutation.
5. The frozen provenance chain contract requires every security-relevant event to consume the exact current `(logical database identity, epoch, parent link digest)` and rejects siblings/replay after the authenticated head advances.
6. The frozen canonical-byte contract rejects coercion and gives authority records domain-separated exact-byte identities. The precursor must use the same `YTIMPRV1` family; it must not use JSON/string concatenation or a mutable-row self-hash.

## Decision

`PROVIDER_ACTIVATION_RESERVATION_AUTHENTICATOR_IDENTITY_V1_FROZEN`

A reservation precursor is authorization for **one reversible/idempotent same-id call to successor `prepare_activation()` only**. It is not a provider-generation transition, does not advance any authority head, and cannot authorize provider commit/release.

### 1. Canonical precursor identity

Domain:

```text
ytim.provider-activation-reservation.v1
```

Required V1 fields:

```text
1  logical_database_identity_digest       DIGEST32
2  parent_chain_link_digest               DIGEST32
3  parent_chain_epoch                     U64
4  old_generation_id                      UTF8
5  new_generation_id                      UTF8
6  provider_id                            UTF8
7  new_provider_generation                U64
8  new_provider_verification_key_id       UTF8
9  expected_position                      U64
10 activation_id                          UTF8
11 reservation_protocol_version           U64
```

There is deliberately no `fence`: it is not knowable before provider prepare. The final V2 transition event separately commits the exact LAB-099 activation-ticket digest containing the returned fence.

`activation_id` remains deterministic from the intended successor generation plus exact expected position under the LAB-090 contract. V1 adds no random nonce: the authenticated parent/head is the replay namespace, and deterministic same-id retry is required for crash recovery.

### 2. Dual authenticator rule

The exact canonical precursor bytes/digest MUST be authenticated by both:

- the **currently authenticated predecessor provider-generation authority**; and
- the **candidate successor provider-generation authority**.

For the current HMAC prototype this is exactly analogous to `TransitionProof.old_mac` + `TransitionProof.new_mac`: two independent MACs over the same precursor identity, verified with keys resolved from the authenticated old/new generation descriptors.

A precursor carrying only successor authentication is invalid because it would let the successor self-authorize a provider-side reservation. A precursor carrying only predecessor authentication is invalid because it would not prove possession/acceptance by the successor authority that will own the reservation.

Future non-HMAC providers may replace the concrete authenticator mechanism only under a versioned authority protocol; the semantic requirement remains predecessor + successor authentication of the same canonical precursor digest.

### 3. Runtime provider/verifier pairing before mutation

Dual stored authenticators prove authority over the reservation statement but do not prove that the concrete runtime `provider` object paired with `new_attested.verifier` is the successor authority.

Before Tx R is allowed to authorize provider mutation, perform a **side-effect-free successor preflight observation**:

1. require the exact supported `AttestedCatchup`/registered LAB-100 authority surface;
2. require verifier expected identity to equal the candidate successor descriptor `(provider_id, generation)`;
3. issue a fresh challenge/read against the candidate runtime provider;
4. verify the returned observation through that exact successor verifier;
5. require the verified observation identity to equal the successor descriptor used by the precursor;
6. only after this pairing proof and dual precursor authenticator verification may Tx R persist the precursor and `prepare_activation()` be invoked.

This uses the existing source-proved `authenticated_read()` semantics: the provider must produce a fresh response accepted by the verifier for the expected provider id/generation and verification key. Merely comparing Python attributes, class identity, or `new_attested.verifier.expected` is insufficient.

The preflight read is not itself durable authorization. The durable authorization is the dual-authenticated precursor bound to the current provenance parent; the preflight establishes that the live provider object receiving the mutation is the successor authority described by that precursor.

### 4. One-to-one parent/head rule

Tx R may persist a precursor only if all of these still match inside the same `BEGIN IMMEDIATE` transaction:

```text
logical_database_identity_digest == authenticated DB identity
parent_chain_link_digest          == authenticated current chain head
parent_chain_epoch                == authenticated current epoch
old_generation_id                 == authenticated current provider-generation head
expected_position                 == current exact shared-anchor tail
```

The relation MUST be unique for the authenticated parent/head and for `activation_id`. A different precursor for the same `(DB identity, parent link, parent epoch)` is a fork and fails closed; the verifier does not pick latest/rowid/timestamp.

Persisting the precursor does **not** move provider-generation head or provenance-chain head.

### 5. Replay / retirement rules

Before every first or retried provider mutation, re-verify the precursor against the authenticated current parent/head.

Allowed retry:

- current authenticated head is still the precursor parent;
- predecessor/successor authenticators verify over byte-identical precursor bytes;
- successor runtime pairing preflight succeeds;
- same deterministic `activation_id` and `expected_position` are used;
- provider reports the same reservation or accepts the same idempotent prepare.

Rejected before provider mutation:

- provenance head/epoch advanced for any reason;
- provider-generation head no longer equals `old_generation_id`;
- logical DB identity differs;
- any precursor field differs, even if both generation keys remain available;
- only one authenticator verifies;
- successor verifier identity matches but live provider cannot produce a fresh verified observation;
- a second semantically different precursor exists for the same parent;
- an old valid precursor is copied back after a later committed chain head.

Thus retirement is structural: once the authenticated parent/head changes, the old precursor has no mutation authority even if its historical MAC/signature remains cryptographically valid.

### 6. Restart classification

Startup verifies complete retained construction/provenance history before any provider recovery side effect.

For an authenticated precursor whose parent is still current:

- no V2 ticket event and provider status `ABSENT` -> operation can be treated as not externally prepared; same precursor may retry exact prepare;
- no V2 ticket event and provider status `PREPARED` for the exact deterministic id -> recover by obtaining/revalidating the exact ticket and then constructing the V2 event; never invent a fence from SQLite;
- no V2 ticket event and provider status inconsistent/unknown/mismatched -> fail closed;
- provider reservation with no valid precursor -> fail closed, no synthesized authorization;
- precursor whose parent is no longer current but lacks an exact committed descendant -> fail closed as orphaned/ambiguous; do not replay provider mutation under the newer head.

Existing LAB-090 activation rows without this precursor/V2 provenance remain `LEGACY_LAB090_UNATTESTED`; they are not upgraded by hashing their current contents.

## Minimum RED-first matrix

Freeze these before implementation:

1. valid current parent + old authenticator + new authenticator + successful successor preflight -> precursor may persist; provider remains unmutated until after Tx R commit;
2. successor-only authenticated precursor -> reject before provider mutation;
3. predecessor-only authenticated precursor -> reject before provider mutation;
4. old authenticator from non-current predecessor generation -> reject;
5. new authenticator from generation other than `new_generation_id` -> reject;
6. verifier descriptor claims successor but live provider uses another provider id -> fresh preflight fails before prepare;
7. verifier descriptor claims successor but live provider uses another generation/key -> fresh preflight fails before prepare;
8. exact provider object paired with unrelated verifier -> preflight fails before prepare;
9. valid precursor persisted, crash before prepare, restart under unchanged head -> exact same-id prepare allowed;
10. valid precursor persisted, exact prepare happened, crash before V2 event, restart under unchanged head -> exact reservation may be reconciled; no new activation id/fence invented;
11. parent chain head advances after precursor but before first prepare -> old precursor rejected before provider mutation;
12. provider-generation head advances after precursor -> old precursor rejected before mutation;
13. copy valid precursor to another logical DB identity -> reject;
14. mutate expected position or activation id while retaining authenticators -> authenticator failure;
15. create two different precursor rows for one parent/epoch -> startup/operation fails fork, no heuristic winner;
16. byte-identical retry under same parent -> idempotent observation, not a second authorization;
17. old valid precursor restored after later committed V2 transition/head -> reject by parent/epoch/head before provider mutation;
18. provider reports PREPARED but no valid precursor exists -> fail closed without commit/release/reconstruction;
19. legacy LAB-090 activation row is present but precursor/V2 provenance absent -> classify legacy/unattested, never auto-upgrade;
20. historical provenance/ticket verification failure plus a current recoverable activation -> fail before current provider/SQLite recovery side effects (composition with LAB-100 verify-before-recover).

## Implementation seam when exact execution returns

1. Add canonical precursor schema/reference vectors to the shared provenance encoder tests.
2. Add a dual-authenticator record analogous to the current provider-generation `TransitionProof`, but over the precursor digest/domain and current provenance parent.
3. Add the fresh successor provider/verifier preflight before Tx R.
4. Persist precursor + both authenticators in Tx R with parent/activation uniqueness constraints.
5. Re-check authenticated head/tail in Tx R immediately before commit.
6. Only after Tx R commit call exact same-id `prepare_activation()`.
7. Build/freeze the exact activation ticket digest and V2 transition/provenance event from the returned ticket; continue the already-frozen atomic V2 state machine.
8. On startup verify all provenance/precursor authentication before any activation recovery side effect.
9. Execute the minimum RED matrix plus LAB-090, LAB-097..100, LAB-080/081, LAB-087/093 confinement and compileall gates.

Do not implement this precursor as a mutable-row self-hash, a successor-only signature, a runtime attribute comparison, or an unauthenticated recovery hint.
