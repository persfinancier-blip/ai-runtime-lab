import importlib
import sys
import types
import unittest
from dataclasses import dataclass, replace

import experiments
from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    ProviderUnavailable,
    SignedAnchorProvider,
    receipt_ref,
)

shared_pkg = types.ModuleType("experiments.shared_anchor_intent_ledger")
shared = types.ModuleType("experiments.shared_anchor_intent_ledger.protocol")
class Intent:
    def __init__(self, intent_id): self.intent_id=intent_id
class IntentSubstitution(RuntimeError): pass
class PendingIntent(RuntimeError): pass
shared.Intent=Intent; shared.IntentSubstitution=IntentSubstitution; shared.PendingIntent=PendingIntent
sys.modules["experiments.shared_anchor_intent_ledger"]=shared_pkg
sys.modules["experiments.shared_anchor_intent_ledger.protocol"]=shared
setattr(experiments,"shared_anchor_intent_ledger",shared_pkg)
setattr(shared_pkg,"protocol",shared)

@dataclass(frozen=True)
class Entry:
    intent_id:str
    position:int
    request_id:str
    status:str="PREPARED"
    receipt_binding:str|None=None

parent_mod=types.ModuleType("experiments.mutable_shared_anchor_writer.operation_scoped_integration")
class Parent:
    def reserve(self,intent): return self.current
    def _runtime_matches_entry(self,entry): return True
    def _reauthenticate(self,entry):
        c=self.attested.challenge()
        obs=self.attested.provider.reconcile_increment(challenge=c,request_id=entry.request_id)
        if obs is None: raise ProviderUnavailable("provider result unavailable")
        verified=self.attested.verifier.verify(obs,expected_challenge=c,allowed_kinds={"RECONCILE"})
        return receipt_ref(verified)
    def _commit_confirmation(self,intent_id,entry,receipt):
        self.current=replace(entry,status="CONFIRMED",receipt_binding=receipt)
        return self.current
parent_mod.SupportedOperationScopedAsymmetricSharedAnchorLedger=Parent
sys.modules["experiments.mutable_shared_anchor_writer.operation_scoped_integration"]=parent_mod

# reload exact module after stubs are installed
sys.modules.pop("experiments.mutable_shared_anchor_writer.convergent_operation_scoped",None)
m=importlib.import_module("experiments.mutable_shared_anchor_writer.convergent_operation_scoped")
ExactLedger=m.SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger

class Ledger(ExactLedger):
    def _commit_confirmation(self,intent_id,entry,receipt):
        self.current=replace(entry,status="CONFIRMED",receipt_binding=receipt)
        return self.current

class CommitThenLoseFirstReconcile(SignedAnchorProvider):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.fail_reconcile_once=True
    def reconcile_increment(self,*,challenge,request_id):
        if self.fail_reconcile_once:
            self.fail_reconcile_once=False
            raise ProviderUnavailable("first reconciliation path unavailable")
        return super().reconcile_increment(challenge=challenge,request_id=request_id)

class UnknownRecoveryTests(unittest.TestCase):
    def test_timeout_after_commit_remains_pending_then_retry_converges_without_reincrement(self):
        provider=CommitThenLoseFirstReconcile(value=0)
        verifier=AttestationVerifier({("anchor-A",1):b"k1"},ProviderIdentity("anchor-A",1))
        ledger=Ledger.__new__(Ledger)
        ledger.attested=AttestedCatchup(provider,verifier)
        ledger.current=Entry("intent-1",1,"request-1")
        intent=Intent("intent-1")

        with self.assertRaises(PendingIntent):
            ledger.execute(intent,timeout_after_commit=True)

        self.assertEqual(provider.value,1)
        self.assertEqual(provider.increment_calls,1)
        self.assertEqual(ledger.current.status,"PREPARED")

        out=ledger.execute(intent)
        self.assertEqual(out.status,"CONFIRMED")
        self.assertIsNotNone(out.receipt_binding)
        self.assertEqual(provider.value,1)
        self.assertEqual(provider.increment_calls,1)

if __name__=="__main__":
    unittest.main()
