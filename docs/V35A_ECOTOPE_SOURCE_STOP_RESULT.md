# v35-A — Wadden Sea ecotope original GIS source-only STOP

**Status: `V35_PUBLIC_HABITAT_SOURCE_NOT_ADMITTED`. 2026-10-31 JST.** This is a metadata/provider availability check, **not a test of animal habitat use**. The protocol was publicly frozen at commit `1d7a818b9b199ee5391b22310f6ba246710df137`, before any new GIS/GPS positions or habitat effects were opened.

## Source research and provenance

The target was Baptist et al. corrected v2 trilateral Wadden Sea ecotope map, original DOI [10.17632/27mysx289g.2](https://doi.org/10.17632/27mysx289g.2), representative for 2008–2012, with geo-content `EctpWZ3L_gpkg.zip`. Publication documentation states original v1 had an incorrect shallow-sublittoral / low-intertidal cutoff (0.001% instead of 4% exposed), and v2 corrects it. GeoPackage includes polygon ecotope class, bivalve beds and seagrass, but does not itself supply actual pointwise daily mudflat elevation or exposure.

**Official original Mendeley Data public API** queries against exact dataset/version `27mysx289g?version=2` and two alternative file metadata endpoints each returned **HTTP 401 Unauthorized**. No source ZIP file, source checksum, native geometry, CRS or legend code was fetched from this host.

**Official Wageningen Marine Research public GeoServer WFS** source-only `GetCapabilities` and three `DescribeFeatureType` calls for the previously identified layer names `WS3shp:ws3_ecotope_mp_basic`, `WS3shp:ws3_ecotope_mp_litoral_zones_and_dynamics`, `WS3shp:ws3_bivbeds_focc` each returned **HTTP 503 Service Temporarily Unavailable**. The public service's catalog presence alone would not prove corrected-v2 content identity.

[Read-only original-source GitHub Actions run 41190295572](https://github.com/zuizui0223/boids/actions/runs/41190295572) passed all five known-truth data-privacy/source-schema tests and emitted the complete **negative source-admission receipt**. The workflow itself passing does not make the external data accessible, and no original bird GPS, location, original tide heights, ecotope polygons or model outcomes were opened.

## Ecological claim gate

No corrected map version/legend/geometry has passed; **do not state that Schiermonnikoog oystercatcher GPS fixes fall within specific exposure, sediment or bivalve-bed polygons.** No habitat overlap fraction, resource accessibility or tidal-state interaction has been computed. In particular, dynamic `exposed(x,t) = 1[z_bed(x)>H(t)]` requires compatible real bed elevation (z_bed) and correctly propagated water level, not just a static ecotope class.

This STOP does **not** contradict earlier confirmed within-one-population observational RWS/GPS tide-speed association (v33-D, v34, v34-B). It identifies the next empirical source dependency. Replacing provider/period/field definitions after looking at previous results requires a **separately documented source protocol**; do not reclassify this failed source gate as an ecological null.

Machine-readable [exact receipt](../validation_v35/results/wadden_ecotope_source_only_v35.json), fixed [source code](../validation_v35/source_only.py), and [original protocol](V35_ORIGINAL_WADDEN_ECOTOPE_SOURCE_PROTOCOL.md). Main and all previous draft PRs left untouched.
