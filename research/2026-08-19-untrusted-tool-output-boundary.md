# LAB-020 — Untrusted tool-output control/data separation

Date: 2026-08-19

## Research question

How can an autonomous runtime prevent web/file/MCP/tool/peer-agent content from promoting itself into control-plane authority, even when the content looks like instructions or arrives in structured fields?

## Primary-source donors

1. **Model Context Protocol specification / tools security**
   - https://modelcontextprotocol.io/specification/2025-11-25
   - https://modelcontextprotocol.io/specification/2025-11-25/server/tools
   - MCP treats tool annotations as untrusted unless they come from a trusted server, requires input validation/access control, and recommends validating tool results before passing them onward.
   - Transfer: protocol metadata and tool results need explicit trust classification; server trust alone is not equivalent to runtime control authority.

2. **OpenAI prompt-injection security guidance**
   - https://openai.com/safety/prompt-injections/
   - https://openai.com/index/designing-agents-to-resist-prompt-injection/
   - OpenAI frames prompt injection as third-party content attempting to cause actions the user did not request and uses layered defenses, least access, confirmations, sandboxing, and source-sink analysis rather than claiming input classification solves the problem.
   - Transfer: preserve the user's intended action and constrain dangerous sinks independently of whether malicious content is detected perfectly.

3. **OWASP AI Agent Security / Prompt Injection / Excessive Agency**
   - https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
   - https://genai.owasp.org/llmrisk/llm01-prompt-injection/
   - https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
   - OWASP identifies indirect injection from external sources, tool abuse/privilege escalation, data exfiltration, and excessive agency as distinct but composable risks.
   - Transfer: control authority, data trust, tool privilege and escalation must be enforced by deterministic runtime policy, not only prompt wording.

## Authority taxonomy

- **Trusted control**: explicit control envelope + trusted source + declared control channel. May narrow policy, never silently widen user-granted authority.
- **Untrusted data**: web/file/tool/MCP response/peer message. May contribute facts to reasoning only.
- **Evidence candidate**: a claim/receipt supplied by an external source. It is not completion evidence until independently observed/validated and bound to the current artifact version.
- **Protected sink**: action, permission, escalation decision, target/destination, secret-bearing transmission, destructive/payment/legal/identity operation. Data-plane content cannot mutate it.

## Seeded unsafe design

`UnsafeConcatenatingAgent` treats structured fields in tool data as instructions. A malicious result containing `requested_action=send_secret` and `redirect_target=attacker.example` changes the authorized `summarize/report-A` request into an exfiltration action. The retained expected-failure test fails exactly on that unauthorized promotion.

## Corrected experiment

The `PolicyKernel` keeps the authoritative `ControlRequest` separate from model-visible envelopes and enforces:

- allowed-action constraint before execution;
- privileged/human-gated actions remain escalated regardless of peer/tool text;
- data-plane control-like fields are logged as smuggling attempts but have no authority;
- trusted-server metadata arriving through `tool_output` remains non-authoritative;
- only explicit trusted `control` channel input is control-classified, and it may narrow/deny but not widen allowed actions;
- evidence must be observed, independent, and current-artifact-version bound.

Observed local corrected suite: **12/12 tests passed**.

Observed unsafe seed: **fails as intended**, because unsafe output becomes `('send_secret', 'attacker.example')` instead of the authorized request.

`python -m compileall -q` passed.

## Audit findings

The first corrected draft had two defects that were fixed before publication:

1. trusted control `deny_actions` was recorded but did not actually block the current action;
2. evidence trust checked observation/independence but omitted artifact-version binding, weakening LAB-006 stale-evidence semantics.

Both now have regression tests.

## Integration implications

The runtime should carry explicit envelope metadata across every tool/resource/peer boundary: source identity, channel, authority class, trust class, artifact/version binding, and provenance reference. The LLM may read external content, but the deterministic action kernel should derive executable action/target/permissions from trusted control state, not from free-form tool output.

This composes with prior labs:

- LAB-006: untrusted success claims cannot satisfy completion evidence;
- LAB-008: capability constraints cannot be widened by tool data;
- LAB-012: escalation cannot be skipped by peer/tool content;
- LAB-014/015: protected invariants remain storage/action-layer authority, not preferences;
- LAB-019: envelope/control schema itself must be versioned explicitly during upgrades.

## Residual risk

This does **not** solve prompt injection. Malicious data can still bias reasoning, summaries, ranking, or model-generated proposals. A sufficiently manipulated model may propose a bad action that is nevertheless inside the user's broad allowed set. The kernel reduces blast radius by preventing external content from creating new authority or bypassing protected sinks. Model training, monitoring, least privilege, confirmation, sandboxing and source-sink controls remain necessary layers.

## Non-goals

- no universal prompt-injection detector;
- no natural-language sanitizer/firewall;
- no MCP trust registry;
- no model-jailbreak benchmark;
- no claim that trusted sources are truthful;
- no claim that structured output is safe merely because it validates against JSON schema.

## Stop-condition assessment

Three current primary-source security/protocol families were compared; one unsafe authority-promotion design was falsified; the corrected injection/control-confusion matrix passes deterministically after audit fixes. Remaining work is repository audit/integration and durable-state advancement.
