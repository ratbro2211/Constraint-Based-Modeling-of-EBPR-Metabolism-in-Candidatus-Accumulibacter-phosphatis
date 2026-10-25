"""Generate publication-style figures and transparent model-result tables.

The figures summarize the illustrative steady-state FBA model. They are not
experimental growth curves or calibrated wastewater-treatment predictions.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from ebpr_model import ROOT, build_model, optimize_phase
from sensitivity_analysis import run_sweeps

RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"

COLORS = {
    "anaerobic": "#1F74AD",
    "aerobic": "#E98E2E",
    "support": "#61A9BD",
    "reserve": "#9267C6",
    "text": "#263238",
    "muted": "#65727A",
    "grid": "#D7DEE2",
    "panel": "#F4F7F8",
    "white": "#FFFFFF",
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.edgecolor": COLORS["muted"],
        "axes.linewidth": 0.7,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
    }
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Cannot write an empty result table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _fmt(value: float) -> str:
    return f"{value:.6g}"


def collect_phase_results() -> list[dict[str, Any]]:
    """Optimize each phase and return interpretable, sign-normalized metrics."""
    rows: list[dict[str, Any]] = []
    for phase, objective_name in (
        ("anaerobic", "PHA accumulation"),
        ("aerobic", "Polyphosphate accumulation"),
    ):
        model = build_model(phase)
        solution = optimize_phase(model)
        fluxes = solution.fluxes
        rows.append(
            {
                "phase": phase,
                "status": solution.status,
                "objective": objective_name,
                "objective_flux": _fmt(float(solution.objective_value)),
                "acetate_uptake": _fmt(max(0.0, -float(fluxes["EX_ac_e"]))),
                "oxygen_uptake": _fmt(max(0.0, -float(fluxes["EX_o2_e"]))),
                "pha_synthesis": _fmt(float(fluxes["PHA_SYN"])),
                "pha_degradation": _fmt(float(fluxes["PHA_DEG"])),
                "polyphosphate_synthesis": _fmt(float(fluxes["PP_SYN"])),
                "polyphosphate_degradation": _fmt(float(fluxes["PP_DEG"])),
                "phosphate_exchange": _fmt(float(fluxes["EX_pi_e"])),
            }
        )
    return rows


def _save_figure(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / f"{stem}.png"
    pdf_path = FIGURES_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png_path, pdf_path


def make_phase_cycle_figure(rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    """Draw the qualitative two-phase cycle encoded by the teaching model."""
    by_phase = {row["phase"]: row for row in rows}
    anaerobic = by_phase["anaerobic"]
    aerobic = by_phase["aerobic"]

    fig, ax = plt.subplots(figsize=(12, 5.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.suptitle(
        "Illustrative EBPR cycle represented by the model",
        fontsize=13,
        fontweight="bold",
        color=COLORS["text"],
        y=0.98,
    )

    for x, color in ((0.025, COLORS["anaerobic"]), (0.515, COLORS["aerobic"])):
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.09),
                0.46,
                0.82,
                boxstyle="round,pad=0.012,rounding_size=0.018",
                linewidth=1.1,
                edgecolor=color,
                facecolor=COLORS["panel"],
                zorder=0,
            )
        )

    ax.text(
        0.255,
        0.855,
        "ANAEROBIC PHASE",
        ha="center",
        va="center",
        color=COLORS["anaerobic"],
        fontsize=10,
        fontweight="bold",
    )
    ax.text(
        0.745,
        0.855,
        "AEROBIC PHASE",
        ha="center",
        va="center",
        color=COLORS["aerobic"],
        fontsize=10,
        fontweight="bold",
    )

    def node(x: float, y: float, w: float, h: float, text: str, color: str) -> None:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.012,rounding_size=0.012",
                linewidth=1,
                edgecolor=color,
                facecolor=COLORS["white"],
                zorder=2,
            )
        )
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            color=COLORS["text"],
            fontsize=8,
            zorder=3,
        )

    def arrow(
        x1: float, y1: float, x2: float, y2: float, color: str, style: str = "solid"
    ) -> None:
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=11,
                linewidth=1.25,
                linestyle=style,
                color=color,
                zorder=1,
            )
        )

    # Anaerobic carbon storage and phosphate release.
    node(0.055, 0.57, 0.115, 0.14, f"Acetate uptake\n{float(anaerobic['acetate_uptake']):.2f}", COLORS["anaerobic"])
    node(0.205, 0.57, 0.115, 0.14, "Acetyl-CoA\n(lumped)", COLORS["support"])
    node(0.355, 0.57, 0.105, 0.14, f"PHA storage\n{float(anaerobic['pha_synthesis']):.2f}", COLORS["anaerobic"])
    arrow(0.17, 0.64, 0.205, 0.64, COLORS["anaerobic"])
    arrow(0.32, 0.64, 0.355, 0.64, COLORS["anaerobic"])
    node(0.09, 0.29, 0.135, 0.14, f"Poly-P reserve\nuse {float(anaerobic['polyphosphate_degradation']):.2f}", COLORS["reserve"])
    node(0.285, 0.29, 0.145, 0.14, f"Phosphate release\n{float(anaerobic['phosphate_exchange']):.2f}", COLORS["support"])
    arrow(0.225, 0.36, 0.285, 0.36, COLORS["support"])
    ax.text(
        0.255,
        0.18,
        "Glycogen → glycolysis → pyruvate oxidation is included as a lumped route.",
        ha="center",
        va="center",
        color=COLORS["muted"],
        fontsize=7,
    )

    # Aerobic reserve oxidation, oxygen use, and polyphosphate storage.
    node(0.54, 0.57, 0.105, 0.14, f"PHA oxidation\n{float(aerobic['pha_degradation']):.2f}", COLORS["aerobic"])
    node(0.675, 0.57, 0.105, 0.14, "TCA +\nOXPHOS", COLORS["support"])
    node(0.81, 0.57, 0.105, 0.14, "ATP\nsupply", COLORS["reserve"])
    node(0.90, 0.31, 0.075, 0.15, f"Poly-P\nstorage\n{float(aerobic['polyphosphate_synthesis']):.2f}", COLORS["aerobic"])
    arrow(0.645, 0.64, 0.675, 0.64, COLORS["aerobic"])
    arrow(0.78, 0.64, 0.81, 0.64, COLORS["aerobic"])
    arrow(0.915, 0.57, 0.935, 0.46, COLORS["aerobic"])
    node(0.58, 0.28, 0.125, 0.14, f"O₂ uptake\n{float(aerobic['oxygen_uptake']):.2f}", COLORS["support"])
    node(
        0.735,
        0.28,
        0.135,
        0.14,
        f"Phosphate uptake\n{abs(float(aerobic['phosphate_exchange'])):.2f}",
        COLORS["support"],
    )
    arrow(0.642, 0.42, 0.705, 0.57, COLORS["support"])
    arrow(0.87, 0.35, 0.90, 0.38, COLORS["support"])
    fig.text(
        0.5,
        0.025,
        "Flux values are arbitrary model units; arrows summarize pseudo-reactions, not measured rates or a time trajectory.",
        ha="center",
        fontsize=8,
        color=COLORS["muted"],
    )
    return _save_figure(fig, "figure_01_ebpr_phase_cycle")


def make_baseline_flux_figure(rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    by_phase = {row["phase"]: row for row in rows}
    panels = [
        (
            "anaerobic",
            "A  Anaerobic: storage and release",
            [
                ("Acetate uptake", "acetate_uptake"),
                ("PHA synthesis", "pha_synthesis"),
                ("Poly-P degradation", "polyphosphate_degradation"),
                ("Phosphate release", "phosphate_exchange"),
            ],
            COLORS["anaerobic"],
        ),
        (
            "aerobic",
            "B  Aerobic: oxidation and storage",
            [
                ("PHA degradation", "pha_degradation"),
                ("Oxygen uptake", "oxygen_uptake"),
                ("Poly-P synthesis", "polyphosphate_synthesis"),
                ("Phosphate uptake", "phosphate_exchange"),
            ],
            COLORS["aerobic"],
        ),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), sharex=True)
    for axis, (phase, title, metrics, color) in zip(axes, panels):
        row = by_phase[phase]
        labels = [label for label, _ in metrics]
        values = []
        for label, key in metrics:
            value = float(row[key])
            # Uptake and export are displayed as positive magnitudes; the CSV
            # retains signed EX_pi_e in phosphate_exchange.
            if label == "Phosphate uptake":
                value = abs(value)
            values.append(value)
        y = list(range(len(labels)))
        bars = axis.barh(y, values, color=color, height=0.62, edgecolor="white", linewidth=0.6)
        axis.set_yticks(y, labels)
        axis.invert_yaxis()
        axis.set_title(title, loc="left", pad=10, color=COLORS["text"])
        axis.set_xlim(0, 22)
        axis.grid(axis="x", color=COLORS["grid"], linewidth=0.65)
        axis.set_axisbelow(True)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_visible(False)
        axis.tick_params(axis="y", length=0, pad=6)
        for bar, value in zip(bars, values):
            axis.text(
                bar.get_width() + 0.35,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.2f}",
                va="center",
                ha="left",
                fontsize=8,
                color=COLORS["text"],
            )
    axes[0].set_xlabel("Flux magnitude (arbitrary model units)")
    axes[1].set_xlabel("Flux magnitude (arbitrary model units)")
    fig.suptitle(
        "Baseline phase-specific fluxes",
        fontsize=13,
        fontweight="bold",
        color=COLORS["text"],
        y=1.02,
    )
    fig.text(
        0.5,
        0.015,
        "Exchange values are converted to positive uptake/release magnitudes for display; the results CSV preserves the signed phosphate exchange.",
        ha="center",
        fontsize=7.5,
        color=COLORS["muted"],
    )
    fig.tight_layout()
    return _save_figure(fig, "figure_02_baseline_fluxes")


def make_sensitivity_figure(rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    panels = [
        ("anaerobic_acetate_max", "anaerobic", "pha_accumulation", "Acetate uptake cap", "PHA accumulation"),
        ("anaerobic_polyP_reserve", "anaerobic", "pha_accumulation", "Poly-P reserve cap", "PHA accumulation"),
        ("anaerobic_glycogen_reserve", "anaerobic", "pha_accumulation", "Glycogen reserve cap", "PHA accumulation"),
        ("aerobic_oxygen_max", "aerobic", "pp_accumulation", "Oxygen uptake cap", "Poly-P accumulation"),
        ("atp_maintenance", "anaerobic", "pha_accumulation", "ATP maintenance demand", "PHA accumulation"),
        ("atp_maintenance", "aerobic", "pp_accumulation", "ATP maintenance demand", "Poly-P accumulation"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(11, 6.6), constrained_layout=True)
    for index, (axis, spec) in enumerate(zip(axes.flat, panels)):
        parameter, phase, metric, xlabel, ylabel = spec
        selected = sorted(
            (
                row
                for row in rows
                if row["parameter"] == parameter and row["phase"] == phase
            ),
            key=lambda row: float(row["value"]),
        )
        feasible = [row for row in selected if row["status"] == "optimal"]
        x = [float(row["value"]) for row in feasible]
        y = [float(row[metric]) for row in feasible]
        color = COLORS["anaerobic"] if phase == "anaerobic" else COLORS["aerobic"]
        axis.plot(x, y, color=color, linewidth=1.8, marker="o", markersize=4)
        axis.set_title(f"{chr(65 + index)}  {xlabel}", loc="left", color=COLORS["text"])
        axis.set_xlabel(xlabel + " (arbitrary units)")
        axis.set_ylabel(ylabel + " (arbitrary units)")
        axis.grid(color=COLORS["grid"], linewidth=0.6)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.margins(x=0.08, y=0.15)
        infeasible = [row for row in selected if row["status"] != "optimal"]
        if infeasible:
            values = ", ".join(f"{float(row['value']):g}" for row in infeasible)
            axis.text(
                0.98,
                0.95,
                f"Infeasible at cap = {values}",
                transform=axis.transAxes,
                ha="right",
                va="top",
                fontsize=7,
                color=COLORS["muted"],
            )
    fig.suptitle(
        "One-at-a-time sensitivity of phase objectives",
        fontsize=13,
        fontweight="bold",
        color=COLORS["text"],
    )
    return _save_figure(fig, "figure_03_sensitivity_analysis")


def _write_results_notes(
    phase_rows: list[dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
) -> None:
    anaerobic, aerobic = phase_rows
    infeasible = sum(row["status"] != "optimal" for row in sensitivity_rows)
    model_results = f"""# Model results

