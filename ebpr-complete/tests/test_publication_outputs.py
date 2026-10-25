"""Regression tests for model outputs and the attributed qPCR time series."""

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
            "figures/figure_04_measured_population_dynamics.png",
            "figures/figure_04_measured_population_dynamics.pdf",
            "results/phase_summary.csv",
            "results/sensitivity_analysis.csv",
            "results/qpcr_population_summary.csv",
            "results/model_results.md",
            "results/growth_curve_status.md",
            "results/figure_captions.md",
            "results/data_provenance.md",
            "data/external/r1_accumulibacter_ppk1_qpcr_raw_averages.csv",
        ]
        for relative_path in expected_paths:
            path = ROOT / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertGreater(path.stat().st_size, 0, relative_path)

        growth_status = (ROOT / "results" / "growth_curve_status.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("not a biomass-versus-time growth curve", growth_status)

    def test_qpcr_summary_uses_attributed_source_data_and_units(self):
        with (ROOT / "results" / "qpcr_population_summary.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 106)
        self.assertEqual(rows[0]["date"], "2005-02-03")
        self.assertEqual(rows[-1]["date"], "2013-11-16")
        self.assertAlmostEqual(
            float(rows[0]["clade_IA_mean_copies_per_ng_DNA"]), 599000.0, places=4
        )
        self.assertEqual(rows[0]["clade_IA_n_technical_wells"], "3")


if __name__ == "__main__":
    unittest.main()
