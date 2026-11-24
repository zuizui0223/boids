# v44 supplementary: control-specificity and scale sensitivity of the v43 predictive hierarchy

2026-11-25 JST. Post-result descriptive analysis, not an independent replication. The 25 held-out evaluation units (6 tetra recordings, 7 ayu recordings, 12 stickleback shoals) come from v42 and v33b, with overlapping training folds; tetra/ayu independent biological group identities remain unverified. No new raw trajectory fit. All signed increments retained.

Run the v43 reaggregation on its three pinned original ZIPs, then:
```sh
python validation_fish_school_v44/control_specificity.py v43_reaggregation.json v44_controls_receipt.json
```
Input v43_reaggregation.json SHA256 dac5b632f676920700b6410d109c9684ccd26a42dcc9d2d910c48615d8769157 from local regeneration/receipt. The local control calculation executed against the saved v43 source-safe scores, seed 20261125, 10000 paired resamples. Dg = loss(G_geometry) - loss(GLOBAL); all 25 Dg positive in both horizons. For each contrast C calculate 100*mean(C)/mean(Dg), independently by study and horizon. Alternative denominator loss(G_geometry) tests interpretation; ratios are order-dependent, not causal information shares. All seven contrasts and both scales included in code/output. The primary descriptive result is delayed minus short difference; bootstrap over existing units is not independent-sample inference.

| C | Tetra change pp [descriptive 95%] | Ayu | Stickleback |
|---|---:|---:|---:|
| GLOBAL−NEAR | −8.1669 [−8.8968,−7.5889] | −6.4315 [−9.2336,−2.4519] | −15.6730 [−18.7175,−12.5444] |
| GLOBAL−FAR | −7.4357 [−8.2868,−6.7429] | −5.8084 [−8.3493,−2.0417] | −10.4624 [−12.4468,−8.2587] |
| GLOBAL−ROT | −0.2399 [−0.3420,−0.0843] | −0.0210 [−0.0783,+0.0370] | −0.5836 [−0.8845,−0.2727] |
| GLOBAL−STALE | −0.8245 [−1.2007,−0.5431] | −0.6166 [−1.1772,+0.4808] | −14.3686 [−16.4342,−11.9807] |
| ROT−NEAR (mapping) | −7.9270 [−8.6843,−7.3385] | −6.4105 [−9.2035,−2.4359] | −15.0893 [−17.9133,−12.1410] |
| FAR−NEAR (proximity) | −0.7313 [−1.1093,−0.4539] | −0.6231 [−1.3218,−0.0233] | −5.2106 [−6.5794,−3.7196] |
| STALE−NEAR (freshness) | −7.3424 [−7.9990,−6.7253] | −5.8149 [−8.0733,−2.8864] | −1.3044 [−2.7576,+0.1805] |

Near, far, mapping and proximity changes remain negative under every single existing heldout-unit deletion in each of three studies. Mapping decline appears in 6/6, 6/7, 12/12 units, proximity in 6/6, 4/7, 12/12; do not call 25 independent biological shoals. Freshness differs in stability, especially stickleback, so no universal freshness claim.

Critical denominator sensitivity: normalizing NEAR increment by G_geometry MSE changes the delayed-short contrast to −1.4477 pp in tetra, −0.7344 in ayu, +0.7098 in stickleback (0/12 stickleback negative). Mapping similarly −1.4061, −0.7307, +0.6894. Therefore the reproducible finding is *relative to the global increment*, not absolute or baseline-normalized decay of local predictability. Local and global increments may both increase. The matched controls test predictive specificity and are not physical interventions; spatially correlated common drivers and trajectory filtering remain possible explanations. 