## Baseline optimization

| Phase | Objective flux | Key supporting fluxes |
| --- | ---: | --- |
| Anaerobic | PHA accumulation {anaerobic['objective_flux']} | Poly-P degradation {anaerobic['polyphosphate_degradation']}; phosphate exchange {anaerobic['phosphate_exchange']} (release) |
| Aerobic | Poly-P accumulation {aerobic['objective_flux']} | PHA degradation {aerobic['pha_degradation']}; oxygen uptake {aerobic['oxygen_uptake']}; phosphate exchange {aerobic['phosphate_exchange']} (uptake) |

All values are arbitrary steady-state flux units produced by the checked-in
teaching model. They are not measured rates, biomass growth, or plant-scale
predictions. Exchange fluxes are negative for uptake and positive for release.

## Sensitivity

The one-at-a-time analysis contains {len(sensitivity_rows)} optimization runs;
{infeasible} are infeasible under the fixed ATP-maintenance constraint. See
`sensitivity_analysis.csv` and `../figures/figure_03_sensitivity_analysis.png`.
The sweep demonstrates model constraint behavior, not parameter uncertainty or
statistical significance.
"""
    future_work = """# Future work

This project currently contains model outputs only. No wet-lab experiments or
experimental measurements were conducted for this project.

The current model has no biomass reaction, biomass state variable, or time
integration, so its steady-state fluxes cannot produce a growth curve. Future
work could add a dynamic model and, if experimental work becomes available,
validate it using documented biomass and phosphorus measurements with matched
units, sampling times, and operating conditions.
"""
    figure_captions = """# Figure captions

