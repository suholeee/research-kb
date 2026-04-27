# Chromatin compaction ↔ chromatin dynamics

## Variables
- [Chromatin compaction](../variables/chromatin-compaction.md)
- Chromatin dynamics, including [chromatin displacement correlation](../variables/chromatin-displacement-correlation.md) and [mean square network displacement](../variables/mean-square-network-displacement.md)

## Relationship
- Chromatin compaction state is repeatedly linked to both the amplitude and the coherence of nucleus-scale chromatin motion.
- [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md) states directly that undifferentiated chromatin is less compact and more dynamic than differentiated chromatin.
- [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md) reports that mechanical stress produces coupled changes in chromatin compaction, dynamics, and rheology, with `60%` of injected nuclei remaining in an altered state.
- [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md) links spatial heterogeneities of chromatin compaction to emergent genome-wide motions, with low-compaction regions permitting activity-dependent larger-scale motion and high-compaction chromatin providing tighter baseline coupling.

## Evidence
- [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md)
- [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md)
- [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md)

## Interpretation
- Across the live-cell chromatin papers, compaction is not just a static state variable; it helps determine whether chromatin behaves more like a tightly coupled elastic network or a faster, more weakly coupled dynamic medium.
- The current KB therefore supports a mixed relationship rather than a single monotonic rule: higher compaction can suppress motion amplitude while strengthening spatial correlation, whereas lower compaction can allow larger displacements and activity-driven rearrangements.

## Caveats
- The papers use different dynamical readouts and perturbations, so the relationship is consistent but not yet reduced to one universal quantitative law.
- [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md) and [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md) still contain manual-review gaps in their normalized quantitative sections.
- Compaction proxies such as `I_ch` and `I_n` are assay-specific and should not be merged with volumetric density measures like `CVC`.

## Confidence
- Medium
