---
tags:
  - variable
  - membrane
---

# Cholesterol content

## Definition
- Cholesterol content is the membrane composition variable used to tune ordering, phase behavior, and lamellar structure in the current membrane papers.
- In the current KB, it is typically reported as a sample composition rather than as a derived structural measurement.
- The normalized meaning is cholesterol fraction within a specified lipid mixture, not a universal structural coordinate that can be compared across different host compositions without context.

## Units
- Mole percent (`mol%`).

## Where Used
- Concept pages: [[lamellar-spacing]], [[lipid-raft-alignment]], [[liquid-ordered-phase]], [[x-ray-reflectivity]].
- Papers: [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md), [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md).

## Measurement Methods
- Defined by mixture preparation and sample composition.
- Used as a controlled input variable in fluorescence and X-ray reflectivity experiments.
- Interpreted as a regime-setting composition variable for whether ordered-domain coexistence or cholesterol-driven ordering is even present in the sample.

## Conflicts / Ambiguities
- This variable is a composition control parameter, not a structural state variable.
- It should therefore stay separate from outputs such as [[lamellar-spacing|lamellar spacing]] or [[domain-area|domain area]].
- The same `mol%` value is not automatically comparable across different lipid mixtures. [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md) uses supported DPPC/cholesterol multilayers with a ripple-to-`LO` transition inferred near `5-7 mol%`, whereas [Tayebi_NatMat_2012](../notes/Tayebi_NatMat_2012.md) uses `SM/DOPC/cholesterol` mixtures where `Lo/Ld` coexistence persists up to about `40%` cholesterol.
