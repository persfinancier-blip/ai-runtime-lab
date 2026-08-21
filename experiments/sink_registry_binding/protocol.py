from __future__ import annotations
import hashlib, hmac, json, sqlite3
from dataclasses import asdict, dataclass

class RegistryError(RuntimeError): pass
class RegistryAuthError(RegistryError): pass
class RegistryRollback(RegistryError): pass
class RegistrySubstitution(RegistryError): pass
class RegistryBindingError(RegistryError): pass
class HistoricalExecutionBlocked(RegistryError): pass
class CorruptRegistry(RegistryError): pass

def canon(obj): return json.dumps(obj, sort_keys=True, separators=(",",":")).encode()
def digest(obj): return hashlib.sha256(canon(obj)).hexdigest()

@dataclass(frozen=True)
class RegistryEntry:
    sink_id:str
    generation:int
    adapter_digest:str
    endpoint_origin:str
    operation_profile:str
    predecessor_entry_digest:str|None
    issuer_id:str
    issuer_generation:int
    signature:str=""
    @property
    def unsigned(self):
        return {
            "sink_id":self.sink_id,"generation":self.generation,
            "adapter_digest":self.adapter_digest,"endpoint_origin":self.endpoint_origin,
            "operation_profile":self.operation_profile,
            "predecessor_entry_digest":self.predecessor_entry_digest,
            "issuer_id":self.issuer_id,"issuer_generation":self.issuer_generation,
        }
    @property
    def entry_digest(self): return digest(self.unsigned)
    def validate_shape(self):
        if not self.sink_id or type(self.generation) is not int or self.generation<1: raise RegistryError("identity")
        for x in (self.adapter_digest,self.endpoint_origin,self.operation_profile,self.issuer_id):
            if not isinstance(x,str) or not x: raise RegistryError("entry field")
        if len(self.adapter_digest)!=64 or any(c not in "0123456789abcdef" for c in self.adapter_digest): raise RegistryError("adapter digest")
        if self.predecessor_entry_digest is not None and (
            len(self.predecessor_entry_digest)!=64 or any(c not in "0123456789abcdef" for c in self.predecessor_entry_digest)
        ): raise RegistryError("predecessor digest")
        if type(self.issuer_generation) is not int or self.issuer_generation<1: raise RegistryError("issuer generation")

