# LAB-099 independent authority reference vectors

Date: 2026-09-12
Status: test-only reference-vector slice staged; repository RED/GREEN still pending
Related: LAB-099/#184, PR #186, LAB-092/#176

## Objective

Advance the recorded LAB-099 fallback without inventing precursor SQL or production behavior. The exact DDL remains intentionally implementation-gated, but three authority-object byte schemas are already frozen and can be given independent test vectors now:

1. `ytim.provider-activation-reservation.v1` precursor identity;
2. `ytim.lab099.activation-reservation-precursor-cutover-prepared.v1`;
3. `ytim.lab099.activation-reservation-precursor-cutover-confirmed.v1`.

The vectors are deliberately independent from future production provenance code so later RED/GREEN can detect encoder drift instead of reproducing it.

## Source audit

The canonical provenance contract fixes `YTIMPRV1`, u16be domain length, domain bytes, u16be field count, ordered fields encoded as `(u16be field id, u8 type, u32be length, value)`, strict UTF-8, exact U64 big-endian encoding, exact DIGEST32, and SHA-256 over the complete domain-separated envelope.

The precursor authenticator contract fixes eleven precursor fields and requires predecessor + successor authority over the same canonical precursor identity. The current provider-history prototype authenticates a canonical transition body directly with two distinct HMAC keys; the staged vectors therefore include HMAC-SHA256 prototype reference tags over the same precursor canonical bytes. They are test vectors, not a commitment to a future production signing primitive.

The one-way cutover contract fixes the PREPARED and CONFIRMED domains and fields. CONFIRMED field 2 is the exact PREPARED digest, so a sibling PREPARED cannot satisfy the reference vector.

## Staged file

PR #186 now contains:

`experiments/provider_generation_history/tests/lab099_precursor_reference_vectors.py`

Branch commit: `96f0b9c9fa28142e1379e2a1c0932c808d4941d3`.

It imports only Python standard-library `hashlib`, `hmac`, and `struct`; it does not import production provenance code.

Reference digests:

- precursor: `499482ff043df31ef3f6ba56b5acf3d51bf7359ccf5aa2089435d443dc88c943`;
- PREPARED: `322ed4112534f6e159f70800d5e5eca2c2e71dec24cbdeca1f6865a4976009d7`;
- CONFIRMED: `d9032ca982484ab8db66fb7f0a68fcdde381dffaa3c031b2520b2170805a9620`.

Prototype dual-HMAC vectors over the same precursor canonical bytes:

- predecessor: `4017c0b29e154d048180379da7c49b74f16be4f101ffd1da4e835282f04d3a3d`;
- successor: `62a99592f44dd9ca3493b61782de8b82206e0619226b23a6ca0913742cd1ec65`.

## DDL boundary retained

PREPARED contains a `precursor_relation_definition_digest`, but the exact precursor SQL spelling is not frozen yet. The reference module therefore uses a visibly synthetic fixed 32-byte value only to exercise the already-frozen DIGEST32 field. It explicitly states that this value does not freeze, imply, or identify any SQL/DDL.

The existing `lab099_precursor_fixture_adapter.py` expects a separate `lab099_precursor_fixture_vectors` module with exact relation name, SQL, and mutation plans. This run intentionally did **not** create that module, so SQL mutation remains fail-closed.

## Validation actually performed

Before publication, an independent standard-library encoder in the execution runtime reconstructed the three envelopes and recomputed all three SHA-256 digests plus the two prototype HMAC vectors successfully. The committed repository snapshot itself was **not executed**: direct git materialization again failed before repository code execution with `Could not resolve host: github.com`.

Therefore this run claims source-audited/reference arithmetic consistency only, not repository RED/GREEN, compileall, or behavioral PASS.

## Topology

Against pinned LAB-092 PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, PR #186 is now ahead 4 / behind 0 with exactly three changed files, all under `experiments/provider_generation_history/tests/`. PR remains open, draft, and mergeable.

## Next engineering seam

Do not write production LAB-099 code yet. Once exact execution or a legitimate exact DDL contract becomes available, the next smallest slice is:

1. freeze the exact precursor relation DDL identity and independent mutation plans;
2. wire the existing adapter to those independent fixture vectors;
3. make the RED-intent file discoverable/executable only after the fixture contract is complete;
4. observe the six cutover cases RED against the real LAB-092/LAB-090 stack;
5. only then implement the smallest production behavior required to turn them GREEN.

Verdict: `LAB099_INDEPENDENT_AUTHORITY_REFERENCE_VECTORS_V1_FROZEN`.
