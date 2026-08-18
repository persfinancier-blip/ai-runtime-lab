# Human/Agent Escalation Policy

Date: 2026-08-18  
Issue: #22 / LAB-012  
Branch: `lab/012-escalation-policy`

## Question

When should an autonomous agent proceed, use a safe fallback, gather more evidence, escalate to a human, or block entirely?

## Donor mechanisms

### OpenAI agent-building guidance
Primary source: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

Transferable mechanisms:
- human intervention is appropriate after repeated failure thresholds;
- high-risk, sensitive, irreversible, or high-stakes actions warrant human oversight;
- ordinary agent work should continue autonomously behind guardrails rather than escalate by default.

### NIST AI RMF
Primary source: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/

Transferable mechanisms:
- human-oversight processes should be defined, assessed, and documented;
- oversight and controls should be proportional to mapped risk and context rather than attached indiscriminately to every AI action;
- risk controls for system components and third-party technologies should be explicit.

### EU AI Act Article 14
Primary source: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14

Transferable mechanisms:
- human oversight is proportional to risk, autonomy, and context of use;
- operators must be able to understand limitations, monitor operation, override or reverse output, and stop the system safely;
- oversight aims to reduce residual risk, not replace all automation.

### Supporting OpenAI Operator system-card mechanism
Primary source: https://openai.com/index/operator-system-card/

Transferable mechanism:
- action risk depends partly on severity and reversibility;
- consequential actions such as purchases, sending emails, or deleting events receive additional safeguards/confirmation while lower-risk navigation can proceed.

## Synthesized decision contract

The policy uses five explicit outcomes:

- `PROCEED` — safe route, sufficient evidence, no human-only authority boundary;
- `FALLBACK` — preferred route failed/unavailable, but an equivalent safe supported route exists;
- `PROBE` — uncertainty/conflict/unknown outcome can be resolved by a cheap reversible observation or reconciliation step;
- `ESCALATE` — human judgment or authorization is genuinely required: irreversible consequential action, explicit authority boundary, material evidence conflict without a resolving probe, genuine product-direction fork, or available payment/legal/identity/secret authority that still requires a human decision;
- `BLOCK` — no safe/authorized path exists in the current run. `BLOCK` is not an invitation to weaken constraints.

### Ordering rule

Hard authority/safety constraints are evaluated before confidence or preferences. `PROBE` and `FALLBACK` should precede human escalation when they are safe, reversible, and sufficient to resolve the uncertainty.

## Composition with earlier LAB mechanisms

This policy does not duplicate existing subsystems:

- LAB-005 remains authoritative for side-effect state and `UNKNOWN` outcome semantics. LAB-012 only decides whether reconciliation is available or whether the action must block/escalate.
- LAB-006 remains authoritative for evidence verification. LAB-012 consumes evidence quality/conflict as policy inputs rather than deciding truth itself.
- LAB-008 remains authoritative for route safety/capability selection. LAB-012 consumes whether a safe primary/fallback route exists.

## Experiment

Prototype: `experiments/escalation_policy/`

Observed local command:

```bash
cd experiments/escalation_policy
python -m unittest -v
```

Initial result: **12/12 tests passed**.

Remote patch audit then found an authority-boundary defect: a payment/legal/identity/secret gated action with technical access could fall through to ordinary policy if `requires_human_authorization` was not independently set. The policy was hardened so these categories always `ESCALATE` when authorization is available and `BLOCK` when it is unavailable. A regression test was added.

Corrected result: **13/13 tests passed**.

Covered cases include reversible technical choice, safe fallback, no safe route, irreversible external action, missing or available payment/secret/identity authority, high uncertainty with a cheap probe, conflicting evidence, product-direction fork, unknown side-effect reconciliation, and explicit human authorization.

## Seeded naive-policy failures

The deliberately naive policy says: “if uncertain, escalate; otherwise proceed.” It fails in both directions:

- **over-escalation:** high uncertainty on a reversible action with a cheap diagnostic becomes `ESCALATE` instead of `PROBE`;
- **dangerous under-escalation:** a high-confidence irreversible external action becomes `PROCEED` instead of `ESCALATE`.

Therefore confidence alone is not a safe autonomy boundary.

## Residual human judgment that should not be mechanized away

The deterministic policy can identify structural escalation conditions but cannot itself decide:

- major product-direction forks where values/priorities are genuinely underdetermined;
- commercial/payment commitments outside pre-authorized policy;
- legal acceptance or representation of identity;
- disclosure/use of secrets or privileged credentials not already authorized;
- irreversible externally consequential actions whose acceptable risk depends on human intent;
- situations where two high-quality evidence sets remain materially contradictory after available safe probes.

## Decision

Adopt **risk/authority/evidence/route-first escalation**, not confidence-first escalation.

Default autonomous behavior should be:

`safe PROCEED -> safe FALLBACK -> cheap reversible PROBE -> ESCALATE only for real judgment/authorization -> BLOCK when no safe route exists`.

This preserves autonomy for ordinary engineering uncertainty without silently automating consequential human decisions.

## Non-goals

- no general governance platform;
- no legal/compliance engine;
- no duplicate implementation of evidence verification, capability planning, or side-effect reconciliation;
- no attempt to infer human intent when the task genuinely requires a human decision.
