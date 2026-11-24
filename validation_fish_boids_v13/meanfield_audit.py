"""Analytical and numerical audit of the deterministic Boids mean-field map.

For constant B and 0 <= alpha < 1, every equilibrium satisfies
    g = k*p + chi*B,
    p = sigmoid(h + L*p),
where L = beta*k + eta and h = theta + (beta*chi + phi)*B.

This module supports finite nonnegative gains 0 <= L <= 100. It uses only
the Python standard library. Equilibria are isolated on monotone intervals
in log-odds coordinates, including stationary roots that a sign-change grid
would miss. Returned probabilities can round to 0 or 1 in saturated tails.
"""

import math
import sys


def _finite(value, name):
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _gain(value):
    value = _finite(value, "gain")
    if not 0 <= value <= 100:
        raise ValueError("gain must lie in [0, 100]")
    return value


def _sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    exp_z = math.exp(z)
    return exp_z / (1.0 + exp_z)


def _fold_geometry(gain):
    """Return delta, positive stationary log-odds, and intercept halfwidth."""
    delta = math.sqrt((gain - 4.0) / gain)
    z_critical = 2.0 * math.atanh(delta)
    if delta < 0.25:
        # A = sum_{n>=1} 4n/(2n+1) * delta^(2n+1).
        # This avoids subtracting two nearly equal terms near L = 4.
        power = delta * delta * delta
        halfwidth = 0.0
        for n in range(1, 80):
            term = 4.0 * n / (2.0 * n + 1.0) * power
            halfwidth += term
            if term <= sys.float_info.epsilon * halfwidth:
                break
            power *= delta * delta
    else:
        halfwidth = gain * delta / 2.0 - z_critical
    return delta, z_critical, halfwidth


def folds(gain):
    """Return exact-form saddle-node locations, evaluated in floating point.

    The result is empty for L <= 4. Otherwise p_lower < p_upper and
    h_lower < h_upper; p_lower is the tangency at h_upper, while p_upper
    is the tangency at h_lower. Extremely close to L = 4, the two h values
    can round to the same float; equilibria() still resolves the centered
    three-root case using the unrounded halfwidth calculation.
    """
    gain = _gain(gain)
    if gain <= 4.0:
        return {}
    delta, _, halfwidth = _fold_geometry(gain)
    return {
        "p_lower": (1.0 - delta) / 2.0,
        "p_upper": (1.0 + delta) / 2.0,
        "h_lower": -gain / 2.0 - halfwidth,
        "h_upper": -gain / 2.0 + halfwidth,
    }


def _centered_residual(z, gain, centered_intercept):
    """z - L/2*tanh(z/2) - (h+L/2), stable near the triple root."""
    tangent = math.tanh(z / 2.0)
    if abs(z) < 0.05:
        z2 = z * z
        # Taylor series for z - 2*tanh(z/2), through z^11.
        cubic = z * z2 * (
            1.0 / 12.0 + z2 * (
                -1.0 / 120.0 + z2 * (
                    17.0 / 20160.0 + z2 * (
                        -31.0 / 362880.0 + z2 * (691.0 / 79833600.0)
                    )
                )
            )
        )
        return math.fsum((cubic, -(gain - 4.0) * tangent / 2.0, -centered_intercept))
    return math.fsum((z, -gain * tangent / 2.0, -centered_intercept))


def _bisect(function, left, right, f_left, f_right):
    """Bisection with known endpoint signs and no absolute root-merging rule."""
    if f_left == 0.0 or left == right:
        return left
    if f_right == 0.0:
        return right
    if (f_left < 0.0) == (f_right < 0.0):
        raise ArithmeticError("root interval does not bracket a sign change")
    for _ in range(160):
        middle = left + (right - left) / 2.0
        if middle == left or middle == right:
            return middle
        f_middle = function(middle)
        if f_middle == 0.0:
            return middle
        if (f_middle < 0.0) == (f_left < 0.0):
            left, f_left = middle, f_middle
        else:
            right, f_right = middle, f_middle
    return left + (right - left) / 2.0


