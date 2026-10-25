"""Run one-at-a-time sensitivity sweeps and save a CSV plus a PNG figure."""

from __future__ import annotations

import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ebpr_model import ARTIFACTS_DIR, build_model, load_parameters


SWEEPS = {
    "anaerobic_acetate_max": ("anaerobic", [0, 2.5, 5, 7.5, 10]),
    "anaerobic_polyP_reserve": ("anaerobic", [0, 1, 2.5, 5, 7.5]),
    "anaerobic_glycogen_reserve": ("anaerobic", [0, 0.25, 0.5, 1, 2]),
    "aerobic_oxygen_max": ("aerobic", [0, 2.5, 5, 7.5, 10]),
    "atp_maintenance": ("both", [0, 0.1, 0.25, 0.5, 1]),
}


def _run(phase: str, overrides: dict[str, float]) -> dict[str, object]:
    model = build_model(phase, overrides)
    solution = model.optimize()
    row: dict[str, object] = {
        "phase": phase,
        "status": solution.status,
        "objective_flux": "",
        "pha_accumulation": "",
        "pp_accumulation": "",
        "phosphate_exchange": "",
        "oxygen_exchange": "",
        "acetate_exchange": "",
    }
    if solution.status == "optimal":
        fluxes = solution.fluxes
        row.update(
            objective_flux=f"{solution.objective_value:.8g}",
            pha_accumulation=f"{fluxes['PHA_ACCUM']:.8g}",
            pp_accumulation=f"{fluxes['PP_ACCUM']:.8g}",
            phosphate_exchange=f"{fluxes['EX_pi_e']:.8g}",
            oxygen_exchange=f"{fluxes['EX_o2_e']:.8g}",
            acetate_exchange=f"{fluxes['EX_ac_e']:.8g}",
        )
    return row


def run_sweeps() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for parameter, (phase, values) in SWEEPS.items():
        for value in values:
            phases = ("anaerobic", "aerobic") if phase == "both" else (phase,)
            for current_phase in phases:
                rows.append(
                    {
                        "parameter": parameter,
                        "value": value,
                        **_run(current_phase, {parameter: value}),
                    }
                )
    return rows


def _number(row: dict[str, object], field: str) -> float:
    value = row[field]
    return float(value) if value != "" else float("nan")


def write_outputs(rows: list[dict[str, object]]) -> tuple[str, str]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = ARTIFACTS_DIR / "sensitivity_analysis.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    fig, axes = plt.subplots(2, 3, figsize=(13, 8), constrained_layout=True)
    plots = [
        ("anaerobic_acetate_max", "anaerobic", "pha_accumulation", "Acetate cap", "PHA accumulation"),
        ("anaerobic_polyP_reserve", "anaerobic", "pha_accumulation", "Poly-P reserve cap", "PHA accumulation"),
        ("anaerobic_glycogen_reserve", "anaerobic", "pha_accumulation", "Glycogen reserve cap", "PHA accumulation"),
        ("aerobic_oxygen_max", "aerobic", "pp_accumulation", "Oxygen uptake cap", "Poly-P accumulation"),
        ("atp_maintenance", "anaerobic", "pha_accumulation", "ATP maintenance", "PHA accumulation"),
        ("atp_maintenance", "aerobic", "pp_accumulation", "ATP maintenance", "Poly-P accumulation"),
    ]
    for axis, (parameter, phase, metric, xlabel, ylabel) in zip(axes.flat, plots):
        selected = [
            row
            for row in rows
            if row["parameter"] == parameter and row["phase"] == phase
        ]
        x = [float(row["value"]) for row in selected]
        y = [_number(row, metric) for row in selected]
        axis.plot(x, y, marker="o")
        axis.set_title(f"{phase.title()}: {parameter}")
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.grid(True, alpha=0.3)
    fig.suptitle("Illustrative EBPR one-at-a-time sensitivity analysis")
    png_path = ARTIFACTS_DIR / "sensitivity_analysis.png"
    fig.savefig(png_path, dpi=160)
    plt.close(fig)
    return str(csv_path), str(png_path)


def main() -> None:
    rows = run_sweeps()
    csv_path, png_path = write_outputs(rows)
    infeasible = sum(row["status"] != "optimal" for row in rows)
    print(f"Recorded {len(rows)} sensitivity runs ({infeasible} infeasible).")
    print(f"CSV: {csv_path}")
    print(f"Figure: {png_path}")


if __name__ == "__main__":
    main()
