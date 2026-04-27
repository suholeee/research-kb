---
tags:
  - question
  - chromatin
---

# What Controls Chromatin Motion Amplitude and Coherence Across Compaction States?

## Core Question
- What controls chromatin motion amplitude, motion coherence, and locus mean-squared displacement across compaction states and timescales: passive material state, active forcing, structural packing scaling, or a global cell-cycle loading effect such as DNA-content doubling?

## Competing Models
- Passive material-state model: compaction, rheology, and chromosome chain organization largely determine both motion amplitude and coherence.
- Active-motion model: active processes, including gene-linked motion, ATP-dependent remodeling, mechanically imposed stress, and local topology control, are the primary drivers of emergent chromatin dynamics.
- Scale-dependent hybrid model: second-scale local motion can be largely thermal or passive, while larger-scale, lower-frequency, or perturbed dynamics depend strongly on active forcing and structural heterogeneity.
- Structural-scaling model: static packing regimes and fractal-like organization constrain locus MSD and relaxation-time scaling, so motion exponents should be interpreted with the measured packing exponent and lag-time regime.
- Active-extrusion scaling model: nonequilibrium loop extrusion can alter apparent packing dimension, TAD overlap, entanglement, and long-time MSD without reducing to bulk compaction alone.
- Provisional global DNA-loading model: slower interphase motion decreases mainly because DNA-content doubling loads the nucleus more strongly from `G1` to `G2`, even without a dominant cohesin-control effect.
- Readout-mismatch model: some apparent conflicts between compaction and dynamics arise because different assays treat non-equivalent structural descriptors as the same "compaction state."

## Supporting Evidence
- [[chromatin-compaction-dynamics-system|Chromatin compaction-dynamics system]] explicitly treats passive and active explanations as partially compatible rather than mutually exclusive.
- The same system now makes a sharper split between motion amplitude and motion coherence: higher [[chromatin-compaction|compaction]] is associated with lower [[mean-square-network-displacement|MSND]] but stronger [[chromatin-displacement-correlation|Cdx]].
- The same system now adds a structural-scaling branch linking [[chromatin-packing-scaling|chromatin packing scaling]] to [[chromatin-mean-squared-displacement|chromatin mean-squared displacement]], separate from scalar compaction, `MSND`, and `Cdx`.
- [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md) reports that undifferentiated chromatin is less compact and more dynamic than differentiated chromatin, and interprets differentiation as a local sol-gel transition.
- [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md) reports that mechanical stress changes chromatin compaction, dynamics, and rheology together.
- [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md) reports that a single active gene drives larger-scale motions in low-compaction regions, whereas high-compaction chromatin drives gene motion regardless of activity state.
- [Bruckner_Science_2023](../notes/Bruckner_Science_2023.md) jointly reports compact interlocus scaling `1/d = 0.31 +/- 0.07` over `58-190 kb` and locus subdiffusion `beta = 0.52 +/- 0.04`, directly tying static organization to live-locus dynamics in one reporter system.
- [Tamm_PhysRevLett_2015](../notes/Tamm_PhysRevLett_2015.md) predicts fractal-globule monomer motion `<X^2(t)> ~ t^alpha_F`, where `d_f = 3` gives `alpha_F = 2/5`, providing a theory baseline rather than a direct chromatin measurement.
- [Chan_PNAS_2024](../notes/Chan_PNAS_2024.md) predicts that active extrusion can shift apparent `D` from `2` to `4`, reduce TAD overlap to `<35%`, increase effective entanglement strand length up to `50-fold`, and produce long-time `MSD proportional to Delta t^(1/3)`.
- [Ochs_Nature_2019](../notes/Ochs_Nature_2019.md) shows that `53BP1` and `RIF1` actively stabilize DSB-flanking topology, and that loss of these factors decompacts local chromatin and distorts repair architecture.
- [Iida_SciAdv_2022](../notes/Iida_SciAdv_2022.md) reports that local nucleosome motion on `~1 s` and `~200 nm` scales remains steady across `G1`, `S`, and `G2`, with `100 ms` displacements near `76-78 nm`, and is consistent with mainly thermal driving.
- [Lee_BiophysJ_2025](../notes/Lee_BiophysJ_2025.md) shows that image-based fractality or compaction metrics can follow similar cell-cycle trends while differing strongly in absolute values, and that some readouts are highly threshold dependent.
- [Liu_PlosComputBiol_2018](../notes/Liu_PlosComputBiol_2018.md) argues that chromosome chain organization determines subdiffusive chromatin-locus dynamics and sets relaxation-time hierarchies.
- [Shi_NatComm_2018](../notes/Shi_NatComm_2018.md) argues that human interphase chromosomes exhibit out-of-equilibrium glassy dynamics with heterogeneous diffusion behavior.
- [Wei_NatComm_2020](../notes/Wei_NatComm_2020.md) shows that force mode and stress-fiber anisotropy alter chromatin stretching and rapid transcriptional response, adding an external active-control branch.
- Provisional background only: [Rey-Millet_bioRxiv_2026](../notes/Rey-Millet_bioRxiv_2026.md) points to a `G1 -> G2` decrease in diffusivity and drift consistent with DNA-content loading, but the note is still low-confidence and needs manual review before it should outweigh the stronger normalized evidence above.

