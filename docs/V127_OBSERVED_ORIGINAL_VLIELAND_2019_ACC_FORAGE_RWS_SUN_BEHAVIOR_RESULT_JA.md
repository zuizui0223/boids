# v127 observed 2019 Vlieland oystercatcher ACC-classified forage/inactive × RWS measured tide × solar

2026-11-14 JST. **TRUE ORIGINAL FIELD/SENSOR RESULT**, GitHub Actions [#43461048062](https://github.com/zuizui0223/boids/actions/runs/43461048062) SUCCESS, nine tests passed. Frozen protocol committed BEFORE true 2019 ACC tide×sun outcomes. Not visually observed eating, actual feeding time, prey, local dry-flat access or an internal clock.

## Exact authentic sources and sampling
- Corrected original 2019 O_VLIELAND Zenodo [record 10053988](https://zenodo.org/records/10053988), actual ACC-derived behavioral classes original publisher MD5 a902b08ff0163edf91a9bcf3822b1c97, GPS original MD5 65426aedf6f48c36f81990268d267c7b.
- Before any new Y, original v125/v126 source fully REPLAYED: **1,817,033** classifier events across **43** genuine birds; **1,193,728** original 2019 GPS rows / **42** source GPS birds; **1,567,093** same-bird GPS matches ±15min; **792,527** original forage/inactive events within 25km of fixed harbour station; 37 source birds with ≥100 each class in ≥2 months.
- Original June–Sept 2019 192,730 true tagged-bird×UTC-quarterhour source bins (28 tagged birds), 155,472 native forage and 258,830 inactive classifier EVENTS; 31,176 native bins had both labels. Multiple ACC events/burst do not represent multiple birds or a known number of feeding minutes.
- Original RWS gauge Vlieland Haven, four true MONTHLY observed 10min WATHTE cm NAP series: June4,321, July4,465, Aug4,465, Sep4,321; inclusive month-boundary duplicates reduce to **17,569 unique original RWS measured UTC time points**. Tide slope from exactly observed 20min difference, source near GPS classification representative time within 7.5min, exact measured height bins 0.25m NAP and rising/falling; sun elevation at original GPS WGS84 >+3° day/<−3° night, twilight excluded.
- Source 4-condition (rising/falling × day/night) gate in each genuine bird×month×same height source stratum ≥5 bird-quarterhour bins from ≥3 real dates in EACH cell; need ≥8 birds/20 complete groups/1,000 bins/2 months. Original source **PASSED**: **28 real tagged birds**, **803** qualifying bird×month×height four-cell groups, **170,063** genuine tagged-bird quarterhour source windows, all four months. Before full four-cell gate, 177,780 RWS/sun matches, 11,977 true astronomical twilight exclusions, 2,973 missing tide/slack matches. Source day/night recording opportunities differ by month and need monitoring.

## Genuinely observed original 28-bird source conditional classifier-share effects
Y in each source bird×15-minute bin is n_ACC_foragelabel/(n_ACC_foragelabel+n_ACC_inactivelabel), conditional on having one or both original classified categories. Other source labels walk/fly/preen are excluded, NOT treated as inactive. This is NOT observed feeding minutes or true feeding success.

For four source cell means p_FD, p_FN, p_ED, p_EN where F=rising, E=falling, D=day, N=night: B=balanced mean; S=0.5[(p_FN−p_FD)+(p_EN−p_ED)] (night−day); T=0.5[(p_FN−p_EN)+(p_FD−p_ED)] (rising−falling); **primary I=(p_FN−p_FD)−(p_EN−p_ED)** (tide×sun). Equal true height source groups within bird-month, months within bird, then original independently tagged bird equal-weight. 10,000 whole-bird bootstrap, seed20261112. All intervals nominal observational, not causal or multiplicity adjusted.

| Outcome | Original bird-equal estimate | True-bird bootstrap 95% CI | Individual sign |
|---|---:|---|---|
| Balanced conditional ACC forage classifier share B | **0.3883458** | [0.3659975,0.4122247] | 28/28 >0 (baseline) |
| **Solar night−day S** | **−0.1138426** | **[−0.1298397,−0.0979783]** | **0/28 >0; all birds negative** |
| Tide rising−falling T | **−0.0569056** | [−0.0911784,−0.0219415] | 8/28 >0 |
| **Real tide×sun interaction I** | **−0.0459232** | **[−0.0659405,−0.0256683]** | 3/28 >0 |

**Solar temporal association:** Within this genuine 2019 original GPS-ACC source, the share of sensor events classified forage (vs inactive) is lower at night by about 11.38 percentage points after real tagged-bird/month/height/phase source balancing. The sign is negative in all 28 birds. This is closer to real behavior than GPS displacement or mapped wetland locations, but is still a sensor-event class SHARE and cannot be called an 11.38-point difference in feeding-time budget. Sampled bird/ACC recording effort, night-time tag schedule, habitat, prey and classifier errors can generate apparent effects.

**CRITICAL NEGATIVE TIDAL-UNIQUENESS CONTROL**: although I real 2019 source CI excludes0, mandatory phase ghosts (+3,+7,+11 entire calendar days of original REAL RWS stage while GPS/sun/class labels remain unchanged) also pass original source gates, with strong/more extreme I:
- real aligned tide I **−0.0459232**, bird95 [−0.0659405,−0.0256683].
- **wrong +3 days I +0.0797179**, bird95 [+0.053395,+0.105917], OPPOSITE and BIGGER absolute effect.
- wrong +7 days I +0.0100026, bird95 [−0.015106,+0.032239].
- **wrong +11 days I −0.0547481**, bird95 [−0.080082,−0.031426], same sign BIGGER than real.
These ghosts are descriptive (support strata may change under shifts), not formal randomization p or field experiments. They undermine a **correct-tide-specific behavioral entrainment** claim despite a nonzero nominal I. The harbour water level within 25km is not the real water-height h(x,t) of all birds' local intertidal patches.

## What this adds to the overall paper
Physical 2019 tide-form×sun coincidence across 130 source coasts v100 is largely a four-harmonic no-animal expectation, not novel ecology. Genuine 2020 two Larus taxa GPS displacement and static GIC wetland location interactions with true tide×sun v111/v112/v115 were not established or matched by ghosts, although mapped static spatial location enrichment differed. An independent 2019 oystercatcher study now provides true **ACC-inferred behavioral STATE classification** as Y and a consistent solar night/day association; actual tide-phase interaction **still lacks unique correct-phase evidence**. This supports separating solar time organization from tidal phase-specific organization rather than claiming a universal two-clock niche law.

Original study publishes 2016–2021 tags, but 103 cumulative Vlieland tags are not annual 2019 N. Same species as historical 2010 Wadden oystercatchers, different individuals/source. An older oystercatcher accelerometer validation study (DOI 10.1371/journal.pone.0037997) documents classifier ambiguity for forage vs walking, but its error rates are NOT necessarily those of this exact 2019 dataset.

## Next independent falsification (not yet observed)
Fix another calendar-year source **2018 O_VLIELAND**, publisher ORIGINAL GPS MD5 113a796ab087234f4282b97af02e7559 and original ACC-class file MD5 2b079f5504a692a02db57dc7116e5a67. Use exactly the 2019 June–September quarterhour, 25km, same real harbour-stage, astronomical and whole-bird hierarchy with no after-outcome year/threshold tuning. Need honest source availability, track identity overlap between 2018/2019 and original ACC classifier metadata; 2018 would be same study/taxon but independent calendar year, not new independent species/shore.

Source original run #43461048062; prior 2019 native original GPS/ACC and 48-hour true tide source #43220491868; original Zenodo data paper van der Kolk et al. 2022 DOI 10.3897/zookeys.1123.90623. No raw bird ID, GPS lat/lon, exact UTC timestamps, original tide series or per-individual coefficients are published in result artifact.
