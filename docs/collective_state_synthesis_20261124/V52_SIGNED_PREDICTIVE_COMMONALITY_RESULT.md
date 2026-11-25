# v52 — signed predictive commonality across four fish sources

2026-11-25 JST. Post-v51 descriptive score reaggregation, not new fitting, independent confirmation, or a preregistered new biological hypothesis. Original v51 primary residual and all prior failed gates unchanged. Source-safe actual heldout losses from three v51 original CI artifacts and exact locally executed stickleback v51 receipt, all SHA256 pins checked. Original 6 tetra recordings, 7 ayu recordings, 8 zebra trials, 12 stickleback true shoals (84 recordings). Tetra/ayu distinct biological shoal IDs unverified, all study folds share training data. All comparisons study-specific; no pooled effect/p-values.

## Definition and exact checks
Let B, BG, BL, BGL denote held-out MSE of four nested predictive panels. Define
- T=B−BGL: total incremental gain beyond own-history/geometry.
- U_G=BL−BGL: global block conditional additional gain.
- U_L=BG−BGL: local block conditional additional gain.
- C=B−BG−BL+BGL: signed overlap (positive subadditivity of gains; negative complementarity of gains).
- T=U_G+U_L+C, PhiG=U_G+C/2, PhiL=U_L+C/2.

C is a signed predictive-loss commonality term, NOT information-theoretic PID, direct evidence of common environmental forcing, social transmission, or causal redundancy. All terms may be adverse/negative. No clipping. Because the two-order gain allocation is exactly half the overlap plus a conditional increment, R=100(1-b)/(1+b) for b=(U_G−U_L)/T, using ratios of equal-unit means. R and b are algebraically redundant, not two independent results.

Original raw-local encoding Lraw=near3 mean−focal velocity=G+L, residual L=near3 mean−other-fish mean. The full BGL spans are the same but standardized Ridge10 is not generally invariant to basis. The BL panels estimate different predictors. B includes group geometry.

For both encodings and all nine existing states, preserve original loss rows. Normalize in two ways: (i) ratios of equal-unit mean gains to mean T, only if each unit has positive T in both horizons for change comparisons; (ii) equal-unit mean of each unit's signed gain divided by its original B loss. 10000 paired whole-unit bootstrap draws using NumPy default_rng(20261125), descriptive only; delete-one-existing-score reaggregations, no refitting. Per-unit changes in share are based on each unit's own denominator. A ratio of means is not the mean of ratios. 72 encoding×study×state combinations, 60 fully admitted; 12 STOP (ayu P_high, V_low_P_low, V_high_P_high; zebra P_low, V_low_P_low, V_high_P_low, both encodings). All signed gains and all available per-horizon shares retained. No denominator rescue. Full cohort T positive in every unit at both horizons. Replayed all previous native PhiG/PhiL/G0/L0 vectors and exact additive identities.

## Full cohort, direct near-focal encoding
All entries percentage of joint total improvement T, ratios of equal-unit means. Short 0–.2s, delayed .6–.8s.

| Source | U_G short→delayed | U_L short→delayed | C short→delayed |
|---|---:|---:|---:|
| Tetra | 6.2225→22.9673 | 7.5668→.0193 | 86.2107→77.0134 |
| Ayu | 15.3126→36.1655 | 6.0043→−.0435 | 78.6831→63.8780 |
| Zebrafish | 35.2065→37.2936 | 2.2267→1.9144 | 62.5668→60.7920 |
| Stickleback | .1820→1.7675 | 32.0469→23.9471 | 67.7711→74.2854 |

C positive in all 33 units in both horizons, mean share >60% in every source/horizon (direct encoding only). Changes differ: C decreases in tetra/ayu/zebra but increases in stickleback. U_G share increases in all four (31/33 positive), but zebra interval crosses zero. U_L share decreases in all four (30/33 declines), but zebra interval crosses zero and one delete-one reaggregation is positive.

| U_L change pp | Declining units | Descriptive paired 95% | Delete-one range |
|---|---:|---|---|
| Tetra −7.547481 | 6/6 | [−8.168853,−7.055399] | [−7.726979,−7.306372] |
| Ayu −6.047838 | 6/7 | [−8.489279,−2.547637] | [−6.674080,−4.660130] |
| Zebra −.312271 | 6/8 | [−2.090854,1.350490] | [−1.034435,.156651] |
| Stickleback −8.099830 | 12/12 | [−9.430892,−6.548407] | [−8.584292,−7.498462] |

The direct conditional U_G share increases +16.744796, +20.852948, +2.087077, +1.585521 pp respectively; counts 6/6,7/7,6/8,12/12. Zebra interval [−1.986310,6.436728]. The C change is −9.197316, −14.805110, −1.774805, +6.514309 pp respectively. No universal decrease in overlap.

## What survives encoding changes, and why
Residual encoding U_L shares are 7.566763→.019256, 6.004015→−.043978, 2.226561→1.914377, 32.046904→23.947070, in source order above. Every source's two estimates at both horizons differ by less than .0005 percentage points. This near-invariance is expected from the unchanged BG model and identical joint linear spans (small ridge basis effects), NOT independent replication. In contrast, C under residual encoding is −7.573391→6.135543 (tetra), −4.905975→11.889009 (ayu), −.921215→−.880212 (zebra), −19.180177→−16.532364 (stickleback). Changing local feature coordinates changes overlap and global conditional gain radically. Do not claim encoding-invariant allocation. Max absolute difference in per-unit joint gain, as percentage of direct joint gain, by source: .00230313%, .00713505%, .00316715%, .00024972%. Thus the almost-identical joint models do not imply identical allocation.

Base-loss normalized U_L (mean within-unit % of B loss), direct encoding: tetra 1.460318→.003447, ayu .579188→−.011892, zebra .236707→.211966, stickleback .875269→1.617941. Stickleback 12/12 increase on this scale. Hence the result is decreasing **relative conditional local share**, not universal loss of absolute or baseline-normalized local predictive value. U_L/T=L1/(G0+L1) is also a monotone transform of the earlier global-first L1/G0 when G0>0; it is a robustness/interpretability audit of existing results, not a new independent line of evidence.

## Reproducibility
Executed locally: `python validation_fish_school_v52/v52_overlap_audit.py <directory>`. The Git blob 07f0a5ecc6ad6ddff9e1337b38716d8e37e45417 exactly matches the executed script (SHA256 bb469f77606954acdb4f0bcaadf4264f62ee5cc56a944b4e3e721556351da2cd). Input v51-tetra.zip, v51-ayu.zip, v51-zebrafish.zip and exact v51_stickleback_raw_local.json; all original ZIP/JSON hashes pinned in code, source receipt for stickleback SHA256 2755ea333588f7a1484198c1862df9d098cd46a16d8947a59d61587d803cdb7a. Full executed result v52_overlap_audit.json SHA256 ea94fb255c49e7c79fef50648c65ed8ffb32645b4f3eef513b1c9c23bbf82da5 (3,688,596 bytes), contains signed per-unit effects and full state/denominator sensitivity. No raw trajectories or coefficients. 
Main unchanged, draft PR #254. Scientific ceiling: quantitative within-study conditional predictive hierarchy; genuinely new independent source and common-driver/trajectory preprocessing controls needed to identify mechanism. Future prospective test should freeze U_L/T and its base-normalized companion before outcomes, not choose encoding or denominator from observed signs.