1. **Illustrative EBPR phase cycle.** Qualitative reaction flow in the
   two independent steady-state optimizations. Flux labels are arbitrary model
   units; arrows summarize pseudo-reactions and are not a time trajectory.
2. **Baseline phase-specific fluxes.** Magnitudes of selected uptake, storage,
   and release fluxes from the default anaerobic and aerobic optimizations.
   Exchange fluxes are converted to positive magnitudes only for display.
3. **One-at-a-time sensitivity.** Objective flux response to the five varied
   parameter groups. Infeasible boundary cases are noted, not plotted as zero.
   No uncertainty intervals are available because these are deterministic
   teaching-model solves with arbitrary bounds.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "model_results.md").write_text(
        model_results, encoding="utf-8"
    )
    (RESULTS_DIR / "future_work.md").write_text(
        future_work, encoding="utf-8"
    )
    (RESULTS_DIR / "figure_captions.md").write_text(
        figure_captions, encoding="utf-8"
    )


def generate_publication_outputs() -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    phase_rows = collect_phase_results()
    sensitivity_rows = run_sweeps()
    _write_csv(RESULTS_DIR / "phase_summary.csv", phase_rows)
    _write_csv(RESULTS_DIR / "sensitivity_analysis.csv", sensitivity_rows)
    _write_results_notes(phase_rows, sensitivity_rows)

    figures = [
        *make_phase_cycle_figure(phase_rows),
        *make_baseline_flux_figure(phase_rows),
        *make_sensitivity_figure(sensitivity_rows),
    ]
    return {
        "phase_rows": phase_rows,
        "sensitivity_runs": len(sensitivity_rows),
        "infeasible_runs": sum(row["status"] != "optimal" for row in sensitivity_rows),
        "figures": [str(path.relative_to(ROOT)) for path in figures],
        "results": [
            str((RESULTS_DIR / "phase_summary.csv").relative_to(ROOT)),
            str((RESULTS_DIR / "sensitivity_analysis.csv").relative_to(ROOT)),
            str((RESULTS_DIR / "model_results.md").relative_to(ROOT)),
            str((RESULTS_DIR / "future_work.md").relative_to(ROOT)),
            str((RESULTS_DIR / "figure_captions.md").relative_to(ROOT)),
        ],
    }


def main() -> None:
    output = generate_publication_outputs()
    print(
        f"Generated {len(output['figures']) // 2} publication-style figures "
        "(each as PNG and vector PDF) "
        f"from {output['sensitivity_runs']} sensitivity runs "
        f"({output['infeasible_runs']} infeasible)."
    )
    for path in output["figures"] + output["results"]:
        print(path)


if __name__ == "__main__":
    main()
