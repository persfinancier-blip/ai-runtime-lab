# Sensitive-data taint propagation and egress sink gating

Date: 2026-08-19
Issue: #40 / LAB-021
Branch: `lab/021-egress-taint`

## Question
How can an autonomous agent preserve sensitivity metadata across reads, transformations, fallback routing, and evidence creation while preventing a legitimate outbound action from silently becoming a sensitive-data exfiltration path?

## Primary-source mechanisms compared

### OpenAI — source/sink analysis and outbound restriction
Primary sources:
- https://openai.com/index/designing-agents-to-resist-prompt-injection/
- https://openai.com/safety/prompt-injections/
- https://help.openai.com/en/articles/20001061

Transferable mechanisms: model risk as an untrusted source plus dangerous sink; transmitting sensitive information is itself a dangerous sink; restricting outbound capabilities can break the final exfiltration stage even if malicious content remains present.

### NIST SP 1800-39 — discover, classify, label
Primary source: https://csrc.nist.gov/pubs/sp/1800/39/ipd

Transferable mechanism: discover/identify/classify/label sensitive data so controls can reason over explicit data metadata rather than natural-language guesswork at the sink.

### Google Sensitive Data Protection — labels and explicit de-identification
Primary sources:
- https://docs.cloud.google.com/sensitive-data-protection/docs/create-custom-infotypes-metadata-labels
- https://docs.cloud.google.com/sensitive-data-protection/docs/transformations-reference
- https://docs.cloud.google.com/sensitive-data-protection/docs/concepts-deidentify-storage

Transferable mechanisms: metadata labels participate in detection; de-identification is an explicit configured transformation; transformation metadata can be recorded separately from sensitive content.

## Synthesized policy
- Values carry sensitivity, content identity, and provenance.
- Ordinary transforms inherit maximum input sensitivity.
- Summarization, extraction, routing, fallback, memory insertion, and peer handoff are not declassification.
- Downgrade requires trusted-control declassification authority bound to exact source identity, target sensitivity, rule, and current generation.
- Confidential/secret egress requires trusted-control authorization bound to exact payload identity, destination, purpose, sensitivity ceiling, and current generation.
- Destination/purpose/payload/generation changes invalidate prior approval.
- Evidence stores opaque keyed references and provenance/labels, not secret plaintext.

## Failure injection and corrected results
Unsafe seed drops SECRET taint during transformation; the resulting PUBLIC-labeled value is incorrectly allowed to an untrusted sink. Observed expected failure: `AssertionError: True is not false`.

Corrected suite: **15/15 tests passed**. `python -m compileall -q experiments` passed.

Coverage includes public flow, unauthorized secret egress, derived-data inheritance, explicit trusted declassification, forged/untrusted grant rejection, source-bound declassification, redirect blocking, fallback taint preservation, non-plaintext evidence, payload/destination/purpose-bound disclosure, stale authorization, and authorization-reuse prevention.

## Audit defects fixed before publication
1. Boolean `approved=True` declassification was forgeable by data-plane code; replaced with trusted-control source-bound grant.
2. Structurally valid Authorization did not prove trusted-control origin; issuer enforcement added.
3. Disclosure approval was not payload-bound; exact content identity binding added so another confidential payload cannot reuse it.
4. Evidence initially used raw content SHA-256; keyed HMAC is used for evidence identity to reduce low-entropy dictionary-oracle risk. Production keys require protected storage/rotation.

## Composition
- LAB-007: evidence ledger stores opaque refs/labels/provenance, never secret plaintext.
- LAB-008: fallback may choose only routes satisfying the same sink policy and cannot drop taint.
- LAB-012: missing/stale protected-data approval maps to BLOCK/ESCALATE; capability preference cannot downgrade policy.
- LAB-020: tool/web/peer/model data cannot mint authorization or declassification authority.
- LAB-005: durable side-effect intent should persist opaque payload identity, destination, purpose, policy generation, and grant reference.

## Production implications and limits
Revalidate at the actual sink/commit boundary to prevent TOCTOU; preserve labels/provenance across adapters/handoffs; bind authorization to payload+destination+purpose; model declassification as privileged transformation. This does not solve covert channels, steganography, timing/metadata leakage, semantic reconstruction, incorrect source classification, or model-level prompt injection. It is not enterprise DLP or a general information-flow type system.

## Stop-condition assessment
Three current primary-source mechanism families were compared, one unsafe taint-loss design was falsified, and the corrected required matrix passes deterministically. Ready for remote patch audit/integration.
