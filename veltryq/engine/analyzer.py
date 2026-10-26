"""Explicit path-to-invariant mapping; this is not universal source analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Analysis:
    analyzed_paths: list[str]
    selected_invariants: list[str]
    confidence: str
    rationale: str


PATH_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "examples/demo/refund_candidate.py",
        ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE"),
    ),
    (
        "veltryq/fixtures/",
        ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE"),
    ),
    ("app/models.py", ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE")),
    ("app/refunds.py", ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE")),
    ("app/storage.py", ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE")),
    ("app/main.py", ("FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT")),
    ("ledger", ("FIN-LEDGER-BALANCE",)),
)


def analyze_paths(paths: list[str]) -> Analysis:
    selected: set[str] = set()
    matched = False
    for path in paths:
        normalized = path.replace("\\", "/").lower()
        for token, invariant_ids in PATH_RULES:
            if token.lower() in normalized:
                selected.update(invariant_ids)
                matched = True
    if not matched:
        return Analysis(
            analyzed_paths=paths,
            selected_invariants=[],
            confidence="inconclusive",
            rationale="No configured financial-operation mapping matched these paths.",
        )
    return Analysis(
        analyzed_paths=paths,
        selected_invariants=sorted(selected),
        confidence="selected_checks",
        rationale="Checks were selected by the repository's explicit path mapping.",
    )
