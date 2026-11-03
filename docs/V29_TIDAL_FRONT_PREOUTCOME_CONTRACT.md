# v29 — Tidal exposure front, apparent synchrony and moving ecological niches

**2026-11-02. Status: pre-outcome observational protocol + verified *synthetic-only* known-truth implementation.** This addition does not revise or re-interpret any frozen v4–v28 endpoint. No wild GPS–gauge–LiDAR joining was executed for this document, and no observed tide-effect coefficient, p-value, Boids social-force coefficient or shorebird species-niche score is claimed.

## Ecological question and limited novelty

Can **moving environmental boundaries** organize synchronized movement without requiring agent-agent alignment; and does tidal **exposure history**, in addition to water height and phase, improve heldout movement predictions? Individual shorebirds following tides is already known (e.g. van Gils et al. *Ecology* 2006, DOI 10.1890/0012-9658(2006)87[1189:FIATSE]2.0.CO;2; WATLAS *Animal Biotelemetry* 2022, DOI 10.1186/s40317-022-00307-w). We test an additional prediction: **at matched water levels, ebb and flood need not be biologically interchangeable** because last exposure times differ.

This is a causal-mechanism *candidate*, not evidence that tides cause observed synchronization or niche partition. A common externally driven direction can produce apparent group alignment by construction even if the social steering coefficient is zero. Conditional differences between phases are associations unless changes in prey, disturbance, individual choices, and habitat exposure are adequately measured.

## Public independent field sources (not downloaded or merged here)

