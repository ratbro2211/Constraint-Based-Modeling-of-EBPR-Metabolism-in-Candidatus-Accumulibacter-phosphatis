# Future work

This project currently contains model outputs only. No wet-lab experiments or
experimental measurements were conducted for this project.

The core FBA model still solves two independent steady states and has no biomass
state variable. `dynamic_illustration.py` integrates selected storage fluxes
over one illustrative cycle, but it does not re-solve FBA as pools change and is
not a calibrated dynamic model or growth curve. Its polyphosphate pool drift
shows that the current phase optima do not close a balanced repeating cycle.

Future modeling work should couple the phase constraints and storage pools
before making cycle-level claims. If experimental work is later performed,
validation could use documented biomass and phosphorus measurements with
matched units, sampling times, and operating conditions.
