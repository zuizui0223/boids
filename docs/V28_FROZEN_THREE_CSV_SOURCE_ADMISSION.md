# v28-B — exact bat RSF/GPS/individual ledger admission, source-only

**Registered 2026-10-29 JST after official Zenodo 7535030 metadata-only verification, and BEFORE opening original bat positions, ecological turbine/landcover outcomes or case-specific numerical covariates.** Original A1 run [40860616465](https://github.com/zuizui0223/boids/actions/runs/40860616465) passed exact source/license and identified three original named tabular files. Original record license **CC BY 4.0**, source DOI **10.5281/zenodo.7535030**, paper [Reusch et al. 2023](https://doi.org/10.1016/j.cub.2022.12.050).

## Fixed source original files from the Zenodo provider

| Original exact name | Bytes | Provider MD5 |
|---|---:|---|
| `Model_dataset_RSFFlight_Complete_EPSG25833.csv` | **17,582,302** | `fb0d7967d552b855ab530eeedcede7ff` |
| `Observed_GPS_locations.csv` | **3,080,045** | `a1583b48487a78259f7e63937af232e5` |
| `Individual_Characteristics_Capture.csv` | **6,388** | `84e78242135fc50b12e5e2ffff91bcb5` |

Official published `Data_Structure_UploadedFiles.pdf` is 514,289 bytes, MD5 `8d3b124e81aa3a6c1d866da0ee6c3e8a`; its published metadata and paper can inform pre-outcome source fields, but download is not required for the actual CSV source integrity.

## Source-only B1 exact receipt

- Download all **three original CSV files**, source URL directly from published Zenodo file manifest, enforce per-file 100MB and combined 200MB, validate original exact bytes and MD5, compute independent SHA256. Fail closed if any differs or direct original access is blocked. Do not redistribute original bat GPS or private roost coordinates.
- Inspect full original CSV **header names, total record counts and categorical identifiers ONLY**, never parse numeric x/y UTM, altitude, turbine distance, forest cover or original source habitat values. For RSF model original table, record only the presence/values of `batid`, `trackid`, `case_`, `response_rvso`, `field_period`, `sex`, `age_class`, `move_state` and any other *source category* whose name is independently documented in the original published dictionary. Do not infer `case_` value meaning from fit sign; source dictionary says TRUE observed vs FALSE random.
- Record exact number of independent `batid` tokens; `trackid` per bat; original distinct flight dates encoded in `trackid` if unambiguous (do NOT guess by arbitrary substrings); number of bats with ≥3 distinct flights/dates, true/false frequency, observed/random records per track, and whether random positions are flight-level or per-step. The 17MB original model table can include many more generated random points than the original 8,129 GPS positions; **these are not independent GPS fixes or bats**.
- For actual observed GPS CSV and individual ledger: source header, number of records, ID fields, number of unique IDs and same-ID coverage across original sources; do not inspect date, geographic coordinates or exact animal IDs unless required for source schema verification.
- Require ≥8 original independent bat tokens with ≥3 source-declared flights on ≥3 dates and ≥200 true/false matched source strata with a source ORIGINAL link to event/decision time before any future individual history claim. A `trackid` identifies an entire flight path: it is NOT one movement-decision step. If only track-level random points without per-time matched strata, consider a **separate preregistered RSF heldout-individual** ecological habitat ranking test, never a true step-level choice predictor.
- Even if source passes, original paper's 60 tags are NOT 60 independent turbine sites, and the population covers one northeastern German study landscape. Source x/y UTM EPSG 25833 are horizontal coordinates not validated vertical ecology.

**B1 contains no biological effect estimates.** All v13–v27 field results, including v25's corrected private-history null, remain frozen.
