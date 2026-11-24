"""Deterministic mean-probability closure at a fixed microscopic geometry.

For H_ij = exp(-distance_ij/5), H_ii = 0 and A = heard_weight/(N/4) * H,
the diagnostic iterates T(q) = sigmoid(theta + A q) from all-zero and all-one
vectors. These monotone sequences enclose every fixed point of T.

T(c) is the exact conditional probability of the next binary calling vector
given c and this geometry. Iterating T on fractional q is a deterministic
closure: E[T(c)] generally differs from T(E[c]). Its fixed points are not
stationary distributions of the stochastic microscopic calling process.
"""

from numbers import Integral

import numpy as np
from scipy.special import expit


def geometry_diagnostic(pos, heard_weight=3.0, theta=-2.8, tol=1e-12, max_iter=10000):
    """Return JSON-serializable numerical bounds and local stability diagnostics.

    ``pos`` is a finite array of shape (N, 2), with N >= 1. ``heard_weight``
    must be finite and nonnegative, ``theta`` finite, ``tol`` finite and
    positive, and ``max_iter`` a positive integer.

    ``low_fixed_point`` and ``high_fixed_point`` contain the final lower and
    upper iterates. Despite their field names, they are only approximate
    fixed points when ``converged`` is true. Their residuals are infinity
    norms of T(q)-q. Both residuals must be <= tol before either converged
    classification is returned. A maximum componentwise gap <= 1e-8 gives
    ``collapsed_bounds``; a larger converged gap gives
    ``separated_fixed_points``; all other results are ``unresolved``.
    These are numerical labels, not interval-arithmetic root certificates.
    Small residuals alone do not formally prove distinct exact roots near
    a neutral multiplier, and collapsed bounds imply only the stated
    numerical gap without an additional uniqueness argument.

    Each spectral radius is that of the true Jacobian at the returned
    endpoint, diag(T(q)*(1-T(q))) @ A. A radius strictly below one certifies
    local attraction at an exact fixed point; equality to one is
    inconclusive. The symmetric matrix sqrt(D) @ A @ sqrt(D) has the same
    eigenvalues and is used to evaluate the radius.

    ``global_contraction_bound`` is heard_weight/N * rho(H), the Euclidean
    Lipschitz bound because H is symmetric and sigmoid' <= 1/4. A value
    strictly below one is sufficient for a unique globally attracting
    closure fixed point; a larger value is inconclusive.

    ``weighted_degree_min/mean/max`` summarize row sums of A, including
    heard_weight and the N/4 normalization, rather than raw row sums of H.
    """
    try:
        positions = np.asarray(pos, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("pos must be a finite array of shape (N, 2)") from exc
    if (positions.ndim != 2 or positions.shape[1] != 2
            or positions.shape[0] < 1 or not np.isfinite(positions).all()):
        raise ValueError("pos must be a finite array of shape (N, 2), N >= 1")

    try:
        heard_weight = float(heard_weight)
        theta = float(theta)
        tol = float(tol)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("heard_weight, theta and tol must be finite scalars") from exc
    if not np.isfinite(heard_weight) or heard_weight < 0:
        raise ValueError("heard_weight must be finite and nonnegative")
    if not np.isfinite(theta):
        raise ValueError("theta must be finite")
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError("tol must be finite and positive")
    if isinstance(max_iter, bool) or not isinstance(max_iter, Integral) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")

    n = len(positions)
    with np.errstate(over="ignore"):
        offsets = positions[None, :, :] - positions[:, None, :]
        distances = np.linalg.norm(offsets, axis=2)
    hearing = np.exp(-distances / 5.0)
    np.fill_diagonal(hearing, 0.0)
    coupling = (heard_weight / (n / 4)) * hearing

    low = np.zeros(n)
    high = np.ones(n)
    next_low = expit(theta + coupling @ low)
    next_high = expit(theta + coupling @ high)
    for iteration in range(1, max_iter + 1):
        low, high = next_low, next_high
        next_low = expit(theta + coupling @ low)
        next_high = expit(theta + coupling @ high)
        low_residual = float(np.max(np.abs(next_low - low)))
        high_residual = float(np.max(np.abs(next_high - high)))
        if low_residual <= tol and high_residual <= tol:
            break

    converged = low_residual <= tol and high_residual <= tol
    max_gap = float(np.max(high - low))
    if not converged:
        classification = "unresolved"
    elif max_gap <= 1e-8:
        classification = "collapsed_bounds"
    else:
        classification = "separated_fixed_points"

    radii = []
    for mapped_endpoint in (next_low, next_high):
        root_derivative = np.sqrt(mapped_endpoint * (1.0 - mapped_endpoint))
        symmetric_jacobian = (
            root_derivative[:, None] * coupling * root_derivative[None, :]
        )
        radii.append(float(np.max(np.abs(np.linalg.eigvalsh(symmetric_jacobian)))))
    hearing_radius = float(np.max(np.abs(np.linalg.eigvalsh(hearing))))
    weighted_degree = coupling.sum(axis=1)

    return {
        "low_fixed_point": low.tolist(),
        "high_fixed_point": high.tolist(),
        "low_mean": float(low.mean()),
        "high_mean": float(high.mean()),
        "max_gap": max_gap,
        "low_residual": low_residual,
        "high_residual": high_residual,
        "iterations": iteration,
        "converged": converged,
        "classification": classification,
        "low_spectral_radius": radii[0],
        "high_spectral_radius": radii[1],
        "global_contraction_bound": (heard_weight / n) * hearing_radius,
        "weighted_degree_min": float(weighted_degree.min()),
        "weighted_degree_mean": float(weighted_degree.mean()),
        "weighted_degree_max": float(weighted_degree.max()),
    }
