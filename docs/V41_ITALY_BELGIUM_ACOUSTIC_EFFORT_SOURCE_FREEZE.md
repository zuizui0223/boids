# v41 — Independent Italian and Belgian acoustic effort and source-grain audit

**Frozen on 2026-11-19 JST before opening any source \`bat_presence\`, pulse-count, \`PULSES\`, call parameters, feeding activity, arthropod abundance or other behavioral numerical values.** Explicitly source-only; not a post-hoc rescue of Finnish v39 negative region transfer.

## Scientific aim

Determine whether the Italian and Belgian original published acoustic tables can be treated as *effort-complete recording windows* comparable to Finland’s original source. If not, do NOT fit joint regional bat activity or apparent zero-activity models.

**Previously verified exact original files:**
- Italy \`Databats_Cansiglio.csv\`, Zenodo 21808015, publisher MD5 \`76b954fd896ad182aa5a9b97516b6535\`. v38 verified 64,275 detection records, 17 SITE labels, 119 DATE labels, 29 SPECIES labels. Relevant source columns: SITE, TREATMENT, DATE, TIME-12, SPECIES, PULSES, FILES, USERID.
- Belgium \`Obs.AudioMoths-bats_activity.csv\`, Zenodo 20137204, publisher MD5 \`d0588f30bf4ed86a168c5438373e6019\`. v38 verified 2,834 bat-acoustic activity rows. Relevant source columns: Loc, Consent, Filepath, Filename, Group, bat_presence, Date, Time, Valid.
- Belgium \`metadata_loc.csv\`, Zenodo 20137204, publisher MD5 \`9672cb0e7dec4d0811540458375229b1\`, 27 original field-level rows, includes Loc, Datum_audio, cover/tree-structure variables.
- Source accompanying methods state the Belgian acoustic deployments sampled 1 minute in every 15-minute interval for 48 h. This published **schedule alone does NOT establish that an event table includes all zero-detection microphone minutes**.

## Exact structural questions only

1. Re-download each original file from the exact public Zenodo record and reverify complete published MD5/SHA256; refuse any non-original file. Do not log original site name, filename, GPS or exact timestamps.
2. Count original **site × date × recorded time token** combinations, fully qualified original file tokens (as opaque hashed IDs), number of activity rows per such file/time token and per site-date, and proportion of site-dates with multiple recording-time tokens. Do not read numerical \`bat_presence\`, PULSES or \`Valid\` values.
3. For Belgian original \`Loc\` labels, report count (not identity) matching the independently published 27 metadata plot \`Loc\` values, and count unmatched labels; no data-row amplification or recorded numeric ecological response values.
4. For Italy, separately count rows and unique file tokens per site-date and whether \`FILES\` is nonempty. A token labeled FILES may be source reference or count, **not proof that all untriggered zero-detection recordings exist**.
5. Explicit **complete-effort admission** only when source files themselves provide enumerated **all scheduled recorder windows (including zero-activity minutes)** and independent recording start/stop or per-window validity. Mere presence of unique timestamps, repeated filenames, a fixed scheduled sampling statement or a \`bat_presence\` field cannot alone prove that all missing windows are true zeros. No more than source grain can be claimed.
6. A country-comparable intensity model additionally requires measured, physically equivalent effort denominators and compatible call classification across Finland, Italy and Belgium. If not established, status \`EFFORT_DENOMINATOR_NOT_VERIFIED_STOP\`. This is a **source observability stop**, not a test of a true ecological absence of common thermal activity rules.

## No outcome and new-hypothesis ceiling

The original Finnish paper’s environmental activity response and the v39 7-year/3-region forecast were already opened, so any additional Finnish modeling is post-outcome and may not be relabelled preregistered. No output of v41 may convert Finnish p=.0625 into a positive universal bat finding. Source metadata alone does not show predator avoidance, sonar steering, prey detection, energy gain, learning or competition.

Preserve all frozen prior empirical results; keep v38/v39/v40 separate from the source-only v41. A genuinely new cross-country prediction requires a **new preregistered task and independently source-confirmed effort denominator**; do not define 0-night recording windows by assuming silence wherever no detector record was published.
