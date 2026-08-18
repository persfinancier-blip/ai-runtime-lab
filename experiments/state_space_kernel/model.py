from dataclasses import dataclass,replace
from collections import deque
import random
@dataclass(frozen=True)
class State:
 phase:str="NEW"; fence:int=0; max_fence:int=0; intent:bool=False; effect_count:int=0; confirmed:bool=False; evidence:bool=False; evidence_valid:bool=False; ever_done:bool=False
ACTIONS=("claim","intent","effect_ok","effect_unknown","reconcile","append_evidence","invalidate","complete","duplicate","stale_mutate")
def step(s,a,variant="correct"):
 if a=="claim": return replace(s,fence=s.max_fence+1,max_fence=s.max_fence+1)
 if a=="intent" and s.fence>0 and s.fence==s.max_fence and s.phase!="DONE": return replace(s,intent=True,phase="INTENT")
 if a in ("effect_ok","effect_unknown") and s.intent and s.fence>0 and s.fence==s.max_fence and s.phase in ("INTENT","UNKNOWN"):
  n=s.effect_count+(1 if s.effect_count==0 else 0)
  return replace(s,effect_count=n,confirmed=a=="effect_ok",phase="CONFIRMED" if a=="effect_ok" else "UNKNOWN")
 if a=="reconcile" and s.effect_count==1 and s.phase=="UNKNOWN": return replace(s,confirmed=True,phase="CONFIRMED")
 if a=="append_evidence" and s.confirmed and s.phase!="DONE": return replace(s,evidence=True,evidence_valid=True)
 if a=="invalidate" and s.evidence:
  return replace(s,evidence_valid=False,phase="INVALID" if s.phase=="DONE" else s.phase,ever_done=s.ever_done or s.phase=="DONE")
 if a=="complete":
  if variant=="split_unsafe" and s.evidence:return replace(s,phase="DONE",ever_done=True)
  if variant!="split_unsafe" and s.confirmed and s.evidence and s.evidence_valid:return replace(s,phase="DONE",ever_done=True)
 if a=="duplicate" and variant=="reopen_unsafe" and s.phase=="DONE":return replace(s,phase="INTENT",intent=True)
 if a=="stale_mutate" and variant=="stale_unsafe" and s.max_fence>0 and s.intent:return replace(s,effect_count=s.effect_count+1)
 return s
def violations(s,prev=None):
 out=[]
 if s.effect_count>1:out.append("duplicate_effect")
 if s.effect_count and not s.intent:out.append("effect_without_intent")
 if s.phase=="DONE" and not(s.confirmed and s.evidence and s.evidence_valid):out.append("done_without_current_evidence")
 if prev and prev.phase=="DONE" and s.phase not in ("DONE","INVALID"):out.append("terminal_reopened")
 return out
def explore(depth=8,variant="correct"):
 q=deque([(State(),[])]);seen={(State(),0)};states=0
 while q:
  s,tr=q.popleft();states+=1
  if len(tr)>=depth:continue
  for a in ACTIONS:
   n=step(s,a,variant);bad=violations(n,s)
   if bad:return {"ok":False,"states":states,"trace":tr+[a],"violations":bad}
   k=(n,len(tr)+1)
   if k not in seen:seen.add(k);q.append((n,tr+[a]))
 return {"ok":True,"states":states,"depth":depth}
def replay(trace,variant):
 s=State()
 for a in trace:
  n=step(s,a,variant);bad=violations(n,s)
  if bad:return bad,n
  s=n
 return [],s
def randomized(seed=17017,runs=1000,steps=20):
 rng=random.Random(seed)
 for i in range(runs):
  s=State();tr=[]
  for _ in range(steps):
   a=rng.choice(ACTIONS);n=step(s,a);bad=violations(n,s);tr.append(a)
   if bad:return {"ok":False,"run":i,"trace":tr,"violations":bad}
   s=n
 return {"ok":True,"seed":seed,"runs":runs,"steps":steps}
