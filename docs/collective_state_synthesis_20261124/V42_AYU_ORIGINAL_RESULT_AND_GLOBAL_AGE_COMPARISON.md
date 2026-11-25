# v42 initial actual-source result: Ayu does not pass the joint locality-age replication gate

2026-11-24 JST. [Original run 45404183787](https://github.com/zuizui0223/boids/actions/runs/45404183787), ayu job 138480329911 SUCCESS. [Original aggregate artifact 14923998689](https://github.com/zuizui0223/boids/actions/runs/45404183787/artifacts/14923998689). Actual downloaded ZIP SHA256 ab935d966b2bca6c54b56a68b8908004b24f625143ffc6f26bf410310466749b; original ayu.json SHA256 84e30c425ec498b0474ea6be78de506514331f0f49038ce4cf0ebcc3a6676119. Independent local NumPy reaggregation of all seven signed file-level D and three matched-control contrast vectors agreed with receipt; all 11 v30 and four new v42 synthetic tests passed in original job. Source commit 158e8d7ebdef73752da63192ee36e3a099dd5dfa, original seven author Git blob hashes/size, 30fps native source, v30 cohort and baseline replay PASS. No raw fish trajectories shared.

| Matched six model MSE | Short | Delayed |
|---|---:|---:|
| G | 9089.390661008143 | 33202.574651311894 |
| GLOBAL | 8052.661206246253 | 28766.867592393617 |
| NEAR_TRUE | 7986.43987617193 | 28768.81748273432 |
| FAR_TRUE | 7992.494885673668 | 28767.085053926956 |
| NEAR_ROT1 | 8053.132271339652 | 28769.81510092455 |
| NEAR_STALE_0.2S | 8044.573519059101 | 28759.615854030508 |

Equal-recording GLOBAL minus NEAR: short +66.2213301 (0.822353% relative MSE improvement), 6/7 positive, descriptive 95% bootstrap [17.8043,122.3377]; delayed −1.9498903 (−0.006778%), 3/7 positive, interval [−7.1061,2.7894]. Source units are original numeric XY/s squared, not comparable with other studies. All file IDs/order and individual values remain in original artifact.

Short correct mapping vs rotated +66.6923952 (6/7); correct vs far +6.0550095 (5/7); current vs stale +58.1336429 (7/7). Delayed +0.9976182 (5/7), −1.7324288 (2/7), −9.2016287 (1/7) respectively. The short current-vs-stale contrast is positive in all files, but delayed near gain does not reliably persist. Because D is nonpositive in some files in both horizons, frozen primary paired ratio test is NOT ADMITTED (RATIO_GATE_STOP_NONPOSITIVE_DENOMINATOR). Delayed mean D negative, ratio of means undefined. No exclusion of adverse files or denominator rescue. This is not a new independent species test beyond earlier ayu source, nor a causal null of fish social behavior.

## Separate secondary existing global-state age comparison

[Machine-readable comparison](POSTRESULT_GLOBAL_AGE_ACROSS_HORIZONS_RECEIPT.json) reaggregates fixed v30 three-species and v32 12-shoal global-state age curves, distinct from local-neighbor v42. At age .2s the delayed relative loss increases in tetra +8.165pp, ayu +2.000pp, and 12-shoal stickleback +3.034pp (three-file stickleback sensitivity +.582pp). At .4s same directions in full group stickleback +2.785pp, tetra +2.992pp, ayu +.980pp, but three-file stickleback −2.869pp. At 1s and 2s directions are mixed. These are aggregate normalized predictive score differences, no pooled effect, no cross-species mechanistic or general age law, no new fits. The robust unifying question is when the current collective state retains predictive value; the local horizon pattern is not universal.

Tetra job status not yet included in this note. Frozen protocol and main remain unchanged.
