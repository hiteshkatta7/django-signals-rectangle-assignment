from django.test import SimpleTestCase, TransactionTestCase

from . import proofs


class Q1SynchronousTests(SimpleTestCase):
    def test_signal_receivers_run_synchronously(self):
        result = proofs.prove_synchronous(delay=0.5)
        # The receiver finished before send() returned to the caller.
        self.assertEqual(
            result["log"],
            [
                "caller: before send",
                "receiver: started",
                "receiver: finished",
                "caller: after send",
            ],
        )
        self.assertGreaterEqual(result["elapsed_seconds"], 0.5 * 0.9)
        self.assertTrue(result["synchronous"])


class Q2ThreadTests(SimpleTestCase):
    def test_signal_receivers_run_in_callers_thread(self):
        result = proofs.prove_same_thread()
        a, b = result["case_a"], result["case_b"]
        self.assertEqual(a["caller"], a["receiver"])
        self.assertEqual(b["caller"], b["receiver"])
        self.assertEqual(b["receiver"][0], "custom-worker-thread")
        self.assertNotEqual(a["caller"][1], b["caller"][1])
        self.assertTrue(result["same_thread"])


class Q3TransactionTests(TransactionTestCase):
    def test_signal_receivers_share_the_callers_transaction(self):
        result = proofs.prove_same_transaction()
        self.assertEqual(result["control_counts_order_auditlog"], (1, 1))
        # Rolling back the caller's transaction also undid the receiver's write.
        self.assertEqual(result["rollback_counts_order_auditlog"], (0, 0))
        self.assertTrue(result["caller_in_atomic_block"])
        self.assertTrue(result["receiver_in_atomic_block"])
        self.assertTrue(result["same_connection_object"])
        self.assertTrue(result["same_transaction"])
