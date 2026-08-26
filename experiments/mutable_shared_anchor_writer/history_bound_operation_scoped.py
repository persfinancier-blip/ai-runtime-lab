from __future__ import annotations

from .cross_table_guards import install_cross_table_guards
from .full_operation_guards import install_full_operation_guards
from .history_binding_guards import install_history_binding_guards
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

    def _install_guards(self):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            install_full_operation_guards(q)
            install_cross_table_guards(q)
            install_history_binding_guards(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
