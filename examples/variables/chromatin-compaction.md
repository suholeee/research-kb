---
tags:
  - variable
  - chromatin
---

# Chromatin compaction

## Definition
- Chromatin compaction is a local or regional proxy for how concentrated, condensed, or decondensed chromatin appears within a nucleus.
- In the current KB, this usually means a live-cell imaging or label-free physical-state proxy rather than a direct volumetric density measurement.
- The changed notes broaden this page from fluorescence intensity alone to include label-free condensation/decondensation metrics and repair-associated chromatin decompaction.

## Units
- Usually unitless or reported in normalized fluorescence-intensity, scattering, or assay-specific proxy units.
- Common notations and surface forms in the current KB: `I_ch`, `I_n`, chromatin compaction level, chromatin condensation level, chromatin decompaction.

## Where Used
- Concept pages: [[chromatin-condensates]], [[transcription-chromatin-coupling]], [[double-strand-break-repair]].
- Papers: [Caragine_SoftMatt_2022](../notes/Caragine_SoftMatt_2022.md), [Chu_NatComm_2024](../notes/Chu_NatComm_2024.md), [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md), [Hsiao_ACSNano_2021](../notes/Hsiao_ACSNano_2021.md), [Hsiao_CommBiol_2024](../notes/Hsiao_CommBiol_2024.md), [Rybczynski_CellRepMethods_2025](../notes/Rybczynski_CellRepMethods_2025.md), [Vinayak_NatComm_2025](../notes/Vinayak_NatComm_2025.md).

## Measurement Methods
- H2B-labeled live-cell spinning-disk confocal microscopy followed by intensity mapping.
- Relative compaction or compaction-gradient calculations from chromatin fluorescence fields.
- Comparative analysis across perturbations such as differentiation, DNA damage, or mechanical stress.
- Label-free DYNAMICS or iSCORS-style scattering/diffusion readouts when papers explicitly interpret the signal as chromatin condensation or decondensation.
- Fixed-cell or live-cell repair imaging when local decompaction is the chromatin-state output around an induced locus.

## Conflicts / Ambiguities
- This variable should not be merged automatically with [[chromatin-volume-concentration]], which is a volumetric electron-microscopy quantity rather than an intensity proxy.
- It also should not be merged automatically with [[chromatin-condensability]], which measures propensity to enter or remain in a condensate-like state.
- `I_n` is ambiguous in the current KB: [Eshghi_PhysRevLett_2021](../notes/Eshghi_PhysRevLett_2021.md) uses it as a compaction proxy, whereas [Arsenadze_BiophysJ_2024](../notes/Arsenadze_BiophysJ_2024.md) uses the same symbol for intervening chromatin density between nucleoli.
- Relative compaction gradients such as `S_rel` are derived from compaction maps, not synonyms for the underlying compaction variable.
- [Hsiao_ACSNano_2021](../notes/Hsiao_ACSNano_2021.md) and [Hsiao_CommBiol_2024](../notes/Hsiao_CommBiol_2024.md) support condensation/decondensation dynamics, but their label-free signals are not locus-resolved genomic-domain measurements.
- [Rybczynski_CellRepMethods_2025](../notes/Rybczynski_CellRepMethods_2025.md) is a methods resource for repair imaging, so chromatin decompaction should be treated as a validated locus-level readout rather than a general repair mechanism by itself.
