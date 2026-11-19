# v34 Chrotopterus original Dryad acquisition — SOURCE ACCESS STOP

**Completed:** 2026-11-19 JST  
**Run:** https://github.com/zuizui0223/boids/actions/runs/44455001875 — all five offline tests PASS, source-only workflow PASS.  
**Official publication:** Trujillo et al. 2026, *J Anim Ecol*, DOI 10.1111/1365-2656.70391. Dataset DOI 10.5061/dryad.7d7wm38c0.

Frozen pre-outcome source file IDs:
- `5036052`: `Raw_movement_data.zip` (original fix records)
- `5036051`: `Movement_data.zip` (30-second interpolated trajectories)

Both official file-stream URLs returned **HTTP 200 but a 4,268-byte `text/html` validation/challenge document, not original ZIP**. Both REST file download endpoints returned **HTTP 401**. Exact files/headers, bat IDs, trajectories, fixes and origin/interpolation rates were therefore **not acquired or verified**, notwithstanding the published paper's description (17 animals, 57 trajectories, 3 landscapes).

**Outcome:** `SOURCE_ACCESS_OR_STRUCTURE_STOP`. No numerical original movement, HMM-state, landscape selection or heldout movement score opened. This is NOT an ecological negative and does not imply the deposited dataset is missing for normal authorized users.

**Scientific implications:** The paper already finds land cover more predictive of where two inferred behaviors occur than of when transitions occur; that published finding is prior art and was not independently replicated here. Three nearby landscapes also cannot establish taxon-wide or global predictive generality.

**Next scientific avenue:** independent 49-species, 22-country, 166-study telemetry meta-dataset (Laforge et al. 2021, Dryad DOI `10.5061/dryad.qnk98sfhh`, mirrored as Zenodo record `5794471`) for *new cross-study/country/species transportability*, without reusing this blocked source or changing any prior negative endpoints. Keep the two research programmes distinct.