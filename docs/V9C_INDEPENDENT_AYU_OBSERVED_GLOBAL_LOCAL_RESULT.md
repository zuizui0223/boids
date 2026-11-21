# v9c independent ayu species: global school velocity predicts individual future motion; k=3 local increment fails delayed transfer

**2026-11-20 original source**, seven independent recording *files* of 10 *Plecoglossus altivelis* fish (Niizato et al. 2024 *Scientific Reports* 14:29758; DOI 10.1038/s41598-024-79232-2), original [GitHub](https://github.com/t-niizato/Information-structure-of-heterogeneous-criticality) pinned commit `158e8d7ebdef73752da63192ee36e3a099dd5dfa`.

[GitHub Actions #44760500567](https://github.com/zuizui0223/boids/actions/runs/44760500567) **SUCCESS** after fixing only a synthetic fixture sample count. [Full original no-raw-position numerical receipt](https://github.com/zuizui0223/boids/actions/runs/44760500567/artifacts/14640044277). **All 7 original file Git SHA values verified and all 4 regression/known-truth tests passed.** No source tracks or per-fish positions redistributed.

## Important source clock correction before ecological effects

Separate original-source `v9b` [Actions #44759606259](https://github.com/zuizui0223/boids/actions/runs/44759606259) showed source 22 numeric columns, no missing fish XY, first column native frame index +1 per row, second elapsed clock time, ~30fps from original frame count and time span. The original 2024 article used 20Hz for a separate *processed* analysis, **not the rate of these unmodified source TXT lines**. Author's published MATLAB importer maps source columns 3–12 to X and 13–22 to Y. Do not fit physical speeds using 20fps for these unmodified 7 files. Units of X/Y are original file units, and are not asserted to be centimeters.

## Fixed original-source cross-recording test

Seven source recordings (10 fish × 10,101–13,861 native rows), each entire recording held out with six others used for training. Fixed `Ridge(alpha=10)`, train-only scaling, one source time each 6 frames; fixed target future average 2D velocity:
- Short: t→t+6 frames = 0.0–0.2s.
- Delayed: t+15→t+21 = 0.5–0.7s.
- G: own x/y, own prior two 0.1-second velocity segments and acceleration/speed, mean displacement + distance to *topological 3 nearest fish*, displacement to school center.
- G+Global: two extra velocity components of the mean **other nine fish** relative to the focal fish.
- G+Local3: two components of relative velocity of **three closest fish**, different from the whole school by construction.
- G+Both: same G+Global with actual local3 components.
- G+RotatedLocal: the same nine other-fish velocities, rotated across original other-fish positions per focal/time, preserving global speed distribution while deliberately changing local correspondence. Not an exchangeable experimental intervention.

No spatial radius was tuned by outcomes. The three-nearest rule was registered before reading original ayu movement predictor outcomes after the source-only schema. **The original article already discussed critical information / Boids comparisons, so this is not a new discovery of generic collective motion**. The possible novel contrast is fixed out-of-recording *global-versus-local predictive transfer* in a new species.

## Original whole-recording heldout results

All MSEs in squared *unknown original numeric coordinate units per second*; **never compare these absolute MSEs with the black neon tetra (cm/s)^2**. Smaller is better.

| Endpoint | G geometry | G+Global | G+Local3 | G+Both | G+RotatedLocal |
|---|---:|---:|---:|---:|---:|
| Short 0.0–0.2s | **7343.4456** | **6604.3269** | 6635.4036 | **6541.2588** | 6604.6330 |
| Delayed 0.5–0.7s | **31090.9166** | **26311.9455** | 27898.0720 | **26312.0732** | 26314.3611 |

### Primary ecological evidence hierarchy

1. **Whole-school velocity information is repeatably positive in a different fish species.** Short G→G+Global absolute MSE reduction +739.1187 = **10.065% relative to G**, original recording signs **7/7**, descriptive recording-bootstrap Δ95% [495.0,987.7]. Delayed G→G+Global +4778.9711 = **15.37% relative to G**, **7/7**, descriptive Δ95% [3957.1,5617.9]. Conditional one-sided recording sign p=0.0078125 only under independent recording signs (unknown shared animal origin).
2. **Extra local three-neighbor speed information is much weaker and horizon-dependent.** Short G+Global→G+Both mean gain +63.0681 = 0.955% of G+Global baseline, **6/7 positive**, one-sided recording sign p=.0625, descriptive Δ95% [+19.060,+113.217]. Does not meet universal seven-recording sign support.
3. **Delayed independent local information is unsupported.** G+Global→G+Both −0.1277 original MSE units (effect ~−0.000485% of G+Global baseline), **4/7 positive**, descriptive Δ95% [−10.201,+9.473].
4. **Spatial speed crosswalk diagnostic:** True local3 vs one fixed other-nine velocity rotation short +63.3742, 6/7; delayed +2.2879, 5/7, descriptive delayed interval [−9.106,+13.707]. Not a causal permutation p.
5. **Global information is complementary to local3:** G+Local3→G+Both +94.1448 short (7/7) and +1585.9988 delayed (7/7). The global state is not simply replaceable by the three-nearest speed.

## Joint interpretation with black neon tetra v5–v8

- **Black neon tetra 8 fish/6 recordings**: full Boids-neighbor predictors over own past +2.5798 (cm/s)^2 in 6/6; v7 revealed global other-seven velocity accounts for nearly all the local-signal gain because **93.669% of focal×time cases have all 7 fish in the 25cm neighborhood**. v8 local velocity assignment advantage +0.0332 for 0.2s in 6/6, yet later t+0.5..0.7s additional global-conditioned local effect 4/6 and uncertainty interval crosses zero.
- **Ayu 10 fish/7 recordings (new independent taxon)**: globally shared velocity predicts withheld recordings for short and delayed outcomes 7/7; true 3 nearest neighbors add little and fail delayed support.
- **Two distinct fish taxa / two published studies** provide **cross-species positive predictive replication of a group-wide movement-state contribution**, not a formal meta-analysis or proof of a universal causal schooling force. Different study geometry and processing prevent direct pooling of motion parameters, MSE units, or a causal force coefficient.
- Neither source has fish calls recorded at matched fish positions. Independent Mouy XAV OSF source 66 localized sound events lacks continuous fish track IDs. **Fish schooling→fish chorus ecological mechanism remains NOT_TESTED.**

## Source-quality boundaries

Some 2024 fish trajectories were corrected/interpolated by their original tracking pipelines, and the Puy paper uses a Gaussian filter with support to ±10 original frames in *its analytical treatment*. The original Puy source CSV smoothing state is unverified. The ayu analysis uses original TXT with no additional smoothing applied in our scripts but upstream manual tracking may have altered frames. No result here is a fully calibrated prospective fish movement predictor. Trial labels may reuse fish; no population-level significance derived from 6 or 7 recording signs.

**Keep PR #248 Draft and main unchanged.** Next extension should be an independently measured, simultaneous fish movement/call source, or a small falsifiable mechanistic simulation with source-verified acoustic observation process, **not a pseudo-join between these two biological studies and the 66 OSF sound points**.

