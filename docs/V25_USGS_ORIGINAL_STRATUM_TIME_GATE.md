# v25-B3 source-only audit: are original 2023 USGS step alternatives matched by birdyear × timestamp?

**Registered 2026-10-29 JST after opening original header and exact CSV MD5/SHA, BEFORE inspecting any original case label frequencies, choice-set membership, ecological predictors or numeric effects.**

## Original byte-frozen source

USGS Overton & Casazza 2023 ScienceBase item `652edfe8d34edd15305a9ab0`, DOI `10.5066/P9ELSUHN`, `Data Release P9ELSUHN.csv`: **27,997,528 original bytes**, provider MD5 `78eb6064eca992225d6907d6e46f5bef`, independently computed SHA256 `1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15`, **380,578 physical lines of data**. Exact 13-column source header read (no original source response values):
`birdyear,timestamp,species,case,season,photoperiod,Corn,Field,Other,Protected,Rice,Urban,Wetland`.

FGDC XML file in same official item `Data Release P9ELSUHN.xml` has provider metadata MD5 `170cf76948ef8604ae41f268bc3bf4f0` and 26,316 reported bytes, but an original independent full-byte attempt did NOT reproduce the provider's MD5; **do NOT treat FGDC byte integrity as passed** until resolved. Original CSV itself HAS independently passed its own MD5+SHA. The original paper's 100 simulated alternatives are a design statement, not a number already counted from our source.

## Fixed categorical and chronology parsing ONLY

1. Download only original SHA-pinned CSV; verify bytes, MD5, SHA256. Inspect **only** `birdyear,timestamp,species,case,season,photoperiod` and categorical label missingness from the original. Never parse or export numeric `Corn,Field,Other,Protected,Rice,Urban,Wetland` source values at this stage.
2. Define possible source choice-set stratum **solely by exact original `(birdyear,timestamp)`**, with no original GPS outcomes or response-derived clustering. Count all source rows; number of unique such keys; counts of `case` labels inside each, number with exactly one used and >=1 available; sample sizes of candidate alternatives; duplicate source step/group keys and missing/ambiguous timestamps. `birdyear` is not a certified stable individual ID over multiple winters; never call it 426 independent marked birds without a separate ledger.
3. Source `case` must unambiguously contain only `0`/ `1` (available/used) or published explicit equivalent; if not, return `STOP_LABEL_SCHEMA` and a redacted token-shape diagnosis, do not guess which category is used from source effect sign.
4. Time must be supported by the original timestamp token format. Count date string shapes only initially; calendar decoding may be a later source-only amendment independent of any habitat model result. Do not fabricate origin coordinates when absent. Categorically NO ex-ante movement-kernel validation from this CSV, which lacks original previous-position coordinates.
5. For an exploratory **retrospective conditional matched habitat ranking** source admission require at least 20 original birdyear identifiers, >=200 matched source strata each with one labeled used and >=1 labeled available, and ≥3 distinct timestamped choice-set keys from each of >=20 identifiers. Report all unsupported and missing strata; do not cherry-pick high-performing species or years after scoring.
6. If `case` and `timestamp` fail to define distinct source strata, source STOP; no arbitrary assembly by every 101 consecutive rows or by posthoc source observed location.
7. Even if this schema passes, the original simulated movement alternatives came from a movement kernel fitted across all original GPS steps; they are **retrospective generated alternatives**, not entirely training-only prospective availability. A new source-frozen model (only after this gate) may compare environmental rankings in original source simulated step choice-sets, not causal human-access/risk, learned personal niche or true next-step prospective prediction.
8. Store source aggregate IDs, original source counts and source SHA only; no precise GPS locations, original `birdyear` strings, exact bird timestamps or original habitat percentages in repo.

All original v13–v24 observed endpoints immutable; Tennessee Dryad v25-A remains `NOT_ADMITTED_SOURCE_RDS_OR_README_BYTES_UNAVAILABLE`.
