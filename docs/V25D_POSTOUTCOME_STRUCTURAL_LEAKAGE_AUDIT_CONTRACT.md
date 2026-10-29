# v25-D2: POST-OUTCOME audit of suspicious 100% original TRUE/FALSE profile ranking

Registered 2026-10-29 JST AFTER v25-D1 outcomes were opened in original [Actions 40841206422](https://github.com/zuizui0223/boids/actions/runs/40841206422). NOT a new confirmatory test. Original v25-C source-domain STOP and D1 observed results remain immutable: M1/M2/M3 all reportedly 100% paired rank, M1 logloss 0.04626, M3 0.04040; 492 birdyear and 188,812 later source profiles.

## Why this audit is mandatory

[Original paper](https://doi.org/10.3389/fevo.2023.1232704) reports each TRUE used GPS location classified by habitat, whereas the FALSE original source row contains summarized proportions of habitats reachable under 100 simulated movements. The USGS original source CSV contains only two rows per timestamp (1 TRUE, 1 FALSE) and not the 101 candidate alternatives. Source-only D0 verified that all seven habitat fields contain percentage integers 0–100. Thus original TRUE may be one-hot and FALSE a mixed average; this *encoding asymmetry* can cause perfect TRUE-vs-FALSE ranking without revealing genuine habitat preferences.

## Post-outcome D2 exact diagnostic (not confirmatory)

1. Acquire exact unchanged USGS CSV 27,997,528 bytes, provider MD5 78eb6064eca992225d6907d6e46f5bef, independent SHA256 1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15. Source 380,578 rows, 190,289 exact TRUE/FALSE source pairs.
2. Calculate for every original source row (separately by original TRUE/FALSE): sum of seven raw % categories, number of nonzero categories, maximum percentage, indicator of exactly one 100 and six 0 fields, normalized Shannon entropy among seven categories. Report full category-count distributions and original TRUE vs FALSE one-hot rates; no habitat original raw data row or original animal identifier exported.
3. Three FROZEN, NO-FITTING structural rules: choose larger maximum habitat category percent, choose fewer nonzero habitat categories, and choose lower Shannon entropy; tie scores=0.5. Score all source pairs, both overall and birdyear-cluster averaged, and report all ties/negative results. These rules have no training labels, ecological coefficients, individual history, or outcome-tuned thresholds. Report fraction paired TRUE and FALSE vectors exactly equal and number of FALSE profiles with max exactly 100.
4. If simple structural rules achieve near-perfect classification, downgrade D1's 100% rank as a likely source-encoding artifact and DO NOT present it as perfect biological habitat choice or cognitive memory inference. D1 numerical result remains reported but interpretation changes in separately logged D2.
5. Do not retrain original M1/M2/M3 or adjust v25-D1. Do not generate imagined 100 random candidates, source step origin or pairwise movement vector. Raw USGS individual timestamps, GPS positions and habitat rows are not redistributed.
6. Original author availability was simulated with movement kernels estimated from observed steps, possibly including test groups, so the source's FALSE summary is retrospective, not operational future destination availability. This remains a fundamental limitation even if structural classification is not perfect.

Full source audit output is post-outcome descriptive credibility checking ONLY. Original v13–v24 frozen results and v25-C stop unchanged.
