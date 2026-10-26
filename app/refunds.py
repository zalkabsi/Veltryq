"""Transactional synthetic payments and refunds; amounts are integer minor units."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from threading import Barrier
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MAX_AMOUNT_MINOR, LedgerEntry, Payment, Refund, record
from app.storage import Storage


class DomainError(Exception):
    status_code = 400


class PaymentNotFound(DomainError):
    status_code = 404


class InvalidTransition(DomainError):
    status_code = 409


class RefundLimitExceeded(DomainError):
    status_code = 409


class IdempotencyConflict(DomainError):
    status_code = 409


def validate_amount(value: int) -> None:
    if type(value) is not int or not 0 < value <= MAX_AMOUNT_MINOR:
        raise ValueError("amount_minor must be a positive bounded integer")


class RefundService:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def create_payment(self, amount_minor: int, currency: str = "USD") -> dict[str, object]:
        validate_amount(amount_minor)
        if currency not in {"USD", "EUR", "SAR"}:
            raise ValueError("currency must be USD, EUR, or SAR")
        payment = Payment(id=str(uuid4()), amount_minor=amount_minor, currency=currency)
        with self.storage.transaction() as session:
            session.add(payment)
            session.flush()
            result = record(payment)
        return result

    @staticmethod
    def _payment(session: Session, payment_id: str, *, lock: bool = False) -> Payment:
        query = select(Payment).where(Payment.id == payment_id)
        if lock:
            query = query.with_for_update()
        payment = session.scalar(query)
        if payment is None:
            raise PaymentNotFound("payment not found")
        return payment

    def capture_payment(self, payment_id: str) -> dict[str, object]:
        with self.storage.transaction() as session:
            payment = self._payment(session, payment_id, lock=True)
            if payment.state != "authorized":
                raise InvalidTransition("only an authorized payment can be captured")
            payment.state = "captured"
            self._post_pair(session, payment, None, payment.amount_minor, capture=True)
            session.flush()
            result = record(payment)
        return result

    def request_refund(
        self,
        payment_id: str,
        amount_minor: int,
        idempotency_key: str,
        *,
        preflight_barrier: Barrier | None = None,
    ) -> dict[str, object]:
        validate_amount(amount_minor)
        if (
            not isinstance(idempotency_key, str)
            or not idempotency_key.strip()
            or len(idempotency_key) > 255
        ):
            raise ValueError("idempotency_key must contain 1 to 255 characters")
        request_hash = hashlib.sha256(
            json.dumps(
                {"payment_id": payment_id, "amount_minor": amount_minor}, sort_keys=True
            ).encode()
        ).hexdigest()
        return self._refund_transaction(
            payment_id, amount_minor, idempotency_key, request_hash, preflight_barrier
        )

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
        with self.storage.transaction() as session:
            payment = self._payment(session, payment_id, lock=True)
            existing = self._existing_refund(session, payment_id, idempotency_key)
            if existing is not None:
                return self._replay_or_conflict(existing, request_hash)
            self._validate_refundable(payment, amount_minor)
            return self._write_refund(session, payment, amount_minor, idempotency_key, request_hash)

    @staticmethod
    def _validate_refundable(payment: Payment, amount_minor: int) -> None:
        if payment.state != "captured":
            raise InvalidTransition("only a captured payment can be refunded")
        if amount_minor > payment.amount_minor - payment.refunded_minor:
            raise RefundLimitExceeded("refund exceeds the remaining captured amount")

    @staticmethod
    def _existing_refund(session: Session, payment_id: str, key: str) -> Refund | None:
        return session.scalar(
            select(Refund)
            .where(Refund.payment_id == payment_id, Refund.idempotency_key == key)
            .order_by(Refund.created_at, Refund.id)
            .limit(1)
        )

    @staticmethod
    def _replay_or_conflict(existing: Refund, request_hash: str) -> dict[str, object]:
        if existing.request_hash != request_hash:
            raise IdempotencyConflict("idempotency key was already used with a different request")
        return record(existing)

    def _write_refund(
        self,
        session: Session,
        payment: Payment,
        amount_minor: int,
        key: str,
        request_hash: str,
    ) -> dict[str, object]:
        refund = Refund(
            id=str(uuid4()),
            payment_id=payment.id,
            idempotency_key=key,
            request_hash=request_hash,
            amount_minor=amount_minor,
            created_at=datetime.now(UTC).isoformat(),
        )
        session.add(refund)
        session.flush()
        payment.refunded_minor += amount_minor
        self._post_pair(session, payment, refund.id, amount_minor)
        session.flush()
        return record(refund)

    @staticmethod
    def _post_pair(
        session: Session,
        payment: Payment,
        refund_id: str | None,
        amount_minor: int,
        *,
        capture: bool = False,
    ) -> None:
        debit, credit = (
            ("settlement_clearing", "merchant_payable")
            if capture
            else ("merchant_payable", "settlement_clearing")
        )
        for side, account in (("debit", debit), ("credit", credit)):
            session.add(
                LedgerEntry(
                    payment_id=payment.id,
                    refund_id=refund_id,
                    account=account,
                    side=side,
                    amount_minor=amount_minor,
                    currency=payment.currency,
                )
            )

    def get_payment(self, payment_id: str) -> dict[str, object]:
        with self.storage.session() as session:
            return record(self._payment(session, payment_id))

    def get_refund(self, refund_id: str) -> dict[str, object]:
        with self.storage.session() as session:
            refund = session.get(Refund, refund_id)
            if refund is None:
                raise PaymentNotFound("refund not found")
            return record(refund)

    def history(self, payment_id: str) -> dict[str, object]:
        with self.storage.session() as session:
            payment = self._payment(session, payment_id)
            refunds = session.scalars(
                select(Refund)
                .where(Refund.payment_id == payment_id)
                .order_by(Refund.created_at, Refund.id)
            ).all()
            ledger = session.scalars(
                select(LedgerEntry)
                .where(LedgerEntry.payment_id == payment_id)
                .order_by(LedgerEntry.id)
            ).all()
            return {
                "payment": record(payment),
                "refunds": [record(r) for r in refunds],
                "ledger_entries": [record(entry) for entry in ledger],
            }
