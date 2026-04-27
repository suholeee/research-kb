---
tags:
  - "paper"
note_key: Miron_SciAdv_2020
title: "Chromatin arranges in chains of mesoscale domains with nanoscale functional topography independent of cohesin"
authors:
  - "Ezequiel Miron"
  - "Roel Oldenkamp"
  - "Jill M. Brown"
  - "David M. S. Pinto"
  - "C. Shan Xu"
  - "Ana R. Faria"
  - "Haitham A. Shaban"
  - "James D. P. Rhodes"
  - "Cassandravictoria Innocent"
  - "Sara de Ornellas"
  - "Harald F. Hess"
  - "Veronica Buckle"
  - "Lothar Schermelleh"
year: "2020"
journal: "Science Advances"
doi: "10.1126/sciadv.aba8811"
source_pdf: "raw/papers/Miron_SciAdv_2020.pdf"
source_text: "raw/extracted/Miron_SciAdv_2020.txt"
paper_type: "research_article"
include_in_synthesis: true
domain: "genome biophysics"
system_type: "fixed and live somatic cell nuclei"
methods:
  - "3d structured illumination microscopy"
  - "scanning electron microscopy"
  - "fluorescence in situ hybridization"
  - "auxin-inducible degron perturbation"
variables:
  - "chromatin domain diameter"
  - "genomic domain size"
  - "cohesin state"
  - "chromatin mark radial position"
concepts:
  - "chromatin-packing-domains"
  - "3d-genome-organization"
  - "topologically-associating-domains"
confidence: "medium"
---

# Chromatin arranges in chains of mesoscale domains with nanoscale functional topography independent of cohesin

## Citation
- Authors: Ezequiel Miron, Roel Oldenkamp, Jill M. Brown, David M. S. Pinto, C. Shan Xu, Ana R. Faria, Haitham A. Shaban, James D. P. Rhodes, Cassandravictoria Innocent, Sara de Ornellas, Harald F. Hess, Veronica Buckle, Lothar Schermelleh
- Year: 2020
- Journal: Science Advances
- DOI: 10.1126/sciadv.aba8811

## Core Question
- What physical structures occupy the mesoscale chromatin regime between nucleosomes and chromosome compartments in single cells?
- Are these physical chromatin domains dependent on cohesin-mediated TAD organization?

## System
- Mouse and human somatic nuclei analyzed in fixed and live-cell imaging assays, with additional cohesin-ablation experiments.

## Methods
- Used 3D structured illumination microscopy to resolve chromatin domain architecture in situ.
- Used scanning electron microscopy to visualize aggregated nucleosome structures at higher resolution.
- Applied RASER-FISH to compare physical chromatin domains with a defined `0.7-Mb` TAD.
- Examined cohesin ablation to test whether mesoscale domains persist without canonical TAD insulation.

## Key Variables
- chromatin domain diameter
- genomic domain size
- cohesin state
- chromatin mark radial position

## Main Findings
- Chromatin forms chains of mesoscale domains rather than a homogeneous polymer mass.
- These chromatin domains are typically a few hundred nanometres across and can overlap individual TAD-sized genomic regions without being identical to them.
- Active marks and cohesin are enriched near domain surfaces, whereas repressive marks are shifted toward domain cores.
- This nanoscale functional topography relaxes transiently after replication but persists after cohesin ablation, arguing that physical chromatin domains are not simply a readout of cohesin-dependent TADs.

## Quantitative Results
- Variable: chromatin domain diameter
- Value: `~200-300`
- Units: `nm`
- Conditions: mesoscale domains identified by 3D super-resolution imaging
- Interpretation (1 line max): Physical chromatin domains occupy a nanoscale-to-mesoscale size regime comparable to packing-domain papers already in the KB.

- Variable: TAD probe size
- Value: `0.7`
- Units: `Mb`
- Conditions: RASER-FISH comparison to TAD `H`
- Interpretation (1 line max): The mapped TAD-scale region falls within the size regime that can overlap a single physical chromatin domain.

- Variable: TAD physical diameter
- Value: `~330`
- Units: `nm`
- Conditions: `0.7-Mb` TAD `H`
- Interpretation (1 line max): A single TAD-sized genomic region can occupy a compact physical domain-like volume in situ.

## Mechanism / Interpretation
- The authors interpret chromatin domains as physical and functional mesoscale modules built from aggregated nucleosomes.
- They argue that genome activity is organized partly by radial topography within these domains, with active processes concentrated at accessible surfaces.
- Because this arrangement persists after cohesin loss, the paper separates physical chromatin-domain architecture from canonical loop/TAD insulation.

## Evidence Map
- 3D-SIM and SEM figures: support chains of physical chromatin domains and their nanoscale structure.
- RASER-FISH figure on TAD `H`: supports partial overlap between a genomically defined TAD and a physical domain.
- Histone-mark mapping figures: support radial segregation of active and repressive signals.
- Cohesin-ablation figures: support persistence of chromatin domains despite loss of cohesin-dependent organization.

## Limitations
- The note is based on extracted text rather than a full figure-by-figure PDF pass.
- The paper supports overlap between physical domains and TADs but does not establish a universal one-to-one mapping.
- Domain architecture is characterized strongly, but direct transcriptional perturbation is not the central axis of the study.

## Concepts
- chromatin-packing-domains
- 3d-genome-organization
- topologically-associating-domains

## Confidence
- medium

## Open Questions
- How directly these cohesin-independent chromatin domains correspond to packing domains measured by ChromSTEM or PWS remains unresolved.
- A later pass should normalize the main cohesin-ablation timing and any domain-size distributions directly from the figures.
