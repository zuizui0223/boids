# Published bat IF/TF reanalysis: stimulus-dependent spectral assumptions are not a validated motor law

**5 November 2026 — SOURCE-BACKED SECONDARY REANALYSIS, NO NEW ANIMAL MEASUREMENTS.** The original 2026 authors already measured and published emitted IF, TF and other acoustic changes. The present model comparison and temporal sensitivity are not independent bat confirmation, a new causal experiment, or evidence of wild sonar foraging benefits. Preserve the frozen JAE/BE and preceding boids acoustic source/model results.

## Specific ecological/mechanistic question

In our previous *synthetic* FM sound model, changing terminal frequency (TF) while either holding emitted initial frequency (IF) constant or holding emitted bandwidth `B = IF−TF` constant produced radically different lag-optimized cross-correlations. Instead of selecting whichever proxy curve yielded the preferred result, we have now tested **which original emitted-sound convention better describes existing bat playback responses**, using the originally recorded IF and TF from the exact same published source calls.

Hase et al. 2026, *Proc. R. Soc. B*, DOI [10.1098/rspb.2026.0921](https://doi.org/10.1098/rspb.2026.0921), source Figshare [10.6084/m9.figshare.30937379](https://doi.org/10.6084/m9.figshare.30937379). Original `Data_jamming.csv` 12,308 source rows, SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`.

**Crucial distinction:** The published 2026 playback jamming stimuli were synthesized with bandwidth FIXED at 40 kHz. That does *not* demonstrate that real responding bats maintained the same bandwidth in their own subsequent emitted calls. Our previous toy model conflated these different quantities, and this secondary original-source analysis investigates the mismatch.

## The prerecord source comparison

- The [IF/TF analysis contract](PUBLISHED_IF_TF_PHYSICAL_CONVENTION_PREOUTPUT_V1.md) was committed BEFORE original numerical IF values were opened in this research branch, though the paper had already published source IF outcomes and the source TF outcomes had been inspected.
- The original source was pin-verified. **No source rows failed the shared finite IF/TF and downward-FM QC**.
- Eleven unique original bat-ID labels; seven source bats in each of **IPIlow**, **IPIhigh** and **SPLlow**. The pairwise original ID intersections are **4,5,5**; they are NOT 21 independent bats.
- Three experiment families each produced 35 eligible bat × stimulus-condition source cells; 105 condition-level observations, averaged within biological bats. Biological unit for model-error comparisons is the original bat ID.
- At bat×experiment×condition we averaged original stimulus Var/jammingTF subgroups equally after calculating source ON−OFF IF and TF medians within each subgroup (at least four original calls per state); require ≥3 original source condition levels per bat.
- Two **fixed**, no-fitted-coefficient approximations:
    - `M_start` predicted IF response `ΔIF=0`, source error `E_start = average(|ΔIF|)` kHz;
    - `M_band` predicted `ΔIF=ΔTF` (constant B), source error `E_band = average(|ΔIF−ΔTF|)` kHz.
  Define `D = E_band−E_start`. `D>0` favours the fixed-start *descriptive approximation*, `D<0` favours constant-bandwidth. This cannot identify a learned motor-control policy or neural adaptation.

### All-source original IF/TF response

| Original stimulus | Unique bats in this experiment | Mean ΔIF (kHz) | Mean ΔTF (kHz) | MAE fixed-IF (kHz) | MAE fixed-B (kHz) | D band−start (kHz) | Bat comparisons |
|---|---:|---:|---:|---:|---:|---:|---|
| **Low-TF playback, interval** (primary) | 7 | +0.789 | +0.535 | 3.170 | 2.941 | **−0.229** | 5/7 prefer B |
| High-TF playback, interval | 7 | +2.164 | −0.056 | 2.774 | 2.901 | **+0.128** | 7/7 prefer IF |
| Low-TF playback, sound level | 7 | +2.512 | +0.810 | 3.985 | 3.415 | **−0.569** | 7/7 prefer B |

Whole-bat percentile bootstrap 95% intervals for D are primary low-IPI **[−0.592,+0.133]**, high-IPI **[+0.059,+0.237]**, sound level **[−0.740,−0.381]**. These are source-specific, post-publication, exploratory and unadjusted for stimulus-family multiplicity; they are **not** independent experimental p-values.

**Numerical interpretation:** all model errors are large, about 2.8–4.0 kHz. In the high-TF condition the mean TF change is only −0.056 kHz, while IF changes by +2.16 kHz. Thus, the `7/7 fixed-IF wins` observation reflects a very small mean model-score margin (+0.128 kHz) **relative to both models' ~2.8 kHz errors**; it does NOT identify a distinct optimal start-frequency policy. For all real numbers `x=ΔIF, y=ΔTF`:
```
||x−y| − |x|| ≤ |y|.
```
When observed TF response has little magnitude, the two candidate predictions themselves differ little and any preferred label is intrinsically low-information. The mean `ΔTF` is not the mean absolute `|ΔTF|`, so do not misapply this bound using signed pooled mean TF alone.

## Source chronology exposes the strongest inferential limit

[Source timing/cohort audit](https://github.com/zuizui0223/boids/actions/runs/41923195416) verified **105/105 eligible original stimulus contexts have all OFF calls before all ON calls**. All three experimental families occur in that fixed order, and the 7+7+7 original bat experiments contain only eleven distinct bats.

The sequence is part of the original controlled playback design, but **stimulus activation and elapsed flight/recording time are perfectly confounded within these archived source contexts**. No new causal control is created merely by reanalysing IF/TF differences. The 2026 original paper's source design and mechanistic inference stand as published; we cannot claim our simple ON/OFF contrast independently distinguishes acoustic stimulus effects from all smooth time trends.

## Three locked post-outcome time-window checks (ALL shown)

The [timing-sensitivity contract](IF_TF_TEMPORAL_SENSITIVITY_POSTOUTCOME_DESIGN_V1.md) was recorded **after opening the full-window results**, but before inspecting IF/TF responses in those exact windows. Full original source was retained as the primary comparison. All windows keep biological n=7 and 35 bat-condition cells per experiment; they are not new independent animal replications.

**D = error of fixed-B − error of fixed-IF (kHz), using original median ON−OFF responses.**

| Stimulus | Full source | 1s before/after | 2s before/after | −2 to −0.5s vs +0.5 to +2s |
|---|---:|---:|---:|---:|
| IPIlow (primary) | −0.229 (B 5/7) | −0.113 (B 5/7) | −0.229 (B 6/7) | −0.292 (B 6/7) |
| IPIhigh | +0.128 (IF 7/7) | +0.171 (IF 6/7) | +0.093 (IF 7/7) | +0.136 (IF 5/7) |
| SPLlow | −0.569 (B 7/7) | **−0.107 (B 5/7)** | −0.490 (B 7/7) | −0.574 (B 7/7) |

The 1s SPLlow D source-bat bootstrap interval **[−0.436,+0.227]** includes zero, contrasting with the full-source negative interval **[−0.740,−0.381]**. The primary 1s IPIlow interval **[−0.354,+0.160]** also overlaps zero. All predeclared windows and mean-vs-median sensitivity variants are held in [permanent aggregate source-ledger JSON](IF_TF_SOURCE_TIME_PHYSICAL_CONVENTION_LEDGER_V1.json), including numerical effect values and original-bat counts.

This makes **temporal sensitivity and weak model performance visible**, rather than rescuing favourable signs from longer windows after inspecting them. Even at shorter windows, ON/OFF order is unaltered; this does not deconfound stimulus from chronological effects.

## Current scientific decision: source effect, but NO general bat control law

1. **Provenanced measured source:** original IF and TF can be compared on the same 2026 published bat calls and stimulus contexts. Contrary to a single universally invariant toy signal property, the simplified fixed-IF/fixed-bandwidth models have **source/context-dependent descriptive errors** and neither is adequately identified as a general motor strategy. This is a **secondary same-study diagnostic**, not a novel first observation that bats modify TF or IF.
2. **Time validity:** all original OFF samples precede ON. The most pronounced full-window apparent source model preference (SPLlow) weakens in the near-onset 1-second comparison, so source-time restriction must accompany any physical narrative.
3. **Ecological inference limit:** nothing here measures actual bat prey capture, echo misidentification, mental sonar "information versus interference", adaptive social decisions, or space/3D niches. Earlier source 2020 model captures and Hase 2026 simulated potential misdetections remain distinct endpoints.
4. **Novelty boundary:** waveform curvature, correlation and frequency adjustment are established prior acoustic concepts. Without original, independently admitted bat waveforms and true receiver/foraging outcomes, do **not** write a third "bats optimize spectral niches" manuscript. Do **not** turn this into a universal law by multiplying three correlated source experiments as independent species.

## Reproducibility and actions

- Source response + 14 fictional unit tests: [CI 41922688245](https://github.com/zuizui0223/boids/actions/runs/41922688245).
- Source-clock/cohort preflight: [CI 41923195416](https://github.com/zuizui0223/boids/actions/runs/41923195416).
- Three fixed source time windows, 7 synthetic tests: [CI 41923633026](https://github.com/zuizui0223/boids/actions/runs/41923633026).
- Full 24-cell permanent source aggregate and signed numerical/CI ledger: [IF_TF_SOURCE_TIME_PHYSICAL_CONVENTION_LEDGER_V1.json](IF_TF_SOURCE_TIME_PHYSICAL_CONVENTION_LEDGER_V1.json).
- Recompute source figures and compare to permanent ledger (also versioned source SHA and Git blob): `verify_IF_TF_source_time_ledger_v1.py` and matching GitHub Actions workflow.

**No raw original bat IDs/rows were committed, no novel animal measurements were performed, and the JAE/BE bat publication versions remain untouched. PR #36 must remain Draft.**
