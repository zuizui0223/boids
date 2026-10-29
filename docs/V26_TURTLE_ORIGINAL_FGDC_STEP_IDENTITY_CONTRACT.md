# v26-B2: original turtle FGDC dictionary and PIT×step/time source grain gate

**Registered 2026-10-29 JST after B1 source header/MD5 validation and BEFORE reading any turtle environmental values, habitat association, conditional choice label or prediction score.**

Independent USGS turtle source item `5faab074d34eb413d5df1f41`, DOI `10.5066/P9UZU4GG`. B1 original CSV `Hart et al_iSSA.csv` **45,669,515 bytes** MD5 `5c5f25398720a663ae332097b49bf740`, independently computed SHA256 `eef4d2dd16c97cd0d8722ed1cac8a031cf3dd336404b2e8e4c085cb2fadd4ec0`, **420,365 physical data lines, exactly 11 fields**:

`orgnl_pit,step_id,step_length,log_step_length,turn_angle,cos_turn_angle,start_time,end_time,protected_status,water_depth,chlorophyll`.

**Critical observation:** NO explicit `used`, `available`, `case` or `chosen` column exists. Never assign a label by CSV row order or a guessed `step_id` number. Source release describes random available steps generated from observed step starting location, but this title does not establish how original used vs random is encoded.

## Next original-source dictionary/identity audit

1. Download **only** official original FGDC `iSSA data release V3.xml`, **22,606 bytes** and provider MD5 `bb23daf440cb8ee6932f60a8fc7293a5`; compute independent SHA256. Never use unverified XML metadata. This dictionary may independently define `step_id` and how used cases are distinguished.
2. Independently reload original SHA/MD5-pinned CSV but read **ONLY** `orgnl_pit`, `step_id`, `start_time`, `end_time` categorical/id columns. Report aggregate distinct original PIT identities, step IDs, original PIT×step ID support, original PIT×start-end date support, whether exact original start/end timestamp tokens parse and how many source groups have repeated dates. Do not output actual PIT IDs or exact animal timestamps.
3. Count whether `step_id` tokens are repeated 2+ times with the same PIT/start/end, and whether a source-defined observed/available indicator can be recovered **from the original FGDC dictionary or original author code/metadata only**. `step_id` alone cannot be assumed case labels. If source case label is unidentifiable, source status **NOT_ADMITTED_FOR_CHOICE_MODEL** even if n PIT≥8 and rows large. A different purely *GPS temporal* endpoint may be possible, but this processed source has NO original lat/lon columns either; don't fabricate a movement path from length/angle without absolute positions.
4. For a future original environmental habitat step selection model, require at least 8 original PITs with ≥3 calendar dates and ≥200 TRUE case/alternative groups where labels and matched start dates are independently source-defined; no arbitrary splitting into blocks of N+1.
5. Same original USGS source with no coordinate, time-series trajectories and no explicit labels cannot by itself validate Reynolds/Boids social steering, individual network contact, chlorophyll causal response or depth-based 3D ecological niches.
6. In parallel, original Zenodo 2026 48-species mammal archive is **1,788,505,978 bytes**, too large for predeclared 250MB/source cap. Its official `README.txt` is only 3,580 bytes, with provider MD5 `b03a51664b620a2cdd3cc38bb20b4215`. Reading that official source dictionary is allowed source-only; do not download or fit the 1.79 GB ZIP. Do not treat author-reported 1,344 individuals/48 species as our independent measured replication.

Everything prior (especially v25-D artifact and corrected v25-F primary history not supported) remains frozen.