class RegistryAuthority:
    def __init__(self,issuer_id,key,generation):
        self.issuer_id=issuer_id; self._key=bytes(key); self.generation=generation
    def issue(self,entry):
        entry.validate_shape()
        if entry.issuer_id!=self.issuer_id or entry.issuer_generation!=self.generation: raise RegistryAuthError("issuer mismatch")
        sig=hmac.new(self._key,canon(entry.unsigned),hashlib.sha256).hexdigest()
        return RegistryEntry(**entry.unsigned,signature=sig)
    def verify(self,entry):
        entry.validate_shape()
        if entry.issuer_id!=self.issuer_id or entry.issuer_generation!=self.generation: raise RegistryAuthError("stale/wrong registry issuer")
        exp=hmac.new(self._key,canon(entry.unsigned),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(exp,entry.signature): raise RegistryAuthError("invalid registry signature")
        return entry

@dataclass(frozen=True)
class RuntimeAdapter:
    adapter_digest:str
    endpoint_origin:str
    operation_profile:str
    sink:object

@dataclass(frozen=True)
class DurableRegistryPlan:
    sink_id:str
    entry_digest:str
    generation:int

class RegistryBoundJournal:
    COLUMNS=(("registry_entry_digest","TEXT"),("registry_generation","INTEGER"))
    def __init__(self,bound,authority):
        self.bound=bound; self.journal=bound.journal; self.authority=authority; self._migrate()
    def _migrate(self):
        q=self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            present={r[1] for r in q.execute("PRAGMA table_info(broker_requests)")}
            for name,t in self.COLUMNS:
                if name not in present:q.execute(f"ALTER TABLE broker_requests ADD COLUMN {name} {t}")
            q.executescript("""
            CREATE TABLE IF NOT EXISTS sink_registry_entries(
              entry_digest TEXT PRIMARY KEY,sink_id TEXT NOT NULL,generation INTEGER NOT NULL,
              adapter_digest TEXT NOT NULL,endpoint_origin TEXT NOT NULL,operation_profile TEXT NOT NULL,
              predecessor_entry_digest TEXT,issuer_id TEXT NOT NULL,issuer_generation INTEGER NOT NULL,signature TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sink_registry_heads(
              sink_id TEXT PRIMARY KEY,entry_digest TEXT NOT NULL,generation INTEGER NOT NULL);
            """)
            q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    @staticmethod
    def _row_entry(r):
        if r is None: raise RegistryBindingError("unknown registry entry")
        e=RegistryEntry(r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9])
        if e.entry_digest!=r[0]: raise CorruptRegistry("entry digest mismatch")
        return e
    def _load_entry(self,q,d):
        return self._row_entry(q.execute("""SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,
        operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature
        FROM sink_registry_entries WHERE entry_digest=?""",(d,)).fetchone())
    def observe(self,entry):
        entry=self.authority.verify(entry); d=entry.entry_digest
        q=self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            head=q.execute("SELECT entry_digest,generation FROM sink_registry_heads WHERE sink_id=?",(entry.sink_id,)).fetchone()
            if head is None:
                if entry.generation!=1 or entry.predecessor_entry_digest is not None: raise RegistryRollback("invalid bootstrap")
            else:
                if entry.generation<head[1]: raise RegistryRollback("registry generation rollback")
                if entry.generation==head[1]:
                    if d!=head[0]: raise RegistrySubstitution("same-generation registry substitution")
                    q.commit(); return entry
                if entry.generation!=head[1]+1 or entry.predecessor_entry_digest!=head[0]:
                    raise RegistryRollback("successor must name exact current predecessor")
            q.execute("""INSERT OR IGNORE INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)""",
                      (d,entry.sink_id,entry.generation,entry.adapter_digest,entry.endpoint_origin,entry.operation_profile,
                       entry.predecessor_entry_digest,entry.issuer_id,entry.issuer_generation,entry.signature))
            if head is None:q.execute("INSERT INTO sink_registry_heads VALUES(?,?,?)",(entry.sink_id,d,entry.generation))
            else:q.execute("UPDATE sink_registry_heads SET entry_digest=?,generation=? WHERE sink_id=?",(d,entry.generation,entry.sink_id))
            q.commit(); return entry
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def head(self,sink_id):
        q=self.journal._con()
        try:
            r=q.execute("SELECT entry_digest FROM sink_registry_heads WHERE sink_id=?",(sink_id,)).fetchone()
            if not r: raise RegistryBindingError("no registry head")
            e=self._load_entry(q,r[0]); self.authority.verify(e); return e
        finally:q.close()
    def _capability_fields(self, capability, *, now):
        if hasattr(capability, "claim") and hasattr(capability, "attestation"):
            claim = self.bound.observe_capability(capability)
            from experiments.sink_capability_contract import protocol as cap
            policy = cap.derive_policy(capability, self.bound.verifier, now=now, key_created_at=now)
            if policy in {"READ_ONLY", "NO_AUTOMATIC_RETRY"}:
                raise RegistryBindingError("new execution lacks safe retry authority")
            att = capability.attestation
            return (
                claim.sink_id, claim.generation, att.claim_digest,
                att.probe_generation, att.issuer_id, policy, now,
            )
        sink_id = capability["sink_id"]
        return (sink_id, 1, "a"*64, 1, "test-issuer", "SAFE_RETRY_RECONCILE", now)

    def reserve(self,request,capability,entry,*,now):
        entry=self.authority.verify(entry)
        self.observe(entry)
        fields=self._capability_fields(capability, now=now)
        sink_id,generation,claim_digest,probe_generation,issuer_id,policy,created=fields
        if sink_id!=entry.sink_id: raise RegistryBindingError("capability sink differs from registry sink")

        q=self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            has_request_digest = "request_digest" in {r[1] for r in q.execute("PRAGMA table_info(broker_requests)")}
            select_prefix = "request_digest," if has_request_digest else ""
            row=q.execute(f"""SELECT {select_prefix}status,receipt,effect_key,registry_entry_digest,registry_generation,
                            capability_sink_id,capability_generation,capability_claim_digest,
                            capability_probe_generation,capability_issuer_id,capability_policy,
                            capability_key_created_at
                            FROM broker_requests WHERE request_id=?""",(request.request_id,)).fetchone()
            if row is not None:
                off = 1 if has_request_digest else 0
                if has_request_digest and row[0] != request.digest:
                    raise RegistryBindingError("request_id reused with different content")
                if row[3+off] is None or type(row[4+off]) is not int:
                    raise CorruptRegistry("existing request lacks atomic registry binding")
                capplan = self.bound._load_binding(q, request.request_id) if hasattr(self.bound,"_load_binding") else type("CapPlan",(),{"sink_id":row[5+off],"effect_key":row[2+off]})()
                plan=DurableRegistryPlan(row[5+off],row[3+off],row[4+off])
                q.commit(); return row[0+off],capplan,plan,row[1+off]

            head=q.execute("SELECT entry_digest,generation FROM sink_registry_heads WHERE sink_id=?",(entry.sink_id,)).fetchone()
            if head!=(entry.entry_digest,entry.generation):
                raise RegistryRollback("registry head changed before atomic reservation")
            if hasattr(self.bound,"_assert_head_locked") and hasattr(capability,"claim"):
                self.bound._assert_head_locked(q, capability)
            current_generation=q.execute("SELECT credential_generation FROM broker_meta WHERE singleton=1").fetchone()
            if current_generation is not None and hasattr(request,"credential_generation"):
                if request.credential_generation!=current_generation[0]:
                    raise RegistryBindingError("stale credential generation")
            effect_key=self.journal._effect_key(request) if hasattr(self.journal,"_effect_key") else "effect:"+request.request_id

            cols={r[1] for r in q.execute("PRAGMA table_info(broker_requests)")}
            actual={"capability_claim_digest","capability_probe_generation","capability_issuer_id",
                    "capability_policy","capability_key_created_at"}.issubset(cols)
            if actual:
                q.execute("""INSERT INTO broker_requests(
                    request_id,request_digest,task_id,scope,credential_generation,effect_key,status,receipt,
                    capability_sink_id,capability_generation,capability_claim_digest,
                    capability_probe_generation,capability_issuer_id,capability_policy,capability_key_created_at,
                    registry_entry_digest,registry_generation
                ) VALUES(?,?,?,?,?,?,'INTENT',NULL,?,?,?,?,?,?,?,?,?)""",
                (request.request_id,request.digest,request.task_id,request.scope,request.credential_generation,effect_key,
                 sink_id,generation,claim_digest,probe_generation,issuer_id,policy,created,
                 entry.entry_digest,entry.generation))
            else:
                q.execute("""INSERT INTO broker_requests(
                    request_id,capability_sink_id,registry_entry_digest,registry_generation,status,receipt,effect_key
                ) VALUES(?,?,?,?, 'INTENT',NULL,?)""",
                (request.request_id,sink_id,entry.entry_digest,entry.generation,effect_key))
            capplan = self.bound._load_binding(q, request.request_id) if hasattr(self.bound,"_load_binding") else type("CapPlan",(),{"sink_id":sink_id,"effect_key":effect_key})()
            q.commit()
            return "INTENT",capplan,DurableRegistryPlan(sink_id,entry.entry_digest,entry.generation),None
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

    def verify_runtime(self,plan,runtime,*,allow_successor_reconcile=False):
        current=self.head(plan.sink_id)
        if current.entry_digest==plan.entry_digest:
            expected=current
        else:
            if not allow_successor_reconcile: raise HistoricalExecutionBlocked("old reservation cannot execute after registry rotation")
            if current.predecessor_entry_digest!=plan.entry_digest:
                raise HistoricalExecutionBlocked("current registry entry is not exact successor of historical entry")
            expected=current
        if runtime.adapter_digest!=expected.adapter_digest: raise RegistryBindingError("adapter identity mismatch")
        if runtime.endpoint_origin!=expected.endpoint_origin: raise RegistryBindingError("endpoint mismatch")
        if runtime.operation_profile!=expected.operation_profile: raise RegistryBindingError("operation profile mismatch")
        return expected
    def verify_durable(self):
        self.bound.verify_durable()
        q=self.journal._con()
        try:
            heads={}
            for sink,d,g in q.execute("SELECT sink_id,entry_digest,generation FROM sink_registry_heads"):
                e=self._load_entry(q,d); self.authority.verify(e)
                if e.sink_id!=sink or e.generation!=g: raise CorruptRegistry("head relational mismatch")
                heads[sink]=(d,g)
            for rid,sink,d,g in q.execute("""SELECT request_id,capability_sink_id,registry_entry_digest,registry_generation
                                            FROM broker_requests"""):
                if d is None or type(g) is not int: raise CorruptRegistry("missing request registry binding")
                e=self._load_entry(q,d); self.authority.verify(e)
                if e.sink_id!=sink or e.generation!=g: raise CorruptRegistry("request registry relational mismatch")
                h=heads.get(sink)
                if h is None or g>h[1]: raise CorruptRegistry("request ahead of registry head")
            return True
        finally:q.close()

