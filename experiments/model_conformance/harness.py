from __future__ import annotations
from dataclasses import dataclass, replace
import json, sqlite3, tempfile
from pathlib import Path

ACTIONS=("claim","intent","effect_ok","effect_unknown","reconcile","append_evidence","invalidate","complete","duplicate","stale_mutate")

@dataclass(frozen=True)
class State:
    phase:str="NEW"; fence:int=0; max_fence:int=0; intent:bool=False
    effect_count:int=0; confirmed:bool=False; evidence:bool=False
    evidence_valid:bool=False; ever_done:bool=False

def model_step(s,a):
    if a=="claim": return replace(s,fence=s.max_fence+1,max_fence=s.max_fence+1)
    if a=="intent" and s.fence==s.max_fence and s.phase!="DONE": return replace(s,intent=True,phase="INTENT")
    if a in ("effect_ok","effect_unknown") and s.intent and s.fence==s.max_fence and s.phase in ("INTENT","UNKNOWN"):
        n=s.effect_count+(1 if s.effect_count==0 else 0)
        return replace(s,effect_count=n,confirmed=a=="effect_ok",phase="CONFIRMED" if a=="effect_ok" else "UNKNOWN")
    if a=="reconcile" and s.effect_count==1 and s.phase=="UNKNOWN": return replace(s,confirmed=True,phase="CONFIRMED")
    if a=="append_evidence" and s.confirmed and s.phase!="DONE": return replace(s,evidence=True,evidence_valid=True)
    if a=="invalidate" and s.evidence:
        return replace(s,evidence_valid=False,phase="INVALID" if s.phase=="DONE" else s.phase,ever_done=s.ever_done or s.phase=="DONE")
    if a=="complete" and s.confirmed and s.evidence and s.evidence_valid:return replace(s,phase="DONE",ever_done=True)
    return s

class Adapter:
    def __init__(self, defect=None):
        self.defect=defect
        self.db=tempfile.NamedTemporaryFile(suffix=".db",delete=False).name
        self.c=sqlite3.connect(self.db)
        self.c.row_factory=sqlite3.Row
        self.c.executescript("""CREATE TABLE work(phase TEXT,fence INT,max_fence INT,intent INT,effect_count INT,confirmed INT,evidence INT,evidence_valid INT,ever_done INT);
        INSERT INTO work VALUES('NEW',0,0,0,0,0,0,0,0);""")
    def obs(self):
        r=self.c.execute("select * from work").fetchone()
        return State(r["phase"],r["fence"],r["max_fence"],bool(r["intent"]),r["effect_count"],bool(r["confirmed"]),bool(r["evidence"]),bool(r["evidence_valid"]),bool(r["ever_done"]))
    def _set(self,s):
        self.c.execute("delete from work")
        self.c.execute("insert into work values(?,?,?,?,?,?,?,?,?)",(s.phase,s.fence,s.max_fence,int(s.intent),s.effect_count,int(s.confirmed),int(s.evidence),int(s.evidence_valid),int(s.ever_done)));self.c.commit()
    def step(self,a):
        s=self.obs(); n=model_step(s,a)
        if self.defect=="reopen_done" and a=="duplicate" and s.phase=="DONE": n=replace(s,phase="INTENT",intent=True)
        elif self.defect=="stale_fence" and a=="stale_mutate" and s.max_fence>0 and s.intent: n=replace(s,effect_count=s.effect_count+1)
        elif self.defect=="invalid_completion" and a=="complete" and s.confirmed and s.evidence: n=replace(s,phase="DONE",ever_done=True)
        elif self.defect=="unknown_retry" and a=="effect_unknown" and s.phase=="UNKNOWN": n=replace(s,effect_count=s.effect_count+1)
        elif self.defect=="terminal_invalidation" and a=="invalidate" and s.phase=="DONE": n=replace(s,evidence_valid=False,phase="DONE",ever_done=True)
        self._set(n); return n

def compare(trace, defect=None):
    m=State(); a=Adapter(defect)
    for i,act in enumerate(trace,1):
        m=model_step(m,act); impl=a.step(act)
        if m!=impl:
            fields=[f for f in State.__dataclass_fields__ if getattr(m,f)!=getattr(impl,f)]
            return {"ok":False,"step":i,"action":act,"fields":fields,"model":m.__dict__,"implementation":impl.__dict__}
    return {"ok":True,"steps":len(trace),"state":m.__dict__}

CORPUS=[
["claim","intent","effect_ok","append_evidence","complete"],
["claim","intent","effect_unknown","reconcile","append_evidence","complete"],
["claim","intent","effect_ok","append_evidence","complete","invalidate"],
["claim","intent","effect_ok","append_evidence","complete","duplicate"],
["claim","intent","stale_mutate"],
]

def save_trace(path, trace): Path(path).write_text(json.dumps({"version":1,"trace":trace},sort_keys=True),encoding="utf-8")
def load_trace(path):
    raw=json.loads(Path(path).read_text(encoding="utf-8")); assert raw["version"]==1; return raw["trace"]
