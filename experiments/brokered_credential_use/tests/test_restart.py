import json, os, socket, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from experiments.brokered_credential_use.protocol import *

def req(rid,generation=1,payload='x'):
    return {'request_id':rid,'task_id':'task','scope':'seller-read','credential_generation':generation,'payload':payload}

def spawn(fd,messages,delay=.2):
    code=r'''import json,os,socket,time
fd=int(os.environ['BROKER_FD']); msgs=json.loads(os.environ['MESSAGES']); delay=float(os.environ['DELAY']); s=socket.socket(fileno=fd)
for m in msgs:
 s.send(json.dumps(m,sort_keys=True).encode()); time.sleep(delay)
time.sleep(1.5)
'''
    env={'BROKER_FD':str(fd),'MESSAGES':json.dumps(messages),'DELAY':str(delay),'PATH':os.environ.get('PATH','')}
    return subprocess.Popen([sys.executable,'-c',code],env=env,pass_fds=(fd,),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

class RestartTests(unittest.TestCase):
    def test_unknown_rotate_exact_retry_returns_prior_receipt(self):
        bs,s=credential_socketpair(); p=spawn(s.fileno(),[req('r'),req('r')]); s.close()
        try:
            b=CredentialBroker(b'old'); permit=b.permit('task','seller-read',p.pid)
            first=recv_kernel_request(bs)
            with self.assertRaises(UnknownOutcome): b.execute(first,permit,timeout_after_commit=True)
            prior=b._effects['r'][1]; b.rotate(b'new')
            ev=b.execute(recv_kernel_request(bs),permit)
            self.assertEqual(ev.outcome,'ALREADY_COMMITTED'); self.assertEqual(ev.receipt,prior); self.assertEqual(b.apply_count,1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); bs.close()

    def test_substitution_after_rotation_is_rejected(self):
        bs,s=credential_socketpair(); p=spawn(s.fileno(),[req('r',payload='a'),req('r',payload='b')]); s.close()
        try:
            b=CredentialBroker(b'old'); permit=b.permit('task','seller-read',p.pid); b.execute(recv_kernel_request(bs),permit); b.rotate(b'new')
            with self.assertRaises(InvalidRequest): b.execute(recv_kernel_request(bs),permit)
            self.assertEqual(b.apply_count,1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); bs.close()

    def test_restart_reacquires_fresh_pidfd_and_preserves_idempotency(self):
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'broker.json'; bs,s=credential_socketpair(); p=spawn(s.fileno(),[req('r'),req('r')],delay=.35); s.close()
            b1=CredentialBroker(b'secret',state_path=state)
            try:
                permit1=b1.permit('task','seller-read',p.pid)
                with self.assertRaises(UnknownOutcome): b1.execute(recv_kernel_request(bs),permit1,timeout_after_commit=True)
                b1.close()
                b2=CredentialBroker(b'secret',state_path=state)
                try:
                    self.assertEqual(b2._pidfds,{})
                    permit2=b2.reacquire_permit('task','seller-read')
                    self.assertTrue(b2._pidfds)
                    ev=b2.execute(recv_kernel_request(bs),permit2)
                    self.assertEqual(ev.outcome,'ALREADY_COMMITTED'); self.assertEqual(b2.apply_count,1)
                finally:b2.close()
            finally:
                b1.close(); p.kill(); p.wait(timeout=2); bs.close()

    def test_restart_does_not_accept_caller_supplied_pid(self):
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'broker.json'; bs,s=credential_socketpair(); p=spawn(s.fileno(),[req('x')]); s.close()
            b1=CredentialBroker(b'secret',state_path=state)
            try:
                b1.permit('task','seller-read',p.pid); b1.close(); b2=CredentialBroker(b'secret',state_path=state)
                try:
                    with self.assertRaises(UnauthorizedSender): b2.reacquire_permit('other-task','seller-read')
                finally:b2.close()
            finally:p.kill(); p.wait(timeout=2); bs.close()

    def test_unknown_rotate_restart_exact_retry_returns_prior_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'broker.json'; bs,s=credential_socketpair(); p=spawn(s.fileno(),[req('r'),req('r')],delay=.35); s.close()
            b1=CredentialBroker(b'old',state_path=state)
            try:
                permit1=b1.permit('task','seller-read',p.pid)
                with self.assertRaises(UnknownOutcome):
                    b1.execute(recv_kernel_request(bs),permit1,timeout_after_commit=True)
                prior=b1._effects['r'][1]
                b1.rotate(b'new')
                b1.close()
                b2=CredentialBroker(b'new',generation=2,state_path=state)
                try:
                    permit2=b2.reacquire_permit('task','seller-read')
                    ev=b2.execute(recv_kernel_request(bs),permit2)
                    self.assertEqual(ev.outcome,'ALREADY_COMMITTED')
                    self.assertEqual(ev.receipt,prior)
                    self.assertEqual(b2.apply_count,1)
                finally:
                    b2.close()
            finally:
                b1.close(); p.kill(); p.wait(timeout=2); bs.close()

    def test_restart_rejects_wrong_supplied_credential_generation(self):
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'broker.json'; b1=CredentialBroker(b'old',state_path=state)
            try:
                b1.rotate(b'new')
            finally:
                b1.close()
            with self.assertRaises(StaleCredential):
                CredentialBroker(b'old',generation=1,state_path=state)

    def test_malformed_durable_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'broker.json'
            malformed = [
                {'schema_version':True,'generation':1,'permits':[],'effects':{},'apply_count':0},
                {'schema_version':1,'generation':1,'permits':[],'effects':{'r':{'request_digest':123,'receipt':[]}},'apply_count':1},
                {'schema_version':1,'generation':1,'permits':[{'task_id':[], 'scope':'seller-read','credential_generation':1,'target_pid':1,'target_starttime':1}],'effects':{},'apply_count':0},
                {'schema_version':1,'generation':1,'permits':[],'effects':{},'apply_count':1},
            ]
            for raw in malformed:
                state.write_text(json.dumps(raw))
                with self.subTest(raw=raw):
                    with self.assertRaises(DurableStateError):
                        CredentialBroker(b'secret',state_path=state)

    def test_durable_state_contains_no_secret(self):
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'broker.json'; bs,s=credential_socketpair(); p=spawn(s.fileno(),[req('x')]); s.close(); secret=b'raw-secret-never-persist'
            b=CredentialBroker(secret,state_path=state)
            try:
                permit=b.permit('task','seller-read',p.pid); b.execute(recv_kernel_request(bs),permit)
                self.assertNotIn(secret.decode(),state.read_text())
            finally:b.close(); p.kill(); p.wait(timeout=2); bs.close()

if __name__=='__main__': unittest.main()
