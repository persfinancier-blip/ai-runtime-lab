from __future__ import annotations
import hashlib, hmac, json, os, shutil
from dataclasses import asdict, dataclass

class RetirementError(RuntimeError): pass
class AuthenticationError(RetirementError): pass
class StalePermit(RetirementError): pass
class CurrentGenerationProtected(RetirementError): pass
class SuccessorAuditFailed(RetirementError): pass
class StrongReacquisitionUnavailable(RetirementError): pass
class NamespaceReplacementDetected(RetirementError): pass

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def mac(key, obj):
    return hmac.new(key, canon(obj), hashlib.sha256).hexdigest()

def digest(obj):
    return hashlib.sha256(canon(obj)).hexdigest()

@dataclass(frozen=True)
class NamespaceRecord:
    generation: int
    path: str
    object_id: str
    archive_chain_commitment: str
    predecessor_id: str | None
    mac: str

    def unsigned(self):
        d=asdict(self); d.pop("mac"); return d

    @property
    def record_id(self):
        return digest(self.unsigned())

@dataclass(frozen=True)
class RetirementPermit:
    predecessor_record_id: str
    successor_record_id: str
    predecessor_generation: int
    successor_generation: int
    archive_chain_commitment: str
    policy_generation: int
    mac: str

    def unsigned(self):
        d=asdict(self); d.pop("mac"); return d

@dataclass(frozen=True)
class RetirementReceipt:
    permit_id: str
    target_record_id: str
    target_generation: int
    status: str
    files_removed: int
    watermark: int

def issue_record(*, generation, path, object_id, archive_chain_commitment, predecessor_id, key):
    if type(generation) is not int or generation < 1: raise ValueError("generation")
    u={"generation":generation,"path":os.path.abspath(os.fspath(path)),"object_id":object_id,
       "archive_chain_commitment":archive_chain_commitment,"predecessor_id":predecessor_id}
    return NamespaceRecord(**u, mac=mac(key,u))

def verify_record(record,key):
    if not hmac.compare_digest(record.mac, mac(key, record.unsigned())):
        raise AuthenticationError("namespace record MAC")
    return record

def issue_retirement_permit(old,new,policy_generation,key):
    verify_record(old,key); verify_record(new,key)
    if new.predecessor_id != old.record_id:
        raise StalePermit("successor does not name predecessor")
    if new.generation != old.generation + 1:
        raise StalePermit("generation discontinuity")
    if new.archive_chain_commitment != old.archive_chain_commitment:
        raise SuccessorAuditFailed("successor chain commitment differs")
    if type(policy_generation) is not int or policy_generation < 1:
        raise ValueError("policy_generation")
    u={"predecessor_record_id":old.record_id,"successor_record_id":new.record_id,
       "predecessor_generation":old.generation,"successor_generation":new.generation,
       "archive_chain_commitment":new.archive_chain_commitment,
       "policy_generation":policy_generation}
    return RetirementPermit(**u, mac=mac(key,u))

def verify_permit(permit,key):
    if not hmac.compare_digest(permit.mac, mac(key, permit.unsigned())):
        raise AuthenticationError("retirement permit MAC")
    return permit

class RetirementLedger:
    """Reference state; production integration will use LAB-066 SQL authority."""
    def __init__(self):
        self.current_record_id=None
        self.current_generation=0
        self.records={}
        self.retirement_watermark=0
        self.receipts={}

    def activate(self,record):
        self.records[record.record_id]=record
        self.current_record_id=record.record_id
        self.current_generation=record.generation

    def receipt(self,permit_id):
        return self.receipts.get(permit_id)

class RetirementEngine:
    def __init__(self, ledger, *, key, policy_generation=1):
        self.ledger=ledger; self.key=key; self.policy_generation=policy_generation

    def _permit_id(self,p):
        return digest(p.unsigned())

    def classify(self, old, permit, *, reacquire, audit_successor):
        verify_record(old,self.key); verify_permit(permit,self.key)
        if permit.policy_generation != self.policy_generation:
            return "STALE_PERMIT"
        if old.record_id == self.ledger.current_record_id or old.generation == self.ledger.current_generation:
            return "CURRENT_GENERATION_PROTECTED"
        if permit.predecessor_record_id != old.record_id or permit.predecessor_generation != old.generation:
            return "STALE_PERMIT"
        successor=self.ledger.records.get(permit.successor_record_id)
        if successor is None or successor.record_id != self.ledger.current_record_id:
            return "STALE_PERMIT"
        verify_record(successor,self.key)
        if permit.successor_generation != successor.generation:
            return "STALE_PERMIT"
        if successor.predecessor_id != old.record_id:
            return "STALE_PERMIT"
        if successor.archive_chain_commitment != permit.archive_chain_commitment:
            return "SUCCESSOR_AUDIT_FAILED"
        if not audit_successor(successor):
            return "SUCCESSOR_AUDIT_FAILED"
        status=reacquire(old)
        if status == "DETACHED_OBJECT_FOUND":
            return "SAFE_TO_RECLAIM"
        if status in {"UNSUPPORTED_STRONG_REACQUISITION","PATH_MISSING","HANDLE_STALE"}:
            return "RETIREMENT_UNSUPPORTED"
        if status in {"PATH_REPLACED","IDENTITY_MISMATCH"}:
            return "DETACHED_OBJECT_FOUND"
        if status == "REACQUIRED":
            return "SAFE_TO_RECLAIM"
        return "RETIREMENT_UNSUPPORTED"

    def retire(self, old, permit, *, reacquire, audit_successor, cleanup):
        pid=self._permit_id(permit)
        existing=self.ledger.receipt(pid)
        if existing: return existing
        classification=self.classify(old,permit,reacquire=reacquire,audit_successor=audit_successor)
        if classification != "SAFE_TO_RECLAIM":
            raise RetirementError(classification)
        classification=self.classify(old,permit,reacquire=reacquire,audit_successor=audit_successor)
        if classification != "SAFE_TO_RECLAIM":
            raise RetirementError(classification)
        removed=cleanup(old)
        self.ledger.retirement_watermark += 1
        receipt=RetirementReceipt(pid,old.record_id,old.generation,"RETIRED",removed,self.ledger.retirement_watermark)
        self.ledger.receipts[pid]=receipt
        return receipt

class UnsafePathRetirement:
    def retire(self,path):
        shutil.rmtree(path)
        return True
