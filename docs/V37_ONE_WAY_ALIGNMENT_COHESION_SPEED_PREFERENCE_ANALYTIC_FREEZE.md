# v37 frozen analytic mechanism — one-way Boids-like attraction/alignment can match heading yet retain spacing

**2026-11-24 JST, frozen BEFORE computing numerical v37 constructed example tables.** This is an exact **one-dimensional/collinear two-agent linear control-law counterexample**, neither a fit to PLOS 2026 fish nor proof of new animal behavior. Earlier v33b empirical source-conditional local velocity results and v35/36 original PLOS source gates are already known.

## Ecological question

The 2026 PLOS Computational Biology authors reported non-reciprocal C3 real-fish follower/virtual-fish leader coordination where headings remained relatively aligned while spacing could increase. A tempting but overly strong explanatory claim is: **"reciprocity is necessary for cohesion; one-way alignment cannot preserve a finite separation."** This need NOT hold mathematically. Test by an exact solvable dynamical system, WITHOUT source fish data, whether one-way interaction can have (a) matching velocity/heading and (b) steady nonzero following distance. The mechanism is **an intrinsic preferred-speed pull competing with finite social attraction**, not necessarily absence of reciprocity.

## Frozen minimal motion law and units

Let a VR leader move along a fixed forward x-axis at constant externally prescribed speed `v_V=v0+Delta`, independent of real follower. The follower moves along the same axis, obeying the strictly one-way rule

    d x_R/dt = v_R
    d v_R/dt = -alpha*(v_R-v_V) - beta*(x_R-x_V) - gamma*(v_R-v0)

where `alpha>0` [s^-1] is follower alignment to leader velocity, `beta>0` [s^-2] is positional attraction to leader, `gamma>=0` [s^-1] pulls the real fish toward its intrinsic speed v0, and `Delta` [cm/s] is the leader's speed excess over the preferred speed. Leader is unaffected by x_R or v_R: **all directed real→virtual feedback coefficients are exactly zero**. No stochastic noise, wall avoidance, nonlinear saturation, 3D or heading reconstruction is present.

Define `e=x_R-x_V` and `u=v_R-v_V` so `e<0` means real follower trails the VR fish along x, while `u=0` means exact speed/heading alignment for v_V>0. Then

    de/dt = u
    du/dt = -(alpha+gamma)*u - beta*e - gamma*Delta

The equilibrium is exactly `u_star=0, e_star= -gamma*Delta/beta`. It follows that **non-reciprocal coupling is compatible with perfect long-term velocity alignment yet a systematic follower distance**. When `gamma=0` or `Delta=0`, equilibrium e*=0, demonstrating that one-way interaction alone does not force cohesion loss. For `alpha+gamma>0,beta>0`, the Jacobian `[[0,1],[-beta,-(alpha+gamma)]]` is Hurwitz (both eigenvalues strictly negative real parts). Hence convergence to this equilibrium from arbitrary finite initial e,u, without VR ever adapting to the real fish.

When beta=0, positional attraction is absent and absolute spacing is not asymptotically constrained by this law; do NOT extrapolate the beta>0 fixed-point formula to beta=0. Finite actuator acceleration or a wall can change feasibility; our analytic claim ceiling is exactly the stated model.

## Fixed source-FREE numerical illustration and decision criteria

Freeze v0=5 cm/s, `alpha=1 s^-1`, `gamma=0.4 s^-1`, and grid `Delta∈{0,2,5} cm/s`, `beta∈{0.25,0.5,1.0,2.0} s^-2`. For every pair compute analytic `e_star=-gamma*Delta/beta`, `u_star=0`, complex/eigen real parts of the A matrix, and independent numerical matrix-exponential solution for one reference case `Delta=5,beta=0.5`, arbitrary initial `e(0)=0,u(0)=0`, at t=40s. Verify relative state converges to exact stable point within absolute 1e-8 using direct eigen decomposition; if not, SOURCE_FREE_NUMERICAL_STOP. This exact constructed example never uses real fish source rows.

Verify at least:
1. One-way C3-like source has equilibrium matched speed and steady separation (e*=−4cm at beta=.5,Delta=5).
2. With same one-way follower control but Delta=0, e*=0: **reciprocity not mathematically necessary for stable cohesion**.
3. Increasing beta 4-fold at constant gamma,Delta makes spacing magnitude shrink 4-fold, with no change in steady speed alignment.
4. Increasing Delta from 2 to 5 at fixed beta scales spacing 2.5-fold, again u*=0.
5. Both eigenvalues are stable in entire specified positive-alpha/beta grid, and first-order dependence of equilibrium on alpha is **zero** (alpha changes relaxation rate, not the steady offset).

## Experimental discrimination, NOT new observed fish results

Prediction: holding the virtual leader's responsiveness fixed OFF and its speed excess Delta fixed, **real follower spacing should scale with speed-preference pull/positional attraction**, while heading/speed alignment may remain high. Reciprocal virtual response can change the effective leader trajectory, and therefore spacing, but reciprocal feedback is not a logically necessary condition for cohesion. Test across original independent C2/C3 fish sessions only if original 9-column DAT schema, native physical clock, subject/session IDs and preprocessing status are authenticated. Original PLOS authors' claims remain theirs. No original fish acoustic events paired with movement, and the equations contain no fish sounds.

All output marked MATHEMATICAL_CONSTRUCTED_NOT_ANIMAL. PR #248 stays Draft and main untouched. 
