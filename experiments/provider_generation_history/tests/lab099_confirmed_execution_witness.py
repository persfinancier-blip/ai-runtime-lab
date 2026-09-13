"""Test-only non-authoritative execution witness for the frozen LAB-099 CONFIRMED bridge.

The deterministic keys in this module exist only to exercise the already-existing
provider-history and anchor-attestation mechanics. They MUST NOT be consumed as
LAB-099 semantic authority, persisted into production state, or used to derive
new receipt/head/provenance values. The only acceptable outcome is reproduction
of the independently frozen reference identities.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.protocol import (
    DurableProviderHistory,
    GenerationDescriptor,
    HistoricalReceipt,
)
from experiments.provider_generation_history.tests import (
    lab099_confirmed_ledger_reference as confirmed,
)
from experiments.provider_generation_history.tests import (
    lab099_cutover_storage_reference as storage,
)

WITNESS_DOMAIN = b"ytim.lab099.confirmed-execution-witness.v1"
WITNESS_PROVIDER_ID = confirmed.REFERENCE_PROVIDER_ID
WITNESS_FIRST_GENERATION = 1
WITNESS_LAST_GENERATION = confirmed.REFERENCE_PROVIDER_GENERATION
WITNESS_START_POSITION = confirmed.REFERENCE_PREDECESSOR_POSITION
WITNESS_INCREMENT_CHALLENGE = "lab099-witness-increment"
WITNESS_RECONCILE_CHALLENGE = "lab099-witness-reconcile"


def _witness_key(generation: int) -> bytes:
    if type(generation) is not int or not (
        WITNESS_FIRST_GENERATION <= generation <= WITNESS_LAST_GENERATION
    ):
        raise ValueError("generation outside execution-witness range")
    return hashlib.sha256(WITNESS_DOMAIN + b":" + str(generation).encode("ascii")).digest()


def witness_descriptors() -> tuple[GenerationDescriptor, ...]:
    return tuple(
        GenerationDescriptor(WITNESS_PROVIDER_ID, generation, _witness_key(generation).hex())
        for generation in range(WITNESS_FIRST_GENERATION, WITNESS_LAST_GENERATION + 1)
    )


def witness_transition_chain():
    descriptors = witness_descriptors()
    return tuple(
        DurableProviderHistory.make_transition(old, new)
        for old, new in zip(descriptors, descriptors[1:])
    )


def install_witness_history(path: str | Path) -> DurableProviderHistory:
    """Build an executable g1..g8 history using fixture-only deterministic keys."""
    descriptors = witness_descriptors()
    proofs = witness_transition_chain()
    history = DurableProviderHistory(path, descriptors[0])
    for new, proof in zip(descriptors[1:], proofs):
        history.rotate(new, proof)
    history.verify_durable()
    current = history.current()
    if current != descriptors[-1]:
        raise AssertionError("execution-witness provider-history head drift")
    return history


def generation8_attested() -> AttestedCatchup:
    """Instantiate exact provider-alpha/g8 at frozen predecessor position 41."""
    current = witness_descriptors()[-1]
    provider = SignedAnchorProvider(
        provider_id=current.provider_id,
        generation=current.generation,
        key=current.key,
        value=WITNESS_START_POSITION,
    )
    verifier = AttestationVerifier(
        {(current.provider_id, current.generation): current.key},
        ProviderIdentity(current.provider_id, current.generation),
    )
    return AttestedCatchup(provider, verifier)


def exercise_frozen_confirmed_reference() -> dict:
    """Exercise increment/reconcile and require exact frozen receipt/head reproduction."""
    attested = generation8_attested()
    provider = attested.provider
    verifier = attested.verifier
    request_id = confirmed.REFERENCE_REQUEST_ID

    increment = provider.increment(
        expected=WITNESS_START_POSITION,
        challenge=WITNESS_INCREMENT_CHALLENGE,
        request_id=request_id,
    )
    verified_increment = verifier.verify(
        increment,
        expected_challenge=WITNESS_INCREMENT_CHALLENGE,
        allowed_kinds={"INCREMENT"},
    )
    if verified_increment.position != confirmed.REFERENCE_POSITION:
        raise AssertionError("execution-witness increment position drift")

    reconciled = provider.reconcile_increment(
        challenge=WITNESS_RECONCILE_CHALLENGE,
        request_id=request_id,
    )
    if reconciled is None:
        raise AssertionError("execution-witness request result was not retained")
    verified = verifier.verify(
        reconciled,
        expected_challenge=WITNESS_RECONCILE_CHALLENGE,
        allowed_kinds={"RECONCILE"},
    )
    receipt = HistoricalReceipt(
        verified.provider_id,
        verified.generation,
        verified.position,
        verified.request_id,
        verified.kind,
        verified.challenge,
        verified.mac,
    )
    if receipt.stable_binding != confirmed.REFERENCE_RECEIPT_BINDING:
        raise AssertionError("execution witness does not reproduce frozen stable receipt")

    entry = confirmed.reference_confirmed_entry()
    if entry["receipt_binding"] != receipt.stable_binding:
        raise AssertionError("frozen CONFIRMED entry receipt mismatch")
    head = storage.confirmed_head_digest(entry)
    if head != confirmed.REFERENCE_CONFIRMED_HEAD_DIGEST:
        raise AssertionError("execution witness does not reproduce frozen confirmed head")

    return {
        "provider_id": verified.provider_id,
        "generation": verified.generation,
        "predecessor_position": WITNESS_START_POSITION,
        "position": verified.position,
        "request_id": verified.request_id,
        "receipt_binding": receipt.stable_binding,
        "confirmed_head_digest": head.hex(),
    }


def validate_execution_witness_contract() -> bool:
    descriptors = witness_descriptors()
    if tuple(d.generation for d in descriptors) != tuple(range(1, 9)):
        raise AssertionError("execution-witness generation chain drift")
    if any(d.provider_id != WITNESS_PROVIDER_ID for d in descriptors):
        raise AssertionError("execution-witness provider identity drift")
    if len({d.generation_id for d in descriptors}) != WITNESS_LAST_GENERATION:
        raise AssertionError("execution-witness generation ids are not unique")
    if len(witness_transition_chain()) != WITNESS_LAST_GENERATION - 1:
        raise AssertionError("execution-witness transition chain length drift")
    result = exercise_frozen_confirmed_reference()
    if result["receipt_binding"] != confirmed.REFERENCE_RECEIPT_BINDING:
        raise AssertionError("frozen receipt reproduction drift")
    if result["confirmed_head_digest"] != confirmed.REFERENCE_CONFIRMED_HEAD_DIGEST.hex():
        raise AssertionError("frozen head reproduction drift")
    return True


if __name__ == "__main__":
    assert validate_execution_witness_contract()
