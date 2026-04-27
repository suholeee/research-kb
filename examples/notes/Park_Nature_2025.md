---
tags:
  - paper
note_key: Park_Nature_2025
title: "Native nucleosomes intrinsically encode genome organization principles"
authors:
  - "Sangwoo Park et al."
year: "2025"
journal: "Nature"
doi: "10.1038/s41586-025-08971-7"
source_pdf: "raw/papers/Park_Nature_2025.pdf"
source_text: "raw/extracted/Park_Nature_2025.txt"
paper_type: "research_article"
include_in_synthesis: true
domain: "nucleosome biophysics and genome organization"
system_type: "native mononucleosome condensability across mammalian genomes"
methods:
  - "condense-seq"
  - "native mononucleosome purification"
  - "next-generation sequencing"
  - "chromatin polymer simulation"
  - "polyamine perturbation"
variables:
  - "nucleosome condensability"
  - "survival probability"
  - "a/b compartment"
  - "gene expression"
  - "polyamine abundance"
  - "histone modification"
concepts:
  - "nucleosome-condensability"
  - "a-b-compartments"
  - "chromatin-condensation"
  - "polyamines"
  - "genome-organization"
confidence: "medium"
---

# Native nucleosomes intrinsically encode genome organization principles

## Citation
- Authors: Sangwoo Park et al.
- Year: 2025
- Journal: Nature
- DOI: 10.1038/s41586-025-08971-7

## Core Question
- Do individual native nucleosomes encode biophysical information sufficient to help organize A/B genome compartments?
- Is nucleosome condensability linked to gene expression, chromatin state, and polyamine-mediated genome organization?

## System
- Native mononucleosomes purified from human and mouse cell types, including H1 human embryonic stem cells, GM12878 cells, mouse embryonic stem cells, and mouse T-cell perturbation contexts.

## Methods
- Developed/used `Condense-seq` to measure genome-wide condensability of purified native mononucleosomes.
- Used physiological polyamines and other condensing agents to induce nucleosome condensation in vitro.
- Sequenced input and supernatant nucleosomal DNA to estimate condensability by survival probability.
- Used chromatin polymer simulations with condensability as input to test reproduction of A/B compartments.
- Perturbed ornithine decarboxylase (`ODC`) genetically or pharmacologically to alter polyamine availability in mouse T cells.

## Key Variables
- nucleosome condensability
- survival probability
- spermine-mediated condensation
- A compartment
- B compartment
- promoter expression level
- AT content
- H3K27ac
- H3K9me3
- polyamine abundance
- ODC knockout
- DFMO inhibition

## Main Findings
- Native mononucleosomes from A-compartment regions have low condensability, whereas those from B-compartment regions have high condensability.
- Chromatin polymer simulations using condensability alone can reproduce A/B compartments without adding trans factors.
- Nucleosome condensability is strongly anticorrelated with gene expression, especially near promoters and in a cell-type-dependent manner.
- Condensability is treated as an emergent low-dimensional biophysical axis summarizing genetic and epigenetic chromatin state.
- Various condensing agents, histone modifications, and mutations indicate that the encoded organization principle is mostly electrostatic.
- Polyamine depletion through ODC loss or inhibition hyperpolarizes condensability, suggesting cells accentuate condensability contrast when polyamines are limited.

## Quantitative Results
- Variable: DNA wrapped around nucleosome core
- Value: `147`
- Units: bp
- Conditions: canonical nucleosome core description
- Interpretation (1 line max): Condense-seq maps condensability at near-single-nucleosome scale.

- Variable: condensability-gene-expression correlation
- Value: `Spearman correlation = -0.8`
- Units: correlation coefficient
- Conditions: H1-hESC chromosome 1 figure excerpt
- Interpretation (1 line max): Higher expression is associated with lower nucleosome condensability in that displayed analysis.

- Variable: active-promoter condensability contrast
- Value: `~7.3 times` less condensable than average
- Units: fold in probabilistic metric
- Conditions: active promoter regions described in extracted text
- Interpretation (1 line max): Active-promoter nucleosomes are strongly depleted from the condensable fraction.

- Variable: regular sampling bin for condensability curves
- Value: `10`
- Units: kb
- Conditions: computation of genome-wide nucleosome condensability
- Interpretation (1 line max): Some analyses aggregate nucleosome counts into 10-kb bins.

- Variable: selected nucleosome sample for NMF analysis
- Value: `0.1`
- Units: million nucleosomes
- Conditions: chromosome 1 nucleosome feature analysis
- Interpretation (1 line max): Feature modeling used a large sampled nucleosome set.

## Mechanism / Interpretation
- The authors interpret native mononucleosome condensability as an intrinsic, mostly electrostatic property that can bias large-scale genome compartmentalization.
- Direct results show condensability patterns and simulation sufficiency under model assumptions; the extent to which condensability alone organizes compartments in cells remains an inferred mechanism.

## Evidence Map
- Condense-seq assays: support genome-wide nucleosome condensability measurements.
- ChromHMM and compartment comparisons: support association with A/B and chromatin states.
- Polymer simulations: support sufficiency of condensability input to recapitulate compartments in silico.
- Condensing-agent and PTM/mutation experiments: support electrostatic contribution.
- ODC knockout/DFMO experiments: support condensability hyperpolarization under polyamine depletion.

## Limitations
- Purified mononucleosome condensation assays remove chromatin connectivity, remodelers, and nuclear context.
- Polymer simulations test sufficiency in a model, not exclusivity in cells.
- Some figure-level units in the extraction are ambiguous; only clearly stated values are used here.

## Concepts
- nucleosome-condensability
- a-b-compartments
- chromatin-condensation
- polyamines
- genome-organization

## Confidence
- medium

## Open Questions
- How does mononucleosome condensability interact with linker DNA and oligonucleosome fiber geometry in vivo?
- Which histone modifications dominate cell-type-specific condensability differences?
- How does polyamine depletion change transcription through condensability versus other metabolic effects?
