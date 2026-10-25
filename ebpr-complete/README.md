# Illustrative constraint-based model of EBPR metabolism

This repository contains a small COBRApy flux-balance-analysis (FBA) teaching
model for the anaerobic/aerobic cycle associated with enhanced biological
phosphorus removal (EBPR). It is designed to demonstrate how environmental
constraints change feasible storage fluxes; it is not a validated reconstruction
of *Candidatus Accumulibacter phosphatis*.

## Project question

In a deliberately simplified steady-state model, how do acetate availability,
polyphosphate and glycogen reserves, oxygen availability, and ATP maintenance
affect PHA storage under anaerobic conditions and polyphosphate storage under
aerobic conditions?

The qualitative two-phase cycle follows published descriptions of anaerobic
acetate uptake/PHA synthesis with phosphate release, followed by aerobic PHA
oxidation and phosphate uptake. The model here does **not** reproduce the
published stoichiometric coefficients; see [References](#references).

## What the model represents

The model is built from aggregate reactions for acetate activation, PHA storage
and degradation, polyphosphate storage and degradation, glycogen mobilization,
lumped glycolysis and pyruvate oxidation, TCA oxidation, oxidative
phosphorylation, and ATP maintenance. It uses separate steady-state
optimizations for the two phases:

- **Anaerobic:** oxygen uptake is blocked; acetate and finite polyphosphate and
  glycogen reserve supplies are available. The objective is PHA accumulation.
  Polyphosphate degradation supplies ATP and releases phosphate.
- **Aerobic:** acetate uptake is blocked; a finite PHA reserve and oxygen are
  available. The objective is polyphosphate accumulation. PHA oxidation
  supplies ATP for phosphate uptake and storage.

The reserve bounds are flux caps used to represent finite availability in each
separate steady-state run. They do not simulate a time-dependent transfer of
storage pools between phases.

Glycogen-derived carbon passes through glucose-equivalent and pyruvate
intermediates. Glycolytic ATP and redox production are omitted; acetate
activation and reserve reactions are also deliberately simplified. These
choices make energy/constraint tradeoffs visible without claiming a detailed
glycogen pathway.

Core reaction IDs follow the starter project where applicable: `AC_ACT`,
`PHA_SYN`, `PHA_DEG`, `PP_SYN`, `PP_DEG`, `GLY_DEG`, `ATPM`, `EX_ac_e`,
`EX_o2_e`, and `EX_pi_e`. COBRApy enforces steady-state balances (`S · v = 0`)
and solves a linear program for each phase-specific objective.

## Run it

From the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/build_model.py
python scripts/run_anaerobic.py
python scripts/run_aerobic.py
python scripts/sensitivity_analysis.py
python scripts/generate_publication_outputs.py
python -m unittest discover -s tests -v
```

The tested runtime is Python 3.13.11 with the dependency versions pinned in
`requirements.txt`.

The phase scripts write detailed reaction-flux tables to `artifacts/`. The
publication-output script writes summary tables and interpretation notes to
`results/`, and four figures as 300-dpi PNG plus vector PDF to `figures/`. Figure
4 uses an independently published, attributed qPCR time series; see
`results/data_provenance.md`.
The build script serializes the default anaerobic model to
`models/ebpr_model.json`.

The unrelated OpenSMOG protein-folding notebook has been separated into its
[own tutorial repository](https://github.com/ratbro2211/opensmog-protein-folding-tutorial);
it is not part of the EBPR model.

## Sensitivity runs

The one-at-a-time sweeps vary acetate uptake, the anaerobic polyphosphate
reserve, the anaerobic glycogen reserve, aerobic oxygen uptake, and ATP
maintenance. Infeasible cases are recorded with their solver status rather
than silently reported as zero flux.

Default bounds are in `data/parameters.csv`. They are arbitrary teaching-model
flux units, not measured rates or calibrated process parameters.

## Results

All values below are solver outputs from the checked-in teaching-model
equations. They are not empirical EBPR rates or predictions.

| Default scenario | Objective flux | Supporting fluxes |
| --- | ---: | --- |
| Anaerobic PHA accumulation | 5.4 | Polyphosphate degradation 5.0; net phosphate release 5.1 |
| Aerobic polyphosphate accumulation | 19.9 | PHA degradation 6.67; oxygen uptake 10.0; net phosphate uptake 19.8 |

The one-at-a-time sweeps show the model's expected constraint response:

- **Anaerobic acetate cap:** PHA accumulation rises from 0.5 at an acetate cap
  of 0 to 5.4 at a cap of 5; increasing acetate further has no effect because
  the polyphosphate/energy supply becomes limiting.
- **Anaerobic polyphosphate reserve:** no reserve makes the phase infeasible
  under the required ATP-maintenance demand; increasing the reserve from 1 to
  7.5 raises PHA accumulation from 1.4 to 7.9.
- **Anaerobic glycogen reserve:** increasing the carbon-only glycogen reserve
  from 0 to 2 raises PHA accumulation from 4.9 to 6.9.
- **Aerobic oxygen cap:** zero oxygen makes the phase infeasible; increasing the
  cap from 2.5 to 10 raises polyphosphate accumulation from 4.9 to 19.9.
- **ATP maintenance:** increasing the demand from 0 to 1 lowers anaerobic PHA
  accumulation from 5.5 to 4.5 and aerobic polyphosphate accumulation from 20
  to 19.

The starter README described glycogen as having minimal effect. This
implementation does not reproduce that claim: the simplified carbon-only
glycogen path produces a visible increase in PHA over the sweep above. That
disagreement is a model limitation to resolve with literature-based glycogen
stoichiometry, not evidence that glycogen has a particular effect in real
EBPR.

The detailed reaction fluxes remain in `artifacts/`; publication-ready
summaries, figure captions, data provenance, and growth-curve status are in
`results/`.
Figures are in `figures/figure_01_ebpr_phase_cycle.*`,
`figures/figure_02_baseline_fluxes.*`, and
`figures/figure_03_sensitivity_analysis.*`, plus the measured
`figures/figure_04_measured_population_dynamics.*`.

### Measured population time series

Figure 4 plots measured Accumulibacter `ppk1` qPCR abundance (copies per ng DNA)
for clades IA and IIA over time in a separate EBPR enrichment reactor. The
source file is included under `data/external/` with CC BY 4.0 attribution. This
is a population-abundance trajectory, **not** a biomass growth curve: it is not
OD600, VSS/TSS, or a cell count, and the time series is not an axenic culture
growth experiment. The dashed line marks the reactor reseeding event reported
by the source study.

The FBA model still has no biomass reaction or time integration; its flux
outputs cannot generate a biomass growth curve. The external qPCR series is
not used to calibrate or validate the teaching model. See
`results/growth_curve_status.md` and `results/data_provenance.md`.

## Important limitations

- The reaction network uses aggregate pseudo-metabolites and pseudo-reactions;
  it is **not elementally or charge balanced** and should not be treated as a
  biochemical reconstruction.
- The ATP yields, reserve caps, and maintenance demand are illustrative
  assumptions. No experimental data or reference stoichiometric model is used
  to calibrate the teaching model.
- The two phases are independent steady-state optimizations. This model does
  not predict cycle duration, intracellular pool concentrations, wastewater
  treatment performance, or full-scale aeration/carbon dosing.
- Results are useful for demonstrating how constraints affect feasible fluxes.
  They are not validated evidence for industrial decisions.

For research use, replace the aggregate reactions and parameter defaults with
stoichiometries and bounds from a cited EBPR/Accumulibacter reconstruction,
document the source, and validate predictions against appropriate data.

## Potential relevance

The starter project names aeration strategy, carbon dosing, phosphate-removal
efficiency, and stress response as potential applications. This implementation
does not calculate plant operating recommendations or removal efficiency; it
only demonstrates qualitative flux tradeoffs under toy constraints.

## Future extensions

These remain outside the current teaching-model scope: dynamic FBA linking
storage pools across phases, additional carbon sources, oxygen gradients,
gene-expression/regulatory constraints, denitrification, and calibration or
validation against wastewater-treatment data.

## References

The first two papers support the qualitative process context only; the toy
model's reaction coefficients and parameter values are not taken from them.

1. Smolders GJ, van der Meij J, van Loosdrecht MCM, Heijnen JJ. “Model of the
   anaerobic metabolism of the biological phosphorus removal process:
   Stoichiometry and pH influence.” *Biotechnology and Bioengineering*.
   1994;43(6):461–470. [PubMed](https://pubmed.ncbi.nlm.nih.gov/18615742/)
   · [DOI](https://doi.org/10.1002/bit.260430605)
2. Smolders GJ, van der Meij J, van Loosdrecht MCM, Heijnen JJ. “Stoichiometric
   model of the aerobic metabolism of the biological phosphorus removal
   process.” *Biotechnology and Bioengineering*. 1994;44(7):837–848.
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/18618851/)
   · [DOI](https://doi.org/10.1002/bit.260440709)
3. McDaniel, E. A., et al. (2022). *Signatures of Microbial Diversity at
   Multiple Scales of Resolution within Engineered Enrichment Communities*.
   bioRxiv preprint. [DOI](https://doi.org/10.1101/2022.10.01.510452)
4. McDaniel, E. (2022). *Accumulibacter ppk1 qPCR Time-Series Raw Averages*.
   Figshare dataset, CC BY 4.0.
   [DOI](https://doi.org/10.6084/m9.figshare.21151624.v1)

## Author

Suraj Rathi