def equilibria(gain, intercept):
    """Sorted distinct roots of p = sigmoid(intercept + gain*p).

    Saddle-node roots at the bounds returned by folds() are emitted once.
    The L=4, h=-2 triple root is emitted once. No broad proximity tolerance
    merges nearby distinct roots. At a floating-point fold bound, the
    intended tangency is recognized explicitly; sub-ulp parameter offsets
    cannot be distinguished from that bound.
    """
    gain = _gain(gain)
    intercept = _finite(intercept, "intercept")
    if gain == 0.0:
        return [_sigmoid(intercept)]
    centered = intercept + gain / 2.0
    residual = lambda z: _centered_residual(z, gain, centered)
    lower_z, upper_z = intercept, intercept + gain
    lower_value = -gain * _sigmoid(lower_z)
    upper_value = gain * _sigmoid(-upper_z)
    if gain <= 4.0:
        if centered == 0.0:
            return [0.5]
        z = _bisect(residual, lower_z, upper_z, lower_value, upper_value)
        return [_sigmoid(z)]

    delta, critical_z, halfwidth = _fold_geometry(gain)
    h_lower = -gain / 2.0 - halfwidth
    h_upper = -gain / 2.0 + halfwidth

    def left_root():
        z = _bisect(residual, lower_z, -critical_z, lower_value, halfwidth - centered)
        return _sigmoid(z)

    def right_root():
        z = _bisect(residual, critical_z, upper_z, -halfwidth - centered, upper_value)
        return _sigmoid(z)

    # Do not interpret a collapsed, rounded fold interval as a double root:
    # for L just above 4, h=-L/2 still has three distinct equilibria.
    at_lower = centered == -halfwidth or (
        centered != 0.0 and h_lower < h_upper and intercept == h_lower
    )
    at_upper = centered == halfwidth or (
        centered != 0.0 and h_lower < h_upper and intercept == h_upper
    )
    if at_lower:
        return [left_root(), (1.0 + delta) / 2.0]
    if at_upper:
        return [(1.0 - delta) / 2.0, right_root()]
    if centered < -halfwidth:
        return [left_root()]
    if centered > halfwidth:
        return [right_root()]
    middle_z = _bisect(
        residual, -critical_z, critical_z,
        halfwidth - centered, -halfwidth - centered,
    )
    return [left_root(), _sigmoid(middle_z), right_root()]


def stability(p, alpha=.65, k=1, beta=4, eta=2):
    """Linear stability of the full (g,p) map in the nonnegative model domain.

    The Jacobian is [[alpha, (1-alpha)*k], [beta*s, eta*s]],
    s=p*(1-p). Eigenvalues are real in this domain and JSON serializable.
    The Jacobian is strictly Schur stable iff (beta*k+eta)*s < 1,
    which is sufficient for local exponential asymptotic stability.
    'nonhyperbolic' denotes spectral radius 1 to floating precision and
    makes no nonlinear-stability claim. An already unstable point remains
    classified as unstable if its second multiplier lies on the unit circle.
    """
    p, alpha = _finite(p, "p"), _finite(alpha, "alpha")
    k, beta, eta = _finite(k, "k"), _finite(beta, "beta"), _finite(eta, "eta")
    if not 0 <= p <= 1:
        raise ValueError("p must lie in [0, 1]")
    if not 0 <= alpha < 1:
        raise ValueError("alpha must lie in [0, 1)")
    if min(k, beta, eta) < 0:
        raise ValueError("k, beta and eta must be nonnegative")
    gain = _gain(beta * k + eta)
    slope = p * (1.0 - p)
    trace = alpha + eta * slope
    determinant = slope * (alpha * eta - (1.0 - alpha) * beta * k)
    discriminant_root = math.hypot(
        alpha - eta * slope,
        2.0 * math.sqrt((1.0 - alpha) * beta * k * slope),
    )
    larger = (trace + discriminant_root) / 2.0
    smaller = determinant / larger if larger else 0.0
    spectral_radius = max(abs(larger), abs(smaller))
    neutral_tolerance = 32.0 * sys.float_info.epsilon
    if spectral_radius > 1.0 + neutral_tolerance:
        classification = "unstable"
    elif abs(spectral_radius - 1.0) <= neutral_tolerance:
        classification = "nonhyperbolic"
    else:
        classification = "stable"
    return {
        "jacobian": [[alpha, (1.0 - alpha) * k], [beta * slope, eta * slope]],
        "trace": trace,
        "determinant": determinant,
        "eigenvalues": [larger, smaller],
        "spectral_radius": spectral_radius,
        "classification": classification,
        "gain_times_slope": gain * slope,
        "jury": {
            "one_minus_trace_plus_det": (1.0 - alpha) * (1.0 - gain * slope),
            "one_plus_trace_plus_det": 1.0 + trace + determinant,
            "one_minus_det": 1.0 - determinant,
        },
    }


