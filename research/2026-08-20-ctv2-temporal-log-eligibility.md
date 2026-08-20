# LAB-048 — Temporal CT eligibility and historical-policy conformance

Date: 2026-08-20

## Question

How should a verifier decide whether a CT log and its operator were eligible at the relevant historical time without either (a) rewriting old attribution after later retirement/distrust/operator changes or (b) letting a caller cherry-pick stale trust metadata to bypass a newer authenticated transition?

## Primary-source mechanisms

### Chromium CT metadata and policy implementation

Current Chromium `certificate_transparency.proto` models a log state history with a timestamp for when each state began, plus operator history with an `operator_start` timestamp. Current policy code exposes `GetOperatorForLog(log_id, timestamp)` and uses time-aware disqualification data. The current log-list data also has explicit `temporal_interval.start_inclusive` / `end_exclusive` fields.

Sources:
- https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/certificate_transparency/certificate_transparency.proto
- https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/certificate_transparency/chrome_ct_policy_enforcer.cc
- https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/certificate_transparency/data/log_list.json

Transferable mechanism: lifecycle and operator identity are temporal facts, not timeless attributes. A later owner must not be projected backwards onto an earlier SCT.

### RFC 9162

RFC 9162 defines CT v2 cryptographic structures and auditing requirements but leaves concrete client compliance decisions to local policy. The LAB therefore records its temporal policy explicitly instead of calling it browser/Chrome policy.

Source: https://www.rfc-editor.org/rfc/rfc9162.html

### RFC 5280 as a comparison temporal authorization primitive

RFC 5280 defines X.509 certificate validity as an explicit time interval from `notBefore` through `notAfter`, inclusive. The transferable lesson is that authorization/trust decisions need an explicit event time and documented boundary semantics; the exact endpoint convention is protocol-specific.

Source: https://www.rfc-editor.org/rfc/rfc5280

## Protocol decision

LAB-048 defines two explicit evaluation modes:

1. `HISTORICAL`: lifecycle eligibility is evaluated at the evidence/SCT timestamp. Later retirement/distrust does not retroactively erase an attribution that was eligible then.
2. `CURRENT_POLICY`: lifecycle eligibility is evaluated at policy decision time. This prevents an old SCT from continuing to satisfy a current/future decision after a newer authenticated ineligibility transition.

Operator identity is always resolved at `evidence_time`, because operator diversity is an attribution about who operated the log when the evidence was issued.

The evaluator does **not** accept an arbitrary snapshot choice. For a given `policy_time`, it selects the newest authenticated/accepted snapshot issued by that time and rejects a caller-requested older snapshot. If that authority snapshot is expired at `policy_time`, evaluation fails closed.

## Interval construction

Accepted authenticated snapshots are the authority chain. For each log:

- state events are keyed by authenticated `state_since` timestamps;
- operator events are keyed by authenticated `operator_since` timestamps;
- conflicting values at the same timestamp fail closed;
- the reference interval convention is `[start_inclusive, end_exclusive)`.

The model keeps verification profile immutable across history.

## Failure injection

Unsafe baseline: allow the caller to select any prior accepted snapshot and evaluate only its current-state field. An attacker selects a snapshot where log A is ACTIVE even though a later authenticated snapshot has RETIRED A. The expected safety assertion fails because the stale snapshot is accepted.

Observed unsafe result: one failing test, showing stale-snapshot bypass.

Corrected observed result after audit fixes: **15/15 deterministic tests passed**; `compileall` passed.

Covered cases include:
- evidence inside/outside an active interval;
- later retirement without retroactive historical erasure;
- current-policy rejection after retirement/distrust;
- operator reassignment at evidence time;
- exact start-inclusive/end-exclusive boundaries;
- stale snapshot cherry-pick rejection;
- expired/frozen metadata rejection;
- decision binding to policy/evidence time and snapshot identity;
- conflicting history rejection;
- future evidence rejection;
- strict integer time validation.

## Audit findings fixed before publication

1. First draft inferred operator changes from snapshot publication time. That is weaker than Chromium's explicit operator history. `operator_since` is now explicit and required.
2. First draft allowed evidence timestamps later than the policy decision time. This could let future evidence affect a past decision. It now fails closed.

## Non-goals

- This is not Chrome/browser certificate compliance policy.
- It does not define how many SCTs a browser must require.
- It does not replace LAB-047 authentication of trust metadata.
- It does not claim RFC 5280 endpoint semantics apply to CT log lifecycle intervals.
- It does not solve distributed freshness beyond the authenticated snapshot history and expiry model.

## Integration implication

LAB-047 should remain the authenticated trust-distribution authority. LAB-048 is a temporal projection layer over that accepted history. Future policy layers should consume a persisted decision containing both evidence time and policy time, because collapsing them into one timestamp recreates the historical-rewrite/cherry-pick ambiguity this experiment removes.
