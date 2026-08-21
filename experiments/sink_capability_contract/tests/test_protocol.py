import unittest
from experiments.sink_capability_contract.protocol import *
def cap(**kw):
    d=dict(sink_id='sink-A',generation=1,mutating=True,stable_idempotency_key=True,request_bound_key=True,reconcile_by_key=True,retention_seconds=3600,source='behavioral+docs',observed=True,behavioral_probe_passed=True); d.update(kw); return SinkCapability(**d)
class Tests(unittest.TestCase):
    def test_same_key_same_request_one_effect(self):
        c=cap(); req={'op':'x'}; p=Planner().plan(c,req,request_id='r1',now=0); s=SimulatedSink(idempotent=True,request_bound=True,reconcile=True); a=BrokerAdapter().execute(p,c,req,s,now=1); b=BrokerAdapter().execute(p,c,req,s,now=2); self.assertEqual(a,b); self.assertEqual(len(s.effects),1)
    def test_same_key_different_request_rejected(self):
        c=cap(); p=Planner().plan(c,{'v':1},request_id='r',now=0); self.assertRaises(RequestMismatch,Planner().revalidate,p,c,{'v':2},now=1)
    def test_unknown_reconcile(self):
        c=cap(); req={'op':'x'}; p=Planner().plan(c,req,request_id='r',now=0); s=SimulatedSink(idempotent=True,request_bound=True,reconcile=True); self.assertEqual(BrokerAdapter().execute(p,c,req,s,now=1,timeout_after_commit=True),'receipt-1'); self.assertEqual(len(s.effects),1)
    def test_unknown_without_reconcile_blocks(self):
        c=cap(reconcile_by_key=False); req={'op':'x'}; p=Planner().plan(c,req,request_id='r',now=0); s=SimulatedSink(idempotent=True,request_bound=True,reconcile=False); self.assertRaises(UnsafeRetryBlocked,BrokerAdapter().execute,p,c,req,s,now=1,timeout_after_commit=True); self.assertEqual(len(s.effects),1)
    def test_expired_retention_blocks(self):
        c=cap(retention_seconds=10); req={'op':'x'}; p=Planner().plan(c,req,request_id='r',now=0); self.assertEqual(Planner().revalidate(p,c,req,now=10),'NO_AUTOMATIC_RETRY')
    def test_unobserved_claim_not_trusted(self): self.assertEqual(derive_policy(cap(observed=False,behavioral_probe_passed=False),now=0,key_created_at=0),'NO_AUTOMATIC_RETRY')
    def test_failed_probe_not_trusted(self): self.assertEqual(derive_policy(cap(behavioral_probe_passed=False),now=0,key_created_at=0),'NO_AUTOMATIC_RETRY')
    def test_generation_change_invalidates_plan(self):
        c=cap(); req={'op':'x'}; p=Planner().plan(c,req,request_id='r',now=0); self.assertRaises(StaleCapability,Planner().revalidate,p,cap(generation=2),req,now=1)
    def test_no_silent_policy_upgrade(self):
        weak=cap(reconcile_by_key=False); req={'op':'x'}; p=Planner().plan(weak,req,request_id='r',now=0); self.assertEqual(Planner().revalidate(p,cap(reconcile_by_key=True),req,now=1),'SAFE_RETRY_IDEMPOTENT_ONLY')
    def test_read_only(self): self.assertEqual(derive_policy(cap(mutating=False,stable_idempotency_key=False,request_bound_key=False,reconcile_by_key=False),now=0,key_created_at=0),'READ_ONLY')
    def test_non_request_bound_not_safe(self): self.assertEqual(derive_policy(cap(request_bound_key=False),now=0,key_created_at=0),'NO_AUTOMATIC_RETRY')
    def test_unsafe_generic_retry_duplicates(self):
        s=SimulatedSink(idempotent=False,request_bound=False,reconcile=False); UnsafeGenericRetry().execute({'op':'charge'},s); self.assertEqual(len(s.effects),2)
if __name__=='__main__': unittest.main()
