# v10b: original localized sound events are NOT fish trajectories

Source: Mouy et al. 2023 MEE DOI 10.1111/2041-210X.14095, [OSF](https://osf.io/q8dz4), six original independent audio/video array configurations. Pre-existing v6 original structural gate [Actions #44750614686](https://github.com/zuizui0223/boids/actions/runs/44750614686) authenticated all six `localization_results.csv` files, 66 total sound-localization records and their SHA256 fingerprints; no repeated individual fish IDs. The six published SHA256 values are rechecked verbatim before opening new values.

**This is an exploratory test of whether acoustic *source locations* are temporally structured. It is NOT a fish schooling / Boids / causal vocal facilitation test.** The original article already localized sounds and identified some calling species by video; that is prior art. A positive test might indicate an active acoustic hotspot, one persistent calling fish, multiple nearby static fish, source movement, or detection bias—not which.

## Fixed test, not chosen from outcome
For each original array:
- parse original `time_min_date` (UTC), `x,y,z` (meter coordinates), `label_class`, and per-axis `*_err_span`. Do not join across array coordinates or dates.
- Restrict primary to all published localizations with fully finite 3D positions and original timestamps; at least six source events and at least five **successive** event pairs with time gaps from .001 to 120s. Only such source-constrained arrays scored; others report SOURCE_SUPPORT_STOP.
- Primary descriptive effect: median 3D distance (m) between consecutive localized acoustic events within 120s. Compare with 1999 fixed-seed shuffles of original event positions across the observed times within the **same array**, preserving original event positions, total count and observation time/gaps. Report observed/permutation mean and one-sided compatibility p conditional on exchangeability, **not biological fish interaction p**.
- Secondary: shuffle positions only within identical original `label_class` (if labels are informative) and strict uncertainty subset with **all three span values ≤1m**. Predeclared, report every failed source support and unchanged null family. Do NOT tune the event-gap window or quality threshold after results.
- Acoustic source `uuid` does NOT guarantee repeated fish identity. All original raw x/y/z and times remain off the commit and artifacts; publish only per-array label counts, N, source SHA, median pair distance and permuted summary. Six arrays are not six independent fish populations, and perhaps only a subset support sufficient close event times.
- No direct independent fish-count data, local Reynolds force, individual velocity, species-specific social synchronization or any causal school→chorus inference can be derived. An author video may identify a calling species at a single event but no continuous tracking for all fish.

The 2026 Dryad same-site UF440/70kHz active-source source-only gate (#TBD) reached public nine-file metadata but exact original payload HTTP 401. That is SOURCE_ACCESS_STOP and cannot be substituted by these other OSF sounds to manufacture paired source evidence.

Keep existing draft PR #248, main unchanged. Same ecological objective: find true data tracking **same identifiable fish** with both location and song at the same time.
