import unittest
from experiments.supervisor_restart.protocol import unsafe_pid_only_alive

class UnsafePidOnly(unittest.TestCase):
    def test_pid_presence_is_not_instance_authority(self):
        self.assertFalse(unsafe_pid_only_alive(1), 'PID presence alone was accepted as durable authority')
