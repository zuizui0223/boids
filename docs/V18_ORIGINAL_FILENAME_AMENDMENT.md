# v18-A0 source-native filename grammar amendment — before any CM GPS outcome opened

**Date: 2026-10-28 JST.** Original author source identity/format correction only. **All original frozen prediction endpoints, 14-pair requirement, site controls, circular shells, TR→CM holdout, and no-rescue policy remain unchanged.**

The initial strict filename grammar in [v18 preregistration](V18_FROZEN_14PAIR_MEMORY_FORECAST_CONTRACT.md) accepted only `pair/solo` and `Nocheck`. The **source-only** [GPS filename audit run 40626226608](https://github.com/zuizui0223/boids/actions/runs/40626226608), which parsed file names only and no coordinate/time/turn outcome records, found **407 recognized** and **19 original filenames** containing `Checked` or `pair*`. The 19 are not missing source, nor a random list of failed GPS forecasts; these tags are explicitly present in original author-controlled filenames. The author-supplied `CM tracks to stats.R` describes planned-solo flights when the two partner birds joined, and recodes `pair*` to actual `pair`.

Therefore the **pre-outcome** repair now recognizes exactly:
- mode: `solo`, `pair`, `pair*` (map `pair*` to actual `pair`, preserving its source social nature);
- quality/metadata: `Nocheck` **or** `Checked` (include BOTH; no outcome selection);
- all other bird, site, TR/CM, date and track-label parsing remains strict;
- **every one of the 426 original CSV files** must now match this original documented grammar, or source admission stops.

All 19 previously unknown filename basenames and their provenance are recorded in [v18 source-only filename gate](../validation_v18/source_filename_gate.py) and its first successful audit CI; none contains GPS coordinates or a scored response. This amendment is a correction to source-file parsing **before any later CM route outcome was examined**. It must not be mistaken for a statistical choice based on forecast performance. Existing v6/v8/v15/v16 studies are untouched.
