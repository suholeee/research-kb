---
tags:
  - variable
  - chromatin
---

# Chromatin packing scaling

## Definition
- Chromatin packing scaling is the effective scaling exponent used to describe how chromatin mass, occupancy, or scattering varies with observation scale.
- In the current KB, it subsumes paper-specific labels such as fractal dimension, chromatin packing scaling, chromosome fractal dimension, mass-density fractal dimension, image texture fractal dimension, and related chromosome-scale spatial-scaling exponents when they are used as structural scaling readouts.
- The changed note set broadens the scope to include theory/model exponents and historical image-texture exponents, while keeping them method-specific rather than one interchangeable scalar.

## Units
- Dimensionless.
- Common notations in the current KB: `D`, `D_f`, `D_m`, `d`, `DMB`, `Ds`, `S`.

## Where Used
- Concept pages: [[chromatin-fractality]], [[chromatin-packing-domains]], [[loop-extrusion]].
- Papers: [Almassalha_SciRep_2017](../notes/Almassalha_SciRep_2017.md), [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md), [Bruckner_Science_2023](../notes/Bruckner_Science_2023.md), [Chan_PNAS_2024](../notes/Chan_PNAS_2024.md), [Einstein_FractBiolMed_1998](../notes/Einstein_FractBiolMed_1998.md), [Iashina_PhysRevE_2021](../notes/Iashina_PhysRevE_2021.md), [Li_MicroscMicroanal_2018](../notes/Li_MicroscMicroanal_2018.md), [Li_SciAdv_2021](../notes/Li_SciAdv_2021.md), [Li_SciRep_2022](../notes/Li_SciRep_2022.md), [Pigolotti_PhysRevRes_2020](../notes/Pigolotti_PhysRevRes_2020.md), [Sarıyer_PhysRevE_2024](../notes/Sarıyer_PhysRevE_2024.md), [Sung_PNAS_2021](../notes/Sung_PNAS_2021.md), [Tamm_PhysRevLett_2015](../notes/Tamm_PhysRevLett_2015.md), [Virk_SciAdv_2020](../notes/Virk_SciAdv_2020.md), [Wang_Science_2016](../notes/Wang_Science_2016.md), [Carter_bioRxiv_2026](../notes/Carter_bioRxiv_2026.md), [Yi_BiophysJ_2015](../notes/Yi_BiophysJ_2015.md).

## Measurement Methods
- Mass-scaling analysis of ChromSTEM or ChromEM images and tomograms.
- Partial wave spectroscopic or inverse spectroscopic optical measurements that infer subdiffraction chromatin scaling.
- Small-angle neutron scattering using `Q`-dependent power-law regimes and crossover `Q_c`.
- Sequential FISH or chromosome-tracing measurements that fit mean spatial distance versus genomic distance with a chromosome-scale scaling exponent.
- Box-counting or density-scaling analysis of chromosome or nuclear images.
- Model or theory fits that infer apparent fractal dimensions from genomic-distance scaling, active extrusion, LAD adsorption, or monomer dynamics.
- Image-texture methods such as Minkowski or spectral fractal dimensions when they are used as nuclear-structure descriptors.

## Conflicts / Ambiguities
- The symbol `D` is overloaded across the KB; in chromatin papers it denotes a scaling exponent, not the membrane spacing variable used in [[lamellar-spacing]].
- Method-specific exponents are related but not interchangeable. A domain-level packing exponent from ChromSTEM, a chromosome-scale spatial-scaling exponent `S` from tracing, a whole-chromosome `D_f` from scattering or imaging, and a live-cell `D_m` from optical measurements should not be compared as if they were the same assay output.
- [Chan_PNAS_2024](../notes/Chan_PNAS_2024.md) reports an apparent nonequilibrium `D = 4` regime from active extrusion theory; this should not be interpreted as an equilibrium packing dimension.
- [Einstein_FractBiolMed_1998](../notes/Einstein_FractBiolMed_1998.md) reports cytology texture descriptors `DMB` and `Ds`; these should not be merged directly with ChromSTEM, scattering, or tracing exponents.
- Contact-map descriptors such as [[contact-probability-scaling|contact probability scaling]], `Z(q, epsilon)`, and `K(q)` in [Pigolotti_PhysRevRes_2020](../notes/Pigolotti_PhysRevRes_2020.md) are related to chromatin fractality but are not one common packing-scaling scalar.
- Scattering descriptors such as generalized Porod exponents `alpha` and constants `K` in [Hemonnot_ACSNano_2016pdf](../notes/Hemonnot_ACSNano_2016pdf.md) belong to the same broader chromatin-fractality family, but they are not normalized here as one common packing-scaling scalar.
- [Lee_BiophysJ_2025](../notes/Lee_BiophysJ_2025.md) reports additional box-counting, grayscale, lacunarity, and multifractal descriptors that belong to the broader chromatin fractality family but are not normalized here into one scalar.
