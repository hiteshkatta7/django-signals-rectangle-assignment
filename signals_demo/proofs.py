"""Code that conclusively answers the three Django-signals questions.

Each function returns a dict of evidence plus a boolean verdict, so the same
logic is used by the management command (human-readable output) and by the
unit tests (assertions).
"""
import threading
import time

from django.db import transaction

from . import signals
from .models import AuditLog, Order


# ---------------------------------------------------------------------------
# Q1: synchronous or asynchronous?
# ---------------------------------------------------------------------------
def prove_synchronous(delay=1.0):
    """The receiver sleeps for `delay` seconds.

    If Django ran receivers asynchronously, send() would return immediately
    and "caller: after send" would be logged BEFORE "receiver: finished".
    Because Signal.send() simply loops over the receivers and calls each one
    inline, the caller is blocked until the receiver is done.
    """
    log = []
    log.append("caller: before send")
    started = time.monotonic()
    signals.sync_check_signal.send(sender=None, log=log, delay=delay)
    elapsed = time.monotonic() - started
    log.append("caller: after send")

    expected_order = [
        "caller: before send",
        "receiver: started",
        "receiver: finished",
        "caller: after send",
    ]
    return {
        "log": log,
        "elapsed_seconds": elapsed,
        "receiver_delay": delay,
        # 0.9 tolerance guards against coarse sleep timers on some platforms.
        "synchronous": log == expected_order and elapsed >= delay * 0.9,
    }


# ---------------------------------------------------------------------------
# Q2: same thread as the caller?
# ---------------------------------------------------------------------------
def prove_same_thread():
    """Compare the thread id of the caller with the thread id seen inside the
    receiver. Done twice: once from the current thread and once from a
    separately created thread, so the match cannot be a coincidence of
    "everything runs in the main thread"."""
    # Case A: caller is the current thread.
    caller_ident = threading.get_ident()
    caller_name = threading.current_thread().name
    record_a = {}
    signals.thread_check_signal.send(sender=None, record=record_a)

    # Case B: caller is a brand-new worker thread.
    worker = {}

    def run_in_worker():
        worker["caller_ident"] = threading.get_ident()
        worker["caller_name"] = threading.current_thread().name
        record_b = {}
        signals.thread_check_signal.send(sender=None, record=record_b)
        worker["receiver"] = record_b

    thread = threading.Thread(target=run_in_worker, name="custom-worker-thread")
    thread.start()
    thread.join()

    case_a_same = record_a["ident"] == caller_ident
    case_b_same = worker["receiver"]["ident"] == worker["caller_ident"]
    return {
        "case_a": {
            "caller": (caller_name, caller_ident),
            "receiver": (record_a["name"], record_a["ident"]),
        },
        "case_b": {
            "caller": (worker["caller_name"], worker["caller_ident"]),
            "receiver": (worker["receiver"]["name"], worker["receiver"]["ident"]),
        },
        # Case B must also differ from case A, proving the receiver follows
        # the caller's thread rather than always using one fixed thread.
        "same_thread": case_a_same
        and case_b_same
        and worker["caller_ident"] != caller_ident,
    }


# ---------------------------------------------------------------------------
# Q3: same database transaction as the caller?
# ---------------------------------------------------------------------------
class _ForceRollback(Exception):
    pass


def _counts():
    return Order.objects.count(), AuditLog.objects.count()


def _clean():
    Order.objects.all().delete()
    AuditLog.objects.all().delete()


def prove_same_transaction():
    """post_save receiver creates an AuditLog row.

    Control run: caller commits normally -> both rows exist (so the receiver
    does work and writes to the database).
    Rollback run: caller raises inside transaction.atomic() AFTER the receiver
    has written -> BOTH rows disappear. The receiver's write could only be
    undone by the caller's rollback if it was part of the caller's
    transaction (same connection, same atomic block).
    """
    _clean()

    # Control: commit.
    with transaction.atomic():
        Order.objects.create(name="control")
    control_counts = _counts()
    _clean()

    # Rollback.
    caller_conn_id = None
    caller_in_atomic = None
    receiver_state = {}
    signals.RECEIVER_STATE.clear()
    try:
        with transaction.atomic():
            conn = transaction.get_connection()
            caller_conn_id = id(conn)
            caller_in_atomic = conn.in_atomic_block
            Order.objects.create(name="will-be-rolled-back")
            receiver_state = dict(signals.RECEIVER_STATE)
            raise _ForceRollback()
    except _ForceRollback:
        pass
    rollback_counts = _counts()
    _clean()

    return {
        "control_counts_order_auditlog": control_counts,
        "rollback_counts_order_auditlog": rollback_counts,
        "caller_in_atomic_block": caller_in_atomic,
        "receiver_in_atomic_block": receiver_state.get("in_atomic_block"),
        "same_connection_object": receiver_state.get("connection_id") == caller_conn_id,
        "same_transaction": (
            control_counts == (1, 1)
            and rollback_counts == (0, 0)
            and bool(receiver_state.get("in_atomic_block"))
            and receiver_state.get("connection_id") == caller_conn_id
        ),
    }
