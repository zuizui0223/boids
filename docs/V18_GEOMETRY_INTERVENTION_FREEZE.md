# v18 frozen causal geometry manipulation in synthetic acoustic Boids

Date 2026-11-22 JST. **SYNTHETIC_ONLY_NOT_FIELD_RESULT**. This is NOT observed fish behavior and not a natural mediation effect.

## Previous data and prespecification status
In v17, the pre-cue compactness vs motor-dependent pulse effect was identified **after viewing outcomes**, rho≈−0.867, n=9 low groups, three extreme positive seeds. This is an exploratory discovery. v18 must not use old seeds 4000–4383 to claim independent replication, and must not tune spatial scaling after looking at v18 results.

## New held-out seed census / fixed state
- New untouched seeds **5000–5767 inclusive (768)**, 32 individual agents, source sim file `validation_fish_boids_v15/simulation.py` SHA256 a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb. Same v15 dynamics. External sound cue 0.8 updates1000–1039, source common history without cue to completed t1000.
- Enroll **every** pre-cue low seed with q=mean(binary calls at completed t1000) <0.90. Keep all 768 pre-cue q values and retain 1000-step original prefixes. No adaptive seed addition, no selecting by future outcome or geometry.
- Manipulate only 32×2 positions at checkpoint t1000 around that checkpoint's original group centroid `mu`: `Xnew=mu+s*(Xoriginal-mu)`; fixed spatial factors **s=0.65 compact**, **s=1.00 native**, **s=1.35 spread**. Copy each fish's original velocity, binary call, individual ID, PCG64 state and global centroid unchanged for all 3 conditions. This manipulates pairwise distances and tank wall interactions as well as acoustic attenuation; it is not a hearing-specific intervention.
- Every arm uses the unchanged 32-agent model, original seed's exact RNG state. Exactly 10 continuations per enrolled seed:
  - motor5/hear3 with cue 0 or fixed40-step cue for each s∈{0.65,1.00,1.35}: 6
  - motor0/hear3 with cue 0 or cue for s∈{0.65,1.35}: 4
  Cue ends at t1040; all arms end at t4040. All arms use same random draws, preserve original individual ordering. n=32 fixed.
- The *only primary outcome*: per seed difference in postcue [1040,4040) average calling fraction under native acoustic motor5 with compact s=.65 versus spread s=1.35:
   `D_i = (pulse-quiet)_{s=.65,motor5,hear3} − (pulse-quiet)_{s=1.35,motor5,hear3}`.
  Group-weighted mean of D, median, signs, 10,000 whole-seed bootstrap percentile95%, fixed RNG seed2026112242. Hypothesis suggested by v17 observation is **positive**, but all results including opposite signs must remain. If n_eligible<8, inferential interpretation stops and only a descriptively labeled result remains.
- Predefined secondary: pulse gains at each s and motor, motor×pulse interaction within each scale, contrast of geometry×pulse under motor0, three-way difference `D_motor5−D_motor0`; original position hull area versus scaled area (must equal s²), distance-based perceived calls at split, no-cue baseline calling in each geometry, 200-update high call confirmation and right censoring at t4040, seed-specific concentration and heldout cohort fraction.
- **Validation:** source SHA protected, all 768 prefix states counted; exact all-position scale and centroid/velocity/calls/RNG preservation; compact vs spread pair distances multiplied by s exactly within 1e-12; source state no mutation; neutral s1 exactly source state; fixed cue schedule; shared end RNG; integer per-seed call totals before differences; all10 arms and all eligible seeds are saved; digest file and source hashes retained. No post-outcome changing signs, thresholds, seed range or horizons.
- **Interpretation gate:** compactness can shift no-pulse calling to saturation. A compact-minus-spread effect of playback is *not* a claim of a pure acoustic signal mediation pathway. Changes to wall forcing, separation, neighbor topology, prey, detection etc. are unmeasured. Two independent artificial seed cohorts are still one generator model; no real fish/coral reef chorus claim, no long-run attractor.
- Remain [Draft PR #248](https://github.com/zuizui0223/boids/pull/248), do not merge to main.
