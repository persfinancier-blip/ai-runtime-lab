# Authenticated Anchor Observations and Provider Identity — LAB-036

Date: 2026-08-19  
Issue: #69 / LAB-036  
Branch: `lab/036-anchor-attestation`

## Question

LAB-035 made monotonic-anchor catch-up safe under crash, UNKNOWN outcome, retries and provider unavailability, but its in-process `anchor.read()` was implicitly trusted. What must a real provider response prove before an anchor position can authorize consequential continuation?

## Primary mechanisms

### RFC 9421 — signed message components + freshness metadata

RFC 9421 HTTP Message Signatures provides a transferable response-authentication pattern: the verifier reconstructs a canonical signature base over explicitly covered components and signature metadata; `keyid` identifies verification material; `created`/`expires` constrain time; and a unique `nonce` can make replay detectable. Its security considerations explicitly warn that signature validity alone does not prevent replay and recommend nonce/timing plus sufficient signed-component coverage.

Transferable rule: an anchor observation must authenticate **provider identity/generation + position + operation kind + request identity + verifier challenge**, not merely the numeric position.

Primary source: https://www.rfc-editor.org/rfc/rfc9421.html

### RFC 9334 RATS — attestation evidence freshness is contextual

The RATS architecture separates attester, verifier, relying party, Evidence and Attestation Results. It discusses nonce-based freshness and, importantly, warns that a nonce by itself does not prove every underlying claim was freshly generated; freshness remains an application/verifier decision with bounded validity semantics.

Transferable rule: a fresh challenge proves that the provider produced a fresh authenticated response to this verifier request. It does **not** magically prove the external monotonic property; monotonicity still comes from the anchor mechanism and LAB-034/LAB-035 consistency rules.

Primary source: https://datatracker.ietf.org/doc/html/rfc9334

### NIST SP 800-63B / nonce guidance — challenge-response replay resistance

NIST defines nonce/challenge mechanisms as replay-resistant when old messages cannot satisfy a newly chosen freshness value. NIST also treats verifier identity binding as a distinct security property.

Transferable rule: challenges must be newly generated for consequential reads/reconciliation; provider identity must be an expected trusted identity rather than self-asserted response data.

Primary sources:
- https://pages.nist.gov/800-63-4/sp800-63b/authenticators/
- https://csrc.nist.gov/glossary/term/nonce

## Protocol contract

A usable anchor observation/receipt is accepted only when all are true:

1. `provider_id` equals the expected configured provider;
2. `generation` equals the current provider/key generation;
3. `challenge` equals the verifier-generated challenge for this exchange;
4. operation `kind` is allowed for the caller state (`READ`, `INCREMENT`, `RECONCILE`);
5. stable `request_id` binds an increment/reconciliation attempt;
6. the MAC/signature validates over every field above plus the anchor `position`;
7. the exact authenticated observation is not replayed inside the verifier consumption window;
8. LAB-035 still checks the authenticated position against DB sequence and one-step catch-up rules.

Authentication, freshness, and monotonicity are separate properties:

- **authentication**: this expected provider/generation vouched for these exact bytes;
- **freshness**: this response is bound to the current verifier challenge and replay policy;
- **monotonicity/rollback protection**: the authenticated position obeys LAB-034/LAB-035 state/anchor invariants.

None substitutes for the others.

## UNKNOWN outcome

The provider uses a stable increment `request_id`. If transport fails after the increment commits, the client does **not** blindly increment again. It asks for reconciliation with a new challenge and the same request identity. The provider returns a freshly authenticated `RECONCILE` receipt for the prior result. The test confirms one provider increment call and one position advance.

This preserves LAB-035's rule: one pending intent, at most one automatic one-step catch-up, and reconcile UNKNOWN before another mutation.

## Failure-injection result

Unsafe baseline: an unauthenticated caller accepts `claimed_position == db_sequence`; a spoofed `7` therefore authorizes continuation. The expected-failure test fails because the forged value is accepted.

Corrected command:

```bash
PYTHONPATH=. python -m unittest discover -s experiments/anchor_attestation/tests -p 'test_protocol.py' -v
```

Observed result: **12/12 passed**.

Covered:

1. current authenticated observation accepted;
2. position tampering rejected;
3. exact replay rejected;
4. wrong provider rejected;
5. stale generation rejected;
6. challenge mismatch rejected;
7. UNKNOWN increment reconciled without duplicate mutation;
8. pre-rotation receipt rejected by new generation;
9. provider unavailability remains `ProviderUnavailable`, not mislabeled rollback;
10. evidence stores a public SHA-256 receipt reference, not signing secret;
11. duplicate stable increment request is idempotent at provider adapter;
12. operation-kind confusion is rejected.

`python -m compileall -q experiments` also passed.

## Audit findings

- HMAC is a deterministic reference mechanism, not a claim that a real TPM/KMS/remote service is configured.
- A signed old observation is not fresh merely because its signature still verifies. The verifier must require its current challenge and current provider generation.
- A nonce proves freshness of the signed exchange, not freshness of all historical state underlying the provider's monotonic counter; the relying protocol still checks position/DB invariants.
- Provider unavailability must be distinguished from authenticated rollback evidence. Fail closed, but do not record a false rollback event.
- Receipt hashes are correlation/evidence identities only; the verifier must retain/resolve the authenticated public receipt fields when re-verification is required.
- The reference keyring is itself a trusted-control input. Secure trust-root distribution/rotation is explicitly outside this issue rather than hidden inside the signed-response mechanism.

## Integration with LAB-033–035

The ordering becomes:

`authenticated launch/watermark state -> DB sequence/pending intent -> fresh authenticated anchor observation -> LAB-035 one-step catch-up/reconcile -> confirmed anchor equality -> consequential continuation`

LAB-036 does not weaken LAB-035. It replaces the implicit trust in `anchor.read()`/increment responses with an explicit provider-identity + generation + challenge verification boundary.

## Non-goals

- no PKI implementation;
- no real TPM/KMS provider claim;
- no distributed consensus;
- no assumption that signed observations create monotonicity;
- no relaxation of anchor equality before consequential continuation.

## Stop-condition assessment

The spoof/replay/provider-generation/UNKNOWN matrix is deterministic and passing. Remaining work is publication, remote patch audit, and integration.