1. **Oystercatcher GPS**: INBO/Sovon/UvA-BiTS/Movebank study 1605799506; `O_SCHIERMONNIKOOG`, 2008–2014, 43 tagged birds; official [INBO IPT v1.3, 2026-07-27](https://ipt.inbo.be/resource?r=o_schiermonnikoog&v=1.3), DOI [10.5281/zenodo.10053970](https://doi.org/10.5281/zenodo.10053970). Its standardized Darwin Core release has **171,132 records** and is deliberately *downsampled to the first GPS fix per hour*. Official source license CC0. These **are not 171,132 instantaneous speed measurements**, independent animals, feeding observations or simultaneous social encounters. The earlier original GPS archive may provide denser fixes, subject to independent admission.
2. **Measured water heights**: RWS Waterinfo, Schiermonnikoog station, ten-minute measurements relative to **NAP metres**. A published independent source describes the matching **1982–2022 station series** in `water/water_schiermonnikoog.txt` from [van de Pol (2024) Dryad 10.5061/dryad.wm37pvmth](https://doi.org/10.5061/dryad.wm37pvmth), but its **complete archive is ~1.43 GB**. The 10-minute series has **not** yet been extracted or independently checksum-verified here. Alternative original RWS historical export is permissible after documenting release/sha/time zone.
3. **Patch elevation/gradient**: site-matched LiDAR DEM (e.g. AHN 2014 in the same Dryad package). Dutch RD New **EPSG:28992** x/y in metres, elevations in **NAP metres**. A GPS fix needs a **geospatial join to actual measured dry/underwater topography** and a measured local gradient. No proxy derived solely from the bird's position or tide is substituted for a DEM.

Historical Dutch gauge local time is **not assumed to be UTC**. Confirm the original station timestamp convention, DST treatment, gauge datum, and shoreline phase lag before any real join. If an input cannot be authenticated, the field claim is **NOT ADMITTED**.

## Mechanistic definition

Let tidal height in NAP metres be `h(t)`, patch elevation `z(x,y)` in the same datum, and local coast-normal magnitude of slope `s(x,y)` in metres/m. Define a first-order *signed* cross-shore front distance as `(z-h)/s` (positive currently exposed). This is a local-plane approximation, **not** an exact shoreline geodesic. `exposed=1[z>h]` measures possible exposure, **not prey, foraging or local accessibility**. Exposure age `a(x,y,t)` equals elapsed hours since the latest rising-water-to-dry crossing of `h(t)` below `z`, found entirely within a 15-hour lookback. If the patch is wet or no crossing was observed, age is **unknown**, not zero.

Phase is a 20-minute trailing change in sea level: positive = flooding, negative = ebbing, near-stationary = 0 (turning). Matched-water-level pairs may have different phase and exposure age. The retrospective gauge interpolation uses adjacent readings and must **not** be advertised as a leakage-free real-time forecast. Prospective prediction would require an independently issued, time-stamped tide forecast available before each animal fix.

## Nested observational prediction design

Primary response from consecutive GPS positions: `log1p(horizontal displacement km/hour)` where the geodesic is replaced by distance **after verified EPSG:28992 projection**; accepted fix intervals 0.5–2.0 h, rejection threshold 120 km/hour (flagged as implausible *displacement*). This is not instantaneous flight speed and not a measure of foraging reward. Train and test units are time-blocked full **weeks** in UTC; first 70% train, one full week purged, remainder heldout. At least 8 distinct weekly blocks are required. All standardization and coefficient fitting use training only; models are ridge with fixed penalty, matched rows across M0–M2; evaluate squared prediction error equally per animal, not per raw fix. Document overlap of animals, seasons and habitats across train and test. Alternate independent holdouts by island/individual are separate future objectives.

- **M0**: measured tide height and its square; exposed mask; local DEM elevation; site x/y; 24-hour UTC phase controls. No hysteresis terms.
- **M1**: M0 + ebb/flood/turning phase, height-by-phase interaction, trailing height-change rate. This tests *same-height hysteresis beyond simple tide height*.
- **M2**: M1 + estimated front distance, age since exposure (capped), missing-age indicator and an explicitly fixed `exp(-age/1.5h)` basis. This is a **candidate basis, not an estimated physical time constant**; a future fully specified independent confirmatory study must freeze/tune the timescale using training data only.
- **M3**: M2 + social movement force. **NOT ADMITTED** in this hourly-downsampled source: requires verified concurrent sub-minute individuals, positional accuracy, and real-neighbor-vs-time/space-shuffled ghosts. WATLAS Wadden Sea high-frequency tags are a possible *separate* source, not an interchangeable replicate of Schiermonnikoog GPS.

A robust pattern should occur at comparable heights within animals, survive day/night, season, site and tidal-range restrictions, plus preannounced identity/weekly-block bootstrap intervals. A positive M1 or M2 lift does **not** establish causal front following until observed directions align with the moving front and time-varying prey/access controls. A positive M3 requires excess versus ghost control, not simply comparing social vs own history.

## Executable v29 known-truth result (not an observed biological result)

`validation_v29/tidal_front.py` synthesizes 90 days of 10-minute sinusoidal-and-amplitude-modulated tides, 12 hypothetical animals, and a response rule with an **explicit positive 1.5-hour exposure-age effect**, and no social forces. The week-block holdout uses 16,704 training and 6,624 testing animal-response rows (14 calendar week blocks; one embargo week).

| Model | Heldout equal-hypothetical-animal MSE | What is built into the generating world |
|---|---:|---|
| M0 height/geometry/UTC | 0.02077745 | Incomplete because omitted phase and age |
| M1 + phase | 0.01070983 | Phase effect is deliberately in the truth |
| M2 + exposure history | 0.00814345 | Exposure-age effect is deliberately in the truth |

The environment-only schematic has **mean heading resultant 0.9705** under synchronized externally imposed heading and **0.1915** after independently randomizing phase. **Social steering is exactly zero by construction.** These are *not* measured flock synchronization, evidence for prey movement, or fitted Boids coefficients. A separate no-exposure-effect negative-control simulation is included. 9 local regression tests cover UTC/datum requirements, gauge-gap rejection, equal-height hysteresis, unknown exposure crossing, data-ingestion schema, environmental synchrony and model/negative-control behavior.

### Reproduce

```bash
python -m pip install -r requirements.txt
PYTHONPATH=validation_v29 python -m unittest discover -s validation_v29 -p 'test_*.py' -v
python validation_v29/tidal_front.py --output validation_v29/results/tidal_front_known_truth_v29.json
```

### Run on **independently sourced and joined** field inputs

The tide CSV must have `timestamp_utc,water_level_nap_m`, strictly ordered and with gaps ≤30 minutes for interpolated events. The GPS CSV must have `individual_id,timestamp_utc,x_rd_m,y_rd_m,elevation_nap_m,slope_m_per_m`, all with verified original data dictionaries/coordinate transforms. These are **processed input fields**, not the unmodified INBO raw schema. An external source-only receipt and transformation audit is required before treating an output as source-verified.

```bash
python validation_v29/tidal_front.py \
  --gps-csv YOUR_INDEPENDENTLY_JOINED_GPS.csv \
  --tide-csv YOUR_INDEPENDENTLY_VERIFIED_UTC_RWS_NAP.csv \
  --output local_retrospective_v29.json
```

The observational script makes only a retrospective M0–M2 *association and predictive* comparison; its output explicitly says `caller_supplied_*_unverified_bytes` unless a separate source-manifest contract is satisfied. Its intended use is offline; keep original animal coordinates out of the repository. **No real empirical score is in this PR.**

## Follow-on ecological endpoints after admission

- **First independent endpoint:** Within-animal and same-water-level ebb/flood differences, verified against each tide cycle and season, for cross-shore displacement direction as well as speed.
- **Second:** M1 vs M2 heldout increment in movement with observed dynamic exposed area; DEM-derived accessible-patch masks and tidal lags are crucial.
- **Third:** Whether social information adds *conditional* prediction beyond a common moving habitat front, on original synchronized WATLAS tracks with contemporaneous and ghost-neighbor controls.
- **Fourth:** Compare multiple shoreline bird species' conditional space-use distributions **at the same tidal phase and available surface area**. A one-species GPS file cannot establish species-niche separation.

**Novelty boundary:** Tide-following itself is an established shorebird phenomenon; the proposed contribution is a *predictive separation of height, phase, dynamic accessibility, and residual social effects*, and potentially an emergent moving-niche interpretation if independently observed and replicated.