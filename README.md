# Illustrative constraint-based model of EBPR metabolism

This repository contains a small COBRApy flux-balance-analysis (FBA) teaching
model for the anaerobic/aerobic cycle associated with enhanced biological
phosphorus removal (EBPR). It is an executable starting point for exploring
phase switching, not a validated reconstruction of *Candidatus Accumulibacter
phosphatis*.

## What the model represents

The model is built from aggregate reactions for acetate activation, PHA storage
and degradation, polyphosphate storage and degradation, glycogen reserve
breakdown, a lumped TCA oxidation step, oxidative phosphorylation, and ATP
maintenance. It uses separate steady-state optimizations for the two phases:

- **Anaerobic:** oxygen uptake is blocked; acetate and finite polyphosphate and
  glycogen reserve supplies are available. The objective is PHA accumulation.
  Polyphosphate degradation supplies ATP and releases phosphate.
- **Aerobic:** acetate uptake is blocked; a finite PHA reserve and oxygen are
  available. The objective is polyphosphate accumulation. PHA oxidation
  supplies ATP for phosphate uptake and storage.

The reserve bounds are flux caps used to represent finite availability in each
separate steady-state run. They do not simulate a time-dependent transfer of
storage pools between phases.

In this abstraction, glycogen contributes a bounded carbon unit but no ATP
credit; acetate activation and reserve reactions are deliberately simplified.
This makes the energy/constraint tradeoffs visible without claiming a detailed
glycogen pathway.

## Run it

From the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/build_model.py
python scripts/run_anaerobic.py
python scripts/run_aerobic.py
python scripts/sensitivity_analysis.py
python -m unittest discover -s tests -v
```

The phase scripts write reaction flux tables to `artifacts/`. The sensitivity
script writes `artifacts/sensitivity_analysis.csv` and
`artifacts/sensitivity_analysis.png`. The build script serializes the default
anaerobic model to `models/ebpr_model.json`.

The existing `SBM_tutorial_1.ipynb` is an unrelated OpenSMOG protein-folding
tutorial; it is not used by the EBPR scripts. A standalone copy is available in
the [OpenSMOG tutorial repository](https://github.com/ratbro2211/opensmog-protein-folding-tutorial).

## Sensitivity runs

The one-at-a-time sweeps vary acetate uptake, the anaerobic polyphosphate
reserve, the anaerobic glycogen reserve, aerobic oxygen uptake, and ATP
maintenance. Infeasible cases are recorded with their solver status rather
than silently reported as zero flux.

Default bounds are in `data/parameters.csv`. They are arbitrary teaching-model
flux units, not measured rates or calibrated process parameters.

With the checked-in defaults, the solver returns a PHA accumulation flux of
5.4 and phosphate release of 5.1 in the anaerobic run. The aerobic run returns
polyphosphate accumulation of 19.9. These are outputs of the illustrative
equations and bounds above—not empirical EBPR rates or predictions.

## Important limitations

- The reaction network uses aggregate pseudo-metabolites and pseudo-reactions;
  it is **not elementally or charge balanced** and should not be treated as a
  biochemical reconstruction.
- The ATP yields, reserve caps, and maintenance demand are illustrative
  assumptions. No experimental data or reference stoichiometric model was
  included in the starter repository.
- The two phases are independent steady-state optimizations. This model does
  not predict cycle duration, intracellular pool concentrations, wastewater
  treatment performance, or full-scale aeration/carbon dosing.
- Results are useful for demonstrating how constraints affect feasible fluxes.
  They are not validated evidence for industrial decisions.

For research use, replace the aggregate reactions and parameter defaults with
stoichiometries and bounds from a cited EBPR/Accumulibacter reconstruction,
document the source, and validate predictions against appropriate data.
