# Independent mean-field mathematics audit

This audit concerns the deterministic model supplied for Boids v12. The
derivations and numerical experiments establish properties of that model;
they do not supply empirical evidence for a biological feedback mechanism.
The v13 implementation is standalone and does not modify v12.

## 1. Fixed points and exact fold bounds

The two-state map is

\[
g_{t+1}=\alpha g_t+(1-\alpha)(k p_t+\chi B_t),\qquad
p_{t+1}=\sigma(\theta+\beta g_t+\eta p_t+\phi B_t).
\]

For constant forcing and \(0\leq\alpha<1\), define

\[
L=\beta k+\eta,\qquad C=\beta\chi+\phi,\qquad h=\theta+CB.
\]

Every equilibrium obeys \(g_*=kp_*+\chi B\) and

\[
p_*=\sigma(h+Lp_*),\qquad
H(p_*):=\log\frac{p_*}{1-p_*}-Lp_*=h.
\]

Consequently, the equilibrium positions and fold locations are independent
of \(\alpha\) within this domain. Transient rates and basins still depend
on \(\alpha\).

Because \(H'(p)=1/[p(1-p)]-L\), there is one equilibrium for \(L<4\).
For \(L=4\), there is still exactly one equilibrium for every intercept.
At \(h=-2\), the unique root \(p=1/2\) has multiplicity three:

\[
H(1/2+x)+2=\frac{16}{3}x^3+\frac{64}{5}x^5+O(x^7).
\]

For \(L>4\), set

\[
\delta=\sqrt{1-4/L},\qquad
p_{\mathrm f,-}=\frac{1-\delta}{2},\qquad
p_{\mathrm f,+}=\frac{1+\delta}{2},
\]

\[
A=\frac{L\delta}{2}-2\operatorname{atanh}\delta>0,
\qquad h_-=-\frac L2-A,\qquad h_+=-\frac L2+A.
\]

The lower-probability stationary point is a local maximum of \(H\), so
\(H(p_{\mathrm f,-})=h_+\). The higher-probability stationary point is a
local minimum, so \(H(p_{\mathrm f,+})=h_-\). This reversal matters when
labeling a diagram or an API.

- If \(h_-<h<h_+\), there are three distinct equilibria.
- At either bound there are two distinct equilibria, one a double root.
- Outside the closed interval there is one equilibrium.

Thus \(L>4\) is necessary but not sufficient for three equilibria or the
two hyperbolic attracting fixed points of this nonnegative-coupling model.
The intercept must also lie strictly inside the fold window.

For a given constant \(B\), the exact theta bounds are
\(\theta_-(B)=h_--CB\) and \(\theta_+(B)=h_+-CB\). For a given theta and
\(C>0\), the forcing bounds are \(B_-=(h_--\theta)/C\) and
\(B_+=(h_+-\theta)/C\). If \(C<0\), their order reverses; if \(C=0\),
forcing does not shift this equilibrium equation.

### Supplied baseline

With \(\alpha=.65,k=1,\beta=4,\eta=2,\chi=.2,\phi=.6,\theta=-3\),
one has \(L=6\), \(C=1.4\), and at \(B=0\):

| Quantity | Value |
|---|---:|
| Lower-probability fold | 0.21132486540518712 |
| Upper-probability fold | 0.7886751345948129 |
| Lower theta fold | -3.4150929106440606 |
| Upper theta fold | -2.5849070893559394 |
| Lower constant-B fold, theta=-3 | -0.29649493617432904 |
| Upper constant-B fold, theta=-3 | 0.29649493617432904 |
| Intercept halfwidth A | 0.4150929106440605849 |

The three baseline probabilities are
\(0.07072018167994483,\;0.5,\;0.9292798183200551\), with \(g_*=p_*\).
At the lower theta fold the other, simple root is
\(0.04014807866379499\); at the upper fold it is
\(0.9598519213362050\). These values were independently checked with
70-digit arithmetic before writing the implementation.

## 2. Full discrete-time stability

The scalar fixed-point reduction is not the transient two-state map. With
\(s=p_*(1-p_*)\), its full Jacobian is

\[
J=\begin{pmatrix}
\alpha &(1-\alpha)k\\
\beta s&\eta s
\end{pmatrix},\qquad
T=\alpha+\eta s,\qquad
D=s[\alpha\eta-(1-\alpha)\beta k].
\]

The characteristic polynomial is \(\lambda^2-T\lambda+D\). The complete
strict Jury conditions for both multipliers to lie inside the unit disk are

\[
1-T+D>0,\qquad1+T+D>0,\qquad1-D>0.
\]

In model parameters these become

\[
(1-\alpha)(1-Ls)>0,
\]

\[
(1+\alpha)(1+\eta s)-(1-\alpha)\beta k s>0,
\]

\[
1-\alpha\eta s+(1-\alpha)\beta k s>0.
\]

Under \(0\leq\alpha<1\) and \(\beta,k,\eta\geq0\), the single condition
\(Ls<1\) is equivalent to strict Schur stability of the Jacobian, and
therefore sufficient for local exponential asymptotic stability. Necessity
for Schur stability follows from the first Jury condition. Sufficiency
follows because \(\eta s\leq Ls<1\) gives \(D<1\), while
\(\beta k s<1-\eta s\) makes the second Jury expression strictly positive.

The eigenvalues are real in this domain because

\[
T^2-4D=(\alpha-\eta s)^2+4(1-\alpha)\beta k s\geq0.
\]

For \(Ls>1\), the positive eigenvalue exceeds one, so the equilibrium is
unstable. For \(Ls=1\), a unit eigenvalue makes linearization inconclusive
about attraction. The module's nonhyperbolic label does not assert
nonlinear stability.

| Baseline equilibrium | Eigenvalues of full J | Classification |
|---|---|---|
| p=0.07072018167994483 | 0.7897590533516358, -0.0083213781854349 | Stable |
| p=0.5 | 1.1713430220938281, -0.0213430220938281 | Unstable saddle |
| p=0.9292798183200551 | 0.7897590533516359, -0.0083213781854349 | Stable |
| Either baseline fold | 1, -1/60 | Nonhyperbolic |

The scalar quantity \(Ls\) is not the full-map convergence multiplier.
At the low baseline equilibrium it is approximately 0.394313, while the
dominant full-map multiplier is approximately 0.789759.

### Edge cases and limits of the claim

- At a generic saddle-node with \(L>4\), the neutral center direction is
  semistable, attracting from one side and repelling from the other.
  Calling the double root a hyperbolic stable state would be incorrect.
- At \(L=4,h=-2\), the unique critical equilibrium is nonhyperbolic. The
  sigmoid's restoring cubic term can still give asymptotic attraction;
  equality in the linear criterion alone must not be called instability.
- At any fold, the other multiplier is
  \(\alpha+\eta/L-1=\alpha-\beta k/L\). It lies strictly between -1 and
  1 except for the special pure-delay case \(\alpha=\eta=0\), when it
  equals -1 and the two multipliers are simultaneously +1 and -1.
- A middle root is not always a saddle across the whole allowed parameter
  domain. For \(\alpha=\eta=0,k=1,\beta=6,p=1/2\), the eigenvalues are
  \(\pm\sqrt{1.5}\), so both directions are unstable. With pure delay,
  \(p_{t+2}=\sigma(h+Lp_t)\); the two parity subsequences can also select
  different attracting roots, creating period-two behavior. Fixed-point
  stability does not establish global convergence for every parameter set.
- The reduction \(g_*=kp_*+\chi B\) fails at \(\alpha=1\), because g
  then does not relax. The implementation excludes that endpoint.
- With signed couplings or alpha outside the supported interval, use all
  three Jury conditions. The simplified nonnegative-coupling criterion and
  real-eigenvalue claim cannot be carried over without checking assumptions.
- For \(L<4\), a stronger sufficient conclusion is available: the global
  derivative bound matrix
  \(\begin{pmatrix}\alpha&(1-\alpha)k\\\beta/4&\eta/4\end{pmatrix}\)
  has spectral radius below one. A suitable weighted maximum norm therefore
  makes the full map a contraction, giving a unique globally attracting
  equilibrium in the usual model state domain.

## 3. Pulse switching versus hysteresis

A finite positive pulse can move a trajectory from the low-state basin to
the high-state basin. Persistence after the pulse is removed is a model
demonstration of attractor switching and memory at the baseline parameter
value. That trajectory alone does not measure an upward/downward
hysteresis loop.

A measured model hysteresis curve requires continuation in a control
parameter in both directions, allowing each point to settle and retaining
the previous settled state as the next initial state. Different settled
states at the same control parameter then demonstrate the loop. Finite
scan resolution and stopping tolerances should be reported separately
from the analytic fold values.

The stable manifold of the middle saddle is a boundary in the full (g,p)
state plane. A scalar rule such as "the pulse takes p above 0.5" does not
by itself establish basin crossing. Pulse duration and the memory state
matter. Nor is a finite-pulse threshold identical to the constant-forcing
fold threshold.

If B denotes nonnegative playback intensity, the baseline lower B fold is
outside that physical range. Returning a positive B sweep to zero may
therefore leave the high branch occupied. The v13 audit instead sweeps
theta from -4.5 to -1.5 and back, spanning both folds without interpreting
negative B as a physical playback intensity.

## 4. Implemented numerical audit and root solver

The module is `boids/validation_fish_boids_v13/meanfield_audit.py` and its
tests are `test_meanfield_audit.py`. It depends only on Python's standard
library. The public API is:

- `equilibria(gain, intercept) -> list[float]`: sorted distinct roots.
- `folds(gain) -> dict`: empty for gain <= 4; otherwise p_lower, p_upper,
  h_lower, h_upper, with the ordering convention in section 1.
- `stability(p, alpha=.65, k=1, beta=4, eta=2) -> dict`: Jacobian, trace,
  determinant, real eigenvalues, spectral radius, classification, Ls,
  and all three Jury expressions.
- `run_audit() -> dict`: parameters, baseline root/stability records,
  fold thresholds, both theta sweeps, and convergence/jump checks.

The solver changes variables to z=logit(p), b=h+L/2, and solves

\[
Q(z)=z-\frac L2\tanh(z/2)-b=0.
\]

For L>4 it brackets roots separately on the three monotone intervals
split by \(z=\pm2\operatorname{atanh}\delta\). Known tangent endpoints
are emitted once, and the L=4 critical root is handled explicitly. It
uses no grid scan or broad proximity rule that could miss a tangency or
merge distinct nearby roots.

Near the cusp, direct subtraction would lose significance. The
implementation instead evaluates z-2*tanh(z/2) by its small-z series and
computes the small fold halfwidth using

\[
A=\sum_{n\geq1}\frac{4n}{2n+1}\delta^{2n+1}.
\]

This resolves, for example, the three distinct roots for the actual
floating-point input L=4+1e-12, h=-L/2:
0.4999995669680510, 0.5, and 0.5000004330319490. The two reported h fold
values can themselves round to the same float this close to L=4; the
centered solver still distinguishes the three roots. Saturated extreme
probabilities may round to 0 or 1 even though finite mathematical roots
are interior.

### Sweep evidence

Each direction uses 201 theta values, spacing 0.015, at B=0. At each point
the full two-state map is iterated until its maximum component residual
is at most 1e-11, with a maximum of 10,000 updates. Every reported state
includes its step count, residual, and convergence flag.

- All 402 sweep points converged.
- Maximum reported full-map residual: 9.988898597157458e-12.
- Maximum updates at one point: 469.
- Upward jump: theta -2.595 to -2.580, delta p = +0.7782974804096316.
- Downward jump: theta -3.405 to -3.420, delta p = -0.7782974804096314.
- Both jump intervals bracket the corresponding analytic folds.
- At theta=-3, the upward path occupies p approximately 0.07072018;
  the downward path occupies p approximately 0.92927982.

### Verification

The tests were written before implementation. The baseline test was
observed failing against an empty root-list stub with `0 != 3`, then
passed after implementation. The 18 new numerical tests cover baseline
roots, one-root regimes, both double roots, both sides of each fold,
the triple root, near-cusp distinct roots, gain=100 saturation, invalid
inputs, full two-state eigenvalues, the pure-delay edge case, actual
sweep convergence, branch separation, fold bracketing, and strict JSON
serialization.

`python -m unittest -v test_meanfield_audit` passed all 18 tests.
`python -m pytest -q` from the `boids` directory passed all 36 tests and
54 subtests present at verification time. The latter run reported one
existing dependency deprecation warning from the anyio pytest plugin
about `CallSpec2`; there were no test failures.
