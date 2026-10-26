"""FastAPI interface for Veltryq's synthetic refund application."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StrictInt

from app.models import MAX_AMOUNT_MINOR
from app.refunds import DomainError, RefundService
from app.storage import Storage


class PaymentRequest(BaseModel):
    amount_minor: StrictInt = Field(gt=0, le=MAX_AMOUNT_MINOR)
    currency: Literal["USD", "EUR", "SAR"] = "USD"


class RefundRequest(BaseModel):
    amount_minor: StrictInt = Field(gt=0, le=MAX_AMOUNT_MINOR)


def create_app(storage: Storage | None = None) -> FastAPI:
    temporary_database = None
    if storage is None:
        database = os.getenv("VELTRYQ_DATABASE_URL") or os.getenv("VELTRYQ_DB_PATH")
        if not database:
            temporary_database = TemporaryDirectory(prefix="veltryq-api-")
            database = Path(temporary_database.name) / "synthetic.db"
        storage = Storage(database, repaired=True)
    storage.initialize()
    service = RefundService(storage)

    @asynccontextmanager
    async def lifespan(_api: FastAPI):
        try:
            yield
        finally:
            storage.close()
            if temporary_database is not None:
                temporary_database.cleanup()

    api = FastAPI(
        title="Veltryq Synthetic Refund API",
        version="0.2.0",
        description="Synthetic payment and refund endpoints for local integrity testing.",
        lifespan=lifespan,
    )
    api.state.refund_service = service
    api.state.temporary_database = temporary_database

    @api.exception_handler(DomainError)
    async def domain_error_handler(_request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

    @api.exception_handler(ValueError)
    async def value_error_handler(_request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic"}

    @api.post("/payments", status_code=201)
    def create_payment(payload: PaymentRequest) -> dict[str, object]:
        return service.create_payment(payload.amount_minor, payload.currency)

    @api.post("/payments/{payment_id}/capture")
    def capture_payment(payment_id: str) -> dict[str, object]:
        return service.capture_payment(payment_id)

    @api.post("/payments/{payment_id}/refunds", status_code=201)
    def request_refund(
        payment_id: str,
        payload: RefundRequest,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=255),
    ) -> dict[str, object]:
        return service.request_refund(payment_id, payload.amount_minor, idempotency_key)

    @api.get("/refunds/{refund_id}")
    def get_refund(refund_id: str) -> dict[str, object]:
        return service.get_refund(refund_id)

    @api.get("/payments/{payment_id}/history")
    def payment_history(payment_id: str) -> dict[str, object]:
        return service.history(payment_id)

    return api


app = create_app()
