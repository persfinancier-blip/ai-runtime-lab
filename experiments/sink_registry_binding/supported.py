"""Supported LAB-075 surface.

The initial prototype remains in ``protocol.py`` for audit history. Production-like
callers and integration tests must import the audited classes from this module so
none of the pre-audit behavior is accidentally selected.
"""

from experiments.sink_registry_binding.protocol import (
    CorruptRegistry,
    DurableRegistryPlan,
    HistoricalExecutionBlocked,
    RegistryAuthError,
    RegistryAuthority,
    RegistryBindingError,
    RegistryEntry,
    RegistryError,
    RegistryRollback,
    RegistrySubstitution,
    RuntimeAdapter,
    UnsafeStringOnly,
)
from experiments.sink_registry_binding.audit_fixes import (
    CorrectedRegistryBoundJournal as RegistryBoundJournal,
    CorrectedRegistryBrokerWorker as RegistryBrokerWorker,
)

__all__ = [
    "CorruptRegistry",
    "DurableRegistryPlan",
    "HistoricalExecutionBlocked",
    "RegistryAuthError",
    "RegistryAuthority",
    "RegistryBindingError",
    "RegistryBoundJournal",
    "RegistryBrokerWorker",
    "RegistryEntry",
    "RegistryError",
    "RegistryRollback",
    "RegistrySubstitution",
    "RuntimeAdapter",
    "UnsafeStringOnly",
]
