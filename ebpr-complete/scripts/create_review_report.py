"""Assemble the generated EBPR outputs into a lightweight, cited PDF brief."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
INK = "#1C2B36"
MUTED = "#5A6D78"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def create_report() -> Path:
    phase_rows = read_rows(RESULTS / "phase_summary.csv")
    sensitivity_rows = read_rows(RESULTS / "sensitivity_analysis.csv")
    report_path = RESULTS / "EBPR_review_report.pdf"
    figure_specs = [
        (
            "figure_01_ebpr_phase_cycle.png",
            "Figure 1. Qualitative EBPR phase-cycle schematic; fluxes use arbitrary model units.",
        ),
        (
            "figure_02_baseline_fluxes.png",
            "Figure 2. Baseline phase-specific flux magnitudes from the illustrative FBA model.",
        ),
        (
            "figure_03_sensitivity_analysis.png",
            "Figure 3. One-at-a-time sensitivity of the phase objectives; infeasible boundary cases are shown.",
        ),
    ]

    with PdfPages(report_path) as pdf:
        metadata = pdf.infodict()
        metadata["Title"] = "EBPR model results"
        metadata["Subject"] = "Review brief for an illustrative EBPR FBA teaching model"
        metadata["Author"] = "EBPR project review package"
        metadata["Creator"] = "create_review_report.py"

        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        ax = fig.add_axes([0.10, 0.08, 0.80, 0.84])
        ax.axis("off")
        ax.text(
            0,
            1,
            "EBPR model results",
            fontsize=21,
            fontweight="bold",
            color=INK,
            va="top",
            linespacing=1.15,
        )
        ax.text(
            0,
            0.905,
            "Model-only results brief • illustrative steady-state FBA",
            fontsize=9.5,
            color=MUTED,
            va="top",
        )
        ax.text(
            0,
            0.83,
            "Baseline model outputs",
            fontsize=12,
            fontweight="bold",
            color=INK,
            va="top",
        )

        table_rows = []
        for row in phase_rows:
            exchange = float(row["phosphate_exchange"])
            exchange_text = (
                f"{abs(exchange):.2f} release"
                if exchange >= 0
                else f"{abs(exchange):.2f} uptake"
            )
            table_rows.append(
                [
                    row["phase"].title(),
                    row["objective"],
                    row["objective_flux"],
                    exchange_text,
                    row["oxygen_uptake"],
                ]
            )
        table = ax.table(
            cellText=table_rows,
            colLabels=["Phase", "Objective", "Flux", "P exchange", "O₂ uptake"],
            cellLoc="left",
            colLoc="left",
            bbox=[0, 0.59, 1, 0.19],
            colWidths=[0.16, 0.29, 0.14, 0.24, 0.17],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(7.5)
        for (row_index, _), cell in table.get_celld().items():
            cell.set_edgecolor("#D6E0E5")
            if row_index == 0:
                cell.set_facecolor("#EAF1F4")
                cell.set_text_props(weight="bold", color=INK)
            else:
                cell.set_facecolor("white")
                cell.set_text_props(color=INK)

        infeasible = sum(row["status"] != "optimal" for row in sensitivity_rows)
        ax.text(
            0,
            0.55,
            f"Sensitivity analysis: {len(sensitivity_rows)} optimization runs; "
            f"{infeasible} infeasible boundary cases.",
            fontsize=8.5,
            color=INK,
            va="top",
        )
        ax.text(
            0,
            0.48,
            "How to read these results",
            fontsize=12,
            fontweight="bold",
            color=INK,
            va="top",
        )
        ax.text(
            0,
            0.435,
            "These figures show fluxes and constraint responses calculated by the "
            "checked-in model. The sensitivity sweep is deterministic and tests model "
            "behavior under selected bounds; it is not a fit, prediction, or estimate "
            "of biological variability.",
            fontsize=8.7,
            color=INK,
            va="top",
            wrap=True,
            linespacing=1.35,
        )
        ax.text(
            0,
            0.30,
            "Interpretation limits",
            fontsize=12,
            fontweight="bold",
            color=INK,
            va="top",
        )
        ax.text(
            0,
            0.255,
            "No wet-lab experiments or experimental measurements were conducted for "
            "this project. The FBA network is an illustrative, non-atom/charge-balanced "
            "teaching model with arbitrary flux units; it has no biomass reaction or time "
            "integration, so it cannot produce a growth curve. Future work could add "
            "dynamic behavior and, if experiments are later performed, validate against "
            "documented biomass and phosphorus measurements.",
            fontsize=8.7,
            color=INK,
            va="top",
            wrap=True,
            linespacing=1.35,
        )
        ax.text(
            0,
            0.08,
            "The model is intended to demonstrate qualitative constraint effects, not "
            "to represent calibrated EBPR kinetics or predict wastewater-treatment performance. "
            "See the README references for the process context.",
            fontsize=7.2,
            color=MUTED,
            va="bottom",
            wrap=True,
        )
        pdf.savefig(fig)
        plt.close(fig)

        for filename, caption in figure_specs:
            fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
            ax = fig.add_axes([0.04, 0.11, 0.92, 0.82])
            with Image.open(FIGURES / filename) as image_file:
                image_file.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
                image = np.asarray(image_file.convert("RGB"))
            ax.imshow(image)
            ax.axis("off")
            fig.text(
                0.05,
                0.045,
                caption,
                fontsize=8.2,
                color=INK,
                ha="left",
                wrap=True,
            )
            pdf.savefig(fig)
            plt.close(fig)
    return report_path


if __name__ == "__main__":
    output = create_report()
    print(f"Created {output.relative_to(ROOT)}")
