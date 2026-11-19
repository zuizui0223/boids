# v41 source audit — original Italy/Belgium bat recording effort NOT confirmed

**Executed 2026-11-19 JST.** Workflow [44465005127](https://github.com/zuizui0223/boids/actions/runs/44465005127), four synthetic no-zero-invention tests PASS, all three original source files fully verified against published Zenodo MD5 and SHA256. Audit only structural source-site, date/time and file tokens, **never** bat_presence, PULSES, call frequency, insect counts, original habitat values, sensor quality response, or per-site GPS.

## Data and structural results

| Structural count | Italy Cansiglio | Belgium DIGITAF bat activity |
|---|---:|---:|
| Original source rows | 64,275 | 2,834 |
| Distinct site tokens | 17 | 27 |
| Distinct date strings | 119 | 22 |
| Distinct site × date keys | **787** | **62** |
| Distinct site × date × time-token keys | 50,845 | 411 |
| Distinct site × date × file-reference keys | 787 | 2,685 |
| Site-date keys with >=2 distinct recorded time tokens | 754 | 50 |
| Nonempty file-reference token rows | 64,275 | 2,834 |

Italy's source \`FILES\` token has only one distinct value per site-date under the inspected original file granularity; it cannot be assumed to be a complete catalogue of all sampling minutes. Belgium has 2,685 site-date-file tokens from 2,834 event rows, some repeated up to five times. A file token or detector-triggered event record is not itself proof of a full 48-hour log of zero/nonzero bins.

**Belgium source habitat linkage:** 27/27 original acoustic \`Loc\` labels appear in the exact original published \`metadata_loc.csv\` (27 metadata records); zero activity-site labels are unmatched. This establishes a plausible valid plot-level association key, **not that bat activity and pitfall prey were sampled simultaneously or that omitted zero detections are true absence**.

## Verdict and next required data

**\`EFFORT_DENOMINATOR_NOT_VERIFIED_STOP\`.** The original CSVs list acoustic activities/detection records and their audio filename/time identifiers but do not independently establish the enumeration and recorder validity of *all* scheduled monitoring windows, including non-detection. Treating missing events as zero detection would be an ungrounded denominator invention. No cross-country bat time-allocation, occupancy or activity-intensity prediction was fitted. This verdict is an observational-source limit, **not evidence that activity differs physiologically or that the Finnish thermal effect is absent elsewhere**.

For genuinely comparable acoustic activity models, acquire original recordings and complete sensor deployment/recorder-on logs, or an explicit effort table listing all attempted windows and valid negatives, plus matched ambient weather and consistent acoustic call labeling. The Belgian 27-site environmental join may be used in a **separately predeclared detection-conditional** comparison if appropriate independent observational units and selection bias are handled; this cannot become a three-country universal behavioral claim.

## Frozen previous results

- v38 7/7 original Finland/Italy/Belgium source MD5 verified.
- v38b original four-bin gate FAIL; six categorical phases were observed.
- v38c separately frozen six-bin source gate PASS on 4,536 active detector-nights; v39 used darkness Q1–Q4 only.
- v39 seven-year +0.017943 nats/night mean but exact sign p=0.0625 => **PRIMARY POSITIVE GATE FAIL**. Three-region gain **−0.038835**. Both frozen.
- v40 post-outcome climate-envelope diagnostic: no new fit or inferential test; spatial failure not explained simply by out-of-envelope environmental conditions.
- v41 source-structure effort STOP; no behavioral values decoded and no zero-night fabrication.

Do not merge v38–v41 into a causally asserted behavioral law or silently dilute the original preregistered decision conditions. Keep original \`batter\` and \`boids\` v30/v37 findings unchanged.
