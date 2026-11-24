# v5 fish school motor-law transfer: original source admission before numerical animal trajectories

## Scientific question
Can Reynolds separation/alignment/cohesion features improve heldout fish *next-velocity* prediction beyond a focal fish's own previous movement? Does extra information that selectively weights **faster** neighbors transfer between entirely withheld experimental fish-school trials?

**Prior art:** Puy et al. 2024 PNAS 121 e2309733121 found selective interactions with faster neighbors already. We are **not claiming discovery** of selective social interactions. The contribution tested here would be out-of-trial (and eventually cross-species) predictive transfer under fixed feature definitions, plus a separate observation/mechanism boundary linking school distributions to fish chorus signals.

## Genuine field source and grain
- Published 2024 50-Hz black neon tetra tracks: 39-fish (2×60min) and 8-fish (6×30min) experiments, Zenodo DOI 10.5281/zenodo.10890112.
- Published XAV fish vocal audio-video dataset: https://osf.io/q8dz4, separate source and species. **No matching subjects, dates or joint acoustics** across these studies. The short six-WAV GitHub example passed acoustic-coherence diagnostics but has 230 unmatched frames on channel 1; strict native frame-sync STOP remains.
- The v5 Actions stage reads **only official metadata/file listing**, never full animal trajectories or numeric motion outcomes.

## Frozen future empirical benchmark (NOT YET EXECUTED)
Primary: six 8-fish recording trials. Entire trial left out; no randomized frame, fish or within-trial block leakage. Group/age as metadata only; 39-fish trials separately as descriptive scale transfer, not pooled independent replicates.

Target: planar future velocity at a fixed +0.20 s (10 native frames) against same original heldout frames. All features at or before t. If source offers only globally smoothed coordinates (using future frames), report *retrospective heldout-trial transport* and NOT fully online causal prediction.

- M0: own past kinematics + wall-proximity terms.
- M1: M0 + same-time separation, alignment and cohesion vectors using train-only standardized fixed radius, no post-outcome threshold tuning.
- M2: M1 + alignment vector restricted to neighbors moving **faster than focal fish** (after including current speed as M0 predictor).
- Ghost: same-dimension whole-trial time-shifted neighbor paths, preserving each trace's autocorrelation but not current social geometry. Compare on *identical* target observations.

Score: equal-trial MSE future Cartesian velocity vector, both coordinates, trial-level sign and bootstrap with n=6, exact one-sided sign test, 95% block interval descriptive. A positive M2–M1 mean without majority-trial improvement does not support a transferable condition. No inference of real interaction coefficient from predictive ridge models.

Eligibility: independent original record MD5/SHA, ≥4 complete 8-fish trials with unique within-trial IDs, coordinates/time and ≥3000 valid native frames per trial, known units/fps, no overlapping trial split. Any failed admission -> SOURCE_STOP and no effect. v4 actual fish vocal interaction not tested.

## Readout limitations
Even if M1 helps, correlated movements and shared tank constraints can cause prediction gains absent true social causation. Movement-only data do not establish chorus or individual calling. No original track files will be redistributed.
