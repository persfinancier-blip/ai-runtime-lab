from __future__ import annotations

from .adoption_validation import validate_existing_mutable_state_locked
from .cross_table_guards import install_cross_table_guards
from .full_operation_guards import install_full_operation_guards
from .history_binding_guards import install_history_binding_guards
from .restart_safe_schema import initialize_shared_anchor_schema
from .state_machine_operation_scoped import (
    SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger,
)
from .state_machine_udfs import install_state_machine_udfs


class SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger(
    SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger
):
    """LAB-091 candidate with deterministic request IDs and history-bound watermarks."""

    def _con(self):
        q = super()._con()
        install_state_machine_udfs(q)
        return q

    def _init(self):
        # SharedAnchorLedger._init() replays INSERT OR IGNORE on every reopen.
        # Persistent LAB-091 BEFORE INSERT guards intentionally fire before
        # conflict resolution, so the historical initializer is incompatible
        # with an already protected database. Dynamic dispatch reaches this
        # override from the LAB-080 base constructor.
        q = self._con()
        try:
            initialize_shared_anchor_schema(q)
        finally:
            q.close()

    def _install_guards(self):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            install_full_operation_guards(q)
            install_cross_table_guards(q)
            install_history_binding_guards(q)
            # Persistent triggers can constrain only future statements. Before
            # completing first adoption/restart, reject preexisting rows that
            # could not have been created by the supported LAB-091 state machine.
            validate_existing_mutable_state_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
