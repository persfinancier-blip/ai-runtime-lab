import json
import os
import socket
import subprocess
import sys
import unittest

from experiments.brokered_credential_use.protocol import *


def _spawn_sender(sender_fd: int, messages: list[dict], *, grandchild_index: int | None = None, delay: float = 0.12):
    code = r'''
import json,os,socket,subprocess,sys,time
fd=int(os.environ["BROKER_FD"])
messages=json.loads(os.environ["MESSAGES"])
grandchild_index=int(os.environ.get("GRANDCHILD_INDEX","-1"))
delay=float(os.environ.get("DELAY","0.12"))
s=socket.socket(fileno=fd)
for i,body in enumerate(messages):
    if i==grandchild_index:
        gcode="import json,os,socket; fd=int(os.environ['BROKER_FD']); socket.socket(fileno=fd).send(json.dumps(json.loads(os.environ['BODY']),sort_keys=True).encode())"
        subprocess.run([sys.executable,"-c",gcode],env={"BROKER_FD":str(fd),"BODY":json.dumps(body),"PATH":os.environ.get("PATH","")},pass_fds=(fd,),check=True)
    else:
        s.send(json.dumps(body,sort_keys=True).encode())
    time.sleep(delay)
time.sleep(1.0)
'''
    env = {
        "BROKER_FD": str(sender_fd),
        "MESSAGES": json.dumps(messages),
        "GRANDCHILD_INDEX": str(-1 if grandchild_index is None else grandchild_index),
        "DELAY": str(delay),
        "PATH": os.environ.get("PATH", ""),
    }
    return subprocess.Popen(
        [sys.executable, "-c", code], env=env, pass_fds=(sender_fd,),
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def req(rid: str, generation: int = 1, task: str = "task", scope: str = "seller-read", payload: str = "x"):
    return {"request_id": rid, "task_id": task, "scope": scope, "credential_generation": generation, "payload": payload}


class Tests(unittest.TestCase):
    def test_kernel_per_message_identity_changes_after_fd_transfer(self):
        broker_sock, sender = credential_socketpair()
        p = _spawn_sender(sender.fileno(), [req("a"), req("b")], grandchild_index=1); sender.close()
        try:
            a = recv_kernel_request(broker_sock); b = recv_kernel_request(broker_sock)
            self.assertEqual(a.sender_pid, p.pid); self.assertNotEqual(b.sender_pid, p.pid); self.assertNotEqual(a.sender_pid, b.sender_pid)
        finally:
            p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_authorized_target_succeeds_but_grandchild_is_rejected(self):
        broker_sock, sender = credential_socketpair()
        p = _spawn_sender(sender.fileno(), [req("target"), req("grand")], grandchild_index=1); sender.close()
        b = CredentialBroker(b"broker-only-secret")
        try:
            permit = b.permit("task", "seller-read", p.pid)
            first = b.execute(recv_kernel_request(broker_sock), permit)
            self.assertEqual(first.outcome, "COMMITTED")
            with self.assertRaises(UnauthorizedSender): b.execute(recv_kernel_request(broker_sock), permit)
            self.assertEqual(b.apply_count, 1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_unsafe_socket_possession_accepts_grandchild(self):
        broker_sock, sender = credential_socketpair()
        p = _spawn_sender(sender.fileno(), [req("target"), req("grand")], grandchild_index=1); sender.close()
        u = UnsafeSocketPossessionBroker()
        try:
            u.execute(recv_kernel_request(broker_sock)); u.execute(recv_kernel_request(broker_sock)); self.assertEqual(u.apply_count, 2)
        finally:
            p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_rotation_revokes_future_old_generation_operation_while_target_lives(self):
        broker_sock, sender = credential_socketpair()
        p = _spawn_sender(sender.fileno(), [req("before", 1), req("after", 1)], delay=0.25); sender.close()
        b = CredentialBroker(b"old")
        try:
            permit = b.permit("task", "seller-read", p.pid); b.execute(recv_kernel_request(broker_sock), permit)
            self.assertIsNone(p.poll()); b.rotate(b"new"); self.assertIsNone(p.poll())
            with self.assertRaises(StaleCredential): b.execute(recv_kernel_request(broker_sock), permit)
            self.assertEqual(b.apply_count, 1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_duplicate_request_is_idempotent(self):
        broker_sock, sender = credential_socketpair(); p = _spawn_sender(sender.fileno(), [req("dup"), req("dup")]); sender.close(); b = CredentialBroker(b"secret")
        try:
            permit=b.permit("task","seller-read",p.pid); a=b.execute(recv_kernel_request(broker_sock),permit); c=b.execute(recv_kernel_request(broker_sock),permit)
            self.assertEqual(a.receipt,c.receipt); self.assertEqual(c.outcome,"ALREADY_COMMITTED"); self.assertEqual(b.apply_count,1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_unknown_after_commit_reconciles_by_request_id(self):
        broker_sock, sender=credential_socketpair(); p=_spawn_sender(sender.fileno(),[req("unknown"),req("unknown")]); sender.close(); b=CredentialBroker(b"secret")
        try:
            permit=b.permit("task","seller-read",p.pid)
            with self.assertRaises(UnknownOutcome): b.execute(recv_kernel_request(broker_sock),permit,timeout_after_commit=True)
            c=b.execute(recv_kernel_request(broker_sock),permit); self.assertEqual(c.outcome,"ALREADY_COMMITTED"); self.assertEqual(b.apply_count,1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_request_id_substitution_is_rejected(self):
        broker_sock, sender=credential_socketpair(); p=_spawn_sender(sender.fileno(),[req("same",payload="a"),req("same",payload="b")]); sender.close(); b=CredentialBroker(b"secret")
        try:
            permit=b.permit("task","seller-read",p.pid); b.execute(recv_kernel_request(broker_sock),permit)
            with self.assertRaises(InvalidRequest): b.execute(recv_kernel_request(broker_sock),permit)
            self.assertEqual(b.apply_count,1)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_wrong_scope_fails_closed(self):
        broker_sock,sender=credential_socketpair(); p=_spawn_sender(sender.fileno(),[req("bad",scope="admin")]); sender.close(); b=CredentialBroker(b"secret")
        try:
            permit=b.permit("task","seller-read",p.pid)
            with self.assertRaises(InvalidRequest): b.execute(recv_kernel_request(broker_sock),permit)
            self.assertEqual(b.apply_count,0)
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

    def test_sender_exit_before_instance_check_fails_closed(self):
        broker_sock,sender=credential_socketpair(); code=r'''import json,os,socket; fd=int(os.environ['BROKER_FD']); socket.socket(fileno=fd).send(json.dumps(json.loads(os.environ['BODY']),sort_keys=True).encode())'''; body=req("late")
        p=subprocess.Popen([sys.executable,"-c",code],env={"BROKER_FD":str(sender.fileno()),"BODY":json.dumps(body),"PATH":os.environ.get("PATH","")},pass_fds=(sender.fileno(),))
        permit_pid=p.pid; permit_start=proc_starttime(p.pid); p.wait(timeout=2); sender.close(); b=CredentialBroker(b"secret"); permit=OperationPermit("task","seller-read",1,permit_pid,permit_start)
        try:
            with self.assertRaises(UnauthorizedSender): b.execute(recv_kernel_request(broker_sock),permit)
        finally: broker_sock.close()

    def test_evidence_contains_no_raw_secret(self):
        secret=b"never-log-this-secret"; broker_sock,sender=credential_socketpair(); p=_spawn_sender(sender.fileno(),[req("safe")]); sender.close(); b=CredentialBroker(secret)
        try:
            permit=b.permit("task","seller-read",p.pid); ev=b.execute(recv_kernel_request(broker_sock),permit); self.assertFalse(b.evidence_contains_secret(ev,secret))
        finally:
            b.close(); p.kill(); p.wait(timeout=2); broker_sock.close()

if __name__ == "__main__": unittest.main()
