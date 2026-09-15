from pathlib import Path

from experiments.provider_generation_history.activation import ActivationTicket
from experiments.provider_generation_history.activation_transition import ActivationTransitionMixin
from experiments.provider_generation_history.protocol import GenerationDescriptor


class RecordingProvider:
    def __init__(self, ticket):
        self.ticket = ticket
        self.events = []

    def prepare_activation(self, *, expected_position, activation_id):
        self.events.append(("prepare", expected_position, activation_id))
        return self.ticket

    def activation_status(self, ticket):
        self.events.append(("status", ticket))
        return "PREPARED"

    def abort_activation(self, ticket):
        self.events.append(("abort", ticket))
        return "ABORTED"


def test_transition_source_uses_private_history_and_single_immediate_transaction():
    source = Path(
        "experiments/provider_generation_history/activation_transition.py"
    ).read_text()
    assert 'q.execute("BEGIN IMMEDIATE")' in source
    assert "self._history()._rotate_locked(q, new, proof)" in source
    assert "self.provider_history" not in source
    insert = source.index('"INSERT INTO provider_generation_activations "')
    rotate = source.index("self._history()._rotate_locked(q, new, proof)")
    commit = source.index("q.commit()", rotate)
    assert insert < rotate < commit


def test_activation_identity_binds_generation_and_reserved_tail():
    new = GenerationDescriptor("provider", 2, "11" * 32)
    identity = ActivationTransitionMixin._activation_id(new, 41)
    assert identity == f"provider-activation:{new.generation_id}:41"


def test_ticket_validation_rejects_wrong_fence_or_position():
    new = GenerationDescriptor("provider", 2, "22" * 32)
    activation_id = ActivationTransitionMixin._activation_id(new, 7)
    good = ActivationTicket("provider", 2, 7, activation_id, 1)
    ActivationTransitionMixin._validate_activation_ticket(good, new, 7, activation_id)

    for bad in (
        ActivationTicket("provider", 2, 8, activation_id, 1),
        ActivationTicket("provider", 2, 7, activation_id, 0),
        ActivationTicket("provider", 2, 7, activation_id + "x", 1),
    ):
        try:
            ActivationTransitionMixin._validate_activation_ticket(
                bad, new, 7, activation_id
            )
        except Exception:
            pass
        else:
            raise AssertionError("mismatched activation ticket accepted")
