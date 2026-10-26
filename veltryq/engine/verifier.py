"""Independent deterministic evaluation of the supported retry contract."""

from __future__ import annotations

from app.refunds import RefundService
from veltryq.engine.scenarios import Implementation, run_duplicate_refund_scenario


def verify(
    implementation: Implementation,
    *,
    database_url: str | None = None,
    service_class: type[RefundService] | None = None,
    captured_amount_minor: int = 10_000,
) -> dict[str, object]:
    evidence = run_duplicate_refund_scenario(
        implementation,
        database_url=database_url,
        service_class=service_class,
        captured_amount_minor=captured_amount_minor,
    )
    evidence["checks"] = [
        {
            "invariant_id": invariant,
            "status": (
                "inconclusive"
                if evidence["verdict"] == "inconclusive"
                else "failed"
                if invariant in evidence["violations"]
                else "passed"
            ),
        }
        for invariant in ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE")
    ]
    return evidence
