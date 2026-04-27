---
tags:
  - system
  - chromatin
---

# Chromatin compaction-dynamics system

## Variables
- [[chromatin-compaction|Chromatin compaction]]
- [[chromatin-packing-scaling|Chromatin packing scaling]]
- [[chromatin-mean-squared-displacement|Chromatin mean-squared displacement]]
- [[chromatin-displacement-correlation|Chromatin displacement correlation]]
- [[mean-square-network-displacement|Mean square network displacement]]
- Locus mobility, including gene mobility and DNA-damage-focus mobility
- Chromatin rheology
- Local gene activity state
- External force mode or mechanical anisotropy
- Measurement timescale

## Interaction Structure
- Supported system core: [[chromatin-compaction|chromatin compaction]] helps set both the amplitude and the coherence of nucleus-scale chromatin motion, but not in the same direction.
- Supported coherence branch: higher [[chromatin-compaction|chromatin compaction]] ↔ stronger [chromatin displacement correlation](../variables/chromatin-displacement-correlation.md) or baseline coherent motion.
- Supported amplitude branch: lower [[chromatin-compaction|chromatin compaction]] ↔ larger [mean square network displacement](../variables/mean-square-network-displacement.md) and larger motion amplitude.
- Supported local branch: surrounding [[chromatin-compaction|chromatin compaction]] and local gene activity state ↔ locus mobility and emergent larger-scale motion.
- Supported rheology branch: perturbing compaction can co-shift chromatin dynamics and rheological state.
- Supported structural-scaling branch: [[chromatin-packing-scaling|chromatin packing scaling]] ↔ [[chromatin-mean-squared-displacement|chromatin mean-squared displacement]] or locus subdiffusion, with theory and engineered-locus evidence linking static packing regimes to dynamic exponents.
- Supported mechanics branch: external force mode and cytoskeletal anisotropy ↔ chromatin stretching, local deformation, and transcription-linked response.
- Supported timescale branch: second-scale local motion can appear near a steady thermal regime even when slower chromosome-scale dynamics remain heterogeneous, active, or glassy.
- A compact summary branch is:
  [[chromatin-compaction|chromatin compaction]] ↔ motion coherence
  [[chromatin-compaction|chromatin compaction]] ↔ motion amplitude
- A parallel structural-scaling branch is:
  [[chromatin-packing-scaling|chromatin packing scaling]] ↔ locus MSD or subdiffusive exponent
- A parallel local-activity branch is:
  local compaction plus gene activity state ↔ locus mobility and correlated chromatin flow
- A parallel perturbation branch is:
  mechanical stress ↔ coupled compaction, dynamics, and rheology changes

## Evidence
- Relationships:
  [chromatin-compaction--chromatin-dynamics](../relationships/chromatin-compaction--chromatin-dynamics.md)
  [chromatin-compaction--chromatin-displacement-correlation](../relationships/chromatin-compaction--chromatin-displacement-correlation.md)
  [chromatin-compaction--locus-mobility](../relationships/chromatin-compaction--locus-mobility.md)
  [chromatin-compaction--mean-square-network-displacement](../relationships/chromatin-compaction--mean-square-network-displacement.md)
  [chromatin-packing-scaling--chromatin-mean-squared-displacement](../relationships/chromatin-packing-scaling--chromatin-mean-squared-displacement.md)
- Papers:
  [Bruckner_Science_2023](../notes/Bruckner_Science_2023.md)
  [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md)
  [Chan_PNAS_2024](../notes/Chan_PNAS_2024.md)
  [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md)
  [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md)
  [Iida_SciAdv_2022](../notes/Iida_SciAdv_2022.md)
  [Liu_PlosComputBiol_2018](../notes/Liu_PlosComputBiol_2018.md)
  [Ochs_Nature_2019](../notes/Ochs_Nature_2019.md)
  [Shi_NatComm_2018](../notes/Shi_NatComm_2018.md)
  [Tamm_PhysRevLett_2015](../notes/Tamm_PhysRevLett_2015.md)
  [Wei_NatComm_2020](../notes/Wei_NatComm_2020.md)

## Interpretation
- The updated relationship layer now supports a cleaner split: compaction does not control one scalar "mobility" variable, but has separable effects on motion amplitude and motion coherence.
- [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md) and [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md) support the compaction-dynamics-rheology branch, with decompacted states or perturbations aligning with larger motion amplitude and altered material response.
- [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md) sharpens the local branch by showing that low-compaction regions need active genes to drive larger-scale motions, whereas high-compaction chromatin maintains stronger baseline coupling regardless of gene activity.
- The added packing-scaling relationship extends the dynamics system beyond scalar compaction: [Bruckner_Science_2023](../notes/Bruckner_Science_2023.md) jointly supports compact interlocus scaling and locus subdiffusion in an enhancer-promoter reporter system, while [Tamm_PhysRevLett_2015](../notes/Tamm_PhysRevLett_2015.md) and [Chan_PNAS_2024](../notes/Chan_PNAS_2024.md) provide model-based scaling frameworks.
- This structural-scaling branch should stay separate from the compaction-amplitude branch because MSD exponents, mean-square network displacement, and displacement-correlation readouts are not interchangeable.
- [Iida_SciAdv_2022](../notes/Iida_SciAdv_2022.md) versus [Liu_PlosComputBiol_2018](../notes/Liu_PlosComputBiol_2018.md) and [Shi_NatComm_2018](../notes/Shi_NatComm_2018.md) preserves a scale-dependent interpretation: subsecond local motion can look near-thermal, while slower large-scale chromosome motion remains heterogeneous and glassy.
- [Wei_NatComm_2020](../notes/Wei_NatComm_2020.md) and [Ochs_Nature_2019](../notes/Ochs_Nature_2019.md) show that active forcing or repair-mediated stabilization can further gate local behavior, so passive compaction alone is not sufficient in every context.
- The best-supported system logic is therefore a context-gated mechanics system with parallel branches for coherence, amplitude, structural-scaling/MSD behavior, and activity-dependent local mobility rather than one monotonic compaction-to-dynamics rule.

## Competing Models (if any)
- One explanation emphasizes passive material-state differences such as compaction-dependent viscoelasticity or local sol-gel behavior.
- A second explanation emphasizes active processes, including transcription-linked motion, mechanical forcing, and ATP-dependent remodeling.
- A third explanation, now better supported, is a scale-dependent hybrid in which second-scale local motion can look thermal while larger-scale or perturbation-induced motion remains active, glassy, or mechanically gated.
- A fourth formulation, now directly supported by the relationship layer, is that compaction has separable effects on dynamical amplitude and dynamical coherence rather than acting as one scalar mobility controller.
- A more local active-control extension is supported by [Ochs_Nature_2019](../notes/Ochs_Nature_2019.md), where 53BP1 and RIF1 actively stabilize DSB-flanking topology and thereby constrain local chromatin behavior.
- A structural-scaling model links compact or fractal-like packing to subdiffusive MSD behavior; an active-extrusion variant predicts altered apparent packing dimensions and long-time MSD scaling, but these remain assay- and model-dependent rather than one universal exponent.

## Confidence
- Medium
