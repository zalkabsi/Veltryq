from __future__ import annotations

import tempfile
import unittest

from veltryq.engine.analyzer import analyze_paths
from veltryq.engine.evidence import build_report, write_report
from veltryq.engine.invariants import serializable_invariants
from veltryq.engine.verifier import verify


class EngineTests(unittest.TestCase):
    def test_vulnerable_fixture_confirms_duplicate_and_over_refund(self) -> None:
        result = verify("vulnerable")
        self.assertEqual(result["verdict"], "confirmed_violation")
        self.assertEqual(result["violations"], ["FIN-IDEMPOTENCY", "FIN-REFUND-LIMIT"])
        self.assertEqual(result["refund_count"], 2)
        self.assertEqual(result["total_refunded_minor"], 20_000)
        self.assertEqual(result["refund_ledger_entry_count"], 4)

    def test_repaired_fixture_passes_same_scenario(self) -> None:
        result = verify("repaired")
        self.assertEqual(result["verdict"], "passed")
        self.assertEqual(result["refund_count"], 1)
        self.assertEqual(result["total_refunded_minor"], 10_000)
        self.assertEqual(result["refund_ledger_entry_count"], 2)

    def test_explicit_analyzer_mapping_and_inconclusive_path(self) -> None:
        selected = analyze_paths(["app/refunds.py"])
        self.assertEqual(selected.confidence, "selected_checks")
        self.assertIn("FIN-IDEMPOTENCY", selected.selected_invariants)
        unrelated = analyze_paths(["docs/typo.md"])
        self.assertEqual(unrelated.confidence, "inconclusive")
        self.assertEqual(unrelated.selected_invariants, [])

    def test_invariants_are_serializable_and_report_uses_execution_data(self) -> None:
        self.assertEqual(len(serializable_invariants()), 3)
        report = build_report(verify("vulnerable"), verify("repaired"))
        self.assertEqual(report["overall_verdict"], "confirmed_violation_repaired")
        with tempfile.TemporaryDirectory() as temporary_directory:
            json_path, html_path = write_report(report, temporary_directory)
            self.assertTrue(json_path.is_file())
            rendered = html_path.read_text(encoding="utf-8")
            self.assertIn("20000", rendered)
            self.assertIn("10000", rendered)
            self.assertIn("FIN-REFUND-LIMIT", rendered)


if __name__ == "__main__":
    unittest.main()
