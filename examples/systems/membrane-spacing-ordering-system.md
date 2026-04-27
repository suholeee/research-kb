---
tags:
  - system
  - membrane
---

# Membrane spacing-ordering system

## Variables
- [[cholesterol-content|Cholesterol content]]
- [[lamellar-spacing|Lamellar spacing]]
- Vertical order, operationalized by X-ray peak FWHM and electron-density-profile amplitude
- Domain alignment state
- [[domain-area|Domain area]]
- [[water-layer-thickness|Water layer thickness]]

## Interaction Structure
- Supported DPPC/cholesterol branch: [[cholesterol-content|cholesterol content]] ↔ [[lamellar-spacing|lamellar spacing]], with a non-monotonic spacing response in the supported multilayer dataset.
- Supported DPPC/cholesterol branch: [[cholesterol-content|cholesterol content]] ↔ vertical order.
- Supported phase-separated multilayer branch: smaller [[lamellar-spacing|lamellar spacing]] ↔ aligned domain state.
- Supported phase-separated multilayer branch: smaller [[lamellar-spacing|lamellar spacing]] ↔ larger ordered-domain area.
- The current membrane evidence is best represented as two parallel subsystem chains rather than one merged pathway:
  [[cholesterol-content|cholesterol content]] ↔ [[lamellar-spacing|lamellar spacing]] and vertical order
  [[lamellar-spacing|lamellar spacing]] ↔ domain alignment state ↔ [[domain-area|domain area]]
- For [Lee_JACS_2024](../notes/Lee_JACS_2024.md), the directional statement that is directly supported is:
  reduced lamellar spacing -> stronger alignment and larger domains

## Evidence
- Relationships:
  [cholesterol-content--lamellar-spacing](../relationships/cholesterol-content--lamellar-spacing.md)
  [cholesterol-content--vertical-order](../relationships/cholesterol-content--vertical-order.md)
  [lamellar-spacing--domain-alignment-state](../relationships/lamellar-spacing--domain-alignment-state.md)
  [lamellar-spacing--domain-area](../relationships/lamellar-spacing--domain-area.md)
- Papers:
  [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md)
  [Lee_JACS_2024](../notes/Lee_JACS_2024.md)
- Concepts:
  [[lamellar-spacing]]
  [[liquid-ordered-phase]]
  [[x-ray-reflectivity]]

## Interpretation
- The membrane papers support two adjacent but not yet fully merged membrane subsystems.
- In the DPPC/cholesterol multilayer system, cholesterol changes spacing non-monotonically and increases vertical order.
- In the phase-separated multilayer system, reduced intermembrane spacing acts as a control parameter for out-of-plane registration and for in-plane ordered-domain growth.
- The current KB therefore supports spacing as a reusable membrane control variable, but it does not yet support a direct cholesterol-to-raft-alignment pathway across the two experimental systems.

## Competing Models (if any)
- For spacing-controlled alignment, the main competition is between a Ca2+-specific chemistry model and a distance-controlled coupling model.
- [Lee_JACS_2024](../notes/Lee_JACS_2024.md) favors the distance-controlled model because `NaCl` or `PEG 10K` can also reduce `D` and induce alignment or growth.
- For cholesterol-driven ordering, the ripple-to-LO and chain tilt-to-untilt interpretation is plausible but still inferred from reflectivity and morphology proxies rather than a direct chain-order probe.
- The KB also does not yet establish whether cholesterol could drive raft alignment indirectly through spacing in the separate phase-separated system, because that perturbation has not been shown directly.
- Hysteresis after salting and desalting indicates that the aligned state is not captured by a purely reversible equilibrium-spacing picture.

## Confidence
- High
