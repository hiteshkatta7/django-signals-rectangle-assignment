# Django Signals + Custom Rectangle Class

Assignment submission as a Django project.

   **GitHub link:** https://github.com/hiteshkatta7/django-signals-rectangle-assignment  *(replace with your real repository URL after pushing)*

## Project layout

```
manage.py
assignment/            Django project (settings, urls, wsgi, asgi)
signals_demo/          Q1-Q3: Django signals proofs
    models.py          Order, AuditLog (used by the Q3 proof)
    signals.py         signals + receivers
    proofs.py          the code that proves each answer
    tests.py           unit tests asserting each proof
    management/commands/run_proofs.py   prints the evidence
shapes/                Rectangle class
    rectangle.py       Rectangle implementation
    tests.py           unit tests
```

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test              # runs every proof and Rectangle test
python manage.py run_proofs        # prints human-readable evidence for Q1-Q3
```

---

## Q1: Are Django signals synchronous or asynchronous by default?

**Synchronous.** `Signal.send()` calls each receiver inline, one after another, in the caller's flow, and only returns once every receiver has finished.

**Proof** (`signals_demo/proofs.py::prove_synchronous`): the receiver sleeps for 1 second. The log order is

```
caller: before send
receiver: started
receiver: finished
caller: after send        <- only after the receiver is done
```

and `send()` blocks for roughly the sleep duration. If signals were asynchronous, "caller: after send" would appear before "receiver: finished" and `send()` would return almost instantly.

## Q2: Do signals run in the same thread as the caller?

**Yes.** The receiver runs on whatever thread called `send()`.

**Proof** (`prove_same_thread`): the receiver records `threading.get_ident()`. The proof sends the signal from the main thread (receiver reports the main thread id) and again from a newly created thread named `custom-worker-thread` (receiver reports that worker's id, which differs from the main thread's). The receiver always matches the caller, never a fixed or separate thread.

## Q3: By default, do signals run in the same database transaction as the caller?

**Yes.** Receivers run on the caller's database connection and do not open a transaction of their own, so they take part in whatever transaction the caller has open (an `atomic()` block, `ATOMIC_REQUESTS`, etc.).

**Proof** (`prove_same_transaction`): a `post_save` receiver on `Order` creates an `AuditLog` row.

- Control: caller saves an `Order` and commits, giving `(Order, AuditLog)` counts of `(1, 1)`, so the receiver really writes.
- Rollback: the caller saves an `Order` inside `transaction.atomic()`, then raises an exception. Counts afterwards are `(0, 0)`. The receiver's `AuditLog` row was rolled back together with the caller's `Order`, which is only possible if both writes were in the same transaction.
- The receiver also reports `in_atomic_block == True` and the same connection object as the caller.

Note: with no surrounding `atomic()` (plain autocommit), each statement commits on its own, but the receiver still uses the caller's connection and never gets a separate transaction.

---

## Rectangle class (`shapes/rectangle.py`)

```python
>>> from shapes.rectangle import Rectangle
>>> list(Rectangle(10, 5))
[{'length': 10}, {'width': 5}]
>>> for side in Rectangle(10, 5):
...     print(side)
{'length': 10}
{'width': 5}
```

- Requires `length: int` and `width: int` (a `TypeError` is raised for missing or non-int values).
- Iterable: yields `{'length': <value>}` first, then `{'width': <value>}`.
