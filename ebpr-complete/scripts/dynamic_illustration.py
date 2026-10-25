"""Integrate one illustrative storage-pool trajectory from baseline FBA fluxes.

This is a model-only visualization, not dynamic FBA, a biomass growth model,
or a calibrated prediction. Time and pool units are arbitrary.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ebpr_model import ROOT


RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
SCENARIO_FILE = ROOT / "data" / "dynamic_scenario.csv"
FIGURE_STEM = "figure_04_illustrative_storage_pools"
COLORS = {
    "anaerobic": "#1F74AD",
    "aerobic": "#E98E2E",
    "text": "#263238",
    "muted": "#65727A",
    "grid": "#D7DEE2",
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_scenario() -> dict[str, float]:
    return {
        row["parameter"]: float(row["value"])
        for row in read_csv_rows(SCENARIO_FILE)
    }


def simulate_pool_trajectory(
    phase_rows: list[dict[str, str]],
    scenario: dict[str, float],
) -> tuple[list[dict[str, object]], dict[str, float]]:
    """Integrate storage fluxes piecewise, choosing aerobic duration to drain PHA."""
    phases = {row["phase"]: row for row in phase_rows}
    anaerobic = phases["anaerobic"]
    aerobic = phases["aerobic"]

    anaerobic_duration = scenario["anaerobic_duration"]
    points = int(scenario["sample_points_per_phase"])
    initial_pha = scenario["initial_pha_pool"]
    pha_synthesis = float(anaerobic["pha_synthesis"])
    polyphosphate_degradation = float(anaerobic["polyphosphate_degradation"])
    pha_degradation = float(aerobic["pha_degradation"])
    polyphosphate_synthesis = float(aerobic["polyphosphate_synthesis"])

    if points < 2 or anaerobic_duration <= 0:
        raise ValueError("Scenario needs at least 2 points and a positive phase duration.")
    if min(pha_synthesis, polyphosphate_degradation, pha_degradation, polyphosphate_synthesis) < 0:
        raise ValueError("Storage fluxes must be nonnegative for this illustration.")
    if pha_degradation <= 0:
        raise ValueError("Aerobic PHA degradation must be positive to close the PHA pool.")

    # Initial poly-P is set to exactly one anaerobic phase's integrated
    # degradation, so the illustrative anaerobic phase depletes that reserve.
    initial_polyphosphate = polyphosphate_degradation * anaerobic_duration
    pha_after_anaerobic = initial_pha + pha_synthesis * anaerobic_duration
    polyphosphate_after_anaerobic = (
        initial_polyphosphate - polyphosphate_degradation * anaerobic_duration
    )

    # The aerobic interval is derived—not measured—to return the PHA pool to
    # its initial value using the independent aerobic baseline optimum.
    aerobic_duration = (pha_after_anaerobic - initial_pha) / pha_degradation
    total_duration = anaerobic_duration + aerobic_duration
    rows: list[dict[str, object]] = []

    for index in range(points):
        fraction = index / (points - 1)
        elapsed = fraction * anaerobic_duration
        rows.append(
            {
                "time": elapsed,
                "phase": "anaerobic",
                "pha_pool": initial_pha + pha_synthesis * elapsed,
                "polyphosphate_pool": max(
                    0.0,
                    initial_polyphosphate - polyphosphate_degradation * elapsed,
                ),
            }
        )

    for index in range(1, points):
        fraction = index / (points - 1)
        elapsed = fraction * aerobic_duration
        rows.append(
            {
                "time": anaerobic_duration + elapsed,
                "phase": "aerobic",
                "pha_pool": max(0.0, pha_after_anaerobic - pha_degradation * elapsed),
                "polyphosphate_pool": polyphosphate_after_anaerobic
                + polyphosphate_synthesis * elapsed,
            }
        )

    final_pha = float(rows[-1]["pha_pool"])
    final_polyphosphate = float(rows[-1]["polyphosphate_pool"])
    summary = {
        "anaerobic_duration": anaerobic_duration,
        "aerobic_duration": aerobic_duration,
        "initial_pha_pool": initial_pha,
        "initial_polyphosphate_pool": initial_polyphosphate,
        "pha_after_anaerobic": pha_after_anaerobic,
        "final_pha_pool": final_pha,
        "final_polyphosphate_pool": final_polyphosphate,
        "polyphosphate_pool_change": final_polyphosphate - initial_polyphosphate,
    }
    return rows, summary


def write_outputs(
    rows: list[dict[str, object]],
    summary: dict[str, float],
) -> tuple[Path, Path, Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    table_path = RESULTS_DIR / "dynamic_pool_trajectory.csv"
    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["time", "phase", "pha_pool", "polyphosphate_pool"],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary_path = RESULTS_DIR / "dynamic_pool_summary.md"
    summary_path.write_text(
        f"""# Illustrative storage-pool time course

