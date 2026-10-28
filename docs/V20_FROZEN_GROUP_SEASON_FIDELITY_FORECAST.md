# v20-B frozen wild group/season held-out ecological fidelity prediction

Registered 2026-10-28 JST BEFORE reading any numeric value from the new public guineafowl group-season response columns. The v20-A verified source has object sDCEFGnu, 45 distinct group x season rows, 21 group IDs, 15 groups in at least two seasons and eight in at least three, zero missing values and zero duplicated (ID,SEASON). This is a derived eLife table, not original Movebank GPS.

## Frozen independent published source
Papageorgiou & Farine (2020), Group size and composition influence collective movement in a highly social terrestrial bird, eLife DOI 10.7554/eLife.59902. Pinned original author GitHub commit 15ea08ed10555beba227792f4ef106d87d52b6a4, file Computed_seasonal_measurements.Rdata, exactly 2717 bytes, Git blob sha1 3fe1e3245cb97026b03125582d5af14ab9fd5b39, independently computed SHA256 c6a534993e99f2cb324e9691ff7ec58095bf7cd7e82d7a38721f3575097cbb55. No original raw GPS is available to this workflow and no animal coordinates will be read.

## Primary new ecological outcome (not homing route)

Primary Y = published group-season variable fidelity, the authors' group space-use overlap between nearby days within a season. It is a derived group-level spatial persistence indicator (expected 0 to 1); it is NOT individual memory, foraging efficiency or ecological fitness. Chronological original old-season codes are C, D, E, F, G; only strictly earlier source seasons may inform predictions.

Two registered secondary outcomes, not substitutes for failed primary: natural log of positive AREA_SQM (estimated group core home-range area in square metres), natural log of positive speed_km_day (estimated group movement speed). All three report complete results and sign including negative. Transform values only when positive finite; a source-domain violation is a source STOP for that outcome, not a license for adaptive transformation.

## Identical held-out target support and source time direction

For each group g and season s with at least 1 historically observed same-group earlier season and at least 3 distinct OTHER groups' observed seasons strictly earlier than s, define exactly one future group-season target. Group eligibility is determined solely by ID and SEASON, not numerical response values. All model forecasts are calculated before referencing target Y(g,s) and evaluated on the exact same eligible group-season cells.

M0 (external historical reference): for each other group, average its earlier Y values (all past seasons strictly before s); then average those other-group means with equal group weight. Does not include current focal group at any season.
M1 (own group history): average Y(g,s0) across the focal group's earlier observed seasons.
M2 (pre-fixed partial pooling): predicted Y=(1-w)M0 + w M1, with w=n/(n+2), n=#earlier observed source seasons for focal group, fixed shrinkage kappa=2 before any values opened. For a single previous season w=1/3; with two, w=1/2. This is a simple demonstrator, not tuned on observed future outcomes. M0 and M1 are in the same transformed outcome scale for each registered target. No model has access to any other group's contemporaneous or future Y in season s.

Primary signed gain G = MSE(M0)-MSE(M2), positive indicating that source-independent previous group history adds next-season fidelity prediction after shrinkage. Secondary contrast H=MSE(M0)-MSE(M1) and shrink-vs-raw MSE(M1)-MSE(M2) (whether shrinkage prevents overtrust). Report all 3 ecological outcomes independently without selecting the most positive.

Metric: squared error in unitless fidelity scale for primary, squared log scale for secondary. Score each eligible future-season target, average within group ID, then equal weight across independent group IDs. Whole-group 10,000-seed bootstrap for 95% interval, RNG seed 20261028, report exact #groups, #held-out seasonal cells and number of groups with positive gains. No iid group-season p-value; do not call 15 groups 45 independent populations. Primary gate: at least 8 independent group IDs and 12 future-season target cells meeting above ID-only eligibility, otherwise stop without opening outcomes.

## Interpretation and limits

M0 is an external prior-season group-state baseline, NOT a climatological model: the file lacks independent climate/rainfall, resource availability and local predator fields. The source shares one ecological region across years. Positive G would mean *incremental future-group space-use predictive information* conditional on this particular previously published seasonal table, not proof of retained cognitive memory, social transmission, individual niche formation or 3D resource use.

If G is nonpositive or interval includes zero, keep the negative result. No retuning kappa, inclusion thresholds, season chronology, fidelity definition or alternative endpoint choice on this same opened source.

Previously frozen v13 synthetic, v15/v16 pigeon observed, v17 source, v18 all-14 stop and v19 conditional observed results are not modified.
