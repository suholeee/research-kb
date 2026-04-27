---
tags:
  - experiment
  - membrane
---

# Experimental Designs for Membrane Interlamellar Ordering Theory

Grounded in [[membrane_interlamellar-ordering-theory|Membrane Interlamellar Ordering Theory]], [[membrane-spacing-ordering-system|Membrane spacing-ordering system]], [[spacing-controlled-raft-alignment]], and [[cholesterol-induced-membrane-ordering-mechanism]].

## Most Critical Open Problems
- Whether [[lamellar-spacing|lamellar spacing]] [`D`] is sufficient to predict Lo-domain alignment across different compression routes, or whether [[water-layer-thickness|water-layer thickness]] [`d_w`] and interfacial-water overlap are more proximal.
- Whether the aligned state is determined by current spacing alone or by perturbation history and kinetic trapping.
- Whether cholesterol-driven vertical ordering is primarily a chain-order transition, a water-layer redistribution effect, or a coupled process.
- Whether larger [[domain-area|ordered-domain area]] is downstream of alignment or whether both are parallel outputs of stronger interlayer coupling.

## Competing Hypotheses
- Distance-controlled interlayer-coupling model
- Interfacial-water-overlap model
- Ion-specific chemistry model
- Equilibrium state model in which current [`D`] sets the phenotype
- History-trapped regime model in which matched final [`D`] can retain different alignment states
- Chain-order-primary cholesterol-ordering model
- Hydration-redistribution-primary model
- Coupled chain-order plus hydration model
- Serial alignment-to-growth model
- Parallel-output model

# Matched-Spacing Compression Matrix

## Question
- Does matched [[lamellar-spacing|lamellar spacing]] collapse alignment and domain-growth behavior across different compression routes, or do states with similar `D` but different hydration structure diverge?

## Competing Models
- Distance-controlled interlayer-coupling model
- Interfacial-water-overlap model
- Ion-specific chemistry model

## Experimental Design
- perturbations: use the phase-separated supported multilayer system from [Lee_JACS_2024](../notes/Lee_JACS_2024.md), and generate matched spacing bins such as `~105`, `~90`, `~80`, and `~70 A` using `CaCl2`, `MgCl2`, `NaCl` added on a low-`CaCl2` background, and `PEG 10K`, with emphasis on route pairs that achieve similar `D` but measurably different [`d_w`] or hydration partitioning.
- controls: untreated multilayers, `NaCl`-only conditions that do not appreciably reduce [`D`], direct replication of the previously observed low- and high-`CaCl2` endpoints, and fresh samples equilibrated directly at each target `D`.
- variables to measure: [[lamellar-spacing|lamellar spacing]] [`D`] and [[water-layer-thickness|water-layer thickness]] [`d_w`] by synchrotron [[x-ray-reflectivity|X-ray reflectivity]], Lo-domain alignment fraction or registration metric by fluorescence microscopy, and [[domain-area|Lo-domain area]] [`A`].

## Expected Outcomes
- Matched-`D` conditions converge to similar alignment and domain area across solutes -> supports the distance-controlled model.
- States matched for `D` but not for [`d_w`] diverge in alignment or domain area, while convergence improves when [`d_w`] is also matched -> supports the interfacial-water-overlap model.
- Conditions matched for both `D` and [`d_w`] still show stronger alignment or larger domains in one ion condition than in `PEG` or another salt route -> supports ion-specific chemistry.
- Alignment collapses across matched `D` but domain area does not -> supports spacing as the proximal predictor of registration, with coarsening controlled by an additional variable.

## Feasibility
- high

# Reversible Compression Hysteresis Map

## Question
- Is the aligned state determined by the instantaneous lamellar spacing and hydration state, or does compression history leave a persistent structural memory?

## Competing Models
- Equilibrium state model
- History-trapped regime model

