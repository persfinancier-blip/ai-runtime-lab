# LAB-011 — Memory contamination, quarantine, and retraction recovery

## Donor mechanisms

1. **OWASP Agentic Security Initiative / ASI06 Memory & Context Poisoning (2026).** Persistent context is explicitly treated as a security-relevant attack surface: poisoned memory can continue influencing future reasoning and tool use after the originating interaction. Transfer: ingestion provenance/trust must be an eligibility gate, not merely a ranking feature.
2. **C2PA 2.4 trust/validation model.** C2PA separates content binding/integrity from trust signals and credential revocation; a valid signed assertion is not itself proof that the assertion is true. Transfer: memory identity/provenance and memory truth/eligibility are separate dimensions; revocation/retraction should preserve historical provenance rather than erase it.
3. **NIST AI 600-1 GenAI Profile (updated 2026).** NIST recommends testing value-chain risks including data poisoning and reassessing risks after retrieval-augmented generation changes. Transfer: persistent/retrieved context requires explicit risk controls and re-evaluation, not implicit trust because it was stored previously.

Primary sources:
- https://genai.owasp.org/2026/05/13/memory-is-a-feature-it-is-also-an-attack-surface/
- https://genai.owasp.org/download/52117/?tmstv=1765059207
- https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

## State model

Memory lifecycle is explicit: `ACTIVE`, `QUARANTINED`, `RETRACTED`, `SUPERSEDED`.

- `QUARANTINED`: syntactically valid memory retained for inspection but excluded from authoritative retrieval pending trust resolution.
- `RETRACTED`: a later evidence reference establishes that a previously accepted memory must no longer influence current decisions; history remains inspectable.
- `SUPERSEDED`: a newer fact replaces an older fact; the old fact remains historical provenance.
- `ACTIVE`: still requires minimum trust eligibility before ranking.

Ranking occurs only **after** eligibility. High similarity cannot promote untrusted/quarantined/retracted/superseded memory into authoritative context.

## Experiment

A naive similarity-only policy intentionally selects a contaminated `FREE` price memory (similarity 0.99) over verified `100` (0.70). The corrected policy first applies lifecycle/trust eligibility and then ranks remaining candidates.

Executed locally with standard-library Python: **7/7 deterministic tests passed** covering all required scenarios: valid retrieval, contamination/quarantine, evidence-backed retraction, supersession with retained history, targeted retraction preserving unrelated facts, high-similarity contamination, and reload persistence.

## Boundary audit

- **Memory eligibility/trust** answers whether a remembered proposition may influence current reasoning.
- **Evidence truth/provenance (LAB-007)** supplies independently inspectable observations/receipts; a memory's `evidence_id` is a reference, not proof by itself.
- **Durable run state (LAB-005)** determines safe execution continuation and side-effect reconciliation; it must not be reconstructed from memory confidence.
- Quarantine is not deletion. Retraction is not rewriting history. Supersession is not evidence that the newer fact is true; the newer fact still needs appropriate trust/evidence.

## Integration implications

Extend LAB-009 typed eligibility with lifecycle status and minimum trust before semantic ranking. Use LAB-007 content/evidence identity for correction/retraction references. Preserve append-only history in production even if the compact prototype serializes current records. Treat external uploads, repository text, peer-agent statements, summaries, and self-reports as non-authoritative until policy/evidence raises trust.

## Non-goals / residual risks

This is not a vector database, prompt-injection detector, truth oracle, identity system, or general policy engine. A malicious memory backed by compromised or colluding evidence can still pass a simple trust threshold; provenance quality and issuer authorization require separate controls. The JSON prototype is deterministic evidence of semantics, not a transactional production store.
