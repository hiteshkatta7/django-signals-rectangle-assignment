from django.core.management.base import BaseCommand

from signals_demo import proofs


class Command(BaseCommand):
    help = "Runs the three Django-signals proofs and prints the evidence."

    def handle(self, *args, **options):
        w = self.stdout.write

        w(self.style.MIGRATE_HEADING("Q1: Are signals synchronous or asynchronous?"))
        r1 = proofs.prove_synchronous()
        for line in r1["log"]:
            w(f"  {line}")
        w(f"  send() blocked for {r1['elapsed_seconds']:.2f}s "
          f"(receiver sleeps {r1['receiver_delay']}s)")
        w(f"  => SYNCHRONOUS: {r1['synchronous']}\n")

        w(self.style.MIGRATE_HEADING("Q2: Do signals run in the caller's thread?"))
        r2 = proofs.prove_same_thread()
        for label, case in (("A (current thread)", r2["case_a"]),
                            ("B (new worker thread)", r2["case_b"])):
            w(f"  Case {label}")
            w(f"    caller   thread: {case['caller']}")
            w(f"    receiver thread: {case['receiver']}")
        w(f"  => SAME THREAD: {r2['same_thread']}\n")

        w(self.style.MIGRATE_HEADING("Q3: Same database transaction as the caller?"))
        r3 = proofs.prove_same_transaction()
        w(f"  (Order, AuditLog) rows after normal commit : "
          f"{r3['control_counts_order_auditlog']}")
        w(f"  (Order, AuditLog) rows after caller rollback: "
          f"{r3['rollback_counts_order_auditlog']}")
        w(f"  caller in atomic block   : {r3['caller_in_atomic_block']}")
        w(f"  receiver in atomic block : {r3['receiver_in_atomic_block']}")
        w(f"  same connection object   : {r3['same_connection_object']}")
        w(f"  => SAME TRANSACTION: {r3['same_transaction']}")
