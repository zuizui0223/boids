# Boids continuation v38–v40: speed, turning demand and source-identified fish-neighbor prediction

**2026-11-24 JST. This is a synthesis of source-only publisher metadata, an exact source-FREE theoretical example, and an as-yet-UNSCORED original observational v40 analysis.** Preserve the boundary between empirical original source results, pre-existing published authors' claims, constructed mathematical examples, and an uncompleted source workflow.

## Previously grounded original fish evidence

[v33b](V33B_ORIGINAL_84_TRIAL_TWELVE_SHOAL_LOCAL_POSITION_ASSIGNMENT_RESULT.md) reconstructed MacGregor & Ioannou's 2021 author Trial→Group crosswalk and reanalyzed all **84 original EIDC stickleback recordings** across **12 actual separate original shoals**, fully held out by Group ID. The current nearest3 neighbor velocities add 0.876%/1.652% MSE improvement over full-group current velocity for 0–0.2s / 0.6–0.8s futures. Correct current velocity–nearest-position assignment beats a fixed rotation surrogate by 0.847%/1.601%, all 12 original heldout Groups positive in both horizons. **No direct social causality**: a spatial shared external driver with zero fish-fish edges can reproduce the same near/global/rotated/far ordering, proven by the independent v33 mathematical counterexample.

[v37](V37_CONSTRUCTED_NONRECIPROCAL_COHESION_ALIGNMENT_EXACT_RESULT.md) constructed a one-way constant-speed VR leader + preferred-speed follower law with exact u*=0, e*=−gamma Delta/beta. This is **not** measured from fish; reciprocity is mathematically unnecessary to maintain stable matched speed and finite spatial cohesion under its stated linear control assumptions.

## NEW 2026 public evidence verification (not new results of our experimental data)

