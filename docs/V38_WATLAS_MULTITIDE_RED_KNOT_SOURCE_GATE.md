# v38 — PRE-OUTCOME WATLAS repeated-tide red-knot original SOURCE gate

2026-11-02 JST. SOURCE admission only, not a hypothesis-effect test and not social force estimation. Related v37 published one-tide supplemental source failed the 200-directed-pair and multiple-cycle thresholds. **Do not relax either threshold after seeing the new source.**

## Independently published source
[Bijleveld et al. WATLAS Additional file 14, Figshare DOI 10.6084/m9.figshare.26553446.v1](https://doi.org/10.6084/m9.figshare.26553446.v1), provider API article 26553446. Contains original red-knot tracking positions for home ranges, including TAG, TIME Unix seconds, X/Y UTM31 metres, NBS, VARX, VARY, COVXY, provider `tideID` (tide cycle ID), `tidaltime` (minutes since high tide) and `waterlevel` (cm at West-Terschelling). These are source fields; **waterlevel datum/local inundation is not independently verified**. Do not treat article 14 as statistically independent of article 12 if animal cohorts overlap.

## Strict original source and quality admission
Download only the original CSV file identified by the publisher's Figshare metadata; verify supplied original MD5 when present, bytes, and calculate SHA256; maximum 150,000,000 bytes, STOP otherwise. No raw bird IDs, coordinates, timestamps, per-tag trajectories or location error vectors are committed.

Require all source fields listed above. Admission for a localization: finite coordinates and Unix timestamp (2017–2023 metadata plausibility), NBS≥3; original VARX and VARY must be finite 0..5000 m², local UTM31 X/Y coordinate bounds. Preserve original tideID, `waterlevel` and `tidaltime` as source metadata; never invent an exact time-to-UTC transformation from `ts`.

Group by tag/30-second Unix time bin, mean recorded original coordinates within bin, tideID=unique original tideID for that bin only, else unavailable. Only original prior 30–90sec own/neighbor movement headings (speed 0.2–30m/s) are candidate predictors; focal next 30–90sec heading only used to count eligibility. Pair different tags in same 30s bin within 50m; keep source tideID only if both contemporaneous animal records have identical source tideID. Count raw pairs, directed prior/next-qualified pairs, distinct tags/dyads, tide cycles and number of qualifying dyad-time observations per cycle; no observed social effect fitted.

**Eligibility for a prospective future multi-tide social-field test**: at least 200 qualified directed pairs total, ≥5 contributing tags, ≥5 dyads, **at least four different original tideID cycles each with ≥10 qualifying directed pairs and ≥2 dyads**. This only permits proposing a separately preregistered actual-vs-ghost social-neighbor forecast; even passing does NOT identify social force and requires event independence and calibration of source localization error.

If some source or tideID fails: hard `SOURCE_STOP` or `NOT_ADMITTED` (not ecological absence). Original `tideID` units/coverage may be source limited by the home-range sampling used in the paper; do not simulate extra localization cadence.
