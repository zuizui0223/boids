# v27-A pre-outcome source admission: 18 long-tailed tit breeding pairs, observed movement and available trees

**Registered 2026-10-29 JST BEFORE opening any animal movement positions, resource-cover numbers, location-choice outcomes or predictive model scores.** Previous v13–v26 empirical and source-integrity endpoints stay frozen, especially the v25 artificial case-scale artifact and v26 missing marine-turtle choice labels.

## Independent original source and ecological question

Ellison-Neary, Oppenheimer, Dehnen, Hatchwell & Street (2026), *An intuitive method to calculate the utilization distribution of an animal from step-selection analysis*, *Methods in Ecology and Evolution*, [DOI 10.1111/2041-210x.70316](https://doi.org/10.1111/2041-210x.70316). Independent public [Dryad DOI 10.5061/dryad.kprr4xhm0](https://doi.org/10.5061/dryad.kprr4xhm0) (deposited April 29, 2026). The published case study used **18 breeding pairs of long-tailed tits (*Aegithalos caudatus*)**, followed on foot with moves >10 m. Birds in each pair traveled together, so **pair or nest** is independent movement unit, not both birds and not all GPS fixes.

The original public Dryad landing page describes **five small files**:
- `GPS_LOCATIONS.csv` (~136 kB): source `set_of_2000_points,point_id,nest_id,female_id,male_id,lat,lon,x,y,start_at_nest,place_in_sequence,date_time`; these are author-prepared field relocation points, not guaranteed exact raw telemetry logger fixes.
- `NestLocations.csv` (~7.74 kB): source breeding nest/ref and pair female/male rings, locations;
- `TREE_SAMPLING_LOCATIONS.csv` (~8.43 kB): independently sampled grid coordinates, grid cell/sampling IDs;
- `Tree_Availability_Data.csv` (~128.5 kB): sampled tree species/canopy/shrub abundance and availability including `point_id, species, c_cover,s_cover,c_sum,s_sum`;
- `README.md` (~2.12 kB): original source data dictionary.

The landing page sizes/names are **not independently verified original data bytes**, and no species-specific resource-use effect is claimed from the authors' results.

## Stage A original provider admission

1. Request public official Dryad API `https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.kprr4xhm0`, require exact dataset DOI, version, original file IDs, exact file lengths, publisher SHA256/MD5 if provided, source license and original download URIs. Source identity is based on provider official record, never approximate webpage text. File caps 5 MB each and 20 MB cumulative.
2. Attempt **public original bytes** for all five named files using only documented Dryad API/public file links; check exact provider length and digest when present, compute new independent SHA256 for each. A Dryad 401/403 failure => `NOT_ADMITTED_ORIGINAL_SOURCE_ACCESS`, not evidence of absent ecological movement or pairs. Two unrelated Dryad original deposits already failed anonymous file downloads in v21/v25, so **do not assume availability** from an open landing page.
3. Only IF bytes actually verified, inspect original table **column names and ID/calendar key grain**, distinct `nest_id` or source pair IDs, tracking event `date_time` format, repeated sequence counts, original tree sampling units, potential join keys and missingness. Stage A must not print original ring IDs, exact sensitive nest coordinates, original animal movement vectors, tree-cover numerical values or model outcomes.
4. Precommitted future source selection: ≥8 independent original breeding pairs/nests each with ≥4 distinct chronological relocation events, ≥200 later movement events on original timestamps, and source-mapped independently sampled tree-resource availability cells **that can be linked without using future relocation outcomes**. If source GPS×tree grid geometry cannot be joined uniquely by original coordinates/IDs using a separately registered spatial protocol, stop before fitting.
5. Distinguish tree species cover proxy from actual food/prey intake. Pair travel together is NOT evidence of social steering coefficients; original simultaneous neighbor relative motion/kinematic body positions are not present. No calibrated true 3D niche from nest height and ground positions.
6. A later v27-B protocol must fix future time split, whole-pair holdout, movement kernel and spatial availability definition, target locations/steps, tree-cover vs route-distance baseline and original habitat map chronology BEFORE looking at numeric movement and resource variables. This is required even if source A succeeds.

Biological goal: whether a **pair's own historical use** adds predictive information beyond independent tree availability and movement-distance kernel for later relocation choices. All earlier v23 positive daily individual movement, v24 positive static wetland ranking, v25-F no private habitat-history gain and v26 source STOP remain separate, not automatically transferable across taxa.
