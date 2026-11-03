# v37 WATLAS published high-frequency red-knot source feasibility only

**2026-11-02 JST, SOURCE-ONLY.** This is a new independent species/telemetry method for Boids source admission, NOT confirmation of the Schiermonnikoog tide-phase result, NOT estimation of social steering.

## Public source and fixed original schema
- [Published WATLAS supplementary Additional file 12, Figshare DOI 10.6084/m9.figshare.26553440.v1](https://doi.org/10.6084/m9.figshare.26553440.v1); source API record 26553440. The original study [Bijleveld et al. 2022, Animal Biotelemetry DOI 10.1186/s40317-022-00307-w](https://doi.org/10.1186/s40317-022-00307-w) explicitly selected seven nonrandom tracked red knots around Griend on **2018-08-31** within one tidal cycle; the original 1/3 Hz localizations were averaged at 30 seconds for the published group movement/network example.
- Figshare original file bytes downloaded directly from provider API metadata, its supplied original MD5 (if present) compared with source bytes; separate SHA256 calculated. Never invent a raw file checksum or report independently verified time resolution from an edited resampling.
- Fixed required original columns: TAG, TIME (Unix seconds), X and Y (UTM zone 31N metres). Source-localization error fields NBS, VARX, VARY and COVXY must be present; require NBS≥3 and both original coordinate variances finite 0≤VAR≤5000 m² as a **quality diagnostic**. Preserve source TIME as Unix, do not reinterpret local `ts` field as UTC.
- No original tag identifiers, georeferenced coordinates or entire trajectories are committed, only source counts/quality receipts.

## Prior-only heading feasibility
Group original positions into 30-second UNIX bins by tag (published social-network resolution); do NOT interpolate missing bins. Heading from prior 30–90-second same-tag displacement (speed 0.2–30 m/s), independent next 30–90-second observed displacement for future outcome **eligibility** only. Pair different TAG at exactly a shared 30-second bin, within 50m Euclidean UTM distance; measure number of raw pair-bin positions and directed pairs with preceding headings for both animals and next-heading outcome for focal. Summarize individual tag count, raw/QC fixes, time bins, unique dyads, unique days, and qualifying pair-bin histories. No motor force fitted.

## Admission
For exploratory **within-one-tide** group-heading analysis, require ≥5 tags, ≥5 dyads, ≥200 directed prior-heading/future-target qualified pair-bin observations and localization quality verified. For independent multi-tide social-force confirmation, require **≥4 independent tidal cycles and connected group holdout**; the published 2018-08-31 one-tide subset cannot qualify regardless of raw near-pair count. A single high-frequency tide may still demonstrate source feasibility without proving generalized social Boids.

A positive near-neighbor heading correlation even from this source would be descriptive only and confounded with common tide/environment and localization error; future claims require timestamp-aware matched ghost controls, whole-dyad independent holdouts, and enough tide cycles.