## Experimental Design
- perturbations: perform stepwise salting and desalting in the [Lee_JACS_2024](../notes/Lee_JACS_2024.md) system, run a parallel compression-decompression series using `PEG 10K` to reach the same final `D` values without changing ionic identity, and include short and long dwell times at each endpoint to separate slow relaxation from stable trapping.
- controls: fresh samples equilibrated directly at each endpoint `D` and [`d_w`], plus repeated cycles ending at the same `D` from different starting points.
- variables to measure: lamellar spacing [`D`] and water-layer thickness [`d_w`] by X-ray reflectivity, alignment fraction and Lo-domain area by time-resolved fluorescence microscopy, and relaxation time back toward the pre-perturbation state after decompression.

## Expected Outcomes
- Samples with the same final `D` and [`d_w`] converge to the same alignment and domain area regardless of path -> supports the equilibrium state model.
- Samples with the same final `D` and [`d_w`] retain different alignment states or domain sizes after both salt and `PEG` routes -> supports the history-trapped regime model.
- Differences disappear only after long holds -> supports kinetic trapping rather than a sharply separated regime.

## Feasibility
- high

# Cholesterol Ordering Mechanism Split Test

## Question
- What microscopic structural change links cholesterol to stronger vertical order in supported DPPC multilayers?

## Competing Models
- Chain-order-primary cholesterol-ordering model
- Hydration-redistribution-primary model
- Coupled chain-order plus hydration model

## Experimental Design
- perturbations: repeat the supported DPPC/cholesterol multilayer system from [Lee_CurrApplPhys_2017](../notes/Lee_CurrApplPhys_2017.md), run a dense cholesterol series with emphasis on `3`, `5`, `7`, `10`, `20`, `30`, `40`, and `50 mol%`, and add a matched-hydration arm by mild osmotic compression at fixed cholesterol above `10 mol%` to test whether water-layer reduction alone can reproduce the high-cholesterol `D` decrease.
- controls: cholesterol-free DPPC multilayers, cholesterol-only multilayer control, and a constant temperature and hydration protocol across the sweep.
- variables to measure: lamellar spacing [`D`], reconstructed bilayer thickness, and water-layer thickness from X-ray reflectivity and electron-density reconstruction; vertical-order readouts such as X-ray peak FWHM and electron-density-profile amplitude; a direct chain-order readout by WAXS; and fluorescence morphology across the `5-10 mol%` transition window.

## Expected Outcomes
- WAXS chain order increases over the same cholesterol window where X-ray peaks sharpen, and bilayer thickening explains the early `D` increase -> supports the chain-order-primary model.
- Vertical order strengthens while WAXS changes weakly and the main structural shift is reduced water-layer thickness above `10 mol%` cholesterol -> supports the hydration-redistribution-primary model.
- Chain order and water-layer thickness both change in distinct but coordinated ranges -> supports the coupled model.

## Feasibility
- medium

# Alignment-Before-Coarsening Time Course

## Question
- Is domain growth downstream of alignment, or are alignment and coarsening parallel outputs of stronger interlayer coupling?

## Competing Models
- Serial alignment-to-growth model
- Parallel-output model

## Experimental Design
- perturbations: apply rapid compression steps from a large-`D` state into an aligning regime using either `CaCl2` or `PEG 10K`, then track the first minutes to hours after the step.
- controls: no-compression time series, a pre-aligned small-`D` state as a positive control, and matched final `D` reached by two different perturbation routes.
- variables to measure: lamellar spacing [`D`] by intermittent X-ray reflectivity, alignment metric and domain number and domain area by live fluorescence microscopy, and coarsening rate as the time derivative of mean domain area.

## Expected Outcomes
- Alignment increases before domain area begins to grow -> supports the serial alignment-to-growth model.
- Alignment and area increase with the same onset and no reproducible lag -> supports the parallel-output model.
- Domain area grows without strong registration -> argues that coarsening can occur independently of alignment.

## Feasibility
- medium
