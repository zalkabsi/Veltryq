"""Fixed concurrent-retry contract, executed in disposable databases/schemas."""

from __future__ import annotations

import os
from collections import defaultdict
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
from typing import Literal
from uuid import uuid4

from app.refunds import RefundService
from app.storage import Storage
from veltryq.fixtures.refund_vulnerable import FixtureRefundService

Implementation = Literal["vulnerable", "repaired"]


@contextmanager
def isolated_storage(*, repaired: bool, database_url: str | None = None) -> Iterator[Storage]:
    url = database_url or os.getenv("VELTRYQ_TEST_DATABASE_URL")
    with TemporaryDirectory(prefix="veltryq-") as directory:
        schema = "veltryq_" + uuid4().hex if url and url.startswith("postgresql") else None
        storage = Storage(url or Path(directory) / "scenario.db", repaired=repaired, schema=schema)
        try:
            storage.initialize()
            yield storage
        finally:
            storage.close(drop_test_schema=True)


def run_baseline(
    database_url: str | None = None, *, implementation: str = "vulnerable"
) -> dict[str, object]:
    """Ordinary sequential assertions pass even against the vulnerable fixture."""
    with isolated_storage(
        repaired=implementation == "repaired", database_url=database_url
    ) as storage:
        service = (FixtureRefundService if implementation == "vulnerable" else RefundService)(
            storage
        )
        payment_id = str(service.create_payment(10_000)["id"])
        service.capture_payment(payment_id)
        first = service.request_refund(payment_id, 2_500, "baseline")
        replay = service.request_refund(payment_id, 2_500, "baseline")
        history = service.history(payment_id)
        passed = first["id"] == replay["id"] and len(history["refunds"]) == 1
        return {
            "verdict": "passed" if passed else "failed",
            "refund_count": len(history["refunds"]),
            "total_refunded_minor": history["payment"]["refunded_minor"],
            "database": storage.dialect,
        }


def evaluate_state(
    refunds: list[dict], entries: list[dict], captured_amount_minor: int
) -> list[str]:
    violations = []
    keys = [(r["payment_id"], r["idempotency_key"]) for r in refunds]
    if len(keys) != len(set(keys)):
        violations.append("FIN-IDEMPOTENCY")
    if sum(int(r["amount_minor"]) for r in refunds) > captured_amount_minor:
        violations.append("FIN-REFUND-LIMIT")
    # Check every refund and currency separately: aggregate errors must not cancel.
    balances: dict[tuple, int] = defaultdict(int)
    counts: dict[tuple, int] = defaultdict(int)
    for entry in entries:
        key = (entry["refund_id"], entry["currency"])
        balances[key] += int(entry["amount_minor"]) * (1 if entry["side"] == "debit" else -1)
        counts[key] += 1
    refund_ids = {r["id"] for r in refunds}
    if (
        any(balances.values())
        or any(n != 2 for n in counts.values())
        or {key[0] for key in counts} != refund_ids
    ):
        violations.append("FIN-LEDGER-BALANCE")
    return violations


def run_duplicate_refund_scenario(
    implementation: Implementation,
    *,
    captured_amount_minor: int = 10_000,
    database_url: str | None = None,
    service_class: type[RefundService] | None = None,
) -> dict[str, object]:
    with isolated_storage(
        repaired=implementation == "repaired", database_url=database_url
    ) as storage:
        service_type = service_class or (
            FixtureRefundService if implementation == "vulnerable" else RefundService
        )
        service = service_type(storage)
        payment_id = str(service.create_payment(captured_amount_minor, "USD")["id"])
        service.capture_payment(payment_id)
        barrier = Barrier(2)

        def request() -> dict[str, object]:
            return service.request_refund(
                payment_id,
                captured_amount_minor,
                "demo-retry-001",
                preflight_barrier=barrier,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(request) for _ in range(2)]
            results, errors = [], []
            for future in futures:
                try:
                    results.append(future.result(timeout=20))
                except Exception as exc:  # noqa: BLE001 -- failed requests make the run inconclusive.
                    # Avoid copying database errors/connection details into public artifacts.
                    errors.append(type(exc).__name__ + ": concurrent request failed")
        history = service.history(payment_id)
        refunds = history["refunds"]
        entries = [e for e in history["ledger_entries"] if e["refund_id"]]
        violations = evaluate_state(refunds, entries, captured_amount_minor)
        complete = not errors and len(results) == 2 and len(refunds) >= 1
        return {
            "implementation": implementation,
            "payment_id": payment_id,
            "currency": "USD",
            "captured_amount_minor": captured_amount_minor,
            "requested_amount_minor_per_call": captured_amount_minor,
            "concurrent_requests": 2,
            "successful_responses": len(results),
            "errors": errors,
            "refund_count": len(refunds),
            "refund_ids": [r["id"] for r in refunds],
            "total_refunded_minor": sum(int(r["amount_minor"]) for r in refunds),
            "refund_ledger_entry_count": len(entries),
            "refund_debit_minor": sum(
                int(e["amount_minor"]) for e in entries if e["side"] == "debit"
            ),
            "refund_credit_minor": sum(
                int(e["amount_minor"]) for e in entries if e["side"] == "credit"
            ),
            "refunds": refunds,
            "ledger_entries": entries,
            "database": storage.dialect,
            "database_version": ".".join(
                map(str, storage.engine.dialect.server_version_info or ())
            ),
            "violations": violations,
            "verdict": ("confirmed_violation" if violations else "passed")
            if complete
            else "inconclusive",
        }
