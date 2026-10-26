"""Portable SQLAlchemy models for synthetic financial records."""

from __future__ import annotations

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

MAX_AMOUNT_MINOR = 9_000_000_000_000_000


class Base(DeclarativeBase):
    pass


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="payment_positive"),
        CheckConstraint("refunded_minor >= 0", name="refund_nonnegative"),
        CheckConstraint("state IN ('authorized', 'captured')", name="payment_state"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    refunded_minor: Mapped[int] = mapped_column(BigInteger, default=0)
    currency: Mapped[str] = mapped_column(String(3))
    state: Mapped[str] = mapped_column(String(16), default="authorized")


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = (CheckConstraint("amount_minor > 0", name="refund_positive"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(255))
    request_hash: Mapped[str] = mapped_column(String(64))
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[str] = mapped_column(String(40))


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        CheckConstraint("side IN ('debit', 'credit')", name="ledger_side"),
        CheckConstraint("amount_minor > 0", name="ledger_positive"),
    )
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.id"))
    refund_id: Mapped[str | None] = mapped_column(ForeignKey("refunds.id"), nullable=True)
    account: Mapped[str] = mapped_column(String(64))
    side: Mapped[str] = mapped_column(String(6))
    amount_minor: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3))


def record(model: Base) -> dict[str, object]:
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}
