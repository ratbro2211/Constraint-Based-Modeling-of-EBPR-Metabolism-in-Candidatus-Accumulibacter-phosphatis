# Illustrative storage-pool time course

This is a model-only, piecewise integration of baseline FBA storage fluxes. It
is not dynamic FBA, a biomass growth curve, or an experimentally calibrated
prediction. Time and pool units are arbitrary.

## Scenario assumptions

- Anaerobic duration: 1 arbitrary time units.
- Initial PHA pool: 0 arbitrary pool units.
- Initial polyphosphate pool: 5 units,
  set to one anaerobic phase's integrated baseline polyphosphate degradation.
- Aerobic duration: 0.81 arbitrary time units,
  derived so the baseline aerobic PHA-degradation flux returns PHA to its
  initial pool.
- The curves connect integrated model fluxes; plotted points are numerical
  rendering points, not experimental samples.

## Interpretation

PHA returns to 0 pool units. Polyphosphate ends at
16.12 units, a net change of
+11.12 units from its initial amount.
Therefore, the independently optimized phase fluxes do not close a
cycle-balanced polyphosphate pool under these assumptions. The drift is a
useful model limitation to address before interpreting this as a repeating
biological cycle.

The underlying FBA model remains two separate steady-state optimizations and
has no biomass state. This figure is an illustrative storage-pool trajectory,
not a growth curve or wet-lab result.
