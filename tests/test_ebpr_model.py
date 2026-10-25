"""Smoke tests for the illustrative phase-specific FBA network."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ebpr_model import build_model  # noqa: E402


class TestEBPRPhases(unittest.TestCase):
    def test_anaerobic_phase_stores_pha_and_releases_phosphate(self):
        model = build_model("anaerobic")
        solution = model.optimize()
        self.assertEqual(solution.status, "optimal")
        self.assertGreater(solution.fluxes["PHA_ACCUM"], 0)
        self.assertGreater(solution.fluxes["PP_DEG"], 0)
        self.assertGreater(solution.fluxes["EX_pi_e"], 0)
        self.assertLess(solution.fluxes["EX_ac_e"], 0)
        self.assertAlmostEqual(solution.fluxes["EX_o2_e"], 0)
        self.assertGreater(solution.fluxes["GLYCOLYSIS"], 0)
        self.assertGreater(solution.fluxes["PDH"], 0)
        self.assertAlmostEqual(solution.fluxes["PHA_ACCUM"], 5.4, places=6)
        self.assertAlmostEqual(solution.fluxes["PP_DEG"], 5.0, places=6)
        self.assertAlmostEqual(solution.fluxes["EX_pi_e"], 5.1, places=6)
        self.assertAlmostEqual(
            solution.fluxes["PHA_SYN"], solution.fluxes["PHA_ACCUM"]
        )

    def test_aerobic_phase_uses_pha_and_accumulates_polyphosphate(self):
        model = build_model("aerobic")
        solution = model.optimize()
        self.assertEqual(solution.status, "optimal")
        self.assertGreater(solution.fluxes["PP_ACCUM"], 0)
        self.assertGreater(solution.fluxes["PHA_DEG"], 0)
        self.assertGreater(solution.fluxes["TCA"], 0)
        self.assertGreater(solution.fluxes["OXPHOS"], 0)
        self.assertLess(solution.fluxes["EX_o2_e"], 0)
        self.assertLess(solution.fluxes["EX_pi_e"], 0)
        self.assertAlmostEqual(solution.fluxes["EX_ac_e"], 0)
        self.assertAlmostEqual(solution.fluxes["PP_ACCUM"], 19.9, places=6)
        self.assertAlmostEqual(solution.fluxes["PHA_DEG"], 20 / 3, places=6)
        self.assertAlmostEqual(
            solution.fluxes["PP_SYN"], solution.fluxes["PP_ACCUM"]
        )

    def test_anoxic_aerobic_phase_cannot_meet_maintenance(self):
        model = build_model("aerobic", {"aerobic_oxygen_max": 0})
        solution = model.optimize()
        self.assertEqual(solution.status, "infeasible")

    def test_zero_polyphosphate_reserve_cannot_meet_anaerobic_maintenance(self):
        model = build_model("anaerobic", {"anaerobic_polyP_reserve": 0})
        solution = model.optimize()
        self.assertEqual(solution.status, "infeasible")


if __name__ == "__main__":
    unittest.main()
