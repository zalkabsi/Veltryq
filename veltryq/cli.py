"""Fixed entry points for the supported adapter; no generated shell execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from veltryq.engine.analyzer import analyze_paths
from veltryq.engine.context import execution_context
from veltryq.engine.contracts import RegressionContract, execute_contract
from veltryq.engine.evidence import build_report, write_report
from veltryq.engine.invariants import serializable_invariants
from veltryq.engine.remediation import source_kind
from veltryq.engine.verifier import verify
from veltryq.engine.workflow import run_workflow
from veltryq.fixtures.refund_repaired import FixtureRefundService as RepairedFixture


def _print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _workflow_summary(report: dict, output: Path) -> dict:
    """Keep the native tool response small; complete persisted rows stay in evidence.json."""
    summary = {
        key: report.get(key)
        for key in (
            "overall_verdict",
            "candidate_path",
            "candidate_source_sha256",
            "candidate_git_blob_sha",
            "regression_contract_sha256",
            "source_commit_sha",
            "merge_request_source_sha",
            "invariants_tested",
            "violations_confirmed",
            "baseline",
        )
    }
    for stage in ("before", "after"):
        summary[stage] = {
            key: report.get(stage, {}).get(key)
            for key in (
                "verdict",
                "implementation",
                "database",
                "refund_count",
                "total_refunded_minor",
                "refund_ledger_entry_count",
                "regression_contract_sha256",
                "errors",
            )
        }
    proposal = report.get("repair_proposal")
    summary["repair_proposal"] = (
        {
            key: proposal[key]
            for key in (
                "target_path",
                "before_sha256",
                "after_sha256",
                "before_git_blob_sha",
                "after_git_blob_sha",
                "patch_sha256",
            )
        }
        if proposal
        else None
    )
    summary["full_evidence_path"] = str(output / "evidence.json")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(prog="veltryq")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="run before/after and produce linked evidence")
    demo.add_argument("--out", type=Path, default=Path("artifacts/evidence"))
    demo.add_argument("--database-url")
    workflow = commands.add_parser(
        "workflow", help="investigate, propose a source patch, verify, report"
    )
    workflow.add_argument("--out", type=Path, default=Path("artifacts/workflow"))
    workflow.add_argument("--paths", nargs="+")
    workflow.add_argument("--candidate", type=Path)
    workflow.add_argument("--database-url")
    workflow.add_argument(
        "--summary",
        action="store_true",
        help="print compact tool evidence; retain full report files",
    )
    regression = commands.add_parser(
        "regression", help="execute the unchanged concurrent-retry contract"
    )
    regression.add_argument("--implementation", choices=("vulnerable", "repaired"), required=True)
    regression.add_argument("--database-url")
    regression.add_argument("--spec", type=Path)
    candidate_regression = commands.add_parser(
        "candidate-regression", help="test a hash-matched MR candidate"
    )
    candidate_regression.add_argument("--candidate", type=Path, required=True)
    candidate_regression.add_argument("--spec", type=Path)
    candidate_regression.add_argument("--database-url")
    analyze = commands.add_parser("analyze", help="map changed paths to supported invariant checks")
    analyze.add_argument("paths", nargs="+")
    commands.add_parser("invariants", help="print the built-in invariant catalog")
    args = parser.parse_args()
    if args.command == "candidate-regression":
        kind = source_kind(args.candidate) if args.candidate.is_file() else "unsupported"
        if kind == "unsupported":
            _print_json({"verdict": "inconclusive", "reason": "unsupported candidate source"})
            raise SystemExit(2)
        contract = (
            args.spec.read_bytes()
            if args.spec
            else RegressionContract(
                invariants=["FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT", "FIN-LEDGER-BALANCE"]
            )
            .model_dump_json()
            .encode()
        )
        result = execute_contract(
            contract,
            kind,
            database_url=args.database_url,
            service_class=RepairedFixture if kind == "repaired" else None,
        )
        _print_json(result)
        raise SystemExit(
            {"passed": 0, "confirmed_violation": 1, "inconclusive": 2}[result["verdict"]]
        )
    if args.command == "workflow":
        if args.candidate is None and Path("examples/demo/refund_candidate.py").is_file():
            args.candidate = Path("examples/demo/refund_candidate.py")
        if args.paths is None:
            args.paths = (
                [str(args.candidate)]
                if args.candidate
                else ["veltryq/fixtures/refund_vulnerable.py"]
            )
        report = run_workflow(
            args.out,
            args.paths,
            database_url=args.database_url,
            candidate=args.candidate,
        )
        if args.summary:
            print(
                json.dumps(
                    _workflow_summary(report, args.out), sort_keys=True, separators=(",", ":")
                )
            )
        else:
            _print_json(report)
        raise SystemExit(
            0
            if report["overall_verdict"]
            in {"confirmed_violation_repaired", "selected_checks_passed"}
            else 2
        )
    if args.command == "demo":
        report = build_report(
            verify("vulnerable", database_url=args.database_url),
            verify("repaired", database_url=args.database_url),
            context=execution_context(args.out.as_posix()),
        )
        report["artifact_urls"] = {
            name: url
            for name, url in report["artifact_urls"].items()
            if name in {"evidence.html", "evidence.json"}
        }
        json_path, html_path = write_report(report, args.out)
        _print_json(
            {
                "verdict": report["overall_verdict"],
                "json_report": str(json_path),
                "html_report": str(html_path),
                "before": report["before"],
                "after": report["after"],
            }
        )
        raise SystemExit(0 if report["overall_verdict"] == "confirmed_violation_repaired" else 2)
    if args.command == "regression":
        amount = 10_000
        if args.spec:
            contract = RegressionContract.model_validate_json(args.spec.read_bytes())
            amount = contract.captured_amount_minor
        result = verify(
            args.implementation,
            database_url=args.database_url,
            captured_amount_minor=amount,
        )
        _print_json(result)
        if result["verdict"] == "inconclusive":
            raise SystemExit(2)
        raise SystemExit(1 if result["verdict"] == "confirmed_violation" else 0)
    if args.command == "analyze":
        _print_json(analyze_paths(args.paths).__dict__)
        return
    _print_json(serializable_invariants())


if __name__ == "__main__":
    main()
