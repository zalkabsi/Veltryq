"""Serializable descriptions of the built-in financial invariants."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Invariant:
    id: str
    name: str
    description: str
    operation: str
    required_data: tuple[str, ...]
    preconditions: tuple[str, ...]
    strategy: str
    expected_behavior: str
    failure_evidence: str
    severity: str
    remediation: str

    def as_dict(self) -> dict[str, object]:
        result = asdict(self)
        for key in ("required_data", "preconditions"):
            result[key] = list(result[key])
        result["source"] = "built_in"
        return result


INVARIANTS: dict[str, Invariant] = {
    "FIN-IDEMPOTENCY": Invariant(
        id="FIN-IDEMPOTENCY",
        name="Refund idempotency",
        description="A repeated request with one idempotency key creates one refund posting.",
        operation="refund request and retry",
        required_data=("payment", "idempotency_key", "refund_rows", "ledger_entries"),
        preconditions=("payment is captured", "retries use the same request payload"),
        strategy="Run two synchronized requests with the same key and compare persisted state.",
        expected_behavior="One refund row is persisted; both callers may receive the same result.",
        failure_evidence="More than one refund row or refund ledger pair exists for the key.",
        severity="critical",
        remediation="Perform idempotency lookup and posting in one transaction; enforce a unique key.",
    ),
    "FIN-REFUND-LIMIT": Invariant(
        id="FIN-REFUND-LIMIT",
        name="Refund limit",
        description="Cumulative successful refunds never exceed the captured payment amount.",
        operation="refund request",
        required_data=("captured_amount_minor", "refund_rows", "refunded_amount_minor"),
        preconditions=("payment is captured", "currency is consistent"),
        strategy="Compare persisted refund total with captured amount after concurrent requests.",
        expected_behavior="Total refunds are less than or equal to the captured amount.",
        failure_evidence="Persisted refund total exceeds captured amount.",
        severity="critical",
        remediation="Serialize the balance check and posting or use an atomic conditional update.",
    ),
    "FIN-LEDGER-BALANCE": Invariant(
        id="FIN-LEDGER-BALANCE",
        name="Ledger balance",
        description="Every defined posting has equal debit and credit totals in one currency.",
        operation="capture or refund posting",
        required_data=("ledger_entries", "currency"),
        preconditions=("posting belongs to one currency"),
        strategy="Sum debit and credit minor units for each transaction and currency.",
        expected_behavior="Debit total equals credit total.",
        failure_evidence="Debit and credit totals differ for a transaction.",
        severity="high",
        remediation="Write a balanced entry pair within the same database transaction.",
    ),
}


def serializable_invariants() -> list[dict[str, object]]:
    return [INVARIANTS[key].as_dict() for key in sorted(INVARIANTS)]
