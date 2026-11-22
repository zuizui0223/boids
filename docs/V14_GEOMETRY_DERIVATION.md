# v14 — Frozen-geometry calling closure: derivation and limits

This note contains derivations, design recommendations, and synthetic-fixture verification. It does not report new simulation outcomes. The historical v13 simulator and its archived outcomes were not modified.

## Fixed-geometry closure and exact statements

For a fixed position configuration, let

\[
H_{ij}=\exp(-\|x_i-x_j\|/5),\quad H_{ii}=0,\qquad
A=\frac{w}{N/4}H,\qquad T(q)=\sigma(\theta\mathbf 1+Aq).
\]

The microscopic defaults are \(N=32,w=3,\theta=-2.8\), giving \(A=(3/8)H\). No playback term is included in the post-pulse diagnostic. The function `geometry_diagnostic` uses the actual input geometry, rather than fitting the separate two-state v13 mean-field model to it.

For nonnegative hearing weight, \(T\) is continuous and order-preserving on \([0,1]^N\). Define

\[
\ell_0=0,\quad u_0=1,\quad
\ell_{k+1}=T(\ell_k),\quad u_{k+1}=T(u_k).
\]

Induction gives \(\ell_k\leq\ell_{k+1}\leq u_{k+1}\leq u_k\), componentwise. Bounded monotone convergence and continuity give limits \(q^-\) and \(q^+\), both fixed points. Every fixed point \(q^*\) satisfies \(\ell_k\leq q^*\leq u_k\), hence \(q^-\leq q^*\leq q^+\). Thus these are the least and greatest fixed points.

More generally, for every \(q_0\in[0,1]^N\),

\[
\ell_k\leq T^k(q_0)\leq u_k.
\]

If the exact limits coincide, the fixed point is unique and every deterministic orbit converges to it. If the exact limits differ, the closure has multiple fixed points. The procedure does not enumerate intermediate roots or characterize their basins, and distinct extrema alone should not be called exactly two stable states.

At any argument \(q\), the true Jacobian is

\[
DT(q)=\operatorname{diag}\{T_i(q)[1-T_i(q)]\}A.
\]

At an exact fixed point, this becomes \(J^*=\operatorname{diag}\{q_i^*(1-q_i^*)\}A\). The Jacobian \(DA\) has the same eigenvalues as the symmetric matrix \(\sqrt D A\sqrt D\), where \(D\) is the diagonal derivative matrix. At an exact fixed point, \(\rho(J^*)<1\) implies local asymptotic attraction; \(\rho(J^*)>1\) implies instability; equality to one is inconclusive. For strictly positive off-diagonal hearing, exact least and greatest fixed points cannot have a Perron eigenvalue greater than one: a small perturbation along the positive Perron vector would construct a lower supersolution or higher subsolution and contradict extremality. Neutral endpoints still require caution.

Since the logistic derivative is at most one quarter and \(H\) is symmetric and nonnegative,

\[
\|DT(q)\|_2\leq\tfrac14\|A\|_2
=\frac{w}{N}\rho(H)=L.
\]

Consequently \(L<1\) proves a unique globally attracting closure fixed point. The code's `global_contraction_bound` is exactly this Euclidean Lipschitz bound. A bound at or above one is inconclusive, and is not evidence of multiplicity. `weighted_degree_min/mean/max` are summaries of \(\sum_j A_{ij}\), including hearing weight and the \(N/4\) normalization.

## Numerical and stochastic claim boundaries

The code stops only after both infinity-norm residuals are at most `tol`, or after `max_iter` iterations. Residual-converged endpoints with maximum componentwise gap at most \(10^{-8}\) receive `collapsed_bounds`; larger converged gaps receive `separated_fixed_points`; other cases receive `unresolved`. These are numerical labels. A persistent finite-iteration gap does not prove multiple roots. Even a small residual is not by itself an error bound or a formal two-root certificate near a neutral multiplier. A formal numerical existence proof would require validated invariant boxes or a comparable certificate. Returned spectral radii use the actual Jacobian at each returned vector, including unresolved iterates.

For binary calling \(c\), \(T(c)\) is the exact conditional next-step calling probability at the frozen geometry. Iterating the map on fractional probabilities is a closure, because

\[
E[c_{t+1}]=E[T(c_t)]\ne T(E[c_t])
\]

in general. Conditional independence of next-step calls given \(c_t\) does not establish independence of the marginal calling process.

At fixed geometry and finite parameters, each calling probability is strictly between zero and one. Assuming the simulator's independent uniforms across agents, the transition matrix on the \(2^N\) binary calling configurations is

\[
P(c,c')=\prod_i p_i(c)^{c'_i}[1-p_i(c)]^{1-c'_i}>0.
\]

The fixed-geometry finite chain therefore has one stationary distribution and converges to it. It can nevertheless have long-lived metastable regimes; the positivity argument gives no practically useful mixing-time guarantee. This finite-state uniqueness result does not establish uniqueness for the full moving system, whose state includes continuous positions and velocities.

Absence of a separate individual internal-memory variable does not imply absence of dynamical memory. Current calling, geometry, and velocity can preserve effects of previous input. Persistent differences to a finite horizon are also not a proof of separate invariant states or of hysteresis.

