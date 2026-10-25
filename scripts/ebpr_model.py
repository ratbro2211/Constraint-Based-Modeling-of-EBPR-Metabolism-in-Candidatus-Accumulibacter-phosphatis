"""A deliberately small, illustrative COBRApy model for EBPR phase switching.

This is a teaching model, not a curated or experimentally validated
Accumulibacter reconstruction. Several aggregate reactions use pseudo-metabolites
and arbitrary flux units; see the repository README before interpreting results.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping

from cobra import Metabolite, Model, Reaction


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_FILE = ROOT / "data" / "parameters.csv"
ARTIFACTS_DIR = ROOT / "artifacts"
BIG_M = 1000.0


def load_parameters(path: Path = PARAMETERS_FILE) -> dict[str, float]:
    """Load numeric model bounds from the tracked CSV parameter table."""
    values: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            values[row["parameter"]] = float(row["value"])
    return values


def _add_reaction(
    model: Model,
    reaction_id: str,
    name: str,
    stoichiometry: Mapping[str, float],
) -> Reaction:
    reaction = Reaction(reaction_id, name=name)
    reaction.lower_bound = 0.0
    reaction.upper_bound = 0.0
    reaction.add_metabolites(
        {model.metabolites.get_by_id(met_id): coefficient
         for met_id, coefficient in stoichiometry.items()}
    )
    model.add_reactions([reaction])
    return reaction


def _network() -> Model:
    model = Model("illustrative_ebpr")
    metabolite_definitions = {
        "ac_e": ("Acetate, external", "e"),
        "ac_c": ("Acetate, cell", "c"),
        "acetyl_c": ("Acetyl-CoA carbon unit", "c"),
        "pha_c": ("PHA repeat unit", "c"),
        "pp_c": ("Polyphosphate unit", "c"),
        "pi_e": ("Phosphate, external", "e"),
        "pi_c": ("Phosphate, cell", "c"),
        "o2_e": ("Oxygen, external", "e"),
        "o2_c": ("Oxygen, cell", "c"),
        "co2_e": ("Carbon dioxide, external", "e"),
        "nad_c": ("NAD+", "c"),
        "nadh_c": ("NADH", "c"),
        "atp_c": ("ATP", "c"),
        "adp_c": ("ADP", "c"),
        "glycogen_c": ("Glycogen carbon reserve unit", "c"),
    }
    for met_id, (name, compartment) in metabolite_definitions.items():
        model.add_metabolites(
            [Metabolite(met_id, name=name, compartment=compartment)]
        )

    reactions = {
        "EX_ac_e": ("Acetate exchange", {"ac_e": -1}),
        "AC_TRANSPORT": ("Acetate transport", {"ac_e": -1, "ac_c": 1}),
        "EX_o2_e": ("Oxygen exchange", {"o2_e": -1}),
        "O2_TRANSPORT": ("Oxygen transport", {"o2_e": -1, "o2_c": 1}),
        "EX_pi_e": ("Phosphate exchange", {"pi_e": -1}),
        "PI_TRANSPORT": ("Phosphate uptake", {"pi_e": -1, "pi_c": 1}),
        "PI_EXPORT": ("Phosphate release", {"pi_c": -1, "pi_e": 1}),
        "EX_co2_e": ("Carbon dioxide exchange", {"co2_e": -1}),
        "ATPM": ("ATP maintenance demand", {"atp_c": -1, "adp_c": 1, "pi_c": 1}),
        "AC_ACT": (
            "Acetate activation (one ATP per carbon unit)",
            {"ac_c": -1, "atp_c": -1, "acetyl_c": 1, "adp_c": 1},
        ),
        "GLYCOGEN_DEG": (
            "Lumped glycogen-to-carbon conversion (no ATP credit)",
            {"glycogen_c": -1, "acetyl_c": 1},
        ),
        "PHA_SYN": ("PHA synthesis", {"acetyl_c": -1, "pha_c": 1}),
        "PHA_ACCUM": ("PHA accumulation sink", {"pha_c": -1}),
        "PHA_DEG": ("PHA degradation", {"pha_c": -1, "acetyl_c": 1}),
        "PP_DEG": (
            "Polyphosphate degradation (one ATP per unit)",
            {"pp_c": -1, "adp_c": -1, "pi_c": 1, "atp_c": 1},
        ),
        "PP_SYN": (
            "Polyphosphate synthesis (one ATP per unit)",
            {"pi_c": -1, "atp_c": -1, "pp_c": 1, "adp_c": 1},
        ),
        "PP_ACCUM": ("Polyphosphate accumulation sink", {"pp_c": -1}),
        "TCA": (
            "Lumped TCA oxidation",
            {"acetyl_c": -1, "nad_c": -3, "co2_e": 2, "nadh_c": 3},
        ),
        "OXPHOS": (
            "Lumped oxidative phosphorylation (three ATP per carbon unit)",
            {"nadh_c": -3, "adp_c": -3, "o2_c": -1.5, "nad_c": 3, "atp_c": 3},
        ),
        "POLYP_RESERVE": ("Finite polyphosphate reserve supply", {"pp_c": 1}),
        "GLYCOGEN_RESERVE": ("Finite glycogen reserve supply", {"glycogen_c": 1}),
        "PHA_RESERVE": ("Finite stored-PHA supply", {"pha_c": 1}),
    }
    for reaction_id, (name, stoichiometry) in reactions.items():
        _add_reaction(model, reaction_id, name, stoichiometry)
    return model


def build_model(
    phase: str,
    overrides: Mapping[str, float] | None = None,
) -> Model:
    """Build a phase-specific model; reserve bounds are finite flux proxies."""
    phase = phase.lower()
    if phase not in {"anaerobic", "aerobic"}:
        raise ValueError("phase must be 'anaerobic' or 'aerobic'")

    params = load_parameters()
    if overrides:
        params.update({key: float(value) for key, value in overrides.items()})

    model = _network()

    def enable(reaction_id: str, lower: float = 0.0, upper: float = BIG_M) -> None:
        model.reactions.get_by_id(reaction_id).bounds = (lower, upper)

    if phase == "anaerobic":
        enable("EX_ac_e", -params["anaerobic_acetate_max"], 0.0)
        enable("AC_TRANSPORT")
        enable("AC_ACT")
        enable("POLYP_RESERVE", 0.0, params["anaerobic_polyP_reserve"])
        enable("PP_DEG")
        enable("GLYCOGEN_RESERVE", 0.0, params["anaerobic_glycogen_reserve"])
        enable("GLYCOGEN_DEG")
        enable("PHA_SYN")
        enable("PHA_ACCUM")
        enable("PI_EXPORT")
        enable("EX_pi_e", 0.0, BIG_M)
        model.objective = "PHA_ACCUM"
    else:
        enable("PHA_RESERVE", 0.0, params["aerobic_PHA_reserve"])
        enable("PHA_DEG")
        enable("TCA")
        enable("OXPHOS")
        enable("EX_o2_e", -params["aerobic_oxygen_max"], 0.0)
        enable("O2_TRANSPORT")
        enable("EX_co2_e", 0.0, BIG_M)
        enable("EX_pi_e", -params["pi_uptake_max"], 0.0)
        enable("PI_TRANSPORT")
        enable("PP_SYN")
        enable("PP_ACCUM")
        model.objective = "PP_ACCUM"

    maintenance = params["atp_maintenance"]
    enable("ATPM", maintenance, maintenance)
    model.objective_direction = "max"
    model.notes = {
        "model_type": "illustrative teaching model",
        "phase": phase,
        "units": "arbitrary steady-state flux units",
        "stoichiometry": "aggregate pseudo-reactions; not atom-balanced",
    }
    return model


def optimize_phase(model: Model):
    solution = model.optimize()
    if solution.status != "optimal":
        raise RuntimeError(
            f"{model.notes.get('phase', 'unknown')} phase is {solution.status}; "
            "check the reserve bounds and ATP maintenance demand."
        )
    return solution


def write_fluxes(model: Model, solution, filename: str) -> Path:
    """Write a deterministic, human-readable reaction-flux table."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    destination = ARTIFACTS_DIR / filename
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reaction_id", "reaction", "flux"])
        for reaction in model.reactions:
            writer.writerow(
                [reaction.id, reaction.name, f"{solution.fluxes[reaction.id]:.8g}"]
            )
    return destination


def print_summary(model: Model, solution) -> None:
    phase = model.notes["phase"]
    print(f"{phase.title()} phase: {solution.status}")
    print(f"Objective ({model.objective.expression}): {solution.objective_value:.6g}")
    for reaction_id in (
        "EX_ac_e",
        "EX_o2_e",
        "PHA_SYN",
        "PHA_DEG",
        "PHA_ACCUM",
        "PP_DEG",
        "PP_SYN",
        "PP_ACCUM",
        "EX_pi_e",
        "ATPM",
    ):
        if reaction_id in model.reactions:
            print(f"  {reaction_id}: {solution.fluxes[reaction_id]:.6g}")
