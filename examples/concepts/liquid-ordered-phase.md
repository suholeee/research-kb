---
tags:
  - concept
  - membrane
concept_id: liquid-ordered-phase
title: "Liquid-ordered phase"
aliases:
  - LO phase
  - Lo domain
status: synthesized
related_concepts:
  - lamellar-spacing
  - lipid-raft-alignment
  - x-ray-reflectivity
---

# Liquid-ordered phase

## Definition
- Liquid-ordered phase is the cholesterol-associated ordered membrane state denoted `LO` or `Lo` in the current membrane papers.
- In the current KB, the term covers two related but distinct uses: a cholesterol-induced ordered state in DPPC-rich multilayers and the ordered domain state within pre-existing Lo/Ld phase-separated stacks.

## How Measured
- [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md) infers an LO transition from fluorescence morphology plus X-ray-derived spacing and ordering changes.
- [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md) studies Lo/Ld coexistence in stacked membranes and uses that coexistence as the substrate for long-range interlayer alignment.
- [Lee_JACS_2024](../notes/Lee_JACS_2024.md) tracks Lo domains in a phase-separated multilayer and links their alignment and area growth to smaller lamellar spacing.
- The current KB therefore treats `LO/Lo` as an operational ordered-membrane state whose exact meaning depends on composition and whether the paper studies a transition into order or behavior of ordered domains once present.

## Evidence Across Papers
| Paper | System | Evidence | Notes |
| --- | --- | --- | --- |
| [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md) | `SM:DOPC + cholesterol` multilayers | Coexisting `Lo` and `Ld` domains align across stacked bilayers over micron-scale thickness. | Establishes Lo domains as the units that register vertically across the stack. |
| [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md) | DPPC/cholesterol multilayer | Fluorescence and reflectivity support a ripple-to-LO transition between `5` and `7 mol%` cholesterol, with increasing vertical order at higher cholesterol. | Here LO is the cholesterol-induced ordered multilayer state. |
| [Lee_JACS_2024](../notes/Lee_JACS_2024.md) | `DPPC:DOPC = 6:4` with `30% cholesterol` | Dark Lo domains grow and align more strongly as spacing decreases. | Here Lo is one phase within a pre-existing domain mixture. |

## Quantitative Summary
- [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md): Lo/Ld coexistence is reported at `<=40%` cholesterol within a broader `10-60%` cholesterol composition range, and aligned stacks span about `1-7 um`.
- [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md): the transition consistent with ripple-to-LO occurs between `5` and `7 mol%` cholesterol.
- [Lee_JACS_2024](../notes/Lee_JACS_2024.md): Lo domain area increases from `24.8 um^2` to `58.42 um^2` as `CaCl2` increases from `100` to `500 mM`.

## Conflicts / Discrepancies
- The term is shared across papers, but the operational definition is not identical.
- [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md) uses LO mainly as the post-transition ordered state of a DPPC/cholesterol multilayer.
- [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md) and [Lee_JACS_2024](../notes/Lee_JACS_2024.md) use Lo mainly as the ordered phase identity inside a coexistence regime.
- Cross-paper synthesis should therefore distinguish transition into an LO state from spacing-dependent behavior of Lo domains once they already exist.

## Related Concepts
- [[lamellar-spacing]]
- [[x-ray-reflectivity]]
- [[lipid-raft-alignment]]

## Source Papers
- [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md)
- [Lee_JACS_2024](../notes/Lee_JACS_2024.md)
- [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md)
