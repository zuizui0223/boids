# v31 original Rhinopoma Mendeley source-only availability result — API ACCESS STOP

**Executed:** 2026-11-19 JST  
**Official public repository DOI:** [10.17632/k7pt2j84f7.1](https://doi.org/10.17632/k7pt2j84f7.1) (Goldshtein et al. 2025, PNAS).  
**Source-only original API workflow:** [run 44445620901](https://github.com/zuizui0223/boids/actions/runs/44445620901), four known-truth/no-outcome tests PASS.

### Fixed API results

| Version 1 public Mendeley metadata endpoint | Actual HTTP |
|---|---:|
| \`api.data.mendeley.com/datasets/k7pt2j84f7?version=1\` | **401** |
| \`api.data.mendeley.com/datasets/k7pt2j84f7/files?version=1\` | **401** |
| \`api.data.mendeley.com/datasets/publics/k7pt2j84f7/files?version=1\` | **401** |

The ordinary public Mendeley landing page publicly identifies title, DOI/version and CC BY 4.0, but its dynamically loaded file list was not exposed to this unauthenticated source-only API route.

**Status:** \`ORIGINAL_PUBLIC_API_NOT_ACCESSIBLE\`. This is a transport/authorization stop, not an assertion that the dataset is absent from the internet, that the authors lack the raw recordings, or that acoustic masking has no biological effect.

No original Mendeley source file IDs/sizes/checksums, event timestamps, raw movement, acoustic amplitudes or per-individual data were retrieved. No behavior model was fitted. As a consequence, original synchronized audio×GPS eligibility and cross-species transfer could **not** be verified. No source-admission criterion was relaxed.

### Biological conclusion

None. The prior [Carollia v30 heldout negative primary](BAT_ACTIVE_SENSING_CAROLLIA_FROZEN_RESULT_V30.md) remains unchanged: the published anticipatory gaze phenomenon is prior art, and acoustic azimuth did not produce a reproducible incremental mean gain over the registered held-out motor baseline. We cannot generalize this failure to other species without independent raw data.

**Next independent candidate (separate ecological endpoint):** [Dryad 10.5061/dryad.6q573n6b0](https://doi.org/10.5061/dryad.6q573n6b0) contains 710 published flight-trajectory summaries spanning five focal bat taxa and 16 sites, which may permit a **site- and species-heldout co-occurrence/foraging-flight behavioral transfer**; it does not include calibrated per-pulse sonar gaze and must not be pooled with the v30 echo-steering endpoint. The next primary and source eligibility must be frozen before opening those outcomes.
