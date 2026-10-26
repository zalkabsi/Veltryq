from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app.models import Refund
from app.refunds import (
    IdempotencyConflict,
    InvalidTransition,
    PaymentNotFound,
    RefundLimitExceeded,
    RefundService,
)
from app.storage import Storage


class RefundServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.storage = Storage(Path(self.temporary_directory.name) / "test.db", repaired=True)
        self.storage.initialize()
        self.service = RefundService(self.storage)

    def tearDown(self) -> None:
        self.storage.close()
        self.temporary_directory.cleanup()

    def test_fractional_boolean_and_unbounded_amounts_are_rejected(self) -> None:
        for value in (True, 1.5, "100", 0, -1, 10**19):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.service.create_payment(value)

    def test_refund_failure_rolls_back_balance_refund_and_ledger(self) -> None:
        payment_id = self.captured_payment()
        with (
            patch.object(
                self.service, "_post_pair", side_effect=RuntimeError("injected ledger failure")
            ),
            self.assertRaises(RuntimeError),
        ):
            self.service.request_refund(payment_id, 2500, "rollback")
        history = self.service.history(payment_id)
        self.assertEqual(history["payment"]["refunded_minor"], 0)
        self.assertEqual(history["refunds"], [])
        self.assertEqual(len(history["ledger_entries"]), 2)

    def test_capture_failure_rolls_back_state_and_ledger(self) -> None:
        payment_id = str(self.service.create_payment(100)["id"])
        with (
            patch.object(self.service, "_post_pair", side_effect=RuntimeError("injected failure")),
            self.assertRaises(RuntimeError),
        ):
            self.service.capture_payment(payment_id)
        history = self.service.history(payment_id)
        self.assertEqual(history["payment"]["state"], "authorized")
        self.assertEqual(history["ledger_entries"], [])

    def captured_payment(self, amount_minor: int = 10_000) -> str:
        payment = self.service.create_payment(amount_minor, "USD")
        payment_id = str(payment["id"])
        self.service.capture_payment(payment_id)
        return payment_id

    def test_create_capture_and_refund_posts_balanced_ledger(self) -> None:
        payment_id = self.captured_payment()
        refund = self.service.request_refund(payment_id, 2_500, "refund-1")
        history = self.service.history(payment_id)
        refund_entries = [entry for entry in history["ledger_entries"] if entry["refund_id"]]
        debits = sum(entry["amount_minor"] for entry in refund_entries if entry["side"] == "debit")
        credits = sum(
            entry["amount_minor"] for entry in refund_entries if entry["side"] == "credit"
        )
        self.assertEqual(refund["amount_minor"], 2_500)
        self.assertEqual(len(history["refunds"]), 1)
        self.assertEqual(debits, credits)
        self.assertEqual(debits, 2_500)

    def test_same_key_and_payload_replays_one_refund(self) -> None:
        payment_id = self.captured_payment()
        first = self.service.request_refund(payment_id, 2_500, "retry-1")
        second = self.service.request_refund(payment_id, 2_500, "retry-1")
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(len(self.service.history(payment_id)["refunds"]), 1)

    def test_database_uniqueness_blocks_a_duplicate_outside_the_service(self) -> None:
        payment_id = self.captured_payment()
        first = self.service.request_refund(payment_id, 2500, "unique-key")
        with self.assertRaises(IntegrityError), self.storage.transaction() as session:
            session.add(
                Refund(
                    id=str(uuid4()),
                    payment_id=payment_id,
                    idempotency_key="unique-key",
                    request_hash=first["request_hash"],
                    amount_minor=2500,
                    created_at=first["created_at"],
                )
            )
            session.flush()
        self.assertEqual(len(self.service.history(payment_id)["refunds"]), 1)

    def test_same_key_with_conflicting_payload_is_rejected(self) -> None:
        payment_id = self.captured_payment()
        self.service.request_refund(payment_id, 2_500, "retry-1")
        with self.assertRaises(IdempotencyConflict):
            self.service.request_refund(payment_id, 2_000, "retry-1")

    def test_partial_refunds_cannot_exceed_capture(self) -> None:
        payment_id = self.captured_payment()
        self.service.request_refund(payment_id, 4_000, "partial-1")
        self.service.request_refund(payment_id, 6_000, "partial-2")
        with self.assertRaises(RefundLimitExceeded):
            self.service.request_refund(payment_id, 1, "partial-3")

    def test_concurrent_distinct_keys_cannot_over_refund(self) -> None:
        payment_id = self.captured_payment()
        start = Barrier(2)

        def issue(key: str) -> str:
            start.wait(timeout=5)
            try:
                self.service.request_refund(payment_id, 10_000, key)
                return "accepted"
            except RefundLimitExceeded:
                return "rejected"

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(issue, ("distinct-1", "distinct-2")))
        self.assertEqual(sorted(outcomes), ["accepted", "rejected"])
        history = self.service.history(payment_id)
        self.assertEqual(len(history["refunds"]), 1)
        self.assertEqual(history["payment"]["refunded_minor"], 10_000)

    def test_invalid_amount_and_currency_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_payment(0)
        with self.assertRaises(ValueError):
            self.service.create_payment(100, "BTC")
        payment_id = self.captured_payment()
        with self.assertRaises(ValueError):
            self.service.request_refund(payment_id, -1, "bad")

    def test_refund_requires_capture_and_capture_is_one_way(self) -> None:
        payment = self.service.create_payment(100)
        payment_id = str(payment["id"])
        with self.assertRaises(InvalidTransition):
            self.service.request_refund(payment_id, 1, "early")
        self.service.capture_payment(payment_id)
        with self.assertRaises(InvalidTransition):
            self.service.capture_payment(payment_id)

    def test_unknown_payment_is_not_found(self) -> None:
        with self.assertRaises(PaymentNotFound):
            self.service.capture_payment("missing")


if __name__ == "__main__":
    unittest.main()
