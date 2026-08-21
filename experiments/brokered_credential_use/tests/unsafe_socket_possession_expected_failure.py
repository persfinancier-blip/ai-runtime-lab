import unittest
from experiments.brokered_credential_use.tests.test_protocol import _spawn_sender, req
from experiments.brokered_credential_use.protocol import credential_socketpair, recv_kernel_request, UnsafeSocketPossessionBroker

class Unsafe(unittest.TestCase):
    def test_transferred_socket_should_not_authorize_grandchild_but_does(self):
        broker_sock, sender = credential_socketpair()
        p = _spawn_sender(sender.fileno(), [req("target"), req("grand")], grandchild_index=1)
        sender.close()
        broker = UnsafeSocketPossessionBroker()
        try:
            broker.execute(recv_kernel_request(broker_sock))
            broker.execute(recv_kernel_request(broker_sock))
            self.assertEqual(broker.apply_count, 1, "unsafe connection/socket possession authorized the grandchild")
        finally:
            p.kill(); p.wait(timeout=2); broker_sock.close()

if __name__ == "__main__": unittest.main()
