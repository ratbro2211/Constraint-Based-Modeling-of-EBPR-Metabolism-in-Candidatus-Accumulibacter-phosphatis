# External qPCR data provenance

## Dataset

The plotted population time series uses the file
`data/external/r1_accumulibacter_ppk1_qpcr_raw_averages.csv`, copied without
editing from Elizabeth McDaniel's public Figshare dataset:

> McDaniel, E. (2022). *Accumulibacter ppk1 qPCR Time-Series Raw Averages*.
> Figshare, version 1. https://doi.org/10.6084/m9.figshare.21151624.v1

The dataset is licensed under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
The downloaded file's MD5 checksum is
`b5ffe441481a93adb9b0adaf483e85c8`.

## Study context

The dataset is associated with:

> McDaniel, E. A., et al. (2022). *Signatures of Microbial Diversity at
> Multiple Scales of Resolution within Engineered Enrichment Communities*.
> bioRxiv preprint, DOI:
> [10.1101/2022.10.01.510452](https://doi.org/10.1101/2022.10.01.510452).

This source is a preprint. It describes the R1 lab-scale EBPR enrichment
reactor, monthly qPCR measurements of dominant Accumulibacter clades IA and IIA,
and a reseeding event after EBPR performance loss on 28 January 2010. The
authors' analysis focuses on the post-reseeding interval; this project shows
the full date range present in the deposited qPCR file and marks that event.

## Processing and interpretation

- The source file contains 317 qPCR-well measurements over 106 sampling dates
  from 3 February 2005 through 16 November 2013.
- The source columns explicitly report `Copies/ng DNA` for clades IA and IIA.
- This project aggregates the technical wells by date using arithmetic means;
  the results CSV also records sample standard deviation, minimum, maximum, and
  well count. Figure 4 plots the mean on a logarithmic y-axis and shows the
  minimum-to-maximum range across the technical wells. These are not
  biological-replicate confidence intervals.
- The qPCR measurements quantify the Accumulibacter `ppk1` gene per DNA mass.
  They are not direct cell counts, OD600, VSS, TSS, or a biomass concentration.
- This is a long-term population-abundance time series from a separate reactor,
  not a batch-culture growth curve. It is shown as measured biological context
  and is not used to calibrate or validate the illustrative FBA model.
