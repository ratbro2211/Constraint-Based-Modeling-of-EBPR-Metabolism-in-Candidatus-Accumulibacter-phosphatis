"""Generate publication-style figures and transparent model-result tables.

The figures summarize the illustrative steady-state FBA model. They are not
experimental growth curves or calibrated wastewater-treatment predictions.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
import statistics
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from ebpr_model import ROOT, build_model, optimize_phase
from sensitivity_analysis import run_sweeps

RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
QPCR_DATA = ROOT / "data" / "external" / "r1_accumulibacter_ppk1_qpcr_raw_averages.csv"
REACTOR_RESEED_DATE = date(2010, 1, 28)

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


def collect_qpcr_summary() -> list[dict[str, Any]]:
    """Aggregate source qPCR wells by date without converting units."""
    if not QPCR_DATA.is_file():
        raise FileNotFoundError(f"Required attributed qPCR data not found: {QPCR_DATA}")

    ia_values: dict[date, list[float]] = defaultdict(list)
    iia_values: dict[date, list[float]] = defaultdict(list)
    with QPCR_DATA.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        if (
            len(header) < 8
            or "Copies/ng DNA" not in header[4]
            or "Copies/ng DNA" not in header[7]
        ):
            raise ValueError("Unexpected qPCR source columns; verify source data and units.")
        for line_number, row in enumerate(reader, start=2):
            if len(row) < 8:
                raise ValueError(f"Malformed qPCR row at line {line_number}.")
            ia_date = datetime.strptime(row[2], "%m/%d/%y").date()
            iia_date = datetime.strptime(row[5], "%m/%d/%y").date()
            ia_values[ia_date].append(float(row[4]))
            iia_values[iia_date].append(float(row[7]))

    if set(ia_values) != set(iia_values):
        raise ValueError("Clade IA and IIA qPCR sample dates do not match.")

    rows: list[dict[str, Any]] = []
    for sample_date in sorted(ia_values):
        row: dict[str, Any] = {
            "date": sample_date.isoformat(),
            "days_from_2010_01_28_reseed": (sample_date - REACTOR_RESEED_DATE).days,
        }
        for clade, values in (
            ("clade_IA", ia_values[sample_date]),
            ("clade_IIA", iia_values[sample_date]),
        ):
            row[f"{clade}_mean_copies_per_ng_DNA"] = _fmt(statistics.mean(values))
            row[f"{clade}_sd_copies_per_ng_DNA"] = _fmt(
                statistics.stdev(values) if len(values) > 1 else 0.0
            )
            row[f"{clade}_min_copies_per_ng_DNA"] = _fmt(min(values))
            row[f"{clade}_max_copies_per_ng_DNA"] = _fmt(max(values))
            row[f"{clade}_n_technical_wells"] = len(values)
        rows.append(row)
    return rows


def make_qpcr_population_figure(
    rows: list[dict[str, Any]],
) -> tuple[Path, Path]:
    """Plot measured ppk1 abundance as population dynamics, not biomass growth."""
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    dates = [datetime.fromisoformat(row["date"]) for row in rows]
    for key, label, color in (
        ("clade_IA", "Clade IA", COLORS["anaerobic"]),
        ("clade_IIA", "Clade IIA", COLORS["aerobic"]),
    ):
        means = [float(row[f"{key}_mean_copies_per_ng_DNA"]) for row in rows]
        lower = [
            mean - float(row[f"{key}_min_copies_per_ng_DNA"])
            for mean, row in zip(means, rows)
        ]
        upper = [
            float(row[f"{key}_max_copies_per_ng_DNA"]) - mean
            for mean, row in zip(means, rows)
        ]
        ax.errorbar(
            dates,
            means,
            yerr=[lower, upper],
            color=color,
            marker="o",
            markersize=3,
            linewidth=1.1,
            elinewidth=0.55,
            capsize=1.3,
            label=label,
            zorder=3,
        )

    reset_at = datetime.combine(REACTOR_RESEED_DATE, datetime.min.time())
    ax.axvline(reset_at, color=COLORS["muted"], linestyle="--", linewidth=1, zorder=1)
    ax.annotate(
        "R1 reseeded\n28 Jan 2010",
        xy=(reset_at, 0.95),
        xycoords=("data", "axes fraction"),
        xytext=(6, -4),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=8,
        color=COLORS["muted"],
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "none", "alpha": 0.9},
    )
    ax.set_yscale("log")
    ax.set_xlabel("Sampling date")
    ax.set_ylabel("ppk1 gene copies per ng DNA (log scale)")
    ax.set_title(
        "Measured Accumulibacter population dynamics in an EBPR reactor",
        loc="left",
        color=COLORS["text"],
        fontweight="bold",
        pad=12,
    )
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.7, which="major")
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.35, which="minor", alpha=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.text(
        0.12,
        0.015,
        "Points are arithmetic means; whiskers span technical qPCR wells (2–3 per date). "
        "This is ppk1 abundance per DNA mass, not biomass concentration or an axenic growth curve.",
        fontsize=8,
        color=COLORS["muted"],
    )
    fig.subplots_adjust(bottom=0.17, top=0.88, left=0.10, right=0.98)
    return _save_figure(fig, "figure_04_measured_population_dynamics")


def _write_results_notes(
    phase_rows: list[dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
    qpcr_rows: list[dict[str, Any]],
) -> None:
    anaerobic, aerobic = phase_rows
    infeasible = sum(row["status"] != "optimal" for row in sensitivity_rows)
    first_qpcr_date = qpcr_rows[0]["date"]
    last_qpcr_date = qpcr_rows[-1]["date"]
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

## Separate measured population time series

Figure 4 and `qpcr_population_summary.csv` summarize a separately sourced
Accumulibacter ppk1 qPCR dataset with {len(qpcr_rows)} sampling dates from
{first_qpcr_date} to {last_qpcr_date}. The measurements are gene copies per ng
DNA, not biomass concentration or model fluxes. They are shown as external
biological context and are not used to fit or validate the teaching model.
See `data_provenance.md` for attribution and processing details.
"""
    growth_status = """# Growth curve status

Figure 4 is a measured Accumulibacter population-abundance time series from
ppk1 qPCR (gene copies per ng DNA) in a separate EBPR enrichment reactor. It is
not a biomass-versus-time growth curve, cell concentration, or axenic growth
experiment. Technical qPCR wells are not biological replicates.

The teaching FBA model itself has no biomass reaction, biomass state variable,
or time integration, so its steady-state fluxes cannot produce a growth curve.
The external qPCR series is included as clearly attributed biological context,
not as calibration or validation of the model. A true biomass growth curve
would need matched OD600, VSS, or TSS measurements, with units and experimental
conditions.
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
4. **Measured Accumulibacter population dynamics.** Arithmetic mean ppk1 qPCR
   copies per ng DNA for clades IA and IIA, with whiskers showing the minimum
   and maximum of 2–3 technical qPCR wells per date. The y-axis is logarithmic.
   The dashed line marks the R1 reseeding event on 28 January 2010 described by
   the source study. This independent reactor time series is not a biomass
   growth curve or validation of the FBA model. See `data_provenance.md`.
"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "model_results.md").write_text(
        model_results, encoding="utf-8"
    )
    (RESULTS_DIR / "growth_curve_status.md").write_text(
        growth_status, encoding="utf-8"
    )
    (RESULTS_DIR / "figure_captions.md").write_text(
        figure_captions, encoding="utf-8"
    )


def generate_publication_outputs() -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    phase_rows = collect_phase_results()
    sensitivity_rows = run_sweeps()
    qpcr_rows = collect_qpcr_summary()
    _write_csv(RESULTS_DIR / "phase_summary.csv", phase_rows)
    _write_csv(RESULTS_DIR / "sensitivity_analysis.csv", sensitivity_rows)
    _write_csv(RESULTS_DIR / "qpcr_population_summary.csv", qpcr_rows)
    _write_results_notes(phase_rows, sensitivity_rows, qpcr_rows)

    figures = [
        *make_phase_cycle_figure(phase_rows),
        *make_baseline_flux_figure(phase_rows),
        *make_sensitivity_figure(sensitivity_rows),
        *make_qpcr_population_figure(qpcr_rows),
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
            str((RESULTS_DIR / "growth_curve_status.md").relative_to(ROOT)),
            str((RESULTS_DIR / "figure_captions.md").relative_to(ROOT)),
            str((RESULTS_DIR / "qpcr_population_summary.csv").relative_to(ROOT)),
            str((RESULTS_DIR / "data_provenance.md").relative_to(ROOT)),
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
    print(
        "Figure 4 is measured qPCR population dynamics, not a biomass growth "
        "curve; the model itself has no biomass dynamics."
    )


if __name__ == "__main__":
    main()
