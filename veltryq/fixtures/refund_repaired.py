"""Reviewed repair template for the bounded synthetic refund adapter."""

from __future__ import annotations

from threading import Barrier

from app.refunds import RefundService


class FixtureRefundService(RefundService):
    def _refund_transaction(
        self,
        payment_id: str,
        amount_minor: int,
        idempotency_key: str,
        request_hash: str,
        preflight_barrier: Barrier | None,
    ) -> dict[str, object]:
        if preflight_barrier is not None:
            preflight_barrier.wait(timeout=10)
        # PostgreSQL FOR UPDATE / SQLite BEGIN IMMEDIATE covers every check and write.
        with self.storage.transaction() as session:
            payment = self._payment(session, payment_id, lock=True)
            existing = self._existing_refund(session, payment_id, idempotency_key)
            if existing is not None:
                return self._replay_or_conflict(existing, request_hash)
            self._validate_refundable(payment, amount_minor)
            return self._write_refund(session, payment, amount_minor, idempotency_key, request_hash)
