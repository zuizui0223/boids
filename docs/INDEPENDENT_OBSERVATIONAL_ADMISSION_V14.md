# v14 observational admission contract (frozen before raw data outcomes)

Date: 2026-10-28 JST. **Scope: independent public-data provenance and structure only.**

## Why v13 does not yet justify a wild-animal social-policy claim

The v12–v13 results are known-truth synthetic worlds; v6/v8 strong contemporaneous-partner tests in wild bats/pigeons did not pass. Do **not** refit those observed sources, select more favorable thresholds after reading movement outcomes, or call a short GPS track a species' ecological niche.

## Source register and priority

1. **Huang et al. 2026 pigeon synchronous GPS/IMU** (article DOI \`10.1186/s40462-026-00689-z\`; data record claimed by the publication \`10.5281/zenodo.21092705\`; code \`10.5281/zenodo.21098976\`). Use for *short-horizon interactions only* if independently retrievable raw files show actual sensor timestamps, valid coordinate and altitude references, paired individual co-positions and independent held-out groups. The publisher's paper alone does not prove raw archive accessibility or sensor precision.
2. **Mehlhausen-Franks 2025 repeated-flock horizontal GPS** (Dryad DOI \`10.5061/dryad.4tmpg4fp6\`). The published CSV is a merged **5 Hz representation** with repeated one-second UTC timestamp strings and a per-bird flight \`Counter\`; contains \`Latitude\`, \`Longitude\`, \`Bird\`, \`Loft\`, \`Date\`, \`Iteration\`, \`Layer\`. There is **no advertised altitude column**, and matching \`Counter\` across birds is **not sufficient to establish physical synchronization**. Suitable potential target: repeated-session *horizontal habitat/route-use* forecasting; NOT 3D/individual-memory mechanisms or contemporaneous partner forces.
3. **Calderón-Capote et al. 2024 bat longitudinal data** (Dryad \`10.5061/dryad.5qfttdzgj\`, Movebank links \`10.5441/001/1.282\`, \`.321\`, \`.322\`). Dryad has analysis files but original GPS requires separate Movebank acquisition and provenance. Candidate for cross-night individual/colony distributions, not automatically synchronous flight steering.

## Stage A: metadata + source admission, no ecological outcomes

- Fetch DOI-linked metadata; pin full API endpoint, version, record/file IDs, reported file sizes, checksum methods and licenses. **Absence, 403/404, or conflicts are an UNKNOWN/STOP, never a success.**
- Download the Dryad candidate CSV only when the published file ID is explicitly found, record raw bytes, SHA256, and compare byte size and source digest when one is supplied. Keep downloaded raw data out of the Git repository. For Zenodo, first enumerate source-listed raw archives and checksum/size. Do not automatically download unbounded multipart archives.
- Profile every row as the stated grain **bird × loft × flight iteration × position counter**; count missing values, duplicate keys, nonfinite/out-of-range coordinates, distinct individuals, repeated sessions per bird and time-string multiplicities. Distinguish spatial observation from derived leadership, group centroid, habitat and velocity features. 
- Flag potential inconsistent \`Counter\` time steps or sequence restarts and all within-flight split trajectories; do not co-register birds on \`Counter\` alone. Segment by \`Loft × Iteration × Bird\`.
- Do **not** estimate 3D niche, spatial competition, memory/learning coefficients, or social-force parameters from this preflight.

## Stage B: outcome-blind task admission before fitting

Only after Stage A is saved with identified hash/version and observed schema:
- (B1) **Repeated individual horizontal-usage prediction** requires stable Bird IDs with >=3 distinct flights and route/position support across train and test; split *whole flights* by chronological iteration, never fixes. Compare flock+route-progress+habitat against flock+route-progress+habitat+bird ID; all predictor features must be known at deployment and the same held-out target support must be scored. Since birds share release geography, clustered independent units are *flights/lofts*, not individual fixes.
- (B2) **Social steering prediction** requires independent raw subsecond timestamps with specified synchronization error (and distances in metric CRS) and actual neighboring birds with near **and** far geometries. With only rounded UTC seconds or reindexed \`Counter\`, DO NOT admit B2.
- (B3) **Three-dimensional occupancy** requires actual calibrated altitude (not inferred/hypothetical). Short homing flights alone do not establish an ecological feeding niche even if 3D data are present.
- A **network-rewiring transfer test** requires recorded changes of individual-to-individual association before outcomes. A fixed single flock membership cannot validate v13's rewiring mechanism.
- Do not score any of B1–B3 on source A until its independent contract, baselines, temporal/identity splits, null, uncertainty and stop conditions are committed. No post-hoc model rescue.

## Stage A executable and output contract

\`validation_v14/source_preflight.py\` fetches public repository API metadata, and optionally a bounded Dryad raw CSV for **structure only**. Run on GitHub Actions without committing raw observations. Save \`validation_v14/results/source_preflight_v14.json\` **as a temporary workflow artifact**, carrying source URLs, source file digests, row-level quality aggregates, admission decisions with reasons, and errors. Do not include GPS coordinates or animal rows in published JSON. Raw download is discarded at the end of the runner job.

A passed source probe is not evidence supporting a Boids ecological hypothesis. Previous v6/v8 outcomes stay frozen.
