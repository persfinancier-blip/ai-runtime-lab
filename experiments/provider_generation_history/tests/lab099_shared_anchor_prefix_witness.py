"""Test-only legitimate shared-anchor prefix builder for the LAB-099 execution witness.

The prefix rows produced here are execution mechanics only. They are created through the
existing supported ledger API and MUST NOT be treated as LAB-099 semantic authority.
No raw shared-anchor row insertion or manual tail metadata mutation is allowed here.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.supported import (
    SupportedHistoricalSharedAnchorLedger,
)
from experiments.provider_generation_history.tests import (
    lab099_confirmed_execution_witness as execution_witness,
)
from experiments.provider_generation_history.tests import (
    lab099_confirmed_ledger_reference as confirmed,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent

PREFIX_COMPONENT_ID = "lab099-confirmed-prefix-witness"
PREFIX_INTENT_TYPE = "archive_checkpoint"
PREFIX_LAST_POSITION = confirmed.REFERENCE_PREDECESSOR_POSITION
PREFIX_PAYLOAD_CONTRACT = "ytim.lab099.non-authoritative-prefix-witness.v1"


@dataclass(frozen=True)
class LegitimatePrefixWitness:
    ledger: Any
    attested: AttestedCatchup
    bootstrap: Any


def _generation8_at_zero() -> AttestedCatchup:
    current = execution_witness.witness_descriptors()[-1]
    provider = SignedAnchorProvider(
        provider_id=current.provider_id,
        generation=current.generation,
        key=current.key,
        value=0,
    )
    verifier = AttestationVerifier(
        {(current.provider_id, current.generation): current.key},
        ProviderIdentity(current.provider_id, current.generation),
    )
    return AttestedCatchup(provider, verifier)


def _prefix_intent(position: int) -> Intent:
    if type(position) is not int or not 1 <= position <= PREFIX_LAST_POSITION:
        raise ValueError("prefix position outside frozen witness range")
    return Intent(
        intent_id=f"lab099-prefix-witness:{position:02d}",
        component_id=PREFIX_COMPONENT_ID,
        intent_type=PREFIX_INTENT_TYPE,
        payload={
            "contract": PREFIX_PAYLOAD_CONTRACT,
            "position": position,
        },
    )


def build_legitimate_prefix(path: str | Path) -> LegitimatePrefixWitness:
    """Create positions 1..41 only via normal provider-history + ledger execution paths."""
    descriptors = execution_witness.witness_descriptors()
    if descriptors[-1].provider_id != confirmed.REFERENCE_PROVIDER_ID:
        raise AssertionError("prefix witness provider id drift")
    if descriptors[-1].generation != confirmed.REFERENCE_PROVIDER_GENERATION:
        raise AssertionError("prefix witness provider generation drift")

    execution_witness.install_witness_history(path)
    runtime = _generation8_at_zero()
    ledger = SupportedHistoricalSharedAnchorLedger(path, runtime, descriptors[0])

    for position in range(1, PREFIX_LAST_POSITION + 1):
        entry = ledger.execute(_prefix_intent(position))
        if entry.status != "CONFIRMED":
            raise AssertionError("legitimate prefix row did not confirm")
        if entry.predecessor_position != position - 1 or entry.position != position:
            raise AssertionError("legitimate prefix row position drift")
        if (entry.provider_id, entry.provider_generation) != (
            confirmed.REFERENCE_PROVIDER_ID,
            confirmed.REFERENCE_PROVIDER_GENERATION,
        ):
            raise AssertionError("legitimate prefix provider identity drift")

    if ledger.verify_durable() is not True:
        raise AssertionError("legitimate prefix durable verification failed")

    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    try:
        meta = q.execute(
            "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()
        counts = q.execute(
            "SELECT COUNT(*),SUM(status='PREPARED'),MIN(position),MAX(position) "
            "FROM shared_anchor_intents"
        ).fetchone()
    finally:
        q.close()
    if meta != (PREFIX_LAST_POSITION,):
        raise AssertionError("legitimate prefix durable tail drift")
    if counts != (PREFIX_LAST_POSITION, 0, 1, PREFIX_LAST_POSITION):
        raise AssertionError("legitimate prefix durable row-set drift")

    challenge = runtime.challenge()
    observed = runtime.authenticated_read(
        challenge=challenge,
        request_id="lab099-prefix-witness-final-read",
    )
    if observed.position != PREFIX_LAST_POSITION:
        raise AssertionError("provider did not finish at legitimate prefix tail")

    return LegitimatePrefixWitness(ledger, runtime, descriptors[0])


def validate_prefix_contract_shape() -> bool:
    if PREFIX_LAST_POSITION != 41:
        raise AssertionError("frozen LAB-099 predecessor position drift")
    intents = tuple(_prefix_intent(position) for position in range(1, 42))
    if len({intent.intent_id for intent in intents}) != 41:
        raise AssertionError("prefix intent identities are not unique")
    if any(intent.component_id != PREFIX_COMPONENT_ID for intent in intents):
        raise AssertionError("prefix component identity drift")
    if any(intent.intent_type != PREFIX_INTENT_TYPE for intent in intents):
        raise AssertionError("prefix intent type drift")
    return True


if __name__ == "__main__":
    assert validate_prefix_contract_shape()
