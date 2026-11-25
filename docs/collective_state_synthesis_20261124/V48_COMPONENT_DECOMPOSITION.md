# v48 post-result near/far component decomposition

2026-11-25 JST. New calculation on all 3 original v48 artifact score matrices. No new source fitting. Original v48 nonreplication outcomes unchanged. Verified all original ZIP digests (see V48_COMPLETE_THREE_SOURCE_HETEROGENEITY_AND_AUDIT.md). Within each source unit/state/horizon define L=100*(GLOBAL−NEAR)/GLOBAL, A=100*(GLOBAL−FAR)/GLOBAL, F=A−L. K(X)=(X_highP−X_lowP)_delayed−(X_highP−X_lowP)_short. Exact identity K(F)=K(A)−K(L). Separate absolute native MSE and other normalization sensitivities calculated, never pool native units.

| Source/state | K(L) pp [descriptive 95%] | K(A) pp [descriptive 95%] | K(F) pp |
|---|---:|---:|---:|
| Tetra all | +.496698 [.260600,.735997] | +.432809 [.224489,.679678] | −.063889 |
| Tetra low speed | +.381842 [.129194,.611894] | +.422474 [.190790,.653045] | +.040632 |
| Tetra high speed | +.819034 [.539830,1.143725] | +.715724 [.493975,1.022835] | −.103310 |
| Ayu all | −.163388 [−.728412,.596869] | +.184662 [−.201143,.632134] | +.348050 |
| Ayu low speed | −.161113 [−.698255,.395335] | +.289126 [−.156687,.690950] | +.450239 |
| Ayu high speed | +.331630 [−.283501,.975089] | +.373166 [−.291981,.981141] | +.041536 |
| Zebrafish all | −.066372 [−.147994,.025719] | +.012833 [−.085990,.120270] | +.079205 |
| Zebrafish low speed | +.008135 [−.035249,.051746] | +.012879 [−.017584,.046104] | +.004744 |
| Zebrafish high speed | −.141135 [−.308973,.048666] | −.033278 [−.242980,.183517] | +.107857 |

Tetra high-speed both component K positive in all 6 files; near larger. In ayu low speed the point estimates have opposite signs, and in zebra high speed both negative with greater near decrease. Both component intervals cross zero for these latter two; not mechanistic attribution. Tetra's all-state and low-speed component intervals are also positive. K>0 is a relative far-advantage interaction, not necessarily higher far MSE gain itself. These descriptive interactions measure a difference of differences across prediction windows, not simple gains for high-polarization fish. 

Speed moderation (high-speed K minus low-speed K):
| Source | Near | Far | Far−near |
|---|---:|---:|---:|
| Tetra | +.437192 | +.293250 | −.143942 |
| Ayu | +.492743 | +.084040 | −.408703 |
| Zebra | −.149270 | −.046156 | +.103114 |

Independent local Python recomputation: same 10000 paired evaluation-unit bootstrap samples per study (NumPy default_rng 20261125); original ZIP SHA verified. All four normalization scales and all three state comparisons plus speed moderation, 48 signed far-minus-near arrays exactly match original v48 within 1e-10 absolute/relative tolerance. Shared original fitting folds, uncertain distinct shoal IDs for tetra/ayu, subgroup postselection and species/arena confounding limit inference. No common causal law, no pooling. v49 frozen separate protocol transfers group-level polarization contrast to original 84 stickleback files / 12 biological shoals. 

Reproduce: download original v48 artifacts as v48-tetra.zip, v48-ayu.zip, v48-zebrafish.zip in one directory; run the accompanying decomposition code on that directory. All output contains scores/contrasts, not source raw coordinates.
