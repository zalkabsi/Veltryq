from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from pydantic import ValidationError

from veltryq.engine.context import execution_context, public_url
from veltryq.engine.contracts import RegressionContract
from veltryq.engine.evidence import build_report, render_html
from veltryq.engine.remediation import prepare_repair, source_kind
from veltryq.engine.scenarios import evaluate_state
from veltryq.engine.verifier import verify
from veltryq.engine.workflow import run_workflow

FIXTURES = Path(__file__).resolve().parents[1] / "veltryq/fixtures"


class WorkflowTests(unittest.TestCase):
    def test_workflow_generates_real_patch_and_uses_identical_regression_contract(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = run_workflow(output, ["veltryq/fixtures/refund_vulnerable.py"])
            self.assertEqual(report["overall_verdict"], "confirmed_violation_repaired")
            self.assertEqual(report["baseline"]["verdict"], "passed")
            self.assertEqual(report["remediation"]["file"], "examples/demo/refund_candidate.py")
            self.assertEqual(
                report["before"]["regression_contract_sha256"],
                report["after"]["regression_contract_sha256"],
            )
            RegressionContract.model_validate_json((output / "regression.json").read_bytes())
            tree = output / "apply-check"
            candidate = tree / "examples/demo/refund_candidate.py"
            candidate.parent.mkdir(parents=True)
            shutil.copyfile(FIXTURES / "refund_vulnerable.py", candidate)
            git = shutil.which("git")
            self.assertIsNotNone(git)
            subprocess.run(
                [git, "apply", "--check", str(output / "repair.patch")],
                cwd=tree,
                check=True,
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                [git, "apply", str(output / "repair.patch")],
                cwd=tree,
                check=True,
                capture_output=True,
                timeout=10,
            )
            self.assertEqual(source_kind(candidate), "repaired")
            self.assertTrue((tree / "examples/demo/repair_schema.sql").is_file())

    def test_unknown_source_is_inconclusive_and_never_executed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "unknown.py"
            candidate.write_text("raise RuntimeError('untrusted source must never execute')")
            result = run_workflow(
                root / "out", ["examples/demo/refund_candidate.py"], candidate=candidate
            )
            self.assertEqual(result["overall_verdict"], "inconclusive")
            self.assertFalse((root / "out/repair.patch").exists())
            with self.assertRaises(ValueError):
                prepare_repair(candidate, root / "out")

    def test_safe_candidate_does_not_report_a_confirmed_bug(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(
                Path(directory),
                ["examples/demo/refund_candidate.py"],
                candidate=FIXTURES / "refund_repaired.py",
            )
            self.assertEqual(result["overall_verdict"], "selected_checks_passed")
            self.assertEqual(result["violations_confirmed"], [])
            self.assertIsNone(result["repair_proposal"])

    def test_unrelated_change_skips_financial_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(Path(directory), ["docs/typo.md"])
            self.assertEqual(result["overall_verdict"], "inconclusive")
            self.assertNotIn("before", result)

    def test_reusing_an_output_directory_removes_stale_repair_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            run_workflow(output, ["veltryq/fixtures/refund_vulnerable.py"])
            self.assertTrue((output / "repair.patch").exists())
            run_workflow(output, ["docs/typo.md"])
            self.assertFalse((output / "repair.patch").exists())
            self.assertFalse((output / "proposal/examples/demo/refund_candidate.py").exists())

    def test_execution_error_cannot_be_reported_as_repaired(self) -> None:
        before, after = verify("vulnerable"), verify("repaired")
        broken = deepcopy(after)
        broken.update(errors=["injected request failure"], verdict="inconclusive")
        result = build_report(before, broken)
        self.assertEqual(result["overall_verdict"], "inconclusive")
        self.assertEqual(result["remediation_status"], "not_verified")

    def test_per_refund_ledger_checks_prevent_cancelling_errors(self) -> None:
        refunds = [
            {"id": "a", "payment_id": "p", "idempotency_key": "a", "amount_minor": 100},
            {"id": "b", "payment_id": "p", "idempotency_key": "b", "amount_minor": 100},
        ]
        entries = [
            {"refund_id": "a", "currency": "USD", "side": "debit", "amount_minor": 100},
            {
                "refund_id": "b",
                "currency": "USD",
                "side": "credit",
                "amount_minor": 100,
            },
        ]
        self.assertIn("FIN-LEDGER-BALANCE", evaluate_state(refunds, entries, 1000))

    def test_contract_rejects_commands_and_non_integer_money(self) -> None:
        for extra in ({"command": "echo unexpected"}, {"captured_amount_minor": 1.5}):
            with self.assertRaises(ValidationError):
                RegressionContract.model_validate({"invariants": ["FIN-IDEMPOTENCY"], **extra})

    def test_ci_provenance_is_linked_and_secrets_excluded(self) -> None:
        env = {
            "GITLAB_CI": "true",
            "CI_COMMIT_SHA": "a" * 40,
            "CI_MERGE_REQUEST_IID": "7",
            "CI_PROJECT_URL": "https://gitlab.com/example/project",
            "CI_PIPELINE_URL": "https://gitlab.com/example/project/-/pipelines/1",
            "CI_JOB_URL": "https://gitlab.com/example/project/-/jobs/2",
            "PRIVATE_TOKEN": "hidden",
        }
        context = execution_context("artifacts/workflow", env)
        self.assertEqual(
            context["merge_request_url"], env["CI_PROJECT_URL"] + "/-/merge_requests/7"
        )
        self.assertIn(
            "/jobs/2/artifacts/file/artifacts/workflow/evidence.html",
            context["artifact_urls"]["evidence.html"],
        )
        self.assertNotIn("hidden", json.dumps(context))
        self.assertIsNone(public_url("javascript:alert(1)"))
        self.assertIsNone(public_url("https://user:password@gitlab.com/"))

    def test_html_escapes_candidate_supplied_content(self) -> None:
        result = render_html(
            {
                "overall_verdict": "inconclusive",
                "analysis_scope": "<script>bad</script>",
            }
        )
        self.assertNotIn("<script>bad</script>", result)
