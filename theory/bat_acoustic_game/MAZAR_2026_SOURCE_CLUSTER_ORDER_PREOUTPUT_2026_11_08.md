# Source helper permutation-invariance gate — 2026-11-08

**Pre-output locked numerical diagnostic, source-inspired and simulator source-microkernel only.** No new bat measurements, no full 2026 *eLife* author simulator replay, and no claim that the published eLife Figure 4 used this particular fallback implementation. This follows discovery that original main GitHub and Zenodo source archives both LACK `BatManueverDecision_FullConfusion_ver08Aug24.m` (although `BatFlightForGui.m` calls it when clustering is enabled in original confusion-workbook defaults). The absence itself is independently verified in source-authority CI `42436920370`, not a behavioral observation.

## Available MIT source code, distinct from missing published clustering path

Original pinned MIT author `omermazar/Colony-Exit-Bat-Simulation` SHA `a74fb61a8efb57ca37693893c3bd7b35fa94fa89` has `findRepeatedClusters.m` Git blob `890bbbfdc0628c2c7d0c8e392c0cd99c55de8e72`, `distanceTHClustering.m` blob `65a6a2079319220d324587ca0260b06e4a4f35dd`, and `BatManueverDecisionXXX.m` blob `e8b6eeed398eec16b6486853fb68358220042c59`.

Important source lineage nuance: `BatManueverDecisionXXX.m` contains `findRepeatedClusters` only when `ObsRepeationsFlag` is TRUE, whereas the accessible `CaveExit_Experiment_Confusion.m` explicitly sets `ObsRepeationsFlag=0`. Its source `ObsClusterFlag=1` instead invokes the **missing distinct function**. Therefore THIS helper's numerical behavior CANNOT be presented as a reproduction or disproof of the paper's actual multi-call clustering result.

## Tested property and fixed synthetic input before numerical output

Source helper `distanceTHClustering(X,maxDist)` iterates through points in original order. For the first unused *seed* it chooses only other unused input points within the fixed Euclidean threshold D of that seed. It forms one cluster and marks direct neighbors used, with **no neighbor-of-neighbor recursion or permutation-invariant graph connected-components**. The source helper `findRepeatedClusters` accepts clusters with number of points >= `echoesTH`; `echoesTH=numOfRelevantCalls*echoesRatioTH` for `echoesRatioTH<1`. Original experiment `ObsEchoesRatioTH=0.22`, and source may remember 10 calls in its confusion experiment.

Prepare exactly 10 **invented** calls, each one static 2D echo:
- three possible positions on a short line: x=0,0.9,1.8 (y=0);
- seven isolated positions x=10,20,30,40,50,60,70 (y=0); no points discarded.
- threshold D=1.0 synthetic units (NOT the original arena units); `echoesRatioTH=.22`; ten nonempty call records -> eligible cluster needs >=2.2 points, i.e. 3.
- Vary only the **six relative orderings** of the three short-line points; keep seven isolated points after them in a fixed order. All ten physical positions and call count identical. No measured original bat signal.
- Run exact source helper direct-seed clustering port, source cluster threshold and mean centers; report number accepted obstacle groups and the positions; compare to a separate explicitly NOT source-equivalent single-link connected-component (union-find) comparator that merges transitive neighbors and is point-permutation invariant. This comparator is a property diagnostic, NOT a fix claimed to be used by bats or published authors.
- Do not tune D, ratio, anchor coordinates or test count after opening result. No exposure or fitness loss assigned. Add invented fixtures for edge cases, permutation invariance of comparison model, and exact source branching.

## Scientific interpretation cap

If the same static point cloud yields different source helper cluster acceptance when input order is permuted, the **available public helper** is order-sensitive. This may be a computational reproducibility/control concern if reused in a bat sensorimotor study, but is NOT evidence that real bats use this order-dependent algorithm, nor that Mazar & Yovel 2026 published simulations were wrong (the specific clustered pathway's source is missing). No original cave-exit, collision, prey-capture or sensory neural outcome generated. The primary publication novelty remains with the original authors.
