from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    PROCEED = "PROCEED"
    FALLBACK = "FALLBACK"
    PROBE = "PROBE"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class Context:
    reversible: bool
    externally_consequential: bool
    requires_human_authorization: bool
    authorization_available: bool
    legal_identity_payment_secret_gate: bool
    uncertainty: float
    evidence_quality: float
    evidence_conflict: bool
    safe_primary_route: bool
    safe_fallback_route: bool
    cheap_reversible_probe: bool
    genuine_product_fork: bool
    side_effect_outcome_unknown: bool = False


@dataclass(frozen=True)
class Result:
    decision: Decision
    reason: str


def decide(ctx: Context) -> Result:
    if ctx.legal_identity_payment_secret_gate:
        if not ctx.authorization_available:
            return Result(Decision.BLOCK, "required_authorization_or_secret_unavailable")
        return Result(Decision.ESCALATE, "payment_legal_identity_or_secret_requires_human_authority")

    if ctx.side_effect_outcome_unknown:
        if ctx.cheap_reversible_probe:
            return Result(Decision.PROBE, "reconcile_unknown_side_effect_outcome")
        return Result(Decision.BLOCK, "unknown_side_effect_without_safe_reconciliation")

    if ctx.requires_human_authorization or ctx.genuine_product_fork:
        return Result(Decision.ESCALATE, "human_judgment_or_authorization_required")

    if (not ctx.reversible) and ctx.externally_consequential:
        return Result(Decision.ESCALATE, "irreversible_external_consequence")

    if ctx.evidence_conflict:
        if ctx.cheap_reversible_probe:
            return Result(Decision.PROBE, "resolve_conflicting_evidence")
        return Result(Decision.ESCALATE, "material_evidence_conflict")

    if ctx.uncertainty >= 0.60 or ctx.evidence_quality < 0.50:
        if ctx.cheap_reversible_probe:
            return Result(Decision.PROBE, "uncertainty_resolvable_by_safe_probe")
        if ctx.safe_fallback_route:
            return Result(Decision.FALLBACK, "use_safer_supported_route_under_uncertainty")
        if ctx.externally_consequential:
            return Result(Decision.ESCALATE, "material_uncertainty_without_safe_probe")
        return Result(Decision.BLOCK, "insufficient_evidence_no_safe_route")

    if ctx.safe_primary_route:
        return Result(Decision.PROCEED, "safe_primary_route")

    if ctx.safe_fallback_route:
        return Result(Decision.FALLBACK, "preferred_route_unavailable_safe_fallback_exists")

    return Result(Decision.BLOCK, "no_safe_supported_route")


def naive_decide(ctx: Context) -> Result:
    """Deliberately unsafe baseline used only by tests."""
    if ctx.uncertainty >= 0.50:
        return Result(Decision.ESCALATE, "uncertain")
    return Result(Decision.PROCEED, "confident")
