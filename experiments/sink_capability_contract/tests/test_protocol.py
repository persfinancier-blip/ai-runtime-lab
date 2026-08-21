import dataclasses, unittest
from experiments.sink_capability_contract.protocol import *
class Tests(unittest.TestCase):
    def setUp(self): self.a=ProbeAuthority(issuer_id='lab-prober',key=b'probe-secret',generation=7)
    def claim(self,**kw):
        d=dict(sink_id='sink-A',generation=1,mutating=True,stable_idempotency_key=True,request_bound_key=True,reconcile_by_key=True,retention_seconds=3600,source='behavioral+provider-contract'); d.update(kw); return CapabilityClaim(**d)
    def verified(self,claim=None,sink=None):
        claim=claim or self.claim(); sink=sink or SimulatedSink(idempotent=True,request_bound=True,reconcile=True); return VerifiedCapability(claim,self.a.attest(claim,sink))
    def test_same_key_same_request_one_effect(self):
        c=self.verified(); req={'op':'x'}; p=Planner(self.a).plan(c,req,request_id='r1',now=0); s=SimulatedSink(idempotent=True,request_bound=True,reconcile=True); x=BrokerAdapter(self.a).execute(p,c,req,s,now=1); y=BrokerAdapter(self.a).execute(p,c,req,s,now=2); self.assertEqual(x,y); self.assertEqual(len(s.effects),1)
    def test_unknown_reconcile(self):
        c=self.verified(); req={'op':'x'}; p=Planner(self.a).plan(c,req,request_id='r',now=0); s=SimulatedSink(idempotent=True,request_bound=True,reconcile=True); self.assertEqual(BrokerAdapter(self.a).execute(p,c,req,s,now=1,timeout_after_commit=True),'receipt-1'); self.assertEqual(len(s.effects),1)
    def test_unknown_without_reconcile_blocks_without_second_effect(self):
        cl=self.claim(reconcile_by_key=False); c=self.verified(cl,SimulatedSink(idempotent=True,request_bound=True,reconcile=False)); req={'op':'x'}; p=Planner(self.a).plan(c,req,request_id='r',now=0); s=SimulatedSink(idempotent=True,request_bound=True,reconcile=False); self.assertRaises(UnsafeRetryBlocked,BrokerAdapter(self.a).execute,p,c,req,s,now=1,timeout_after_commit=True); self.assertEqual(len(s.effects),1)
    def test_forged_structural_attestation_rejected(self):
        cl=self.claim(); f=CapabilityAttestation(sha(dataclasses.asdict(cl)),7,'lab-prober','0'*64); self.assertRaises(UntrustedCapability,derive_policy,VerifiedCapability(cl,f),self.a,now=0,key_created_at=0)
    def test_claim_substitution_after_attestation_rejected(self):
        cl=self.claim(); att=self.a.attest(cl,SimulatedSink(idempotent=True,request_bound=True,reconcile=True)); changed=dataclasses.replace(cl,reconcile_by_key=False); self.assertRaises(UntrustedCapability,self.a.verify,VerifiedCapability(changed,att))
    def test_false_idempotency_claim_fails_behavior_probe(self): self.assertRaises(UntrustedCapability,self.a.attest,self.claim(),SimulatedSink(idempotent=False,request_bound=False,reconcile=False))
    def test_unknown_retention_is_not_infinite_authority(self):
        c=self.verified(self.claim(retention_seconds=None)); self.assertEqual(derive_policy(c,self.a,now=0,key_created_at=0),'NO_AUTOMATIC_RETRY')
    def test_expired_retention_blocks(self):
        c=self.verified(self.claim(retention_seconds=10)); req={'op':'x'}; p=Planner(self.a).plan(c,req,request_id='r',now=0); self.assertEqual(Planner(self.a).revalidate(p,c,req,now=10),'NO_AUTOMATIC_RETRY')
    def test_clock_rollback_fails_closed(self): self.assertRaises(ClockRollback,derive_policy,self.verified(),self.a,now=9,key_created_at=10)
    def test_generation_change_invalidates_plan(self):
        c=self.verified(); req={'op':'x'}; p=Planner(self.a).plan(c,req,request_id='r',now=0); self.assertRaises(StaleCapability,Planner(self.a).revalidate,p,self.verified(self.claim(generation=2)),req,now=1)
    def test_probe_generation_change_rejected(self):
        c=self.verified(); req={'op':'x'}; p=Planner(self.a).plan(c,req,request_id='r',now=0); b=ProbeAuthority(issuer_id='lab-prober',key=b'new',generation=8); newer=VerifiedCapability(c.claim,b.attest(c.claim,SimulatedSink(idempotent=True,request_bound=True,reconcile=True))); self.assertRaises(UntrustedCapability,Planner(self.a).revalidate,p,newer,req,now=1)
    def test_no_silent_policy_upgrade(self):
        weak=self.verified(self.claim(reconcile_by_key=False),SimulatedSink(idempotent=True,request_bound=True,reconcile=False)); req={'op':'x'}; p=Planner(self.a).plan(weak,req,request_id='r',now=0); strong=self.verified(self.claim(reconcile_by_key=True)); self.assertEqual(Planner(self.a).revalidate(p,strong,req,now=1),'SAFE_RETRY_IDEMPOTENT_ONLY')
    def test_read_only(self):
        cl=self.claim(mutating=False,stable_idempotency_key=False,request_bound_key=False,reconcile_by_key=False,retention_seconds=None); c=self.verified(cl,SimulatedSink(idempotent=False,request_bound=False,reconcile=False)); self.assertEqual(derive_policy(c,self.a,now=0,key_created_at=0),'READ_ONLY')
    def test_non_request_bound_not_safe(self):
        cl=self.claim(request_bound_key=False); c=self.verified(cl,SimulatedSink(idempotent=True,request_bound=False,reconcile=True)); self.assertEqual(derive_policy(c,self.a,now=0,key_created_at=0),'NO_AUTOMATIC_RETRY')
    def test_request_substitution_rejected(self):
        c=self.verified(); p=Planner(self.a).plan(c,{'v':1},request_id='r',now=0); self.assertRaises(RequestMismatch,Planner(self.a).revalidate,p,c,{'v':2},now=1)
    def test_unsafe_generic_retry_duplicates(self):
        s=SimulatedSink(idempotent=False,request_bound=False,reconcile=False); UnsafeGenericRetry().execute({'op':'charge'},s); self.assertEqual(len(s.effects),2)
if __name__=='__main__': unittest.main()
