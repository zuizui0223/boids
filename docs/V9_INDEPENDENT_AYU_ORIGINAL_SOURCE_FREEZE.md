# v9 second fish species (Ayu) original data admission — NOT a result yet

This is a **new biological fish species** external validation candidate independent of the original Puy et al. 2024 black neon tetra original 8-fish source.

Original scientific source: Niizato et al. (2024) Scientific Reports 14:29758, https://doi.org/10.1038/s41598-024-79232-2, 10 *Plecoglossus altivelis* fish tracked for 7 recordings of 8–12 min at analytical 20Hz (recording 100 fps). Authors provide raw positions through https://github.com/t-niizato/Information-structure-of-heterogeneous-criticality, fixed commit `158e8d7ebdef73752da63192ee36e3a099dd5dfa`, seven ~1.6–2.2MB positional source TXT files under `Compute_IIT/fish_revised/`.

Before behavior effects, the v9 original source gate:
- Downloads actual published upstream Git commit once (NOT an unpinned branch), checks each of 7 exact Git blobs, expected source byte sizes, numeric rectangularity/line counts without exporting source rows, and reports only structural summary.
- Source processing conventions and identity labels must be audited *before* defining an independent model; the original 2024 article also explicitly compared actual fish against Boids and SPP, which is prior art.
- If admissible, next distinct protocol will fix physically equivalent scales and 0.2s delay at 20Hz, compare global-school velocity and local neighbor information on all 7 whole trial holdouts. **No source-based choice of most favorable feature radii**, and no pooling raw six tetra trials with seven ayu as independent species-level replications. Methods across species/tanks differ; confidence intervals use species or recording-level grouping, not individual frames.
- Any unknown units, missing fish IDs, temporal quality, incompatible trajectory state and limited numeric access -> fail-closed SOURCE_STOP. No ecological effect claimed here.
- No Puy vs Ayu matched calls. Future fish school–chorus joint experiment still requires synchronized attributed acoustic calls and fish tracks from *the same* observations.

This source-only protocol is submitted in the same review-only PR. No main merge.
