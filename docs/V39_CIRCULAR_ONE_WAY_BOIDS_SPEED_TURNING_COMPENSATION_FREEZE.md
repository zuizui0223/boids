# v39 source-free circular one-way Boids tracking: a speed–curvature compensation bound

**2026-11-24 JST. PRE-FROZEN before computing any v39 numerical example or figure.** This is an exact, minimal, 2D kinematic/pursuit control system, NOT an original fish behavioral data fit, new causal treatment effect, or previously unreported finding from the 2026 Royal Society study.

## Existing experimental motivation, originality and claim ceiling

Reynaud et al. (2026), *Proc R Soc B* DOI **10.1098/rspb.2026.0146** (published 2026-06-03), already experimentally imposed one-way/open-loop virtual rummy-nose tetra circular motion at radius **R=15 cm** and six published constant speeds **v_V=(5,7.5,10,11.67,13.33,15) cm/s**, 7–9 one-hour replicates at each speed. Authors already reported higher partner speed associated with weaker attraction and stronger fitted alignment/wall forcing. Their original public Figshare collection ID 8485282 currently has only three confirmed articles (two videos and ESM; not yet independently authenticated fish session trajectories), and previously declared platform experiment DATA article 29097605 returns official API HTTP404. [v38 official source-metadata provenance](v38_verification/SIX_SPEED_OPEN_LOOP_ORIGINAL_PUBLISHED_COLLECTION_AND_VR_TRACKER_CODE_SOURCE_ONLY.json). Do NOT attribute the experimental manipulation or its conclusions to this project.

Previous constructed [v37 1D constant-velocity follower](V37_CONSTRUCTED_NONRECIPROCAL_COHESION_ALIGNMENT_EXACT_RESULT.md) yielded speed matching u*=0 and nonzero e* under intrinsically preferred-speed mismatch, but could not account for turning/heading. v39 models an *independent* geometric mechanism on a fixed circular orbit: even if a real animal's strength of response to the VR leader does not change, a faster VR fish on the SAME radius has a higher angular velocity, thus a larger position/heading lag.

## Frozen minimal **one-way circular** dynamics

Virtual leader is fully prescribed:
- (p_V(t)=R(cosphi_V,sinphi_V)), (dotphi_V(t)=omega=v_V/R>0). No arrow from the real follower to virtual leader. R>0.
- Follower moves on the same radius R under a linearized **unwrapped-phase tracking controller**: (dotphi_R=kappa(phi_V-phi_R)) for gain (kappa>0) with units s^-1. Define lag (delta=phi_V-phi_R). Then **(dotdelta=omega-kappadelta)** and (delta(t)=omega/kappa+[delta(0)-omega/kappa]exp(-kappa t)), stable eigenvalue -kappa.
- We restrict the equilibrium (delta^*=omega/kappa) to the physically unambiguous **near-side following branch 0<=delta*<pi**, rather than claiming this unwrapped-phase control remains valid for a fish repeatedly turning across +/-pi. We set initial lag delta(0)=0 for numerical time-path verification; computed static comparison is independent of this arbitrary initial value.
- The follower's instantaneous tangent heading is (	heta_R=phi_R+pi/2). On the stable orbit the follower's angular speed matches the VR leader, hence **its linear speed matches v_V**, but the heading difference equals the phase lag (delta^*=omega/kappa=v_V/(Rkappa)). The expected cosine *at this deterministic orbit*, not the experimental noise-averaged PDF, is (A^*=cos[delta^*]).
- Since both fish are on radius R, their **chord distance** is exactly (d^*=2Rsin[delta^*/2]) for 0<=delta*<pi. The model yields finite stable spacing with **no reciprocity**, but increasing v at fixed kappa increases angular/heading lag and distance (over the near-side branch).
- For a desired minimum alignment score (A^*ge c), where 0<c<1, exactly ( kappa ge v_V/[Rarccos(c)]) on the principal branch.
- For a desired maximum distance (d^*le d_{max}), 0<dmax<2R, exactly ( kappage v_V/[2Rarcsin(d_{max}/(2R))]).
- To satisfy **both** conditions, require the **larger** of these two gain bounds. Under an unchanged R, if virtual speed triples and both alignment/cohesion bounds are to be maintained, the minimum required angular tracking gain must triple in this model. Increasing responsive gain need not represent increased *social preference*: it can be compensation for kinematic turning demands.
- This is a 2D angle–speed geometry example, not empirical identification of the PLOS/Proc R Soc B paper's alignment force coefficient. The 'controller gain' kappa is not equivalent to the fitted fish social alignment coefficient in prior authors' 3D stochastic model.

## Source-free numerical illustration frozen before evaluation

Set R=15 cm exactly (the experimental specified path radius for intuition, not a fit to real-fish data), speeds v=(5,7.5,10,11.67,13.33,15) cm/s, an ARBITRARILY CONSTRUCTED follower gain kappa0=1.0 s^-1, minimum alignment threshold **c=0.8**, maximum chord distance **dmax=5 cm**, and evaluate all six:
- (omega=v/R), (delta^*=omega/kappa_0), (A^*=cosdelta^*), (d^*=2Rsin(delta^*/2)), and (kappa_{min}(v,c,dmax)=max(v/[Rarccos c], v/[2Rarcsin(dmax/(2R))])).
- Require exact analytic equilibrium and direct closed-form time trajectory at t=0, t=10 and t=40s using (delta(0)=0) and independently check (|delta(40)-delta^*|<1e-14).
- Construct an additional fixed-gain compensation scenario (kappa(v)=kappa_{min}(v,c,dmax)) for each speed; both theoretical constraints are respected within 1e-11.
- For fixed kappa0, require (omega/kappa_0<pi) and test **strictly decreasing** alignment cosine and **strictly increasing** following distance as speed increases; if not, fail. No original fish video, original condition data, individual tracking or acoustic event is accessed.

## Distinguishing mechanisms and limits

In a real circular VR arena, increasing speed also increases turning angular rate (omega=v/R). Observed increased behavioral 'alignment' with speed (as the original authors' model inferred) may indicate gain compensation, or arise from changing wall interactions/relative position/perceptual effects, not just a change in a single isolated innate social force. This model's forced-turn geometric cost is distinct from v37's preferred-speed mismatch along a straight line. A biological test needs original **fish+virtual synchronized positions with true experimental session IDs**, timestamp/fps and processing state. Fix R and vary v, then separately fix (omega) but vary speed by changing radius R, or vary (omega) at constant speed to discriminate speed from angular velocity. Use session-clustered inference; do not use raw frames as independent replicates.

A relevant future experimental design therefore manipulates **speed and curvature independently**, not merely speed at fixed R. No source-original 2026 fish treatment/response is newly measured by v39, and no causal acoustic Boids-choreography connection is supported. Draft PR #248 remains unmerged.
