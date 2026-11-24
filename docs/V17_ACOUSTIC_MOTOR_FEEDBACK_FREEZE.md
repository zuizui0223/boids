# v17 — Acoustic motor feedback versus direct call response: independent 384-seed mechanistic test

**Frozen BEFORE any new v17 seed outcomes. Synthetic simulator only. Not fish field evidence.**
Date 2026-11-22 (JST). Parent verified work v16 on PR #248.

## Scientific problem and prior information
In v16 (new seeds 3000–3191), pre-cue low (<0.90 calling fraction at completed update 1000) predicted large pulse responses; 13 of 192 seeds low, 179 high. Among high, 168 had q=1 and 11 q=31/32: **call fraction is at its measurement ceiling**. We cannot interpret low versus high as an identified intrinsic acoustic susceptibility. The mechanism question here is more specific: **given the same natural low pre-cue state, does acoustic attraction during/after playback improve the pulse's additional calling beyond sound-perception-driven calling?**

## Exact prespecified design
- Same immutable v15 simulator `validation_fish_boids_v15/simulation.py` (SHA256 a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb), n32, dt .06, all steering coefficients unchanged. The model has no natural fish individual memory variable.
- Previously unseen simulator seed census **4000..4383, inclusive, exactly 384**. For each: initialize and simulate 1000 steps WITHOUT playback using default acoustic motor (5) and hearing-to-calling (3). At completion step1000, q = number of actively calling fish/32. **Enroll every seed with q<0.90.** The exact seed range and eligibility are frozen before viewing any of these 384 results. Do not substitute more seeds if few are low. All 384 pre-cue q values are retained in the source-safe receipt.
- From each enrolled checkpoint (same positions, velocities, binary calls and shared PCG64 RNG), run **six** arms to completed t=4040, then evaluate only the post-pulse window update indices **[1040,4040)**:
    * m5h3: acoustic attraction motor=5, hearing-induced calling=3; pulse vs no pulse
    * m0h3: **motor disabled from update1000 onward** with hearing-induced calling=3; pulse vs no pulse
    * m5h0: motor=5 but hearing-induced calling=0; pulse vs no pulse (structural negative control, NOT independent biological evidence)
  Every arm uses the same initial 1000-step checkpoint and exact same RNG state, external pulse 0.8 on [1000,1040) or absent. There is no additional stimulus or state transplant; no changes to positions or calling at t1000.
- Primary per-enrolled-seed estimand: D_motor = [mean_calls(m5h3, pulse)-mean_calls(m5h3, none)] − [mean_calls(m0h3, pulse)-mean_calls(m0h3, none)] in [1040,4040). All differences computed as **integer call totals before division by 32*3000**, preventing false signs from floating-point cancellation.
- **Only primary cohort**: all enrolled q<.90, not any retrospective filter on response or transition time. Primary across-seed equal-weight mean D_motor, median, positive/negative/zero counts; fixed paired seed bootstrap 10,000 draws, seed 2026112231, 95% percentile descriptive interval. If n_low<5, report prespecified SOURCE_SUPPORT_STOP for inference, but retain numerical results; do not add new seeds.
- Secondary descriptive: m5h3 pulse gain, m0h3 pulse gain and m5h0 pulse gain; absolute no-cue baseline call fractions, matched group convex-hull area (same window), group average velocity magnitude at split, split convex hull area, split perceived acoustic input average; pulse influence during [1000,1040), followup call >0.90 in [1040,4040), effect concentration top two, and fraction of old all-384 census eligible.
- Negative control: after pulse, m5h0 paired call traces should exactly match by common RNG, because calling probability is independent of positions when hearing weight=0. This is a **deterministic code property**, not a biological causal validation. A nonzero result is a SOURCE_CODE_STOP.
- Attribution: comparisons of motor 0 vs 5 are **interactions between model parameters and cue effect**, not a natural mediation effect because motor cancellation changes long-run geometry even in no-cue control. Causal statement is at best within the assumed simulation interventions.
- Full 384 prefix receipts, all eligible per-seed contrasts and raw time-series for six arms saved; report checksums and explicit code hashes. No raw animal data; all SYNTHETIC_ONLY_NOT_FIELD_RESULT.
- Main and PR stays Draft, no merge. Prior v12–v16 code and model-source bytes unchanged.