## Missing Evidence
- A unified quantitative framework that compares [[chromatin-displacement-correlation|Cdx]], [[mean-square-network-displacement|MSND]], locus `MSD`, Hi-D diffusivity or drift, rheology, and the specific compaction or fractality descriptor used in each assay.
- Simultaneous measurements of [[chromatin-compaction|chromatin compaction]], DNA content, transcriptional activity, coherent nuclear dynamics, and locus mobility in the same cells and on matched timescales.
- Direct experiments that bridge the `0.05-0.5 s` local-motion regime of [Iida_SciAdv_2022](../notes/Iida_SciAdv_2022.md) to the slower glassy, cell-cycle, or mechanically driven regimes emphasized by [Shi_NatComm_2018](../notes/Shi_NatComm_2018.md), [Wei_NatComm_2020](../notes/Wei_NatComm_2020.md), and the still-unreviewed [Rey-Millet_bioRxiv_2026](../notes/Rey-Millet_bioRxiv_2026.md).
- Same-cell calibration of static packing exponent `D`, live-locus `MSD`, `MSND`, and `Cdx` across the same lag-time windows, because the updated evidence makes these non-interchangeable.
- Perturbations of [[loop-extrusion-activity|loop extrusion activity]], cohesin residence, or topoisomerase state that test active-extrusion MSD predictions without relying only on contact-map changes.
- Direct tests of whether active topology stabilizers such as `53BP1` or `RIF1` alter local mobility beyond what would be predicted from compaction alone.
- Cross-assay calibration showing whether discordant compaction-dynamics trends persist after threshold-dependent image metrics, physical-density metrics, and rheological metrics are mapped onto comparable structural states.

## Testable Predictions
- If passive material state is dominant, matched [[chromatin-compaction|compaction]] or rheological states should produce similar `Cdx`, `MSND`, and locus mobility even when local gene activity or force-delivery mode differs.
- If compaction mainly controls coherence rather than amplitude, increasing [[chromatin-compaction|compaction]] should increase [[chromatin-displacement-correlation|Cdx]] while decreasing [[mean-square-network-displacement|MSND]].
- If active forcing is dominant, suppressing ATP-dependent or transcription-linked activity in low-compaction regions should reduce large-scale motion more than expected from compaction changes alone.
- If the structural-scaling model is correct, matched static packing exponents should predict locus MSD exponents better than bulk compaction metrics alone, within the same genomic-distance and lag-time regime.
- If the active-extrusion scaling model is correct, acute changes in cohesin extrusion or residence should shift long-time MSD and TAD overlap while leaving short-lag local nucleosome motion less affected.
- If the scale-dependent hybrid model is correct, second-scale local motion may remain similar across interphase states while longer-timescale, lower-frequency, or mechanically driven dynamics diverge sharply.
- If the global DNA-loading model is correct, `G1 -> G2` decreases in diffusivity or drift should persist even when cohesin status is perturbed, while the subsecond local-motion regime remains comparatively stable.
- If readout mismatch explains part of the conflict, compaction-motion correlations should tighten once studies are re-expressed with matched structural observables rather than mixed thresholded and non-thresholded descriptors.
- If active local topology control is important, disrupting `53BP1` or `RIF1` should change DSB mobility or local structural persistence more strongly than expected from bulk compaction matching alone.
- If force-transmission architecture matters, equal nominal loads applied in different force modes should yield different chromatin stretching and transcriptional consequences unless cytoskeletal anisotropy is disrupted.

## Confidence
- Medium: coupling between compaction and dynamics is consistent across notes, but the KB now supports separable amplitude, coherence, structural-scaling, and active-extrusion branches rather than one universal mobility law, and the DNA-loading branch remains more provisional than the others.
