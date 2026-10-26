# Boids → observed movement bridge: exploratory prospective-style pipeline (v4)

Date: 2026-10-26. The pre-existing `batter`, `odsp`, `mina`, `louis` manuscripts and all their frozen results are unchanged.

## Status

Previous v3 tested synthetic forward prediction only. This v4 benchmarks **empirical short-horizon vertical-transition policies** on public bat data as a first reverse-inference check; **it cannot estimate social Boids** from asynchronous GPS tracks. Its existence does not itself prove empirical success.

## Source and documented semantics

- Annotated *Tadarida teniotis* CSV for O'Mara et al. (2021), Movebank DOI: `10.5441/001/1.52nn82r9`.
- Bitstream: `a6a6db33-0aca-4902-a58d-f32980c1a3e1`, previous batter provenance 3,630,088 bytes, MD5 `e0f6faedfd1f21bac222d9da430ea5d8`, 9,873 rows.
- `W.Component` is annotated/modelled vertical wind; `height-above-msl` is native GPS MSL height; they must **not** be renamed AGL/actual flow ground truth.
- `animal-id × BatDay` is the grouping; transition requires 3 strictly ordered locations, both gaps 15–75 seconds, >=30 triplets per retained session.

## Predefined tests

M0: unconditional next climb state; M1: previous climb state; M2: previous climb state + W.Component class; M3: M2 plus shrinkage to same-individual other-session history. Climb state down/level/up defined by thresholds ±0.5 m/s; W bins ±0.05 m/s. Sensitivity: 1.0 m/s, and wind 0.15 m/s. Exact conditional pseudocount strengths are implemented in `empirical_transition_benchmark.py` (M0 Jeffreys 0.5; M1 12; M2 20; M3 30); no tuning to test data. Primary score: held-out log probability nats per valid transition; average within night then within individual. M3-M2 evaluated on exact same repeated-individual subset. Permutations shuffle labels of **entire nights**, preserve multiset of sessions per individual, 199 null replicates.

Holdouts: leave one session out; leave one *individual* out for M0/M1/M2. Comparing absolute average scores for M3 vs other models is invalid if evaluations involve different sets of eligible individuals; compare within matched subset.

## Primary claim boundaries

- A positive M2-M1 held-out delta supports incremental *prediction conditional on annotated wind*, not that vertical wind forces cause flight pattern.
- A positive M3-M2 (and positive null-calibrated contrast) supports repeatable individual-specific transition policy above pooled features, not memory or Boids social coefficients.
- GPS intervals may be too coarse to reconstruct turn-scale social interaction. Any new claim about separation/alignment/cohesion **requires synchronous 3D tracks** and detection of neighbors at relevant distance/time scales.
- This Tadarida data was the historical discovery/negative boundary in ODSP and batter, so the current endpoint is exploratory even if the split is prospectively coded. True external transfer requires independent datasets/species.

## Required falsifications

1. M2 vs M1 on heldout sessions and heldout individuals.
2. M3 vs M2 on matched repeat individuals with block-permutation calibration.
3. Vertical-speed threshold and wind-bin robustness.
4. Compare equal-individual weighting, not individual GPS fixes as pseudo-replicates.
5. If performance fails, report failures and do not retrofit gates or select new model terms from test outcomes.
