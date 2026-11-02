# v35 pre-outcome source gate for tidal Boids group-movement test
2026-11-02 JST. This version counts genuine source OBSERVABILITY only. No social parameter, causal interaction, or GPS-derived group alignment effect is fitted in this stage.

Goal: determine whether the original native high-cadence source (not its first-fix-per-hour version) has enough paired positions with independent prior and next displacement headings to attempt actual-neighbor vs ghost-neighbor field prediction.

Data fixed: original 2010 & 2011 Zenodo 22296922 GPS gzip archives, provider-original MD5 checks identical to v30, all valid visible original fixes inside lat [53.2,53.7], lon [5.7,6.6]. Use original native timestamps as **unverified UTC or GPS time**, but within-year relative timestamp tests unaffected by constant 15-second offset. Require unique event-id and source individual-local-identifier.

For every original bird fix, build historical heading only if immediate previous fix 120–1800 seconds earlier and observed displacement speed 0.4–80km/h. Separately build next-step heading for eligibility only if immediate next fix 120–1800s later and same speed range. None of the next-step coordinates may be used as a source predictor in this feasibility gate.

For every actual different-bird pair within 5 recorded seconds and 100m great-circle distance, eligibility requires both animals' **preceding heading** and focal animal **next-step heading** available. For both orientations of an eligible pair count but also collapse distinct (calendar day, undirected bird dyad) units; do not treat thousands of colocated fixes as independent social replicates. Source diagnostics: numbers of raw near-pairs, two-history/neighbour-heading-qualified pairs, unique source birds, dyads, dyad-days and calendar days, per year. No raw GPS, bird IDs, pair locations or timestamps are committed or printed.

Primary feasibility admission rule: >=200 qualifying directed pairs, >=5 participating birds, >=5 distinct dyads and >=10 days in **at least one 2010 or 2011 source year**. Otherwise M3 movement-history forecast marked NOT_ADMITTED. Passing this gate permits designing a future *heldout* neighbor-vs-ghost test; it DOES NOT establish social steering.

Prospective actual movement forecast (separate future prefreeze): own prior heading + tide height/phase + geography/clock baseline versus addition of contemporaneous other-bird **prior-only** heading, versus synthetic ghost drawn from another day at matched site/tide/season; whole dyad connected-group holdout, source clock/GPS error controls. Do not use neighbor's future position or infer Reynolds Boids coefficients from apparent alignment.
