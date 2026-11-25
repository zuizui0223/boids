# v47 original zebrafish state moderation — dispersion hypothesis not supported

2026-11-25 JST. Source run [45569031097](https://github.com/zuizui0223/boids/actions/runs/45569031097) job 139050827305 SUCCESS; original artifact 15001596334 ZIP SHA256 d91ad1a06f5ae1fd6119ebfad77d26637affe473cd966c8ba9954cf81024491e, state.json SHA256 b483c47267a43e9109ec85b68cf1158cfbd11ed30443caf1fd68bab8571477b8. Independently downloaded both v46 and v47 original ZIPs and verified their provider SHA256. All eight source files and v46 full MSEs replay exactly, all state partitions reaggregate to original full MSE within 1.16747e-14. All 2x2 cells admitted: minimum 4019 group times, each marginal half 8993 group times, no raw XY/coefficients exported. Original v46 primary NOT_REPLICATED preserved.

Frozen v47 primary delayed far advantage high-minus-low dispersion = -0.02604845 pp (3/8 positive), descriptive bootstrap [-.096392,+.045677], delete-one [-.051441,-.004277]. **DISPERSION_DIRECTION_NOT_SUPPORTED**. Absolute difference +6.15220e-6 in native loss units (3/8 positive; interval includes 0), demonstrating aggregation sensitivity. Do not change the primary after observing polarization.

## Secondary polarization and spatial structure

F = 100*(MSE_NEAR-MSE_FAR)/MSE_GLOBAL, equal means over the eight heldout trials, computed separately per state. Positive F favors far3, negative F favors near3.

| State | Short F (pp; positive trials) | Delayed F (pp; positive trials) |
|---|---:|---:|
| Compact / low polarization | -.059052 (2/8) | +.026183 (4/8) |
| Compact / high polarization | -.040704 (2/8) | +.076907 (8/8) |
| Spread / low polarization | -.047678 (2/8) | -.034777 (3/8) |
| Spread / high polarization | -.007813 (4/8) | +.101369 (6/8) |
| High minus low polarization, all dispersion | +.025805 (5/8) | +.105010 (6/8) |

Compact/high polarization delayed F positive in all 8; descriptive interval [.046641,.105163]. Marginal delayed polarization contrast interval [-.000723,.194510], crosses zero. Secondary discovery, not independent or predeclared primary. The compact cell is not proof of causal benefit of high polarization (compare high vs low within compact: +.050725, 6/8, interval includes 0). State-specific denominators, dependence between speed and polarization, unmeasured common drivers and source tracking remain possible alternatives.

## New paired horizon interaction and denominator audit (postresult, no refit)

Independently recomputed from all original state score matrices and v46 full scores; matched group order, all signed terms retained. Compute K = (F_highP-F_lowP)_delayed - (F_highP-F_lowP)_short per original shoal. NumPy default_rng(20261125), same 10000 paired eight-shoal resamples for all sensitivity scales. CIs descriptive, shared training folds.

| Scale | Mean K | Positive | Descriptive 95% range | Delete-one range |
|---|---:|---:|---:|---:|
| State GLOBAL loss | +.0792051594 pp | 7/8 | [.04691986,.10732804] | [.07082727,.09227478] |
| Full-trial GLOBAL loss at same horizon | +.0472066117 pp | 7/8 | [.00578981,.08482833] | [.03603107,.06240060] |
| State geometry baseline loss | +.0617828773 pp | 7/8 | [.02512847,.09272065] | [.05301207,.07653986] |
| Raw signed MSE difference | +5.88699495e-6 native | 7/8 | [2.770514e-6,9.034025e-6] | [4.987138e-6,6.799572e-6] |

The longer-horizon polarization moderation is robust to these descriptive normalizations, NOT an independent confirmation or a causal force. The next test should transfer this exact state×horizon contrast to the existing separate tetra and ayu sources and stratify by contemporaneous group speed as a noncausal sensitivity. Physical room/corridor classification remains NOT ADMITTED without coordinate calibration; no claim about arena effects, fish social information flow, or synchronized vocalizations. Main unchanged.