Reynaud et al. *Proc R Soc B* DOI [10.1098/rspb.2026.0146](https://doi.org/10.1098/rspb.2026.0146) **already** performed open-loop real rummy-nose tetra + one virtual partner at **R=15cm** constant circular radius, six speeds **5, 7.5, 10, 11.67, 13.33 and 15cm/s**, with 7–9 original hour-long trials/speed. Their reported increase of directional alignment and lower attraction parameters at faster partner speed are PRE-EXISTING discoveries. This project cannot claim those observations.

Original Figshare collection DOI 10.6084/m9.figshare.c.8485282.v1 was authenticated in [v38](v38_verification/SIX_SPEED_OPEN_LOOP_ORIGINAL_PUBLISHED_COLLECTION_AND_VR_TRACKER_CODE_SOURCE_ONLY.json) and all three original member articles' file metadata in [v38b](v38_verification/SIX_SPEED_SIX_RATE_EXPERIMENT_OFFICIAL_FIGSHARE_ORIGINAL_THREE_FILE_SOURCE_AUDIT.json). Published source files are precisely:
- ESM **rspb20260146_si_001.pdf**, 234,461 bytes, Figshare 32323960, provider MD5 ce0c1737e9bbced25ebb9ba5440e006d.
- S1 low-speed example movie **rspb20260146_si_002.mov**, 28,453,531 bytes, Figshare 32323963, MD5 d25f2070c69bdf86f15fab4de64f72cd.
- S2 high-speed example movie **rspb20260146_si_003.mov**, 25,850,787 bytes, Figshare 32323957, MD5 be1f05e0361755528b6eba48d2204f1d.

These are **original file MANIFESTS only**, no direct publication of per-animal original trajectory recordings with original session IDs in that collection. We have not opened the raw PDF/movie bodies; cannot claim none exist elsewhere. Platform Sanchez et al 2026 PLOS ONE DOI 10.1371/journal.pone.0339909 Data Figshare 29097605 returned official source API 404 (do not invent fallback). Its four original software code Figshare articles did list publisher source file names/MD5: 30188836 tracker, 30188842 simulator, 30188845 rendering/controller, 30188839 calibration. Platform authors share research labs with the Royal/PLOS Computational Biology fish studies, so no independent source animal repetition is assumed. [Issue #251](https://github.com/zuizui0223/boids/issues/251) documents the exact raw experimental subject/session/clock source and speed×radius independent-control experiment gap; [Issue #250](https://github.com/zuizui0223/boids/issues/250) separately seeks 2026 PLOS Computational Biology 2R/C1/C2/C3 9-column data dictionary/true sessions.

## NEW v39 exact **source-free** 2D circular-leader one-way following result

Under virtual leader `phi_V(t)=omega t`, `omega=v/R`, follower `phi_dot_R=kappa (phi_V-phi_R)`, no real→virtual feedback, stable phase error `delta*=v/(R*kappa)` on 0≤delta*<π. Steady angular follower speed and physical speed match virtual but tangent heading agreement and pair chord separation are:

    A*=cos[v/(R*kappa)]
    d*=2R sin[v/(2R*kappa)].

Thus SPEED v and angular velocity omega are NECESSARILY correlated in the existing R=15cm experiment. Fixed kappa=1s^-1, R=15cm and published six **stimulus speed INPUTS** predict A* fall **0.94496→0.54030**, distance rise **4.9769→14.3828 cm** as v rises 5→15cm/s, with NO intrinsic response gain change. This is a constructed kinematic result; original fish could exhibit entirely different A,d.

Under hypothetical alignment target A≥0.8 and maximal distance d≤5cm, exact minimum response gain is

    kappa_min=max{v/[R arccos(.8)], v/[2R arcsin(5/(2R))]}.

With R15 and v=5/15cm/s, kappa_min=0.99533/2.98600s^-1; gain minimum triples as speed triples. Original previous data CANNOT estimate kappa. [Pre-outcome frozen v39](V39_CIRCULAR_ONE_WAY_BOIDS_SPEED_TURNING_COMPENSATION_FREEZE.md), [full v39 mathematical report](V39_EXACT_CIRCULAR_ONE_WAY_SPEED_CURVATURE_RESPONSE_BOUND_RESULT.md), [independent source-free six-speed audit](v39_verification/SIX_SPEED_2D_CIRCULAR_MATH_COMPENSATION_INDEPENDENT_REAGGREGATION.json), [eight synthetic tests / exact mathematical CI #45383273571](https://github.com/zuizui0223/boids/actions/runs/45383273571) SUCCESS. The experimental prediction is to change speed AND curvature/radius independently, comparing same omega with different v and same v with different omega, and control wall-distance/visibility changes.

## v40 ORIGINAL observational source test currently specified, not yet an admitted empirical outcome

[Frozen BEFORE novel speed/turn-stratified original numerical results](V40_STICKLEBACK_84_TRIAL_12_SHOAL_SPEED_TURN_MAPPED_NEIGHBOR_INFO_FREEZE.md): reauthenticate **all 84 original EIDC videos / 12 actual biological shoals** in 12 source-sharded jobs. Use EXACT unchanged v33 G14/current GLOBAL/true nearest3/rotated-nearest3 predictors and future 0–0.2s/0.6–0.8s responses. Source focal own present speed and its *past-to-present* 0.2s heading change (no future Y) define separately each file's stable-low/high-half TEST categories; zero-speed undefined heading is excluded only for turning contrast, never invented as zero turn. Train each original group-fold regression with **all source speeds and turns** from the OTHER ELEVEN original Groups (fixed Ridge10/train-only scaler), score heldout group original file categories, average file then 12 genuine groups. Verify original 84 source hashes/sizes/group IDs/NA roster and v33 global/near/rotation MSE before admitting any source high-vs-low moderation.

Two predeclared response-independent descriptive axes: `L=(MSE_GLOBAL−MSE_NEAR)/MSE_GLOBAL`, `A=(MSE_ROT1−MSE_NEAR)/MSE_GLOBAL`, each with high–low differences by **speed** and by **recent turning**, original 12Group signed differences/whole-group descriptive bootstrap. No experimental effect of speed or turning inferred; observed regimes are confounded and may reuse fish across file sessions. All opposing/null results retained, original 84 frames not treated as 84 independent shoals. The initial source-free v40 fixture run **#45384795666** returned known-truth fixture STOP because synthetic test G14 current-speed column was inconsistent with fake current velocity; it opened NO original fish outcomes. The synthetic fixture alone was repaired (no source model or scientific hypothesis changed) and the new original-source workflow [#45385407184](https://github.com/zuizui0223/boids/actions/runs/45385407184) was triggered. At time of this note new GH run has not produced an admitted original speed/turn result; leave pending and do NOT claim it positive.

**Consolidated claim ceiling:** Distinguish predictive movement organization (observational original 12-shoal), external common driver (source-free counterexample), speed–turning kinematics (v39 source-free), and experimentally measured VR social manipulation (original authors' own published result, but our source-trial reanalysis not admitted). No original fish-origin synchronized acoustic track+sound is available; Boids chorus remains untested. Keep Draft PR #248, main unmerged.
