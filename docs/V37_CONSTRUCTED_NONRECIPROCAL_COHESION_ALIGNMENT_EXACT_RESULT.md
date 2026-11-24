# v37 constructed theory: nonreciprocal follower can align and remain coherently separated

**2026-11-24 JST. This is an exact analytic and 12-case constructed numerical counterexample, NOT a measurement from fish or a new discovery of the PLOS 2026 real–virtual intervention.** The initial scientific model/parameters were [frozen before v37 numerical outputs](V37_ONE_WAY_ALIGNMENT_COHESION_SPEED_PREFERENCE_ANALYTIC_FREEZE.md), then validated with eight independent mathematical fixtures [Actions #45377421561](https://github.com/zuizui0223/boids/actions/runs/45377421561) SUCCESS. Two prior CI runs [#45377131139](https://github.com/zuizui0223/boids/actions/runs/45377131139) and [#45377299201](https://github.com/zuizui0223/boids/actions/runs/45377299201) STOPPED due to source-free Python output-name typos `eig` versus `eigs`; **no changes to the underlying frozen differential equation or parameters**. The final run passed 8/8 fixtures and checked the 12 analytical entries and time-evolution solution.

## Ecological question corrected

Earlier the project tentatively proposed that persistent cohesion may require mutual feedback whereas directional alignment survives one-way following. The strong version **"reciprocity is mathematically necessary for cohesion" is FALSE** even for elementary biologically motivated pursuit/alignment laws. A nonreciprocal virtual leader can be followed with stable bounded separation while speeds/headings match; a *speed-preference mismatch* can set the steady following offset.

Consider one real follower R and one **prescribed** nonresponsive virtual leader V, moving along a common positive-heading direction x. Fix virtual speed v_V = v0 + Delta, no arrow from real to virtual. A minimal acceleration controller contains (i) social velocity alignment alpha, (ii) positional attraction beta, (iii) intrinsic real fish speed preference gamma toward v0:

    dv_R/dt = -alpha*(v_R-v_V) - beta*(x_R-x_V) - gamma*(v_R-v0)

The state e=x_R−x_V and u=v_R−v_V obeys

    de/dt = u
    du/dt = -(alpha+gamma)*u - beta*e - gamma*Delta.

For alpha+gamma>0 and beta>0 the 2×2 homogeneous Jacobian eigenvalues have strictly negative real parts, because the characteristic polynomial is

    lambda^2 + (alpha+gamma)*lambda + beta = 0.

The stable fixed point is EXACTLY

    u* = 0
    e* = -gamma*Delta/beta.

Thus a real follower can converge to the virtual leader's **same positive x-heading and speed** while its position trails by a persistent amount gamma*Delta/beta. When Delta=0 or gamma=0 the steady offset is zero even though the virtual leader never responds, showing that reciprocity by itself is **not mathematically necessary** for speed matching or a stable, bounded cohesive configuration. We do not represent fish collision avoidance, preferred nonzero body-length separation, 3D turns, visual perception or wall geometry in this analytic counterexample.

## Fixed source-free constructed numerical grid

With v0=5 cm/s, alpha=1/s, gamma=0.4/s, virtual speed excess Delta in {0,2,5} cm/s, attraction beta in {0.25,0.5,1,2} /s², all **12/12** cases are asymptotically stable and have exact u*=0. Examples:

| Constructed Delta (cm/s) | Constructed beta (s^-2) | EXACT relative follower position e* (cm) | EXACT relative speed u* (cm/s) |
| ---: | ---: | ---: | ---: |
| 0 | 0.5 | 0 | 0 |
| 2 | 0.5 | −1.6 | 0 |
| 5 | 0.25 | −8.0 | 0 |
| **5** | **0.5** | **−4.0** | **0** |
| 5 | 1.0 | −2.0 | 0 |
| 5 | 2.0 | −1.0 | 0 |

A reference independent matrix exponential solution from initial e(0)=u(0)=0 with Delta=5, beta=0.5 after **40 seconds** gave e(40)=−4.00000000001646 cm and u(40)=+1.0466×10^-11 cm/s. Maximum absolute error from the exact equilibrium was **1.65×10^-11**, eigenvalues' real parts both −0.7/s. This is a numerical implementation check of the proven linear system, not biological measurement.

The original author PLOS 2026 experiment's nominal virtual speeds are about 5 and 10 cm/s; choosing 5 cm/s for v0 and 5 cm/s excess in one constructed row is intended to give an intuitive scale, **not** parameter estimation from original fish. Alpha, beta and gamma were chosen freely and not fit. The published PLOS paper DOI [10.1371/journal.pcbi.1014544](https://doi.org/10.1371/journal.pcbi.1014544) is the independent biological context.

## General measurement prediction beyond a specific species

For any comparable attraction/alignment controlled follower model and known preferred distance scale L>0, define a simple **dimensionless speed-preference spacing stress**

    M = gamma*|Delta|/(beta*L).

This is only nondimensionalizing the exact fixed-point lag, not a new measured parameter. The model predicts |e*|/L=M and u*=0. Thus changing the **unreciprocated agent speed excess** can change inter-agent separation without changing aligned headings/speeds. Weakening attraction beta makes the steady separation larger even if alignment alpha is strong, whereas increasing alpha alone changes convergence time but not steady separation. An observed reduction in cohesion without lost alignment is therefore not sufficient evidence of lost reciprocity: an intrinsic speed preference or a controller's turning/acceleration statistics can mediate it.

The specific 2026 PLOS C2 (fast reciprocal virtual partner) vs C3 (same nominal fast virtual partner with feedback OFF) author manipulation may also alter realized virtual **turning rates and predictability**. The published paper reports virtual-fish U-turn rate per 1000 frames of ~4.8 in C2 vs ~0.4 in C3, so reciprocal-controller total effects are not a direct isolated fixed-trajectory fish perception parameter. Attribution to direct reciprocity rather than changing generated virtual kinematics requires a more tightly controlled/yoked design. These values are **the original paper's published summaries**, not estimates from our original data.

## Source-quality boundary remains

The original PLOS 2026 Figshare 2R/C1/C2/C3 DAT files are all full-byte provider MD5 verified, total 194.35MB, and all have nine numeric columns without field headers. [v35 source gate](V35_2026_EXPERIMENTAL_FISH_VR_ORIGINAL_DATA_AUTHENTICATION_AND_CAUSAL_UNIT_GAPS.md). [v36 original author Python code AST source gate](v36_verification/PLOS_2026_AUTHENTICATED_AUTHOR_CODE_NO_EXPERIMENT_DAT_LOADER_SCHEMA_STOP.json) found the public Model3D-VR.py does NOT read the original four experimentally named DAT files, and references a different Compare-Model-Exp.py not included in the authenticated Figshare source listing. The nine numeric values CANNOT be equated to the nine model-state variables by matching counts. Trial/session fish identities and physical DAT sampling clock unknown. **Issue #250** remains OPEN; no original C2 vs C3 treatment comparison estimated by this project.

## What would refute or support the mechanism empirically

An independently randomized/counterbalanced trial design holding VR nominal speed and relevant turning exposure fixed could ask whether follower speed alignment remains high while separation rises with a mismatch between preferred and leader speed. The analytic model also predicts the target steady gap decreases ~1/beta and grows ~Delta, with response time affected by alpha. Actual fish may have hard maximum accelerations and perceptual/avoidance distance and leave the stable linear regime. A full experimental validation requires authentic real/virtual trajectory coordinates, condition/session IDs, original source filtering state and observation/actor times; the present data cannot resolve it.

There is no fish-origin synchronized acoustic data in this analysis, and no proof of a Boids→chorus loop. Source-safe exact run artifact [#14911407425](https://github.com/zuizui0223/boids/actions/runs/45377421561/artifacts/14911407425), ZIP SHA256 **58fea42000e4eeb6394f813783094b48767af6c60ef918dcb5bede2b2ae523b2**. The synthetic mathematical 12-grid was independently recomputed in the runtime; each row satisfied u*=0, e*=−gamma*Delta/beta and stable eigenvalues. [Source mathematical code](../validation_fish_school_v37/nonreciprocal_alignment_cohesion.py), [8 known-truth tests](../validation_fish_school_v37/test_nonreciprocal_alignment_cohesion.py).

**Publication ceiling**: exact mathematical *example* clarifying a possible interaction rule, **not** a fitted generative explanation of the original species, an independently discovered ecological regularity or a causal virtual-fish experimental effect. Keep PR #248 Draft, main untouched.
