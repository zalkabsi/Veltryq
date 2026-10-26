from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliRegressionTests(unittest.TestCase):
    def run_regression(self, implementation: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "veltryq.cli",
                "regression",
                "--implementation",
                implementation,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_vulnerable_fixture_exits_nonzero_with_confirmed_evidence(self) -> None:
        result = self.run_regression("vulnerable")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('"FIN-IDEMPOTENCY"', result.stdout)
        self.assertIn('"FIN-REFUND-LIMIT"', result.stdout)

    def test_repaired_fixture_exits_zero(self) -> None:
        result = self.run_regression("repaired")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"verdict": "passed"', result.stdout)

    def test_candidate_regression_exposes_failure_then_passes_repaired_source(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for kind, expected in (("vulnerable", 1), ("repaired", 0)):
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "veltryq.cli",
                    "candidate-regression",
                    "--candidate",
                    str(root / "veltryq/fixtures" / ("refund_" + kind + ".py")),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_unknown_candidate_returns_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "unknown.py"
            candidate.write_text("raise RuntimeError('must not execute')")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "veltryq.cli",
                    "candidate-regression",
                    "--candidate",
                    str(candidate),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_workflow_summary_preserves_verdict_hashes_and_full_evidence(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for kind, verdict in (
            ("vulnerable", "confirmed_violation_repaired"),
            ("repaired", "selected_checks_passed"),
        ):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "veltryq.cli",
                        "workflow",
                        "--out",
                        directory,
                        "--candidate",
                        str(root / "veltryq/fixtures" / ("refund_" + kind + ".py")),
                        "--summary",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertLess(len(result.stdout.encode()), 3600)
                summary = json.loads(result.stdout)
                full = json.loads((Path(directory) / "evidence.json").read_text())
                self.assertEqual(summary["overall_verdict"], verdict)
                for key in (
                    "candidate_git_blob_sha",
                    "candidate_source_sha256",
                    "regression_contract_sha256",
                ):
                    self.assertEqual(summary[key], full[key])
                for stage in ("before", "after"):
                    self.assertEqual(summary[stage]["verdict"], full[stage]["verdict"])
                    self.assertIn("refunds", full[stage])
                self.assertEqual(
                    summary["repair_proposal"]["patch_sha256"]
                    if summary["repair_proposal"]
                    else None,
                    full["repair_proposal"]["patch_sha256"] if full["repair_proposal"] else None,
                )


if __name__ == "__main__":
    unittest.main()
