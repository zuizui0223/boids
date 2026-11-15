# Source admission: Eptesicus moving-prey sonar calls & 3D head-target motion — 2026-11-15

**SOURCE-ONLY PRE-OUTPUT GATE. No new bats, recordings, tracked flights or numeric biological outcomes opened.** This is a DIFFERENT original study from Hase 2026, Molossus 2024, and all simulated Steckel/Mazar 2026 bat models.

Original Wilkinson, Wang, Cowan & Moss (2025), *JASA* DOI `10.1121/10.0036252`. Public Johns Hopkins Dataverse DOI **10.7281/T1WF3NZ7**. Original study already found that big brown bats `Eptesicus fuscus` shorten call duration and intervals and adjust head movements while tracking a **moving mealworm on a tether** under clutter manipulation. There were **five identified original bats**. These are trained and PERCHED, not freely flying. This cannot be called independent proof of a 3-D flight policy or natural prey capture.

Original public archive reports:
- `README.md` ~14.4KB, acoustic and video protocol/format guide;
- `AudioData.zip` ~639.8MB with per-bat `*_pulse_data.mat` and `*_pulse_freqs.mat` for five bat IDs and two example trials;
- `VideoData.zip` ~81.1MB with per-bat `*_angle_data.mat` containing head yaw/pitch/roll and tethered mealworm position over trials;
- `Fig#_code.m` source figure scripts. Archive marked Public, **CC BY-NC 4.0**; retain citation and no redistribution.

**Current goal:** validate whether original source recordings and head/target trajectories share original bat & trial alignment, so that a prospective new **bat-heldout sensory-versus-moving-target forecast** could be tested. This is a source availability and grouping preflight, NOT a claim that a new forecast exists or a new behavioral pattern was observed.

### Hard-gated procedure before interpreting original values

1. Query only official Dataverse dataset JSON at `https://archive.data.jhu.edu/api/datasets/:persistentId?persistentId=doi%3A10.7281%2FT1WF3NZ7`; only fallback is the official JHU public catalog page. Record dataset/file persistent identifiers, canonical original IDs, sizes, source MD5/checksums, original license. No original-data outcome values.
2. Fetch only original public `README.md` and `Fig#_code.m` files where size≤100KB and provider access is authorized. Extract source **format / keys / temporal alignment / biological grouping** and short snippets only, not biological results/figure values; do not commit original README or scripts in full.
3. For original `AudioData.zip` and `VideoData.zip`, perform HEAD and at most 4096-byte HTTP range; DO NOT full-download 640/81MB at this gate. If range ignored (HTTP200) do not treat whole dataset as read. If provider access 401/403/451, STOP, no unauthorized bypass or source-redirection guesses.
4. Distinguish each animal from trials, calls, video frames, head rotations, and target locations. Five original bats are biological units even if there are many calls/trials.
5. No bat IDs, exact original call/target time series, sound waveforms or scientific figures in the committed source artifact. Only original provider metadata, schema names/fields and rights.
6. If public JHU source admits original DATA and a documented acoustic-to-video shared trial/time key, **separately freeze new withheld-bat + withheld-condition predictive estimand before opening target outcomes**. If original files cannot be admitted or alignment is missing, SOURCE STOP rather than invented linkage.
7. Original paper's head adjustment, sonar pulse timing and acoustic call frequency response are prior art; repeating them is NOT novel. New question would be a source-blind lagged sensor-control prediction of unseen individual vs static/moving target, not just another plot of shorter calls under clutter.
8. No modified `batter` manuscript, no merge or journal submission; `boids` PR #36 remains Draft.

**Secondary alternative:** Shultz et al. (2026) *PLOS ONE* DOI `10.1371/journal.pone.0352329`, CC BY4 original `AaronJCorcoran/wind-turbine-multi-sensor-study` contains track-level thermal and nightly bat acoustics but authors distinguish track from bat ID; admission is conditional on a grounded same-animal acoustic-to-track identifier. Aggregate night-level co-presence alone cannot establish a bat sonar→trajectory mechanism or 12,047 bat-only 3D tracks. Do not conflate bat calls with tracks of mixed birds/bats.
