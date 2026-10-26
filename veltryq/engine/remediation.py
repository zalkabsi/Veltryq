"""Hash-guarded repair recipe for one reviewed synthetic source adapter."""

from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

KNOWN_SOURCES = {
    "vulnerable": "5e4124ea51d3cdd1fc41e063f7bddf3b51e740bb7c081695662f6c956a8dd846",
    "repaired": "c58eb08706b0f471f65136d49b6a8c0ffa0557200add5a53f799867034c11498",
}

REMEDIATION = {
    "FIN-IDEMPOTENCY": (
        "Move idempotency lookup, refund-limit validation, refund insertion, and ledger posting "
        "into one database transaction. Add a unique constraint on (payment_id, idempotency_key)."
    ),
    "FIN-REFUND-LIMIT": (
        "Serialize updates to the payment balance or use a conditional atomic update so a stale "
        "precheck cannot authorize a second refund."
    ),
    "FIN-LEDGER-BALANCE": (
        "Write both ledger sides in the same transaction as the refund state change."
    ),
}


def source_kind(source: Path) -> str:
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    return next(
        (kind for kind, expected in KNOWN_SOURCES.items() if digest == expected),
        "unsupported",
    )


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode() + b"\0" + data, usedforsecurity=False
    ).hexdigest()


def prepare_repair(source: Path, output: Path) -> dict[str, object]:
    if source_kind(source) != "vulnerable":
        raise ValueError("source does not match the reviewed vulnerable adapter")
    template = Path(__file__).parents[1] / "fixtures/refund_repaired.py"
    if source_kind(template) != "repaired":
        raise ValueError("repair template differs from the reviewed source")
    before, after = (
        source.read_text(encoding="utf-8"),
        template.read_text(encoding="utf-8"),
    )
    target = "examples/demo/refund_candidate.py"
    schema_target = "examples/demo/repair_schema.sql"
    schema_sql = (
        "-- Synthetic sandbox only: existing duplicate rows need reviewed reconciliation.\n"
        "CREATE UNIQUE INDEX refunds_idempotency_unique\n"
        "ON refunds (payment_id, idempotency_key);\n"
    )
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="a/" + target,
            tofile="b/" + target,
        )
    ) + "".join(
        difflib.unified_diff(
            [],
            schema_sql.splitlines(keepends=True),
            fromfile="/dev/null",
            tofile="b/" + schema_target,
        )
    )
    # Apply the exact reviewed replacement to a separate proposal tree. No imported
    # MR code or LLM-generated shell commands are involved.
    proposal = output / "proposal"
    for path, content in ((target, after), (schema_target, schema_sql)):
        destination = proposal / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    if source_kind(proposal / target) != "repaired":
        raise RuntimeError("proposed source does not match the verified repair")
    (output / "repair.patch").write_text(diff, encoding="utf-8")
    return {
        "strategy": "reviewed_source_recipe",
        "target_path": target,
        "before_sha256": KNOWN_SOURCES["vulnerable"],
        "after_sha256": KNOWN_SOURCES["repaired"],
        "before_git_blob_sha": git_blob_id(before.encode()),
        "after_git_blob_sha": git_blob_id(after.encode()),
        "patch": "repair.patch",
        "patch_sha256": hashlib.sha256(diff.encode()).hexdigest(),
        "diff": diff,
        "schema_change": "unique (payment_id, idempotency_key)",
        "migration_scope": "fresh synthetic schema; populated data reconciliation is not automated",
        "human_review_required": True,
    }