This is a model-only, piecewise integration of baseline FBA storage fluxes. It
is not dynamic FBA, a biomass growth curve, or an experimentally calibrated
prediction. Time and pool units are arbitrary.

## Scenario assumptions

- Anaerobic duration: {summary["anaerobic_duration"]:.3g} arbitrary time units.
- Initial PHA pool: {summary["initial_pha_pool"]:.3g} arbitrary pool units.
- Initial polyphosphate pool: {summary["initial_polyphosphate_pool"]:.3g} units,
  set to one anaerobic phase's integrated baseline polyphosphate degradation.
- Aerobic duration: {summary["aerobic_duration"]:.4g} arbitrary time units,
  derived so the baseline aerobic PHA-degradation flux returns PHA to its
  initial pool.
- The curves connect integrated model fluxes; plotted points are numerical
  rendering points, not experimental samples.

## Interpretation

PHA returns to {summary["final_pha_pool"]:.3g} pool units. Polyphosphate ends at
{summary["final_polyphosphate_pool"]:.4g} units, a net change of
{summary["polyphosphate_pool_change"]:+.4g} units from its initial amount.
Therefore, the independently optimized phase fluxes do not close a
cycle-balanced polyphosphate pool under these assumptions. The drift is a
useful model limitation to address before interpreting this as a repeating
biological cycle.

The underlying FBA model remains two separate steady-state optimizations and
has no biomass state. This figure is an illustrative storage-pool trajectory,
not a growth curve or wet-lab result.
""",
        encoding="utf-8",
    )

    times = [float(row["time"]) for row in rows]
    pha = [float(row["pha_pool"]) for row in rows]
    polyphosphate = [float(row["polyphosphate_pool"]) for row in rows]
    boundary = summary["anaerobic_duration"]
    final_time = boundary + summary["aerobic_duration"]
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.7), sharex=True)
    for axis in axes:
        axis.axvspan(0, boundary, color=COLORS["anaerobic"], alpha=0.08, linewidth=0)
        axis.axvspan(
            boundary,
            final_time,
            color=COLORS["aerobic"],
            alpha=0.08,
            linewidth=0,
        )
        axis.axvline(boundary, color=COLORS["muted"], linestyle="--", linewidth=1)
        axis.grid(color=COLORS["grid"], linewidth=0.65)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.set_axisbelow(True)

    axes[0].plot(times, pha, color=COLORS["anaerobic"], linewidth=2.2)
    axes[0].scatter(
        [0, boundary, final_time],
        [
            summary["initial_pha_pool"],
            summary["pha_after_anaerobic"],
            summary["final_pha_pool"],
        ],
        color=COLORS["anaerobic"],
        s=18,
        zorder=3,
    )
    axes[0].set_ylabel("PHA pool\n(arbitrary units)")
    axes[0].set_title(
        "Illustrative storage-pool trajectory from baseline FBA fluxes",
        loc="left",
        color=COLORS["text"],
        fontweight="bold",
    )
    axes[1].plot(times, polyphosphate, color=COLORS["aerobic"], linewidth=2.2)
    axes[1].set_ylabel("Poly-P pool\n(arbitrary units)")
    axes[1].set_xlabel("Time (arbitrary units)")
    axes[1].set_xlim(0, final_time)
    axes[1].text(
        0.01,
        0.94,
        "Anaerobic",
        transform=axes[1].transAxes,
        color=COLORS["anaerobic"],
        fontsize=8,
        va="top",
    )
    axes[1].text(
        0.96,
        0.94,
        "Aerobic",
        transform=axes[1].transAxes,
        color=COLORS["aerobic"],
        fontsize=8,
        va="top",
        ha="right",
    )
    fig.text(
        0.5,
        0.015,
        "Model-only illustration; phase rates come from separate steady-state optima. "
        "The poly-P end pool does not return to its start value.",
        ha="center",
        fontsize=8,
        color=COLORS["muted"],
    )
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    png_path = FIGURES_DIR / f"{FIGURE_STEM}.png"
    pdf_path = FIGURES_DIR / f"{FIGURE_STEM}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return table_path, summary_path, png_path, pdf_path


def main() -> None:
    phase_rows = read_csv_rows(RESULTS_DIR / "phase_summary.csv")
    scenario = load_scenario()
    rows, summary = simulate_pool_trajectory(phase_rows, scenario)
    outputs = write_outputs(rows, summary)
    for path in outputs:
        print(path.relative_to(ROOT))
    print(
        "The illustrative cycle returns PHA to its initial pool but changes "
        f"polyphosphate by {summary['polyphosphate_pool_change']:+.4g} units."
    )


if __name__ == "__main__":
    main()
