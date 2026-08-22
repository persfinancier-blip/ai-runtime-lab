"""Supported LAB-077 threshold-publication surface.

New sink-registry publication requires ``ThresholdEnvelope``. Historical
single-signature LAB-076 publication methods remain available only in older
experiment modules for audit history/backwards regression; this module exposes
only the final audited threshold-aware atomic request/publication ordering.
"""

from experiments.sink_registry_authority_lifecycle.audit_fixes import (
    ConsistentDurableRegistryAuthority as DurableRegistryAuthority,
)
from experiments.sink_registry_authority_lifecycle.protocol import (
    AuthorityRollback,
    AuthoritySubstitution,
    EntryAuthError,
    HistoricalAuthorityMissing,
    LifecycleError,
    UnsafeRecovery,
)
from experiments.sink_registry_binding.supported import RegistryEntry, RuntimeAdapter
from experiments.sink_registry_threshold_publication.final_fixes import (
    FinalThresholdLifecycleRegistryBoundJournal as ThresholdLifecycleRegistryBoundJournal,
    FinalThresholdLifecycleRegistryBrokerWorker as ThresholdLifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_threshold_publication.integration import ThresholdHistoricalMissing
from experiments.sink_registry_threshold_publication.protocol import (
    AuthorityMismatch,
    InvalidSignatureSet,
    ProofSubstitution,
    ThresholdEnvelope,
    ThresholdProof,
    make_envelope,
    publication_entry,
    sign_publication,
    verify_envelope,
)

__all__ = [
    "AuthorityMismatch",
    "AuthorityRollback",
    "AuthoritySubstitution",
    "DurableRegistryAuthority",
    "EntryAuthError",
    "HistoricalAuthorityMissing",
    "InvalidSignatureSet",
    "LifecycleError",
    "ProofSubstitution",
    "RegistryEntry",
    "RuntimeAdapter",
    "ThresholdEnvelope",
    "ThresholdHistoricalMissing",
    "ThresholdLifecycleRegistryBoundJournal",
    "ThresholdLifecycleRegistryBrokerWorker",
    "ThresholdProof",
    "UnsafeRecovery",
    "make_envelope",
    "publication_entry",
    "sign_publication",
    "verify_envelope",
]
