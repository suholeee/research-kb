---
tags:
  - concept
  - chromatin
concept_id: chromatin-condensates
title: "Chromatin condensates"
aliases:
  - chromatin phase separation
  - chromatin condensation
  - nucleosome condensability
status: synthesized
related_concepts:
  - chromosome-compartments
  - chromatin-packing-domains
  - transcription-chromatin-coupling
---

# Chromatin condensates

## Definition
- Chromatin condensates are dense chromatin-rich assemblies whose formation, structure, or material properties are explained with phase separation, nucleosome interaction networks, or nanoscale condensation.
- In this KB, the concept groups reconstituted chromatin LLPS, native nucleosome condensability, cryo-ET condensate structure, and label-free live-cell condensation readouts without assuming they are identical physical states.

## How Measured
- Evidence comes from reconstituted nucleosome arrays, salt and histone-tail perturbations, condensability sequencing, polymer simulations, high-pressure-frozen cryo-ET, subtomogram averaging, light-microscopy material assays, and label-free scattering/diffusion measurements.
- Shared readouts include droplet formation, nucleosome concentration, linker-length-dependent packing, nucleosome network geometry, A/B compartment association, local scattering variance, diffusion-derived condensation metrics, and inhibitor-induced condensation/decondensation.

## Evidence Across Papers
| Paper | System | Evidence | Notes |
| --- | --- | --- | --- |
| [Gibson_Cell_2019](../notes/Gibson_Cell_2019.md) | Reconstituted chromatin arrays and nuclear microinjection | Histone-tail-driven chromatin LLPS is promoted by H1 and antagonized by histone acetylation; bromodomain readers can restore distinct acetylated-chromatin droplets. | Foundational condensate-regulation evidence in the changed notes. |
| [Park_Nature_2025](../notes/Park_Nature_2025.md) | Native mononucleosome condensability and polymer simulations | B-compartment nucleosomes are more condensable than A-compartment nucleosomes; condensability alone can reproduce A/B compartments in simulation. | Connects condensability to genome organization, but through purified particles and modeling. |
| [Zhou_PNAS_2025](../notes/Zhou_PNAS_2025.md) | Cryo-ET workflow for reconstituted and native chromatin | High-pressure freezing plus cryo-FIB milling preserves condensate integrity and resolves dense heterogeneous nucleosome networks. | Primarily a methods/resource contribution. |
| [Zhou_Science_2025](../notes/Zhou_Science_2025.md) | Cryo-ET, simulations, and material assays of linker-defined fibers | 25-bp linker chromatin forms open fibers with stronger intermolecular networks and stronger phase separation; 30-bp linker chromatin forms compact stacked fibers with weaker condensates. | Mechanistic bridge from nucleosome geometry to material properties. |
| [Hsiao_ACSNano_2021](../notes/Hsiao_ACSNano_2021.md) | DYNAMICS label-free live-cell scattering | Detects drug-induced condensation/decondensation and transient nanoscale condensation events over seconds. | Not sequence-resolved. |
| [Hsiao_CommBiol_2024](../notes/Hsiao_CommBiol_2024.md) | iSCORS live-cell chromatin dynamics | Transcription inhibition increases chromatin condensation; DRB addition/removal tracks reversible condensation dynamics. | Supports transcription-condensation coupling, not locus identity. |

## Quantitative Summary
- [Gibson_Cell_2019](../notes/Gibson_Cell_2019.md): chromatin concentration inside LLPS droplets is reported as `~10,000-fold` higher than bulk solution; H1 increases droplet density by `~1.4-fold`.
- [Gibson_Cell_2019](../notes/Gibson_Cell_2019.md): H1 has a larger density effect on `45-bp` linker chromatin, reported as `~1.5-fold`.
- [Park_Nature_2025](../notes/Park_Nature_2025.md): active promoters are `~7.3` times less condensable than average; the displayed condensability-expression correlation is `Spearman = -0.8`.
- [Zhou_PNAS_2025](../notes/Zhou_PNAS_2025.md): reconstituted nucleosome averages reach `6.1 Angstrom`; native nucleosome averages reach `12 Angstrom`.
- [Zhou_Science_2025](../notes/Zhou_Science_2025.md): `25 bp` linkers favor open, intermolecularly connected condensates; `30 bp` linkers favor compact stacked configurations and weaker intermolecular contacts.
- [Zhou_Science_2025](../notes/Zhou_Science_2025.md): dense native chromatin clusters are discussed at `10-100 nm`, with larger chromatin domains at `100-300 nm`.
- [Hsiao_ACSNano_2021](../notes/Hsiao_ACSNano_2021.md): COBRI acquisition is `1000 fps`; transient condensation events occur over a few seconds and continuous observation can exceed `1 h`.
- [Hsiao_CommBiol_2024](../notes/Hsiao_CommBiol_2024.md): iSCORS tests a `5 ms` minimum measurement timescale; DRB time-lapse sampling is every `20 min`; DRB-induced condensation dynamics correlation is `0.79 +/- 0.15`.

## Conflicts / Discrepancies
- Reconstituted LLPS, mononucleosome condensability, native dense chromatin clusters, and live-cell scattering condensation are related but not interchangeable observables.
- [Gibson_Cell_2019](../notes/Gibson_Cell_2019.md) establishes intrinsic chromatin LLPS under controlled conditions, but reconstituted arrays simplify native chromatin composition and nuclear context.
- [Park_Nature_2025](../notes/Park_Nature_2025.md) supports condensability as a low-dimensional organizing principle, but its polymer simulations test sufficiency rather than exclusivity.
- [Zhou_PNAS_2025](../notes/Zhou_PNAS_2025.md) and [Zhou_Science_2025](../notes/Zhou_Science_2025.md) provide structural snapshots and material inference; cryo-ET does not directly measure real-time condensate dynamics.
- [Hsiao_ACSNano_2021](../notes/Hsiao_ACSNano_2021.md) and [Hsiao_CommBiol_2024](../notes/Hsiao_CommBiol_2024.md) are live-cell and label-free but not locus-resolved, so they support global or local physical condensation rather than named genomic domains.

## Related Concepts
- [[chromosome-compartments]]
- [[chromatin-packing-domains]]
- [[transcription-chromatin-coupling]]

## Source Papers
- [Gibson_Cell_2019](../notes/Gibson_Cell_2019.md)
- [Hsiao_ACSNano_2021](../notes/Hsiao_ACSNano_2021.md)
- [Hsiao_CommBiol_2024](../notes/Hsiao_CommBiol_2024.md)
- [Park_Nature_2025](../notes/Park_Nature_2025.md)
- [Zhou_PNAS_2025](../notes/Zhou_PNAS_2025.md)
- [Zhou_Science_2025](../notes/Zhou_Science_2025.md)
