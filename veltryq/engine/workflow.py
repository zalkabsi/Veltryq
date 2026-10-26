"""Bounded investigation, concrete source repair, and unchanged regression contract.

Only reviewed built-in source hashes are supported. Arbitrary source and LLM
patches are never imported or executed. CI and the Duo fixed test tool use this
same entry point; an actual Duo session remains a separate external record.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from veltryq.engine.analyzer import analyze_paths
from veltryq.engine.context import execution_context
from veltryq.engine.contracts import RegressionContract, execute_contract
from veltryq.engine.evidence import build_report, write_report
from veltryq.engine.remediation import prepare_repair, source_kind
from veltryq.engine.scenarios import run_baseline
from veltryq.fixtures.refund_repaired import FixtureRefundService as RepairedFixture


def review_note(report: dict) -> str:
    before, after = report.get("before", {}), report.get("after", {})
    links = report.get("artifact_urls", {})
    return "\n".join(
        [
            "## Veltryq financial integrity review",
            "",
            f"Verdict: **{report['overall_verdict']}**. Human review is required.",
            f"Scope: {report.get('analysis_scope', 'unsupported source')}",
            f"Tested commit: {report.get('source_commit_sha') or 'local; no CI commit recorded'}",
            f"Invariants: {', '.join(report.get('invariants_tested', [])) or 'none executed'}",
            f"Before: {before.get('refund_count', 'unavailable')} refunds / "
            f"{before.get('total_refunded_minor', 'unavailable')} minor units.",
            f"After: {after.get('refund_count', 'unavailable')} refunds / "
            f"{after.get('total_refunded_minor', 'unavailable')} minor units.",
            "Repair: keep lookup, balance check, and postings within one locked transaction; "
            "retain database idempotency uniqueness.",
            f"Pipeline: {report.get('pipeline_url') or 'not recorded'}",
            *[f"{name}: {url}" for name, url in links.items()],
            "",
            "The patch is a proposal for the known synthetic fixture. Review its diff, "
            "the unchanged regression contract, transaction isolation, and schema before accepting it.",
            "A finite scenario does not prove financial safety. No merge or deployment was performed.",
            "",
        ]
    )


def run_workflow(
    output: Path,
    paths: list[str],
    *,
    database_url: str | None = None,
    candidate: Path | None = None,
) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    # Remove only our own previous outputs, so unsupported/safe reruns cannot
    # expose a stale repair proposal as evidence for a different candidate.
    for name in ("repair.patch", "regression.json", "review.md", "evidence.json", "evidence.html"):
        (output / name).unlink(missing_ok=True)
    for name in ("refund_candidate.py", "repair_schema.sql"):
        (output / "proposal/examples/demo" / name).unlink(missing_ok=True)
    context = execution_context(output.as_posix())
    analysis = analyze_paths(paths)
    start = perf_counter()
    trace = []

    def stage(name: str, status: str) -> None:
        trace.append(
            {
                "stage": name,
                "status": status,
                "elapsed_seconds": round(perf_counter() - start, 6),
            }
        )

    stage("analyze", analysis.confidence)
    source = candidate or Path(__file__).parents[1] / "fixtures/refund_vulnerable.py"
    kind = source_kind(source) if source.is_file() else "unsupported"
    if not analysis.selected_invariants or kind == "unsupported":
        report = {
            **context,
            "project": "Veltryq",
            "overall_verdict": "inconclusive",
            "analysis": asdict(analysis),
            "invariants_tested": [],
            "violations_confirmed": [],
            "analysis_scope": "No supported source/operation match.",
            "limitations": ["No arbitrary source was executed."],
            "trace": trace,
        }
        report["artifact_urls"] = {
            name: url
            for name, url in report["artifact_urls"].items()
            if name in {"evidence.json", "evidence.html", "review.md"}
        }
        write_report(report, output)
        (output / "review.md").write_text(review_note(report), encoding="utf-8")
        return report

    contract = {
        "schema_version": 1,
        "scenario": "concurrent_duplicate_refund",
        "captured_amount_minor": 10_000,
        "currency": "USD",
        "requests": 2,
        "idempotency_key": "demo-retry-001",
        "expected_refund_count": 1,
        "expected_maximum_refunded_minor": 10_000,
        "invariants": analysis.selected_invariants,
        "origin": "built_in_adapter",
    }
    contract = RegressionContract.model_validate(contract).model_dump()
    contract_bytes = (json.dumps(contract, sort_keys=True, indent=2) + "\n").encode()
    (output / "regression.json").write_bytes(contract_bytes)
    contract_sha = hashlib.sha256(contract_bytes).hexdigest()
    baseline = run_baseline(database_url, implementation=kind)
    stage("baseline", baseline["verdict"])
    before = execute_contract(
        (output / "regression.json").read_bytes(), kind, database_url=database_url
    )
    stage("reproduce", before["verdict"])
    proposal = None
    if kind == "vulnerable" and before["verdict"] == "confirmed_violation":
        proposal = prepare_repair(source, output)
        stage("propose_repair", "exact_source_patch_generated")
    after = execute_contract(
        (output / "regression.json").read_bytes(),
        "repaired",
        database_url=database_url,
        service_class=RepairedFixture,
    )
    if (output / "regression.json").read_bytes() != contract_bytes:
        raise RuntimeError("regression contract changed during verification")
    stage("verify_repair", after["verdict"])
    report = build_report(before, after, context=context)
    if baseline["verdict"] != "passed":
        report["overall_verdict"] = "inconclusive"
    report.update(
        {
            "analysis": asdict(analysis),
            "baseline": baseline,
            "trace": trace,
            "regression_contract_sha256": contract_sha,
            "repair_proposal": proposal,
            "candidate_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "candidate_path": str(candidate)
            if candidate
            else "veltryq/fixtures/refund_vulnerable.py",
        }
    )
    source_bytes = source.read_bytes()
    report["candidate_git_blob_sha"] = hashlib.sha1(
        b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes,
        usedforsecurity=False,
    ).hexdigest()
    if kind == "repaired":
        report["remediation_status"] = "not_needed"
    if proposal is None:
        report["artifact_urls"].pop("repair.patch", None)
    report["source_location"]["file"] = report["candidate_path"]
    stage("human_review", "required")
    write_report(report, output)
    (output / "review.md").write_text(review_note(report), encoding="utf-8")
    return report
