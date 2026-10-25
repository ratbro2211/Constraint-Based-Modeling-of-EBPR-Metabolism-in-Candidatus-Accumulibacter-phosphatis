"""Regression tests for the model-only EBPR results package."""

import csv
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPublicationOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_publication_outputs.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise AssertionError(
                f"Publication-output generator failed:\n{result.stderr}"
            )
        dynamic = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "dynamic_illustration.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if dynamic.returncode:
            raise AssertionError(f"Dynamic illustration failed:\n{dynamic.stderr}")
        report = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "create_review_report.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if report.returncode:
            raise AssertionError(f"Review-report generator failed:\n{report.stderr}")

    def test_baseline_result_table_matches_model(self):
        with (ROOT / "results" / "phase_summary.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["phase"] for row in rows], ["anaerobic", "aerobic"])
        self.assertAlmostEqual(float(rows[0]["objective_flux"]), 5.4, places=6)
        self.assertAlmostEqual(float(rows[0]["phosphate_exchange"]), 5.1, places=6)
        self.assertAlmostEqual(float(rows[1]["objective_flux"]), 19.9, places=6)
        self.assertLess(float(rows[1]["phosphate_exchange"]), 0)

    def test_publication_outputs_include_png_and_vector_pdf(self):
        expected_paths = [
            "figures/figure_01_ebpr_phase_cycle.png",
            "figures/figure_01_ebpr_phase_cycle.pdf",
            "figures/figure_02_baseline_fluxes.png",
            "figures/figure_02_baseline_fluxes.pdf",
            "figures/figure_03_sensitivity_analysis.png",
            "figures/figure_03_sensitivity_analysis.pdf",
            "figures/figure_04_illustrative_storage_pools.png",
            "figures/figure_04_illustrative_storage_pools.pdf",
            "results/phase_summary.csv",
            "results/sensitivity_analysis.csv",
            "results/model_results.md",
            "results/future_work.md",
            "results/figure_captions.md",
            "results/dynamic_pool_trajectory.csv",
            "results/dynamic_pool_summary.md",
            "results/EBPR_review_report.pdf",
            "data/dynamic_scenario.csv",
        ]
        for relative_path in expected_paths:
            path = ROOT / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertGreater(path.stat().st_size, 0, relative_path)

        future_work = (ROOT / "results" / "future_work.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("No wet-lab experiments", future_work)
        self.assertIn("Future work", future_work)

    def test_dynamic_storage_illustration_exposes_pool_imbalance(self):
        with (ROOT / "results" / "dynamic_pool_trajectory.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["phase"], "anaerobic")
        self.assertEqual(rows[-1]["phase"], "aerobic")
        self.assertAlmostEqual(float(rows[0]["pha_pool"]), 0.0, places=7)
        self.assertAlmostEqual(float(rows[-1]["pha_pool"]), 0.0, places=5)
        self.assertAlmostEqual(float(rows[0]["polyphosphate_pool"]), 5.0, places=5)
        self.assertGreater(float(rows[-1]["polyphosphate_pool"]), 5.0)

        summary = (ROOT / "results" / "dynamic_pool_summary.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("not dynamic FBA", summary)
        self.assertIn("do not close", summary)

    def test_review_report_is_a_nonempty_pdf(self):
        report = (ROOT / "results" / "EBPR_review_report.pdf").read_bytes()
        self.assertTrue(report.startswith(b"%PDF"))
        self.assertGreater(len(report), 50_000)


if __name__ == "__main__":
    unittest.main()
