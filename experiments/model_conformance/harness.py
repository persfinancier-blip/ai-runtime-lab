from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import tempfile

from experiments.state_space_kernel.model import ACTIONS, State, step as model_step
from experiments.transactional_kernel.kernel import InvalidCompletion, Kernel, StaleFence

WORK_ID = "work-1"; OWNER = "worker"; EFFECT_KEY = "work-1:effect:v1"; EVIDENCE_ID = "ev-1"

class KernelAdapter:
    """Drive the real LAB-015 SQLite kernel with LAB-017 action vocabulary."""
    def __init__(self, defect: str | None = None):
        self.defect=defect; self._tmp=tempfile.TemporaryDirectory(); self.db=Path(self._tmp.name)/"kernel.db"
        self.kernel=Kernel(self.db); self.kernel.ensure_work(WORK_ID); self.fence=0; self.effect_count=0
        self.external_receipt: str|None=None; self.ever_done=False
    def close(self): self._tmp.cleanup()
    def _evidence(self):
        c=sqlite3.connect(self.db); row=c.execute("SELECT valid FROM evidence WHERE evidence_id=?",(EVIDENCE_ID,)).fetchone(); c.close()
        return (row is not None, bool(row[0]) if row else False)
    def observe(self):
        row=self.kernel.state(WORK_ID); evidence,evidence_valid=self._evidence()
        if row["phase"]=="DONE": self.ever_done=True
        return State(phase=row["phase"],fence=row["fence"],max_fence=row["fence"],intent=row["effect_key"] is not None,
                     effect_count=self.effect_count,confirmed=row["effect_receipt"] is not None,evidence=evidence,
                     evidence_valid=evidence_valid,ever_done=self.ever_done)
    def _raw(self,sql,args=()):
        c=sqlite3.connect(self.db); c.execute(sql,args); c.commit(); c.close()
    def step(self,action):
        before=self.observe()
        try:
            if action=="claim": self.fence,_=self.kernel.claim(WORK_ID,OWNER)
            elif action=="intent": self.kernel.prepare_intent(WORK_ID,OWNER,self.fence,EFFECT_KEY)
            elif action in ("effect_ok","effect_unknown"):
                if before.intent and before.phase in ("INTENT","UNKNOWN"):
                    if self.effect_count==0: self.effect_count=1; self.external_receipt="receipt-1"
                    elif self.defect=="unknown_retry" and before.phase=="UNKNOWN": self.effect_count+=1
                    if action=="effect_ok": self.kernel.confirm_effect(WORK_ID,OWNER,self.fence,self.external_receipt or "receipt-1")
                    else: self.kernel.mark_unknown(WORK_ID,OWNER,self.fence)
            elif action=="reconcile" and before.phase=="UNKNOWN" and self.external_receipt:
                self.kernel.confirm_effect(WORK_ID,OWNER,self.fence,self.external_receipt)
            elif action=="append_evidence" and before.confirmed and before.phase not in ("DONE","INVALID"):
                self.kernel.append_evidence(WORK_ID,EVIDENCE_ID,"v1")
            elif action=="invalidate":
                if self.defect=="terminal_invalidation" and before.phase=="DONE": self._raw("UPDATE evidence SET valid=0 WHERE evidence_id=?",(EVIDENCE_ID,))
                else: self.kernel.invalidate(EVIDENCE_ID)
            elif action=="complete":
                if self.defect=="invalid_completion" and before.confirmed and before.evidence:
                    self._raw("UPDATE work SET phase='DONE', done_evidence_id=? WHERE work_id=?",(EVIDENCE_ID,WORK_ID))
                elif before.phase=="CONFIRMED" and before.confirmed and before.evidence and before.evidence_valid:
                    self.kernel.complete(WORK_ID,OWNER,self.fence,EVIDENCE_ID)
            elif action=="duplicate":
                if self.defect=="reopen_done" and before.phase=="DONE": self._raw("UPDATE work SET phase='INTENT' WHERE work_id=?",(WORK_ID,))
            elif action=="stale_mutate":
                if self.defect=="stale_fence" and before.max_fence>0 and before.intent: self._raw("UPDATE work SET effect_receipt='stale' WHERE work_id=?",(WORK_ID,))
                elif before.max_fence>0 and before.intent: self.kernel.confirm_effect(WORK_ID,OWNER,max(0,self.fence-1),"stale")
        except (InvalidCompletion,StaleFence): pass
        return self.observe()

def compare(trace,defect=None):
    model=State(); adapter=KernelAdapter(defect)
    try:
        for index,action in enumerate(trace,1):
            model=model_step(model,action); implementation=adapter.step(action)
            if model!=implementation:
                fields=[f for f in State.__dataclass_fields__ if getattr(model,f)!=getattr(implementation,f)]
                return {"ok":False,"step":index,"action":action,"fields":fields,"model":asdict(model),"implementation":asdict(implementation),"prefix":trace[:index]}
        return {"ok":True,"steps":len(trace),"state":asdict(model)}
    finally: adapter.close()

def bounded_traces(depth=4):
    traces=[[]]; frontier=[[]]
    for _ in range(depth):
        frontier=[prefix+[action] for prefix in frontier for action in ACTIONS]; traces.extend(frontier)
    return traces

CORPUS=[["claim","intent","effect_ok","append_evidence","complete"],
        ["claim","intent","effect_unknown","reconcile","append_evidence","complete"],
        ["claim","intent","effect_ok","append_evidence","complete","invalidate"],
        ["claim","intent","effect_ok","append_evidence","complete","duplicate"],
        ["claim","intent","stale_mutate"]]

def save_trace(path,trace): Path(path).write_text(json.dumps({"version":1,"trace":trace},sort_keys=True),encoding="utf-8")
def load_trace(path):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("version")!=1: raise ValueError(f"unsupported trace version: {raw.get('version')}")
    return list(raw["trace"])
