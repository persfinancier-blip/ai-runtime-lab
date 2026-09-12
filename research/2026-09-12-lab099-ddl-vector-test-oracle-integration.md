# LAB-099 — frozen DDL / authority-vector test-oracle integration

Date: 2026-09-12
Status: test-owned integration complete; repository RED not yet executable in this runtime.
Scope: draft PR #186 only for test code; no production LAB-099 behavior and no fixture mutation plan enabled.

## Capability observation

LAB-086 remained first priority. Exact shell materialization was re-probed with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab`

The command failed before repository code execution with `Could not resolve host: github.com` (exit 128). GitHub connector reads/writes remain available. Therefore this slice makes no LAB-086 behavioral/security/compile PASS claim and no LAB-099 repository RED/GREEN claim.

## Objective

Execute the exact fallback recorded in `state/CURRENT.md`: update only PR #186 test-owned layers now that `LAB099_PRECURSOR_PHYSICAL_RELATION_V1_FROZEN` supplies one exact literal SQLite relation identity and frozen relation-definition digest.

## Changes in draft PR #186

Branch: `lab-099-precursor-cutover-red-intent`
Base: pinned LAB-092 PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`
New head: `4d77115ccc3cffe2c2b320886329422717fb76d9`
Topology at verification: ahead 9 / behind 0; six changed files, all under `experiments/provider_generation_history/tests/`.

### 1. Literal DDL identity oracle

Added `lab099_precursor_relation_reference.py`.

It is side-effect-free and freezes the exact V1 test reference for:

- relation name `provider_activation_reservation_precursors`;
- exact literal DDL selected by the durable physical-relation contract;
- repository normalization rule `" ".join(sql.split())`;
- `SHA256(UTF8(normalized DDL))` = `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`.

It does not open SQLite, install schema, create migration evidence, or import future production LAB-099 code.

### 2. Authority vectors promoted from synthetic schema digest to frozen V1 digest

Updated `lab099_precursor_reference_vectors.py`.

The precursor canonical bytes, precursor digest, and dual predecessor/successor reference HMAC vectors are unchanged. Only the relation-definition digest carried inside PREPARED/CONFIRMED moved from the explicitly synthetic historical test value to the now-frozen V1 physical schema digest.

Because relation-definition digest is itself an authenticated canonical field, byte-exact cutover vectors intentionally changed:

- PREPARED digest: `77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e`;
- CONFIRMED binds that exact PREPARED digest;
- CONFIRMED digest: `caeb7b1cac2ff7b990ca54377fa2bd83b639a0af6e86478760de3ee27d5e6406`.

The old synthetic digest is not silently reinterpreted as the real schema digest; current vectors were explicitly re-frozen.

### 3. Three-layer compatibility boundary

Updated `lab099_schema_vector_compatibility.py` so the compatibility oracle now composes:

1. literal DDL -> frozen relation-definition digest;
2. frozen digest -> PREPARED/CONFIRMED canonical authority vectors;
3. those vector fields -> side-effect-free schema-identity authority verifier.

The module still performs no SQLite mutation and defines no production API.

## Local evidence that was actually executed

In an isolated local directory containing only the changed test-owned files:

- `python3 -m py_compile` passed for the literal-DDL oracle, authority-vector module, and compatibility module;
- `python3 lab099_precursor_relation_reference.py` passed;
- `python3 lab099_precursor_reference_vectors.py` passed;
- `git hash-object` matched the published GitHub blobs exactly:
  - DDL oracle: `41f1fa650fa4554d44710fc1e717090e620e533b`;
  - authority vectors: `d1757fa667b8ab7ce4ea1b6ae27136f594716511`;
  - compatibility module: `b121c77a731d7b2aac0846eaffb18d72bcb4f59e`.

The composed compatibility function itself was not claimed executed because its exact imported schema-oracle module was not byte-exactly materialized into the executor through a supported connector path. This is intentionally narrower evidence than a repository test run.

## Non-claims / retained safety boundary

- No production LAB-099 file changed.
- `lab099_precursor_fixture_adapter.py` remains fail-closed; mutation plans are still disabled.
- No PREPARED/CONFIRMED evidence was fabricated.
- No repository RED/GREEN test execution is claimed.
- No LAB-086 PASS is claimed.
- PR #186 stays draft.

## Next slice

After the mandatory LAB-086 exact-materialization probe, if capability remains unavailable, the next safe LAB-099 step is test-owned only: wire the now-frozen literal V1 DDL into `lab099_precursor_fixture_adapter.py` as explicit mutation-plan input and make the first staged cases executable against a test SQLite database, while keeping production behavior unchanged. Prefer the smallest orphan-DDL and DDL+PREPARED-crash cases first. Do not claim RED until the actual PR #186 test closure is materialized and executed; do not add production behavior before an observable executable RED.
