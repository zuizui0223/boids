# v24 post-result mechanism falsification: the observed age curve is not uniquely social

**2026-11-24 JST. Constructed exact analytic counterexample, derived after observing the two original fish taxa's v24 age curves. SYNTHETIC/ANALYTIC ONLY, NOT additional empirical source.** The original preregistered v24 age comparisons, cohorts, source files, outcomes and results are NOT modified.

## A zero-interaction process with collective prediction

Suppose **no fish responds to any other fish**. All fish independently respond to the same latent time-varying physical driver \(U_t\) (flow or an unseen common cue) plus private noise:

\[
v_i(t)=U_t+\epsilon_i(t),\qquad
Y_i(t+\Delta)=aU_t+\eta_i(t+\Delta).
\]

The source is a mean-zero stationary Gaussian process with variance \(\tau^2>0\) and lag autocorrelation \(\rho(\ell)\), while the independent \(\epsilon_i(t)\) have variance \(\sigma^2>0\) and \(\eta\) is independent. The target \(Y_i\) is each fish's later velocity coordinate. There are **no edges from other fish to the focal's motion**.

Condition on the focal's own current velocity \(X=v_i(t)\). The other-\(N-1\)-fish mean at age \(\ell\) is \(Z_\ell=(N-1)^{-1}\sum_{j\ne i}v_j(t-\ell)\). Exact Gaussian partial-covariance algebra gives:

\[
\operatorname{Cov}(Y,Z_\ell\mid X)
=a\tau^2 \rho(\ell)\frac{\sigma^2}{\tau^2+\sigma^2},
\]

\[
\operatorname{Var}(Z_\ell\mid X)
=\tau^2+\frac{\sigma^2}{N-1}-\frac{\tau^4\rho(\ell)^2}{\tau^2+\sigma^2}.
\]

Thus the optimal squared-loss predictive gain of adding the group predictor is

\[
D(\ell)=
\frac{\big[a\tau^2\rho(\ell)\sigma^2/(\tau^2+\sigma^2)\big]^2}
{\tau^2+\sigma^2/(N-1)-\tau^4\rho(\ell)^2/(\tau^2+\sigma^2)}.
\]

For \(\ell=0\) this is strictly positive when the source/private noise and \(a\) are nonzero, **despite no fish-to-fish influence**. As \(|\rho(\ell)|\to0\), the extra gain vanishes. A half-retention crossing, highly positive present versus 2-s-old prediction and a sharply decaying age curve therefore **can all occur without social transmission**.

## Numerical known-truth illustrative grid (not a fit to fish)

Choose fixed illustrative \(\tau^2=\sigma^2=1,\ a=1,\ N=8\), and continuous-time common driver autocorrelation \(\rho(\ell)=\exp(-\ell/T)\). We show three arbitrary \(T\) values to demonstrate the non-identifiability of the age-curve shape. Values are exact \(D(\ell)/D(0)\) for this constructed common-driver model.

| Source correlation time T (arbitrary constructed seconds) | I(0s) | I(0.1s) | I(0.2s) | I(0.5s) | I(1s) | I(2s) |
|---|---:|---:|---:|---:|---:|---:|
| T=0.2s | 1.000 | 0.247 | 0.081 | 0.0038 | 0.000026 | approximately 0 |
| T=0.4s | 1.000 | 0.464 | 0.247 | 0.0479 | 0.0038 | 0.000026 |
| T=0.8s | 1.000 | 0.664 | 0.464 | 0.1843 | 0.0479 | 0.0038 |

The observed **two-taxon** v24 curves retain ~0.52–0.68 at age0.1 and ~0.22–0.44 at age0.2, but this superficial resemblance to a common-driver family **is not evidence that these fish are driven by an OU process**, and \(T\) is not an estimate of true environmental coherence. This counterexample rules out exclusive interpretation of v24 predictive information retention as a socially transmitted neural/sensory memory time.

Original recorded fish velocity may also have unknown smoothing/interpolation extending into future frames. That can make time-lag regressions retrospectively predictive without producing a directly realizable on-line animal signal.

## Discriminating next test, not yet performed

Use **measured experimental external forcing**, stratify acceleration vs deceleration, and compare randomized lateral-line function (intact / impaired / sham) while retaining unmodified original group/session and per-time source properties. The 2026 Peterson et al. lateral-line experiment ([DOI](https://doi.org/10.1093/icb/icag151)) is directly relevant but its original Dryad treatment/trajectory files must first be authenticated and made usable. Under a purely externally shared driver, conditional group-age curves can be similar under alternative sensory treatments once the common driver is controlled; a genuine sensory-mediated transfer effect predicts a treatment-dependent coupling beyond the common-driver surrogate. This is a future discriminating **hypothesis**, not an inference from existing v24 sources.

No vocal-source-identified synchronous fish acoustic events have been admitted. School-to-chorus remains NOT TESTED.

[Original empirical v24](V24_TWO_TAXA_COLLECTIVE_INFORMATION_AGE_RESULT.md) and [earlier v22 independent common-driver proof](V22_COMMON_INPUT_NULL_AND_IDENTIFICATION.md) preserve the same scientific caveat. PR #248 remains Draft, main unchanged.