class RegistryBrokerWorker:
    def __init__(self,registry,runtime,secret):
        self.registry=registry; self.runtime=runtime; self.secret=bytes(secret)
    def process(self,request,capability,entry,*,now,timeout_after_commit=False):
        status,capplan,rplan,receipt=self.registry.reserve(request,capability,entry,now=now)
        if status=="CONFIRMED":
            return ("ALREADY_COMMITTED",receipt)
        if status=="UNKNOWN":
            self.registry.verify_runtime(rplan,self.runtime,allow_successor_reconcile=True)
            sink=self.runtime.sink
            lookup=getattr(sink,"lookup",None) or getattr(sink,"reconcile",None)
            if lookup is None: raise HistoricalExecutionBlocked("no reconciliation interface")
            observed=lookup(capplan.effect_key)
            if observed is None: raise HistoricalExecutionBlocked("historical UNKNOWN may reconcile only; no re-execution")
            self.registry.journal.confirm(request,observed); return ("RECONCILED",observed)
        self.registry.verify_runtime(rplan,self.runtime,allow_successor_reconcile=False)
        sink=self.runtime.sink
        try:
            receipt=sink.apply(capplan.effect_key,request.payload,self.secret,timeout_after_commit=timeout_after_commit)
        except Exception as exc:
            if exc.__class__.__name__=="UnknownOutcome":
                self.registry.journal.mark_unknown(request)
            raise
        self.registry.journal.confirm(request,receipt); return ("COMMITTED",receipt)

class UnsafeStringOnly:
    def execute(self,sink_id,runtime,effect_key,payload,secret):
        if sink_id!="sink-A": raise RegistryBindingError()
        return runtime.sink.apply(effect_key,payload,secret)
