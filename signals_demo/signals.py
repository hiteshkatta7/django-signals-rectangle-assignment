"""Signals and receivers used by the proofs in proofs.py.

Receivers are registered when this module is imported (see apps.py -> ready()).
"""
import threading
import time

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import AuditLog, Order

# --- Custom signals for Q1 and Q2 (no database involved) --------------------
sync_check_signal = Signal()
thread_check_signal = Signal()


@receiver(sync_check_signal, dispatch_uid="slow_receiver")
def slow_receiver(sender, log, delay, **kwargs):
    """Deliberately slow receiver: if signals were async, send() would
    return before this finishes."""
    log.append("receiver: started")
    time.sleep(delay)
    log.append("receiver: finished")


@receiver(thread_check_signal, dispatch_uid="thread_receiver")
def thread_receiver(sender, record, **kwargs):
    """Records which thread the receiver is executing in."""
    record["ident"] = threading.get_ident()
    record["name"] = threading.current_thread().name


# --- Built-in post_save receiver for Q3 -------------------------------------
# Filled in by the receiver so the proof can inspect what the receiver saw.
RECEIVER_STATE = {}


@receiver(post_save, sender=Order, dispatch_uid="order_audit_receiver")
def order_audit_receiver(sender, instance, created, **kwargs):
    conn = transaction.get_connection()
    RECEIVER_STATE["in_atomic_block"] = conn.in_atomic_block
    RECEIVER_STATE["connection_id"] = id(conn)
    # This write goes through the same connection as the caller's save().
    AuditLog.objects.create(message=f"order '{instance.name}' saved")
