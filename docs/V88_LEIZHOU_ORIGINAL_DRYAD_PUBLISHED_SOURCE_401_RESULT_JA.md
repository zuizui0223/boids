# v88 original Leizhou China 4 shorebird species: authentic Dryad metadata and original uploaded SHA256, public original binary 401

**2026-11-09 JST**, original Dryad source-only [GitHub Actions #42577503267](https://github.com/zuizui0223/boids/actions/runs/42577503267) **SUCCESS execution, 7 known-truth/source tests PASS**, but original scientific GPS CSV and habitat GeoTIFF **NOT DOWNLOADABLE by unauthenticated GitHub Actions**. This is a real source-access boundary, **NOT a negative ecological result**. Original Dryad official public dataset metadata and publisher-supplied source file IDs, bytes and SHA256 authentically fetched, **with no original animal locations/individual IDs or UTC collection times inspected**.

## Independently collected non-Wadden shorebird dataset — directly relevant to potential generalization

**[Zhang & Choi, Dryad 2026, DOI 10.5061/dryad.51c59zwm3](https://doi.org/10.5061/dryad.51c59zwm3)** published 2026-06-04. Leizhou, Guangdong, China (2019–2020 and 2020–2021 winters), **4 taxa/16 genuine tracker birds as documented**:
- `Tringa totanus` common redshanks **9**
- `Pluvialis squatarola` grey plovers **3**
- `Charadrius leschenaultii` greater sand plovers **2**
- `Calidris canutus` red knots **2**

The original publication already reports taxon-specific day/night roost habitat use, so recreating that finding alone is not a new discovery. Original `Raw_data.zip` includes GPS `Collecting time` (UTC, **not `Transmitting time`**), original source tag mapping, raster `Habitat map.tif`, native pond boundaries, code legend, and shorebird field-survey counts. The field survey's categorical `Tide rise/Tide fall` applies to **survey time**, not each GPS fix: **no site-local original measured 2019–21 tidal gauge has been established**, so NO tide-phase × daylight biological effect can be claimed at this point.

### Actual original Dryad public metadata authenticated

| Public original dataset provenance | Original publisher record |
|---|---|
| Correct original DOI | `10.5061/dryad.51c59zwm3` |
| Original published date | `2026-06-04` |
| Original Dryad version ID | **445867** |
| Original `Raw_data.zip` file ID and advertised bytes | **4795469**, **1,295,635 bytes** |
| Original `Raw_data.zip` uploader-provided SHA256 | `34ef16b3450be41e40bd1ad89a487e866cd0c5409e4c3dc62a594702bffd3aa4` |
| Original `README.md` file ID and advertised bytes | **4795504**, **13,557 bytes** |
| Original `README.md` uploader-provided SHA256 | `954c392935e953b3c0c8d13f052077671501f45d3037baad3a7492759ec51e42` |
| **Data ZIP + README actual bytes downloaded** | **NO, HTTP 401** |
| Wild GPS source rows/month/individual/UTC quality verified | **NOT ESTIMATED; actual GPS binary inaccessible** |
| External tidal×solar response | **NOT ESTIMATED** |

Official original public Dryad `GET /api/v2/datasets/{encoded DOI}`, version list and `GET /api/v2/versions/445867/files` provided the above metadata and ORIGINAL PUBLIC uploader SHA. Actual official dataset package `/api/v2/datasets/{encoded DOI}/download` was **HTTP 401**, **and even the source metadata advertised literal publisher** `/api/v2/files/4795469/download` (and README original ID) were **HTTP 401** without authentication. No file bytes, GeoTIFF pixels, animal source GPS table, or originally measured tidal height ever entered the analysis. We did not guess alternative web-host file UUIDs or bypass authorization. A future authorized upload of those two ORIGINAL SHA-matching public files could unlock a separately frozen source audit; it would still not independently verify tidal height.

### What can and cannot be concluded

Compared to the 2010 Dutch original Wadden `Haematopus ostralegus`, this Leizhou original publication is **different species and a truly different coastline and year**, so it is the first relevant field-transfer candidate for a bird tide/daylight ecological mechanism. But a published source description **does not** prove the original GPS tide/solar four cells or even source GPS location counts per bird meet strict gates. Also `Tringa totanus` n9 may support within-species bird-cluster inference with source support; the other taxa n3/n2/n2 are exploratory/descriptive, not independent species-level generalization.

v86 historical Schier wild GPS mid/high-class fraction × actual 2010 RWS flood/ebb × day/night `D=-0.05615567` bird95 `[-0.07699717,-0.03575020]`, Ameland D `-0.02037975` bird95 `[-0.09331358,+0.08415048]`, original two-site bird difference `-0.0357759` 95 `[-0.145053,+0.040866]` NOT ESTABLISHED. Prior v87 2011 new-only individual IDs **0/0 across Schier/Ameland**, no independent annual cohort. Both were authentic source-backed results on a different region/species and do NOT imply any biological prediction about this Leizhou data.

## Reproduction

- [v88 GitHub Actions source-only #42577503267](https://github.com/zuizui0223/boids/actions/runs/42577503267), 7 test passes; original public Dryad provenance and HTTP 401 recorded.
- [Before opening source/original 4 species + habitat data frozen protocol](V88_FROZEN_LEIZHOU_4_SHOREBIRD_DRYAD_GPS_HABITAT_SOURCE_ONLY.md), `validation_v88/leizhou_original_dryad_source.py`, `validation_v88/test_leizhou_original_dryad_source.py`, `.github/workflows/v88-leizhou-original-dryad-shorebird-source-only.yml`.
- Original anonymous source-only GitHub artifact `v88-original-Leizhou-Dryad-four-shorebird-GPS-habitat-public-SOURCE`: record exactly the actual official metadata and 401. No wild GPS coordinates/individual tags, field survey use records, GIS raster pixels or constructed tide phase was released.
- This is SOURCE-ACCESS INCOMPLETE, not a valid test of general tide×daylength ecology. Do not present 16 birds as actually analyzed GPS individuals until original raw publication downloaded and verified.
