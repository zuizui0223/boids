# v46 — PRE-OUTCOME: authenticate original bird GPS coverage by historical AHN2 NAP substrate

**2026-11-05 JST, SOURCE-ONLY.** v44 and v45 prior original results are already known. This stage uses original GPS **positions as source availability metadata** (not their tide-associated outcomes) and official AHN2 original WCS DTM. It neither joins nor evaluates 2010–2012 RWS tidal phases, and cannot test the wet/dry front hypothesis yet.

## Question

Can the publicly available AHN2 (2007–2012) georeferenced DTM actually cover the *destination positions of original 2011/2012 oystercatcher movement triples*, for enough independent birds/weeks to support a subsequent frozen **destination-relative-to-newly-exposed-substrate** hypothesis?

Source: original Zenodo `O_SCHIERMONNIKOOG` and `O_AMELAND` GPS gzip (2010,2011,2012) with provider MD5 and SHA256 verification and fixed source lat/lon study envelopes; official original AHN2 **DTM not DSM** WCS 1.0.0 `e96b10b9-e964-414c-958c-57a9dbe24e62` via AHN Dataroom, RD New EPSG:28992 horizontal and agency-described NAP vertical datum, original 2007–2012 collection. No original GPS coordinates, tag identifiers or exact times committed.

### Define spatial tiles using 2010 source positions ONLY

1. Read original GPS source event-id/visible/individual/local timestamp/finite WGS84 coords, first earliest original fix per native UTC hour and original geographic gate, with **no original tide phase or direction target used in selecting cells**. Native source clock UTC-vs-GPS ambiguity remains; a constant offset does not meaningfully change spatial location but original hourly selection can shift slightly.
2. Project original 2010 hourly fixes to EPSG:28992. Partition the Dutch RD grid into **2km × 2km** cells (integer floor of RD easting/2000 and northing/2000, anchored at origin, no data-dependent grid offsets).
3. Select exactly **K=8** 2010 cells **per island** ranked by count of unique `(source_bird, calendar_day)` observations per 2km cell, then total hourly fixes; ties broken by ascending integer cell coordinates. This reduces a few frequently sampled individuals dominating site selection but does not use 2011/2012 heldout locations or tide movement results. Fixed selection is observational coverage optimization, not ecological habitat selection.
4. For every selected cell, request one source official AHN2 WCS GetCoverage GeoTIFF of exactly 256×256 pixels covering 2000×2000 metres; 7.8125m derived source resolution. Bound each network response to 3MB and never download an entire AHN tile. Verify original source CRS EPSG:28992, first DTM height candidate band Float32, second normalized 0–1 auxiliary source field. Its formal mask/alpha semantics remain **unverified**. Keep only first-band finite −20..+50m and second-band ≥0.999; no fill of water/nodata.
5. Source land/tidal-height **coverage QA**, not actual physical exposure: record valid pixels, valid cells with first-band −3..+3m NAP, and original datasource SHA256. *Never* interpret all valid 2km cells as flooded/hydrostatic dry flats.

### Evaluate ONLY source observation support on 2011 and 2012

1. For each already fixed source test year, use exactly original three consecutive hourly fixes A,B,C of each bird; A→B and B→C each 30–120min, each source step speed 0.4–120km/h, with future C used only as **candidate destination observation location**, not a predictor of tide/selection. No original RWS data opened.
2. Count original observed test triples, original birds/weeks/days, how many true original C destinations fall within any one of the **2010-selected** K=8 cells, how many original C positions sample *source-valid* AHN2 DTM pixel, and how many fall in broad −3..+3m NAP candidate height. Also report unique birds and ISO weeks with valid original height.
3. Fixed feasibility gate per site/test year: ≥**500** original C endpoints with valid original DTM substrate candidate, ≥**3** contributing birds, ≥**4** distinct ISO weeks and ≥**2** distinct eligible DTM cells. This gate checks whether a follow-on ecological exposure test is feasible; no biological effect should be interpreted if it fails. All site/year results, including source absence and denominator, must be reported. If underlying WCS inaccessible/ambiguous or fewer than K source cells in training, source STOP not biological effect.
4. No RWS tide heights/phases, no AHN2-vs-2014 DEM difference, no `z>η(t)` source habitat accessibility, no prey density, no visited-vs-available step analysis and no social Boids force is estimated here.

**Important domain constraints:** AHN2 DTM is chiefly surveyed land surface; under-water shallow flats may have NODATA or water return errors; 2010 source-visit hotspot selection may emphasize roosts instead of tidal flats and cannot independently identify ecological resource selection. Original survey dates may vary throughout 2007–2012. Strictly distinguish successful source overlap from the proposed causal moving wet/dry front.

## Next biological admission, only if source overlap passes

Precommit before opening new outcomes: on original 2011/2012 target triples, join measured RWS NAP tide h(t), local substrate NAP z at the actual destination, determine `z−h(t)` and potentially newly exposed `h(t_B)>z≥h(t_C)`; quantify whether actual directed steps end near the historical hydrostatic exposure band more often than location/time/length and prior-direction matched negative controls. Site-specific tide phase propagation and AHN2 exact survey dates remain crucial, so `z−h>0` at remote gauge is *proxy hydrostatic accessibility only*, not verified individual prey availability.
