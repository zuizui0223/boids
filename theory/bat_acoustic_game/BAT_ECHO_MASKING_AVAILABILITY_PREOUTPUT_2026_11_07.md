# Independent-echo-loss bat memory boundary — 2026-11-07

**Source-motivated independent filtering model only.** No new bat measurements and no source-original 2026 MATLAB code replay. The eLife authors (Mazar & Yovel 2026, DOI `10.7554/eLife.105571`) ALREADY modeled echo masking/missing detections, multi-call memory and immediate collision avoidance. Original public source GitHub pinned commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89`, independently audited all seven selected original files in Actions 42339355443. This calculation is not a reproduction of their published obstacle clustering, wall tracking or cave exit outcomes.

## Why the previous all-echoes-available assumption is not enough

Previous standalone exact filtering theorem for a random-walk world position `x_t`:
`x_t=x_{t-1}+η_t`, independent `η~N(0,q)`; accepted echo `y_t=x_t+ε_t`, `ε~N(0,r)`. Averaging K last accepted source observations (assuming all available) yields
`MSE(K)=r/K + q*(K-1)*(2K-1)/(6*K)`. With K=5, memory helps against K=1 iff `q/r<2/3`. This is standard memory bias-variance theory, not a discovered real-bat biological threshold.

**New independent dropout law:** exactly K attempted sonar pulses at lags `j=0,..,K-1`; each independently produces a usable echo with probability `p`, regardless of target location or past availability. The bat's hypothetical estimator averages the `n≥1` actually returned original echoes, not the last K accepted echoes. If NONE is returned, it has NO position estimate; report that failure separately. Keep the current+past target random walk and the same q/r and r=1. This is a source-motivated toy **not the original nonindependent physical masker/jamming process**.

For an available subset S of pulse lags, `n=|S|`, the exact conditional position MSE is:

`MSE(S) = r/n + q/n² * sum_{h=1}^{K-1} [number of j in S with j≥h]²`.

The subset probability is `p^n (1-p)^(K-n)`. Conditional MSE given at least one echo is the weighted mean over all `2^K−1` nonempty subsets divided by `1-(1-p)^K`. Missing-all probability = `(1-p)^K`. These endpoints are **NOT the same**: never score a no-echo trial as an error=0, and never invent a collision/reward penalty for losing all echoes.

## Frozen matrix before output

- `K=1..10` emitted pulses (Mazar source default `ObsMemorySize=5` is a reference, not a calibrated optimum).
- `p in {1.0, 0.75, 0.50, 0.25}`.
- `q/r in {0,0.25,0.50,1.0,2.0,4.0}`, with r=1 by nondimensionalization; **240 fixed exact cases**, no search for favourable source signs.
- Exact enumeration, no Monte Carlo error or original flight data. At p=1, all 60 outcomes must agree exactly with the previously verified all-echo MSE formula. At p=.25,K=5, all-missing probability exactly `.75^5`; at p=0 (TEST fixture only), Pmiss=1 and conditional MSE undefined.
- Compute Pareto non-dominated memory lengths under `(all-echoes-missing risk, conditional localization error)`, using strict numerical tolerance 1e−12. Do NOT pick an 'optimal' K without measured relative cost of no usable echo versus stale target coordinates.
- Source-relevant physically interpretable predictions: static targets (q=0) can benefit from more successful memory observations, but if target mobility q/r is high, older observations can cost accuracy even when they strongly reduce all-echoes-missing events. These are *conditional theoretical contrasts*, not evidence of actual bat strategies.

## Claims, biases, and stops

Real masking can be spatially and temporally correlated, echo reliability can vary by distance and spectral similarity, bat position estimation may use clustering rather than arithmetic averaging, prey targets can accelerate and maneuver, and wall coordinates are static only after accurate ego-motion correction. Our independent p and random-walk q/r are not directly observed in original Goldshtein 2025, Hase 2026 or Molossus 2024 source data. The effect is a generic estimator frontier and likely known mathematically; ecological novelty would require calibrated measurement of p, q, r and independent task outcomes. Do not promote this source model to a new bat-specific universally valid law, actual species memory, prey capture mechanism, or a claim the original 2026 eLife MATLAB simulations were reproduced.

Run with GitHub CI, check source rights, exact non-dropout recovery, all-source-failure classification, and no new bat observations. Preserve the original source archives and Draft PR #36; freeze prior `batter` JAE/BE releases.
