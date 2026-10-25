# Model results

## Baseline optimization

| Phase | Objective flux | Key supporting fluxes |
| --- | ---: | --- |
| Anaerobic | PHA accumulation 5.4 | Poly-P degradation 5; phosphate exchange 5.1 (release) |
| Aerobic | Poly-P accumulation 19.9 | PHA degradation 6.66667; oxygen uptake 10; phosphate exchange -19.8 (uptake) |

All values are arbitrary steady-state flux units produced by the checked-in
teaching model. They are not measured rates, biomass growth, or plant-scale
predictions. Exchange fluxes are negative for uptake and positive for release.

## Sensitivity

The one-at-a-time analysis contains 30 optimization runs;
2 are infeasible under the fixed ATP-maintenance constraint. See
`sensitivity_analysis.csv` and `../figures/figure_03_sensitivity_analysis.png`.
The sweep demonstrates model constraint behavior, not parameter uncertainty or
statistical significance.

## Separate measured population time series

Figure 4 and `qpcr_population_summary.csv` summarize a separately sourced
Accumulibacter ppk1 qPCR dataset with 106 sampling dates from
2005-02-03 to 2013-11-16. The measurements are gene copies per ng
DNA, not biomass concentration or model fluxes. They are shown as external
biological context and are not used to fit or validate the teaching model.
See `data_provenance.md` for attribution and processing details.
