---
tags:
  - concept
  - chromatin
concept_id: chromatin-packing-domains
title: "Chromatin packing domains"
aliases:
  - packing domains
  - PDs
status: synthesized
related_concepts:
  - chromatin-fractality
  - chromatin-compaction
  - transcription-chromatin-coupling
  - loop-extrusion
---

# Chromatin packing domains

## Definition
- Chromatin packing domains are nanoscale chromatin regions with distinct internal packing behavior, typically described by a size, density, and packing-scaling or fractal parameter.
- In the current KB, the term refers to physically defined structural domains or closely related domain-like hierarchy in microscopy, rather than automatically assuming equivalence to TADs or other genomically defined units.

## How Measured
- Current papers measure packing domains with ChromSTEM tomography, ChromTEM, partial wave spectroscopic microscopy, super-resolution microscopy and chromatin tracing, and supporting polymer, cascade, or crowding models.
- The note set also includes super-resolution imaging of epigenetic domains and subchromosomal nanodomains, which supports hierarchical domain-like packing without using the same segmentation rules as ChromSTEM-derived packing domains.
- Common shared descriptors are domain size, packing scaling `D`, chromatin density or volume concentration, internal heterogeneity, domain life-cycle state, and relation to transcription, loop extrusion, or genome connectivity.
- Some papers support the concept through compact hierarchy descriptors rather than discrete segmentation, so "domain" does not always mean the same boundary-finding procedure.

## Internal Structure

### Sub-concepts
- [[chromatin-fractality|Chromatin fractality]]: many packing-domain papers also quantify internal scaling behavior with fractal descriptors.
- [[transcription-chromatin-coupling|Transcription-chromatin coupling]]: packing-domain organization repeatedly links to transcription or its perturbation.
- [[topologically-associating-domains|Topologically associating domains]]: some physical domains overlap TAD-scale units, but not one-to-one.

### Key Variables
- [[chromatin-packing-scaling|chromatin packing scaling]] [D]
- [[chromatin-volume-concentration|chromatin volume concentration]] [CVC]
- [[packing-domain-size|packing domain radius]] [R_f]
- [[genomic-domain-size|genomic domain size]] [N_d]
- [[packing-domain-size|packing domain diameter]]
- genome connectivity
- transcriptional output

### Descriptors
- domain heterogeneity
- domain anisotropy
- porous packing
- domain integrity
- nanodomains versus genomic-domain boundaries

## Evidence Across Papers
| Paper | System | Evidence | Notes |
| --- | --- | --- | --- |
| [Huang_SciAdv_2020](../notes/Huang_SciAdv_2020.md) | Interphase nuclei and theory | Proposes tree-like chromatin organization with packing domains as functional modules. | Strong conceptual framing. |
| [Boettiger_Nature_2016](../notes/Boettiger_Nature_2016.md) | Super-resolved Drosophila epigenetic domains | Different epigenetic states show distinct folding at kilobase-to-megabase scales, implying that domain packing depends on chromatin state rather than one universal architecture. | Domain classes are epigenetic-state-defined, not identical to ChromSTEM PD segmentation. |
| [Fang_ACSNano_2018](../notes/Fang_ACSNano_2018.md) | dSTORM of individual human subchromosomal regions | Resolves few-kb nanoscopic building blocks that cluster into higher-order chromatin structure across nuclear locations. | Supports a hierarchy in which smaller nanodomains can feed larger packing-domain-like organization. |
| [Li_SciAdv_2021](../notes/Li_SciAdv_2021.md) | nano-ChIA platform | Reports packing domains of about `200 nm` diameter with sub-megabase genomic size and links them bidirectionally to transcription. | Strong multimodal bridge paper. |
| [Li_SciRep_2022](../notes/Li_SciRep_2022.md) | ChromSTEM on human nuclei | Reports heterogeneous domains with mean radius `~80.6 nm`. | Refines single-domain structural descriptors. |
| [Miron_SciAdv_2020](../notes/Miron_SciAdv_2020.md) | Super-resolution and SEM in somatic nuclei | Resolves `~200-300 nm` physical chromatin domains that can overlap TADs yet persist after cohesin ablation. | Important non-equivalence bridge. |
| [Szabo_NatGenet_2020](../notes/Szabo_NatGenet_2020.md) | Single-cell TAD and nanodomain imaging | Reveals heterogeneous TAD-scale nanodomains with resilient but variable borders. | Connects nanodomains to genomic-domain logic without collapsing them. |
| [Noah_PlosComputBiol_2021](../notes/Noah_PlosComputBiol_2021.md) | `3D STED` imaging of zebrafish euchromatin | Uses multiplicative cascades to capture domain-within-domain euchromatin hierarchy across a continuum of nuclear states. | Supports scale-spanning hierarchy more than one discrete segmentation rule. |
| [Virk_SciAdv_2020](../notes/Virk_SciAdv_2020.md) | Modeling plus ChromEM/PWS | Links packing scaling and domain size to phenotypic plasticity. | Connects domain structure to transcriptional heterogeneity. |
| [Carter_bioRxiv_2026](../notes/Carter_bioRxiv_2026.md) | Pol-II perturbation in human nuclei | Shows that Pol-II loss disrupts packing domains, genome connectivity, and transcription. | Strongest direct perturbation evidence in the current KB. |
| [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md) | ChromSTEM tomography plus transcription and RAD21 perturbations | Defines heterogeneous packing domains with nascent and mature states; transcription and RAD21 contribute to nascent domain formation, while mature domains partly persist after RAD21 depletion. | Materially refines packing domains from static objects into life-cycle states. |

