# v6 source gate for genuine joint fish calls and movement in Mouy XAV
2026-11-20; **source-only**, prior to opening original call/event values.

Original publication: Mouy et al. 2023 *Methods in Ecology and Evolution*, https://doi.org/10.1111/2041-210x.14095; original OSF https://osf.io/q8dz4. The source says individual sound-source 3D localization was matched manually with fish visible in videos. It does **not assert frame-by-frame individual tracking for all silent fish**.

Prior Actions v5 OSF catalogue validated 71 original file names across 12 API pages, including six `localization_results.csv` and .nc results plus 16 WAV and 11 MP4 videos, source result #44743169531.

Here we freeze the six exact original OSF file IDs from that audited catalogue:
6335fcfa31d65303352de2bc (large OGD), 6335fd860db48e0365e127a5 (mini), 6335fdb30db48e0364e11e09 (mobile A), 6335fdd331d65303352de44a (mobile B), 6335fdf4ec7f3f0332f61087 (mobile C), 6335fd3aec7f3f0337f5f9a4 (large HI).

Checks: read official OSF per-file metadata, bounded CSV download <=60,000 original bytes and provider hash if offered, preserve SHA256, record **only column names and row counts**, never individual coordinates, original timestamps or waveforms. No materialization of all raw data. Every source STOP retained. A true joint school+call model requires individually identifiable fish trajectories on video *including non-calling fish* synchronized with attributed call source; a sparse event-localization table cannot by itself identify individual school movement.

Do not borrow Puy et al. 2024 8-fish tank positions for these unrelated OSF recordings. No fish acoustic social influence or full Boids forces are demonstrated by this source gate.
