from __future__ import annotations

from .convergent_operation_scoped import (
    SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger,
)
from .cross_table_guards import install_cross_table_guards
from .full_operation_guards import install_full_operation_guards


class SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger(
    SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger
):
    """LAB-091 candidate with one-shot permits plus cross-table state-machine binding."""

    def _install_guards(self):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            install_full_operation_guards(q)
            install_cross_table_guards(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
