# Durable launch-record integrity and anti-replay conformance

Date: 2026-08-19
Issue: #63 / LAB-033
Branch: `lab/033-launch-record-integrity`

## Question

How can LAB-032 restart records be authenticated and rejected when tampered, substituted, rolled back, or signed under obsolete authority before any fresh pidfd is reacquired?

## Primary-source mechanisms

1. **RFC 2104 HMAC**: a shared-secret MAC provides integrity/authentication of stored bytes; key secrecy and key refresh are part of the security boundary.
2. **RFC 8785 JCS**: cryptographic operations over JSON need an invariant representation; canonicalization removes representation-order/whitespace ambiguity. The prototype uses a deliberately narrower canonical JSON subset with fixed ASCII field names, sorted keys, UTF-8, no floats, and strict duplicate-key rejection.
3. **RFC 9421 replay guidance**: message authentication alone does not prevent replay. Replay resistance requires application freshness context such as nonce/time/covered authority fields. For launch records the equivalent freshness domain is task identity + authority epoch + sandbox/credential/capability generations + monotonic record sequence.

## Protocol

The signed payload binds task identity, PID/starttime/process group, sandbox/credential/capability generations, authority epoch, monotonic record sequence, launch nonce, schema/algorithm, and key ID.

Verification happens before LAB-032 process reacquisition:

`strict parse -> current key check -> MAC verify -> task/authority/generation checks -> replay floor -> LAB-032 fresh pidfd/starttime reconciliation`

Authenticity and liveness remain separate. A correctly authenticated record can still point to a dead process; only LAB-032 can establish current process-instance authority.

## Failure-injection results

Corrected suite: `python -m unittest discover -s experiments/launch_record_integrity/tests -p 'test_*.py' -v`

Observed: **12/12 passed**.

Unsafe seed: `python -m unittest experiments.launch_record_integrity.tests.unsafe_unsigned_expected_failure -v`

Observed: expected failure because unsigned structural trust accepted a forged PID.

Covered cases: valid record; field tamper; cross-task substitution; rollback; key rotation; authority rotation; canonical reformat; duplicate JSON keys; truncated/corrupt JSON; generation drift; no raw key in evidence; unsafe unsigned structural trust.

`python -m compileall -q experiments` also completed successfully.

## Audit findings

- **HMAC does not provide freshness.** Production must persist authority epoch/generation/sequence watermarks in an independently trusted transactional store. A rolled-back record plus rolled-back watermark defeats anti-replay.
- **Key ID is not authority by itself.** The verifier accepts only the currently trusted key ID and current authority epoch in this reference design.
- **Canonicalization is part of the cryptographic boundary.** The prototype avoids general JSON-number and Unicode-key complexity by using a closed schema with ASCII field names and integer/string values. A production interoperable format should adopt a specified canonicalization scheme such as RFC 8785 or deterministic binary encoding.
- **HMAC shared-key reference is not a KMS design.** Production should use protected key storage/KMS/HSM or asymmetric signatures where writer/verifier separation is required.
- **No raw key material is persisted in launch records, evidence, or logs.** `key_id` and record fingerprint are safe identifiers; the secret remains outside durable evidence.
- **Record authentication precedes but never replaces LAB-032 liveness checks.**

## Integration implication

The restart recovery contract should become:

`authenticate durable record -> enforce freshness/authority domain -> acquire fresh pidfd -> bind pidfd target to signed PID/starttime/task/generations -> then allow consequential continuation`.

## Non-goals

No general PKI, KMS, certificate lifecycle, encrypted storage, or replacement for process liveness was built.

## Stop-condition assessment

The required tamper/replay matrix passed, the unsafe structural-trust baseline failed as expected, and the LAB-032 boundary is explicit. LAB-033 is ready for repository audit/integration.