def _settle(theta, g, p, parameters, tolerance, max_steps):
    for steps in range(max_steps + 1):
        next_g = parameters["alpha"] * g + (1.0 - parameters["alpha"]) * (
            parameters["k"] * p + parameters["chi"] * parameters["B"]
        )
        next_p = _sigmoid(
            theta + parameters["beta"] * g + parameters["eta"] * p
            + parameters["phi"] * parameters["B"]
        )
        residual = max(abs(next_g - g), abs(next_p - p))
        if residual <= tolerance or steps == max_steps:
            return {
                "theta": theta, "g": g, "p": p, "steps": steps,
                "residual": residual, "converged": residual <= tolerance,
            }
        g, p = next_g, next_p
    raise AssertionError("unreachable")


def _sweep(thetas, initial_p, parameters, tolerance, max_steps):
    p = initial_p
    g = parameters["k"] * p + parameters["chi"] * parameters["B"]
    rows = []
    for theta in thetas:
        row = _settle(theta, g, p, parameters, tolerance, max_steps)
        rows.append(row)
        g, p = row["g"], row["p"]
    return rows


def _largest_jump(rows):
    before, after = max(
        zip(rows, rows[1:]), key=lambda pair: abs(pair[1]["p"] - pair[0]["p"])
    )
    return {
        "from_theta": before["theta"],
        "to_theta": after["theta"],
        "delta_p": after["p"] - before["p"],
    }


def run_audit():
    """Return baseline roots, stability, exact folds, and converged theta sweeps.

    Both sweeps use the full two-state updates, continuation from the
    previous settled state, 201 theta values over [-4.5, -1.5], and an
    explicit fixed-point residual check at every reported state. This is
    a deterministic model experiment, not empirical evidence about fish.
    """
    parameters = {
        "alpha": 0.65, "k": 1.0, "beta": 4.0, "eta": 2.0,
        "chi": 0.2, "phi": 0.6, "theta": -3.0, "B": 0.0,
    }
    gain = parameters["beta"] * parameters["k"] + parameters["eta"]
    coefficient = parameters["beta"] * parameters["chi"] + parameters["phi"]
    intercept = parameters["theta"] + coefficient * parameters["B"]
    parameters.update({
        "gain": gain, "effective_intercept": intercept,
        "forcing_intercept_coefficient": coefficient,
    })
    roots = []
    for p in equilibria(gain, intercept):
        g = parameters["k"] * p + parameters["chi"] * parameters["B"]
        roots.append({
            "p": p, "g": g, "residual": abs(p - _sigmoid(intercept + gain * p)),
            "stability": stability(
                p, parameters["alpha"], parameters["k"],
                parameters["beta"], parameters["eta"],
            ),
        })
    boundaries = folds(gain)
    boundaries.update({
        "theta_lower": boundaries["h_lower"] - coefficient * parameters["B"],
        "theta_upper": boundaries["h_upper"] - coefficient * parameters["B"],
        "B_lower": (boundaries["h_lower"] - parameters["theta"]) / coefficient,
        "B_upper": (boundaries["h_upper"] - parameters["theta"]) / coefficient,
    })
    tolerance, max_steps = 1e-11, 10000
    thetas = [-4.5 + 3.0 * index / 200.0 for index in range(201)]
    increasing = _sweep(thetas, 0.0, parameters, tolerance, max_steps)
    decreasing = _sweep(list(reversed(thetas)), 1.0, parameters, tolerance, max_steps)
    all_rows = increasing + decreasing
    return {
        "parameters": parameters,
        "roots": roots,
        "folds": boundaries,
        "sweeps": {
            "parameter": "theta", "B": parameters["B"],
            "settle_tolerance": tolerance, "max_steps": max_steps,
            "increasing": increasing, "decreasing": decreasing,
        },
        "checks": {
            "roots_residual_max": max(root["residual"] for root in roots),
            "all_sweep_points_converged": all(row["converged"] for row in all_rows),
            "sweep_residual_max": max(row["residual"] for row in all_rows),
            "bistability_at_baseline": sum(
                root["stability"]["classification"] == "stable" for root in roots
            ) == 2,
            "increasing_jump": _largest_jump(increasing),
            "decreasing_jump": _largest_jump(decreasing),
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_audit(), indent=2, allow_nan=False))
