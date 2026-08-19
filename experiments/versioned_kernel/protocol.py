from __future__ import annotations
import copy
from dataclasses import dataclass, asdict
from typing import Any

CURRENT_STORAGE_VERSION = 2
CURRENT_PROTOCOL_VERSION = 2

class VersionError(RuntimeError): pass
class FutureVersionError(VersionError): pass
class OldWorkerError(VersionError): pass
class TraceTranslationError(VersionError): pass
class MigrationError(VersionError): pass

@dataclass
class VersionedState:
    work_id: str
    storage_version: int
    protocol_version: int
    migration_epoch: int
    worker_epoch: int
    phase: str
    fence: int
    generation: int
    effect_key: str | None = None
    effect_receipt: str | None = None
    evidence_id: str | None = None
    artifact_version: str | None = None
    migration_marker: str | None = None
    def clone(self): return VersionedState(**copy.deepcopy(asdict(self)))

def v1_state(work_id='w', *, phase='CONFIRMED', fence=3, generation=7, effect_key='w:effect:v1', effect_receipt='receipt-1', evidence_id='ev-1', artifact_version='artifact-A'):
    return VersionedState(work_id,1,1,0,0,phase,fence,generation,effect_key,effect_receipt,evidence_id,artifact_version)

def classify_state(state):
    if state.storage_version > CURRENT_STORAGE_VERSION or state.protocol_version > CURRENT_PROTOCOL_VERSION: return 'REJECT'
    if state.storage_version < CURRENT_STORAGE_VERSION: return 'MIGRATE'
    if state.protocol_version < CURRENT_PROTOCOL_VERSION: return 'TRANSLATE'
    return 'ACCEPT'

def assert_worker_authority(state, worker_epoch, fence):
    if worker_epoch < state.worker_epoch or worker_epoch < state.migration_epoch: raise OldWorkerError('worker fenced by migration/worker epoch')
    if fence != state.fence: raise OldWorkerError('stale fence')

def unsafe_migrate_v1_to_v2(state):
    out=state.clone(); out.storage_version=2; out.protocol_version=2; out.effect_key=f'{state.effect_key}:migrated'; out.evidence_id=f'{state.evidence_id}:migrated'; out.generation+=1; return out

def migrate_v1_to_v2(state, *, crash_after_marker=False):
    if state.storage_version > 2 or state.protocol_version > 2: raise FutureVersionError('future state must not be coerced')
    if state.storage_version == 2: return state.clone()
    if state.storage_version != 1: raise MigrationError('unsupported source storage version')
    out=state.clone(); out.migration_marker='v1->v2'
    if crash_after_marker: raise MigrationError('injected crash after migration intent')
    out.storage_version=2; out.protocol_version=2; out.migration_epoch=max(state.migration_epoch,state.worker_epoch)+1; out.worker_epoch=out.migration_epoch; out.fence=state.fence+1; out.generation=state.generation+1; out.migration_marker=None
    return out

ACTION_TRANSLATIONS={1:{'claim':'claim','intent':'prepare_effect','effect_ok':'confirm_effect','effect_unknown':'mark_unknown','evidence':'append_evidence','done':'complete','invalidate':'invalidate'},2:{'claim':'claim','prepare_effect':'prepare_effect','confirm_effect':'confirm_effect','mark_unknown':'mark_unknown','append_evidence':'append_evidence','complete':'complete','invalidate':'invalidate'}}

def translate_action(action, *, from_protocol, to_protocol=2):
    if from_protocol>2 or to_protocol!=2: raise TraceTranslationError('unsupported protocol target/source')
    m=ACTION_TRANSLATIONS.get(from_protocol)
    if not m or action not in m: raise TraceTranslationError(f'no deterministic translation for {action!r}')
    return m[action]

def translate_trace(actions, *, from_protocol): return [translate_action(a,from_protocol=from_protocol) for a in actions]

def semantic_projection(state): return {'work_id':state.work_id,'phase':state.phase,'effect_key':state.effect_key,'effect_receipt':state.effect_receipt,'evidence_id':state.evidence_id,'artifact_version':state.artifact_version}

class VersionedKernel:
    def __init__(self,state): self.state=state.clone()
    def load_for_worker(self,worker_protocol,worker_epoch):
        s=self.state
        if s.storage_version>2 or s.protocol_version>2: raise FutureVersionError('future state rejected')
        if worker_protocol==1 and s.storage_version>=2: raise OldWorkerError('v1 worker cannot interpret v2 storage')
        if worker_epoch<s.migration_epoch: raise OldWorkerError('worker fenced by migration epoch')
        return s.clone()
    def migrate(self,*,crash=False):
        original=self.state.clone()
        try: migrated=migrate_v1_to_v2(original,crash_after_marker=crash)
        except MigrationError: self.state=original; raise
        self.state=migrated; return migrated.clone()
    def mutate_phase(self,worker_epoch,fence,phase): assert_worker_authority(self.state,worker_epoch,fence); self.state.phase=phase; self.state.generation+=1
