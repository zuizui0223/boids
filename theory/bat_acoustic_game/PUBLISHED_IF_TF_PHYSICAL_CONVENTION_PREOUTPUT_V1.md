# Source-reuse analysis freeze — emitted IF vs TF and bandwidth (2026-11-05)

**Recorded before opening numerical IF measurements in this branch.** This is a **secondary reanalysis of already-published, previously studied bats**, not a registered independent experiment, new acoustic recordings, new validation species, or a causal demonstration. The Hase 2026 original paper and Fig. S2 already addressed IF behavior; do not rebrand established IF or TF patterns as a novel discovery. Keep original 2020/2026 model runs and earlier `boids` PR #36 outcomes immutable.

## Motivation: test a physical intervention-definition gap in our own v1/v2

Source 2026 Hase et al. *Proceedings B* DOI 10.1098/rspb.2026.0921, Figshare DOI 10.6084/m9.figshare.30937379. The published `Data_jamming.csv` has **12,308** rows, exactly **11 original bat-ID labels**, `IF` (initial emitted frequency kHz), `TF` (terminal emitted frequency kHz), `DUR`, source `Experiment`, `Condition`, `Var`, `jammingTF`, `isON` and timestamps. Original SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`.

In our toy pulse crosswalk, one manipulation fixes IF and changes bandwidth (fixed-start); the other fixes bandwidth and shifts IF with TF (fixed-B). But the 2026 source paper explicitly studied emitted TF. Which signal constraint is a better **descriptive approximation** to the existing source's playback response? This source reanalysis can bound our toy's latent degree of freedom, NOT establish an evolutionary optimal frequency policy.

## Frozen source and biological units

1. Download ONLY the original single Figshare CSV through verified official metadata and compare exact SHA256 against `2998...`. STOP on mismatch; never upload raw rows, original IDs or animal timestamps to GitHub artifacts.
2. Parse `IF` and `TF` in their original kHz without rounding, filling or arbitrary rescaling, as finite float on the **same source row**; parse `DUR` only for optional source-quality diagnostics. Require IF > TF for an admitted FM pulse, otherwise exclude as a source-quality issue and report counts, not repaired values.
3. Group by exact `ID × Experiment × Condition × Var × jammingTF × isON`, accepting source `isON` 0 vs 1 only, **minimum 4 source rows per ON and OFF** after row-level quality filters. This matches earlier TF-only reanalysis structure but the IF+TF complete-case cohort may differ.
4. For each admitted context, calculate `ΔIF = median(IF_ON)-median(IF_OFF)`, `ΔTF = median(TF_ON)-median(TF_OFF)`, `ΔB = ΔIF-ΔTF`. Means instead of medians using **the identical eligible source groups** form the fixed sensitivity. No pulse-level inferential independence.
5. Aggregate Var/jammingTF subcontexts **equally** within each individual × experiment × stimulus condition. For each bat × experiment with at least **3 eligible distinct levels**, compare:
   - `M_start` fixed emitted initial frequency: expected `ΔIF=0`, error per condition `|ΔIF|` kHz.
   - `M_band` fixed emitted bandwidth: expected `ΔIF=ΔTF`, error per condition `|ΔIF-ΔTF|` kHz.
   Calculate bat-level mean errors `E_start`, `E_band`, `D=E_band-E_start`. **D>0** favours fixed-start; D<0 favours fixed-bandwidth; D=0 tie. Model comparison is descriptive approximation error, *not an independently discovered biological reaction model or probability*.
6. **Primary experiment = IPIlow**, the one with the reproducible 7/7 TF dose response in earlier source-reuse. Do not select the best looking experiment or stimulus window after viewing IF. IPIhigh and SPLlow are exploratory secondary; report all alongside IPIlow, and report unique vs reused biological individuals across experiments as denominators.
7. Report mean and median `ΔIF`, `ΔTF`, `ΔB` per bat (mean across condition averages), mean and median D across bats, both raw model errors, biological animal count and number of eligible bat-condition cells. 5,000-seed whole-bat nonparametric bootstrap (fixed RNG seed 20261105) for **descriptive** mean D uncertainty. An exact bat-level sign test may be reported with explicit post-publication status; do not call it confirmatory or multiply the three experiment n values as new biological replicates.
8. Required sensitivity: replicate the same fixed complete-case source groups with ON/OFF **means**, and additionally report a leave-one-bat-out range of equal-bat D (no source subgroup or threshold selection).
9. **No source-defined sequence-causal claim:** ON and OFF may differ in stimulus chronology, time since playback, and bat state. No evidence of differential real prey capture, sound-source masking, true echo-arrival ranging or original 2026 moving-group model replication can follow. Trial duration differences and observer measurement limits remain possible.
10. Predefined STOP: if fewer than 5 actual bats with ≥3 eligible IPIlow stimulus conditions (after shared IF/TF QC), publish source eligibility STOP only and **do not** change thresholds or substitute high-TF/SPL as the primary.

## What an informative result would mean

- If `M_start` predicts observed IF shifts better: the fixed-bandwidth FM pulses in the existing **toy simulation** should be declared a potentially inappropriate *physical perturbation model* for real emitted response; a result does not prove real bats optimize 3D sonar overlap.
- If `M_band` predicts better: fixed-bandwidth toy is less contradicted by these source IF/TF responses, but the published individual-signal measurement definitions and source 2018 group-flight contexts remain different.
- If mixed/near tie: the true physical coupling of IF and TF is not adequately identified as one universal model by this archive; no exponents should be tuned to obtain an interesting correlation.
- All outcomes carry original paper prior-art constraints. Freeze both model hypotheses independent of the IF values; store source SHA, source bat counts, complete method and all source eligible errors (aggregates only) with reproducible CI tests.

**Required next stop:** preserve v1/v2 waveform results, never present a conclusion about JAR capture benefits, novel learning, phylogenetic generality or bona fide biological sonar motor laws without independent endpoint data.
