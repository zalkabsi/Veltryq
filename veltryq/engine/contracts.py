"""Declarative regression contracts, with no executable expressions or commands."""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from app.models import MAX_AMOUNT_MINOR


class RegressionContract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1] = 1
    scenario: Literal["concurrent_duplicate_refund"] = "concurrent_duplicate_refund"
    captured_amount_minor: StrictInt = Field(default=10_000, gt=0, le=MAX_AMOUNT_MINOR)
    currency: Literal["USD"] = "USD"
    requests: Literal[2] = 2
    idempotency_key: Literal["demo-retry-001"] = "demo-retry-001"
    expected_refund_count: Literal[1] = 1
    expected_maximum_refunded_minor: StrictInt = 10_000
    invariants: list[Literal["FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE"]]
    origin: Literal["built_in_adapter"] = "built_in_adapter"

    @model_validator(mode="after")
    def consistent_balance(self) -> RegressionContract:
        if self.expected_maximum_refunded_minor != self.captured_amount_minor:
            raise ValueError("regression limit must equal the captured amount")
        return self


def execute_contract(
    data: bytes, implementation: str, *, database_url=None, service_class=None
) -> dict:
    from veltryq.engine.verifier import verify

    contract = RegressionContract.model_validate_json(data)
    result = verify(
        implementation,
        database_url=database_url,
        service_class=service_class,
        captured_amount_minor=contract.captured_amount_minor,
    )
    result["regression_contract_sha256"] = hashlib.sha256(data).hexdigest()
    return result
