# Original echo clustering helper: repeated points versus repeated calls — pre-output 2026-11-08

**Separate exact SOURCE-HELPER MICROBENCHMARK, not original Mazar & Yovel 2026 clustered-cave simulation.** Source MIT GitHub pinned SHA `a74fb61a8efb57ca37693893c3bd7b35fa94fa89`, `findRepeatedClusters.m` blob `890bbbfdc0628c2c7d0c8e392c0cd99c55de8e72`, `distanceTHClustering.m` blob `65a6a2079319220d324587ca0260b06e4a4f35dd`. The main cluster function required by `BatFlightForGui.m` is missing from both original GitHub and Zenodo archives (Actions `42436920370`). The archived Confusion experiment sets `ObsRepeationsFlag=0`; it is NOT an authentic reproduction of the paper's used cluster branch.

## Narrow audit question

The available helper computes `echoesTH = numOfRelevantCalls*ObsEchoesRatioTH` for ratio<1 but evaluates `numPointsInCluster>=echoesTH`. Does this treat multiple detections from **one emitted call** as if they provided repeat support over **multiple calls**? This is an implementation/measurement-grain audit, not a claim that the original authors did not know or that real bats make this error.

## Freeze exactly two synthetic 10-call cases before output

- 10 *source-like* distinct calls, all have ≥1 valid detection; invented 2D positions with **three close echo points** at x=0,0.9,1.8, plus **nine independent isolated** positions x=10,20,...,90 at y=0. Same 12 point cloud, all coordinates and total calls identical.
- Preserve near echo ordering within concatenated vector as [.9,0,1.8] as far as the source helper clustering seed; arrange other distant points after the seed in order that does not affect the near cluster. Use D=1 synthetic units, original-source ratio `ObsEchoesRatioTH=0.22`; ten echo-bearing source calls → count threshold 2.2, accepting integer groups of size≥3. Do not tune after result.
- **Scenario A one-call triplicate:** all three near detections belong to ONE call, the other 9 source calls each have one distant detection.
- **Scenario B three-call repetition:** near detections belong to THREE separate calls, distribute nine isolated far detections across the same ten nonempty calls so the 12 point coordinates are identical. Their within-source sequential geometry order may differ, but clustering outcome should be identical because first near seed sees both other near points irrespective of distant isolated points.
- Compare SOURCE-helper cluster acceptance based on **points** and alternative NOT-SOURCE comparator based on **number of distinct call IDs contributing to accepted cluster**. Report source accepted group size, call count, number of original calls, ratio, and no new animal data.
- No inference on real bat false obstacle detection, wall collisions, cave exit, prey handling, biological memory, or the main source's published clustered algorithm. The possibility that within-one-call multiple reflections should count as valid spatial evidence is real; this is NOT automatically a code bug, merely a different estimand than cross-call recurrence.

If distinct-call count differs while source acceptance is equal, record the decision-grain discrepancy. No parameter retuning, original-model substitution, hidden source file recreation or causal bat claim.
