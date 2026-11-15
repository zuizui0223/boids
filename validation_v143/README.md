# v143: original six-site source time niche + uncalibrated tide gauge proxy

Original source in California: Kim et al. 2025 DOI 10.3354/meps14910; publicly retrievable original 60 workbook Dryad version 7 doi:10.5061/dryad.q2bvq83sw. Source origin and 160,166 nominal hours plus 278 Off effort and 43 Noise logs were fully read in v142.

This incremental investigation covers **2019-04-01 00:00 to 2019-08-01 00:00 UTC**, with deployments active at six recording sites MB01, MB02, CI01, CI02, CI04 and CI05 (two sanctuary areas). Verified original presence of each acoustic chorus is obtained from start/end cells. Site deployment intervals are used solely for NOMINAL recording opportunity, and explicit Off effort and Noise time intervals are separately removed in a sensitivity analysis. Outside-effort time is never set to observed zero.

Astronomical solar altitude is calculated at the original hydrophone coordinates and actual UTC center-of-hour using Astral 3.2; fixed primary day/night cutoff is -0.833 degrees, secondary -6 degrees. This is substantially more defensible than fixed 06:00–18:00 clocks, though acoustic-detection audibility is not fully validated.

Physical high/low water is **from a different site**: NOAA CO-OPS verified hourly_height, April–July 2019 UTC, nearest among four v141 coastal reference gauges. MB01/MB02 use Monterey; CI01/CI02/CI04/CI05 Santa Barbara; geometry is not an offshore tidal-phase or amplitude calibration. Sensitivity shifts -1,0,+1 hour are computed for reference gauge hours, but are NOT a justified correction to hydrophone tides. We reject cross-coast meta pooling.

Three separate observation effort denominators (nominal, exclude Off effort, also exclude Noise) and two solar thresholds are crossed with site, five chorus classes and ±1-hour proxy tide shifts; any 2×2 where fewer than 20 opportunities, fewer than 5 presence and fewer than 5 non-presence in any cell is **STOP**. Even admitted 2×2 contrasts are **descriptive continuity-corrected odds contrasts, with no standard errors, p-values or causal interpretation**. These are correlated hourly recording events in only six recording points, not six independent studies.

The 2019 April–July observation window was fixed before running the new code, using site metadata and only external source audit information rather than selecting significant biological results. Full original per-hour data are not redistributed; only aggregation, original source-digest and code.

**DO NOT treat these as fish abundance, individual movement, actual offshore tide, causal tide×solar interactions or global meta effects.**
