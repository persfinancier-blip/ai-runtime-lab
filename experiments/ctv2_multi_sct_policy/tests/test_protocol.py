import unittest
from experiments.ctv2_multi_sct_policy.protocol import *
class T(unittest.TestCase):
 def setUp(self):
  self.logs={x.log_id:x for x in [TrustedLog('A','op1',5,b'a'),TrustedLog('B','op2',5,b'b'),TrustedLog('C','op1',5,b'c')]}; self.p=Policy(1,9,5,2,0); self.leaf='leaf-77'
 def ev(self,l,s,a=None): return issue_evidence(self.logs[l],self.leaf,s,a or l+s.value)
 def go(self,ev,p=None,pg=9,tg=5): return evaluate(p or self.p,current_policy_generation=pg,current_trust_generation=tg,trusted_logs=self.logs,expected_leaf_id=self.leaf,evidence=ev)
 def test_distinct(self): self.assertEqual(self.go([self.ev('A',PromiseStatus.FULFILLED),self.ev('B',PromiseStatus.FULFILLED)]).status,ComplianceStatus.COMPLIANT)
 def test_duplicate(self):
  e=self.ev('A',PromiseStatus.FULFILLED); self.assertEqual(self.go([e,e]).status,ComplianceStatus.NONCOMPLIANT)
 def test_unknown(self):
  u=AuditEvidence('Z',self.leaf,PromiseStatus.FULFILLED,5,'z','fake'); d=self.go([self.ev('A',PromiseStatus.FULFILLED),u]); self.assertEqual(d.status,ComplianceStatus.NONCOMPLIANT); self.assertEqual(d.ignored_unknown_logs,('Z',))
 def test_pending(self): self.assertEqual(self.go([self.ev('A',PromiseStatus.FULFILLED),self.ev('B',PromiseStatus.NOT_YET_AUDITABLE)]).status,ComplianceStatus.PENDING)
 def test_violation(self): self.assertEqual(self.go([self.ev('A',PromiseStatus.FULFILLED),self.ev('B',PromiseStatus.FULFILLED),self.ev('C',PromiseStatus.MMD_VIOLATION)]).status,ComplianceStatus.VIOLATION)
 def test_inconclusive(self): self.assertEqual(self.go([self.ev('A',PromiseStatus.FULFILLED),self.ev('B',PromiseStatus.INCONCLUSIVE_AFTER_DEADLINE)]).status,ComplianceStatus.INCONCLUSIVE)
 def test_stale_policy(self):
  with self.assertRaises(StalePolicy): self.go([],pg=10)
 def test_stale_trust(self):
  with self.assertRaises(StaleTrust): self.go([],tg=6)
 def test_operator(self):
  p=Policy(1,9,5,2,2); self.assertEqual(self.go([self.ev('A',PromiseStatus.FULFILLED),self.ev('C',PromiseStatus.FULFILLED)],p).status,ComplianceStatus.NONCOMPLIANT); self.assertEqual(self.go([self.ev('A',PromiseStatus.FULFILLED),self.ev('B',PromiseStatus.FULFILLED)],p).status,ComplianceStatus.COMPLIANT)
 def test_forged(self):
  e=self.ev('A',PromiseStatus.FULFILLED); b=AuditEvidence(e.log_id,e.leaf_id,PromiseStatus.MMD_VIOLATION,e.trust_generation,e.audit_id,e.authenticator)
  with self.assertRaises(ForgedEvidence): self.go([b])
 def test_wrong_leaf(self):
  e=self.ev('A',PromiseStatus.FULFILLED); b=AuditEvidence(e.log_id,'other',e.status,e.trust_generation,e.audit_id,e.authenticator)
  with self.assertRaises(ForgedEvidence): self.go([b])
 def test_conflict(self):
  with self.assertRaises(ForgedEvidence): self.go([self.ev('A',PromiseStatus.FULFILLED,'1'),self.ev('A',PromiseStatus.NOT_YET_AUDITABLE,'2')])
 def test_bool(self):
  with self.assertRaises(PolicyError): Policy(1,True,5,2).validate()
if __name__=='__main__': unittest.main()