## Quantitative Summary
- [Fang_ACSNano_2018](../notes/Fang_ACSNano_2018.md): single-chromosome labeling improves effective imaging resolution from `>80 nm` to about `20 nm`, enabling direct visualization of nanoscopic chromatin building blocks.
- [Li_SciAdv_2021](../notes/Li_SciAdv_2021.md): average packing-domain diameter is reported around `200 nm`, with sub-megabase genomic size.
- [Li_SciRep_2022](../notes/Li_SciRep_2022.md): mean packing-domain radius is reported near `80.6 nm`, with estimated genomic sizes of `207 kb` in A549 cells and `82 kb` in BJ cells.
- [Miron_SciAdv_2020](../notes/Miron_SciAdv_2020.md): chromatin domains are reported around `~200-300 nm`, with a `0.7-Mb` TAD occupying a physical domain near `330 nm`.
- [Szabo_NatGenet_2020](../notes/Szabo_NatGenet_2020.md): within-TAD versus between-TAD imaging differences appear at `185 nm` versus `349 nm` median distances, with registration precision near `34 nm`.
- [Noah_PlosComputBiol_2021](../notes/Noah_PlosComputBiol_2021.md): the hierarchy description is compressed into `4` cascade parameters fitted across `78` nuclei from `10,000` candidate images, with the best `100` retained per target nucleus.
- [Carter_bioRxiv_2026](../notes/Carter_bioRxiv_2026.md): packing domains are treated as roughly `50-300 nm` structures, with PWS sensitivity concentrated over about `20-200 nm`.
- [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md): ChromSTEM spatial resolution is `~2 nm`; packing-domain size range is `50-200 nm`; modeled maturation changes `D` from `~2.2` to `~2.8`.
- [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md): `4 um` actinomycin D produces a `69%` decrease in nascent domains; the note flags the `60%` packing-efficiency change in swollen/decaying domains as ambiguous and requiring figure verification.

## Conflicts / Discrepancies
- Domain sizes vary across methods and definitions, so diameter or radius values should not be compared without checking the assay and segmentation rule.
- [Fang_ACSNano_2018](../notes/Fang_ACSNano_2018.md) reports few-kilobase nanodomains and [Boettiger_Nature_2016](../notes/Boettiger_Nature_2016.md) reports epigenetic-state-specific folded domains, both of which are domain-like but not operationally identical to the `~200 nm` packing domains in [Li_SciAdv_2021](../notes/Li_SciAdv_2021.md) and the ChromSTEM-resolved domains in [Li_SciRep_2022](../notes/Li_SciRep_2022.md).
- Several papers compare packing domains or nanodomains to TAD-scale genomic units, but none in the current KB proves a universal one-to-one mapping.
- [Miron_SciAdv_2020](../notes/Miron_SciAdv_2020.md) and [Szabo_NatGenet_2020](../notes/Szabo_NatGenet_2020.md) both strengthen partial-correspondence models rather than literal equivalence.
- [Noah_PlosComputBiol_2021](../notes/Noah_PlosComputBiol_2021.md) supports hierarchical euchromatin organization, but it does so with a phenomenological cascade representation rather than direct packing-domain boundary calls.
- Physical domain size in `nm` and genomic domain size `N_d` in `kb` or `Mbp` are related but distinct normalized variables.
- [Huang_SciAdv_2020](../notes/Huang_SciAdv_2020.md) is theory-heavy and helps frame the concept, but it does not by itself establish the experimental identity of any one domain class.
- Some papers emphasize transcriptional coupling or transcription-maintained integrity ([Li_SciAdv_2021](../notes/Li_SciAdv_2021.md), [Carter_bioRxiv_2026](../notes/Carter_bioRxiv_2026.md)), while others emphasize morphology or architecture ([Li_SciRep_2022](../notes/Li_SciRep_2022.md), [Miron_SciAdv_2020](../notes/Miron_SciAdv_2020.md), [Noah_PlosComputBiol_2021](../notes/Noah_PlosComputBiol_2021.md)); this concept page keeps those lines of evidence connected without collapsing them.
- [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md) adds a state distinction: nascent domains are sensitive to transcription inhibition and RAD21 depletion, whereas mature domains can become partly independent of ongoing extrusion.
- The current evidence distinguishes packing domains from TADs: [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md) explicitly treats TADs as connectivity features and packing domains as single-cell conformational structures with continuous life-cycle states.

## Related Concepts
- [[chromatin-fractality]]
- [[topologically-associating-domains]]
- [[transcription-chromatin-coupling]]
- [[loop-extrusion]]

## Source Papers
- [Boettiger_Nature_2016](../notes/Boettiger_Nature_2016.md)
- [Almassalha_SciAdv_2025](../notes/Almassalha_SciAdv_2025.md)
- [Carter_bioRxiv_2026](../notes/Carter_bioRxiv_2026.md)
- [Fang_ACSNano_2018](../notes/Fang_ACSNano_2018.md)
- [Huang_SciAdv_2020](../notes/Huang_SciAdv_2020.md)
- [Li_SciAdv_2021](../notes/Li_SciAdv_2021.md)
- [Li_SciRep_2022](../notes/Li_SciRep_2022.md)
- [Miron_SciAdv_2020](../notes/Miron_SciAdv_2020.md)
- [Noah_PlosComputBiol_2021](../notes/Noah_PlosComputBiol_2021.md)
- [Szabo_NatGenet_2020](../notes/Szabo_NatGenet_2020.md)
- [Virk_SciAdv_2020](../notes/Virk_SciAdv_2020.md)
