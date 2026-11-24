# v27 pre-result: collective-velocity autocorrelation versus information-age retention

**2026-11-24 JST; frozen before any original v27 group-state autocorrelation outcomes.** This follow-on is openly motivated by already-observed original v24 and v26d fish movement information-age curves. It does NOT independently rediscover the association and it does NOT establish causal fish interaction.

Three observed movement sources give different retained predictive MSE advantages for other-fish movement aged 0.2 seconds: Puy black neon tetra I=.322/.221 (short/delayed), Niizato ayu I=.432/.440, exploratory MacGregor stickleback I=.783/.777. A falsifiable competing explanation is the **time persistence of group mean velocity**, independently of fish-to-fish transfer.

For every original study recording at the exact time roster already used in its frozen age forecast, define U(t)=mean_i [(XY_i(t)-XY_i(t-s))/(s/FPS)], where native s=5 at 50fps for Puy, s=3 at 30fps Niizato, and s=5 at 25fps MacGregor. Calculate **centered 2D vector correlation** C(age) at ages {0.2,1,2} seconds, comparing U(t) with U(t-age) on identical source t rows. Center each vector by the mean across eligible times and compute covariance-dot-product divided by the product of both centered vector norms. No resampling, time-shifting, SDE fitting, prewhitening, background group motion inferred or fish future targets opened by this v27 computation.

Source exact admission:
- Puy: all six 2024 native source recordings, original provider MD5, original frozen v8 source indices, 50fps, age frames 10/50/100.
- Ayu: seven original source Git blobs at pinned Niizato commit 158e8d7ebdef73752da63192ee36e3a099dd5dfa, unchanged 30fps and source t>=66 frozen v24 cohort, age frames 6/30/60.
- Stickleback: EIDC 2021 original source 01.txt,02.txt,105.txt at frozen original SHA, last-column frame +1 verified, 25fps, missing XY exclusions exactly the v26d common input/output time roster, **6966 / 8015 / 5567** eligible source times, age frames 5/25/50; three files **not verified three biological shoals**.

Any source, identity, timestamp, finite predictor, cohort count, header, group-velocity-variance or SHA mismatch => SOURCE_OR_COHORT_STOP with no biological conclusion. Never reselect fish timepoints after seeing correlation. Report all 3 lags, per-file correlations and equal-recording source mean, no population-level p or 3-taxon quantitative pooled meta-effect. No raw original fish coordinates or timestamped tracks to repository.

**Decision rule frozen before results:** the simple shared-state-persistence *ordering* explanation predicts stickleback mean C(0.2) should exceed both tetra and ayu, whose normalized predictive retention at 0.2 was lower. If not, describe ordering FAIL rather than fitting alternative autocorrelation lags. A positive ordering is only consistency, not proof: a latent externally driven process can create both C and predictive retention without fish-to-fish causal influence. Differences in source tracking smoothing, model geometry and swimming context remain uncontrolled.

All prior original source forecasts unchanged. No acoustic calling events; PR #248 Draft, main unchanged.