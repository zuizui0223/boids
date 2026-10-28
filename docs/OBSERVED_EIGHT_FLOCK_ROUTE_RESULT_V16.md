# v16 observed result I — Repeated-release route memory did not transfer consistently across eight flocks

**2026-10-28 JST. Frozen exploratory independent public-data benchmark.** This is a new numerical evaluation on original animal GPS from Watts et al. (2016), not the paper's published hypothesis-test result and not an experimental manipulation by the present project.

## Source and reproduction

- Original *Misinformed leaders lose influence over pigeon flocks*: Watts, Nagy, Burt de Perera & Biro (2016), *Biology Letters* DOI [10.1098/rsbl.2016.0544](https://doi.org/10.1098/rsbl.2016.0544). Public GPS: [Zenodo 4943714](https://zenodo.org/records/4943714), data DOI `10.5061/dryad.508j2`, **CC0**.
- Original ZIP 272,270,105 bytes; published MD5 `ab0950ffebd924950632f727cd487c27` matched; independent SHA256 `7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa`. ZIP contains 559 recognized original GPS CSV members plus 178 AppleDouble `._` metadata sidecars, which were excluded.
- [Source-blind gate and schema tests](EIGHT_FLOCK_INDEPENDENT_SOURCE_CONTRACT_V16.md) and [pre-outcome fixed dual-timescale contract](DUAL_TIMESCALE_ROUTE_PREDICTION_CONTRACT_V16.md) were saved before target prediction outcomes were computed.
- [GitHub Actions observed-data run 40614826472](https://github.com/zuizui0223/boids/actions/runs/40614826472) completed **11/11 route-forecast no-leakage tests**, original ZIP integrity and registered eight-flock future-release route prediction. [Reproducible code](../validation_v16/route_memory_forecast.py) and [machine-readable all-flock numerical receipt](../validation_v16/results/slow_route_aggregate_v16.json). Workflow artifact ZIP digest `sha256:9f4010956b41b97cac8e697b73693d6c74bdaf4e8424251999d2f8c9f71672a9` refers to the **workflow artifact ZIP**, not the raw source or JSON inside.

## Predeclared design

- Eight source flocks, release numbered 1–15 (some end at 14); **historic source releases 5–8 only**, **future held-out releases 9–15**.
- Response = *first recorded outward crossing* bearing from the published Bladon release site at nine preselected 500–4,500m radial shells. No coordinates or timestamps were interpolated. Observed step ≤50m, UTC gap ≤1s, radial overshoot ≤50m. Neither original altitude nor possible GPS speed-unit ambiguities are used.
- **S0:** other-seven-flock circular historical bearing at each shell (flock-balanced population baseline). **S1:** this flock's prior-release route template (bird-balanced). **S2:** individual's prior-release template (historical-support-only group fallback). The same held-out target records are scored by all three models.
- Performance is wrapped circular bearing MSE in **rad²** (smaller better). Each release first receives a within-release score; each flock then an *equal-weight average across future releases*, followed by eight-flock mean. The independent sampling units are eight flocks, not 559 GPS files, 11.6 million recording rows or radial shells.

## Frozen primary and secondary outcomes

| Flock | S0 − S1: group historical advantage (rad²) | S1 − S2: individual historical advantage (rad²) | Future test releases |
|---|---:|---:|---:|
| 01 | +0.017559 | −0.007405 | 7 |
| 02 | +0.004063 | −0.000633 | 6 |
| 03 | +0.025938 | +0.000073 | 6 |
| 04 | −0.039308 | +0.032990 | 7 |
| 05 | −0.002118 | +0.000000 | 6 |
| 06 | −0.008798 | +0.000704 | 6 |
| 07 | −0.036040 | −0.003341 | 7 |
| 08 | +0.067053 | +0.001066 | 7 |

- **Primary group-history contrast:** `MSE(S0)−MSE(S1)=+0.00354346 rad²`, **4/8 flocks positive**, fixed-seed 10,000 whole-flock bootstrap 95% **[−0.01817089,+0.02696008]**. **Generalizable advantage NOT SUPPORTED.**
- **Secondary individual-history contrast:** `MSE(S1)−MSE(S2)=+0.00293174 rad²`, **5/8 positive**, bootstrap 95% **[−0.00284486,+0.01219310]**. **Generalizable individual-history improvement NOT SUPPORTED.**
- All eight flocks passed the predeclared structural score gate; no successful subset was selected after results. Source data quality, parsing and outcome restrictions are unchanged.

## Ecological and inferential meaning

The results reject the **strong claim** that a static route template from prior flights reliably improves prediction of later experimental releases *across all eight flocks*. This is **not evidence that pigeons lack spatial memory, navigation learning, leader-follower structure, or social interactions**. Historical route templates may fail because route choice depends on navigation context, the clock-shift experiment, environment, changing leadership, and source measurement uncertainty; these are possible explanations, **not demonstrated mechanisms**.

Several later releases had much larger error than others, including at identical radial shells. The treatment-by-release schedule has **not** been independently frozen and this study does **not** use it as an observed covariate; neither a condition-specific rescue nor a new post-hoc treatment claim is authorized on these same outcomes. Future conditional models require independently recorded experimental labels with a prospective endpoint.

The user programme's v13 private reward/social-choice **simulation** remains mechanistic known truth only, not vindicated by this field result. v15 original 2026 GPS short-step **negative** and v6/v8 results remain frozen. The next registered secondary layer is the independent same-source short-step fast-turn comparison, which must remain a separate endpoint and be reported regardless of direction.
