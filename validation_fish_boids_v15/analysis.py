"""Independent algebra for the frozen v15 synthetic state-transplant audit.

This module imports no simulator or predecessor analysis code. Factorial rows
are seeds; columns are masks 0..7 with X=4, V=2, C=1. Generate one bootstrap
index matrix per fixed cohort, then reuse it for every arm and derived vector.
"""
from fractions import Fraction
from numbers import Integral, Real

import numpy as np


def _integer(value, name, minimum=0):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def decompose(values):
    """Return per-seed factorial terms and Shapley allocations of 111-000.

    ``values`` must have finite shape (n, 8), including the valid empty shape
    (0, 8). Insertion is 100-000; deletion is 111-011. Signed contributions
    remain in endpoint units even when positive and negative terms cancel.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[1] != 8 or not np.isfinite(values).all():
        raise ValueError("factorial values must have finite shape (n, 8)")
    f0, f1, f2, f3, f4, f5, f6, f7 = values.T
    mobius = {
        "X": f4 - f0,
        "V": f2 - f0,
        "C": f1 - f0,
        "XV": f6 - f4 - f2 + f0,
        "XC": f5 - f4 - f1 + f0,
        "VC": f3 - f2 - f1 + f0,
        "XVC": f7 - f6 - f5 - f3 + f4 + f2 + f1 - f0,
    }
    shapley = {
        "X": mobius["X"] + (mobius["XV"] + mobius["XC"]) / 2 + mobius["XVC"] / 3,
        "V": mobius["V"] + (mobius["XV"] + mobius["VC"]) / 2 + mobius["XVC"] / 3,
        "C": mobius["C"] + (mobius["XC"] + mobius["VC"]) / 2 + mobius["XVC"] / 3,
    }
    return {
        "total": f7 - f0,
        "insertion_X": f4 - f0,
        "deletion_X": f7 - f3,
        "mobius": mobius,
        "shapley": shapley,
        "shapley_X_minus_C": shapley["X"] - shapley["C"],
    }


def decompose_counts(counts, denominator):
    """Decompose integer call totals, preserving exact cancellations.

    ``counts`` is an integer array of shape (n, 8); ``denominator`` is a
    positive integer shared by every corner. Divide only after all integer
    numerators, including Shapley X-minus-C, are complete. For continuous
    endpoints use ``decompose`` instead.

    Absolute counts above int64_max//128 are rejected conservatively: every
    intermediate numerator has magnitude at most 104 times the largest input
    magnitude. This prevents overflow even for signed count fixtures.
    """
    denominator = _integer(denominator, "denominator", minimum=1)
    counts = np.asarray(counts)
    if (counts.ndim != 2 or counts.shape[1] != 8
            or not np.issubdtype(counts.dtype, np.integer)):
        raise ValueError("factorial counts must have integer shape (n, 8)")
    limit = np.iinfo(np.int64).max // 128
    if np.any(counts < -limit) or np.any(counts > limit):
        raise ValueError("factorial counts risk integer overflow")
    counts = counts.astype(np.int64, copy=False)
    f0, f1, f2, f3, f4, f5, f6, f7 = counts.T
    mobius = {
        "X": f4 - f0,
        "V": f2 - f0,
        "C": f1 - f0,
        "XV": f6 - f4 - f2 + f0,
        "XC": f5 - f4 - f1 + f0,
        "VC": f3 - f2 - f1 + f0,
        "XVC": f7 - f6 - f5 - f3 + f4 + f2 + f1 - f0,
    }
    shapley = {
        "X": 6 * mobius["X"] + 3 * (mobius["XV"] + mobius["XC"]) + 2 * mobius["XVC"],
        "V": 6 * mobius["V"] + 3 * (mobius["XV"] + mobius["VC"]) + 2 * mobius["XVC"],
        "C": 6 * mobius["C"] + 3 * (mobius["XC"] + mobius["VC"]) + 2 * mobius["XVC"],
    }

    def divide(numerators, divisor):
        # Python integer division also handles a denominator larger than int64.
        return np.fromiter((int(value) / divisor for value in numerators),
                           dtype=float, count=numerators.size)

    return {
        "total": divide(f7 - f0, denominator),
        "insertion_X": divide(f4 - f0, denominator),
        "deletion_X": divide(f7 - f3, denominator),
        "mobius": {term: divide(value, denominator) for term, value in mobius.items()},
        "shapley": {term: divide(value, 6 * denominator) for term, value in shapley.items()},
        "shapley_X_minus_C": divide(shapley["X"] - shapley["C"], 6 * denominator),
    }


def bootstrap_indices(n, replicates=10000, seed=2026112205):
    """Draw paired whole-seed indices of shape (replicates, n).

    An empty cohort returns an integer matrix with zero columns. A singleton
    returns zero indices; its summary interval remains undefined.
    """
    n = _integer(n, "n")
    replicates = _integer(replicates, "replicates", minimum=1)
    seed = _integer(seed, "seed")
    if n == 0:
        return np.empty((replicates, 0), dtype=np.int64)
    return np.random.default_rng(seed).integers(0, n, size=(replicates, n))


def summarize(values, indices):
    """Summarize a per-seed vector using the supplied cohort resamples.

    Empty cohorts have null estimates and intervals; singleton intervals are
    null. Positive concentration divides by positive mass, never net effect.
    ``top_two_indices`` are zero-based positions in this supplied cohort;
    ties are resolved by the earlier position. No per-seed data are duplicated.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("summary values must be a finite one-dimensional vector")
    n = values.size
    indices = np.asarray(indices)
    if (indices.ndim != 2 or indices.shape[1] != n
            or not np.issubdtype(indices.dtype, np.integer)
            or np.any(indices < 0) or np.any(indices >= n)
            or (n >= 2 and indices.shape[0] == 0)):
        raise ValueError("bootstrap indices must be an integer matrix of paired cohort rows")

    positive_indices = np.flatnonzero(values > 0)
    positive_total = float(values[positive_indices].sum())
    ranking = positive_indices[np.argsort(-values[positive_indices], kind="stable")]
    top_two = ranking[:2]
    concentration = {
        "positive_total": positive_total,
        "top_two_indices": top_two.tolist(),
        "top_two_share": float(values[top_two].sum() / positive_total) if positive_total else None,
        "largest_share": float(values[ranking[0]] / positive_total) if positive_total else None,
    }
    ci95 = None
    if n >= 2:
        replicate_means = values[indices].mean(axis=1)
        ci95 = np.quantile(replicate_means, [.025, .975]).tolist()
    return {
        "n": int(n),
        "mean": float(values.mean()) if n else None,
        "median": float(np.median(values)) if n else None,
        "ci95": ci95,
        "positive": int(np.count_nonzero(values > 0)),
        "negative": int(np.count_nonzero(values < 0)),
        "zero": int(np.count_nonzero(values == 0)),
        "positive_concentration": concentration,
    }


def arrival_record(values, start_step=1040, window=200, threshold=.90, n=32):
    """Find the first completed high-call window in continuation-only samples.

    Fractions must exactly represent integer counts divided by ``n``. Window
    totals and the threshold comparison use integer arithmetic; the threshold
    is interpreted as its decimal string (so .90 means exactly nine tenths).
    Confirmation is ``start_step + window_end``. A last-window confirmation is
    observed, although its restricted latency equals the censored latency.
    """
    start_step = _integer(start_step, "start_step")
    window = _integer(window, "window", minimum=1)
    n = _integer(n, "n", minimum=1)
    if (isinstance(threshold, (bool, np.bool_)) or not isinstance(threshold, Real)
            or not np.isfinite(threshold) or not 0 <= threshold <= 1):
        raise ValueError("threshold must be a finite real number in [0, 1]")
    values = np.asarray(values, dtype=float)
    if (values.ndim != 1 or values.size < window or not np.isfinite(values).all()
            or np.any(values < 0) or np.any(values > 1)):
        raise ValueError("arrival values must be finite fractions with at least one complete window")
    counts = np.rint(values * n).astype(np.int64)
    if not np.array_equal(values, counts / n):
        raise ValueError("arrival fractions must lie on the exact integer-calling grid")
    cumulative = np.concatenate(([0], np.cumsum(counts, dtype=np.int64)))
    window_totals = cumulative[window:] - cumulative[:-window]
    exact_threshold = Fraction(str(float(threshold))) * window * n
    required_calls = -(-exact_threshold.numerator // exact_threshold.denominator)
    qualifying = np.flatnonzero(window_totals >= required_calls)
    if qualifying.size:
        latency = int(qualifying[0]) + window
        return {"confirmation_step": start_step + latency, "event_observed": True,
                "censored": False, "restricted_latency": latency}
    return {"confirmation_step": None, "event_observed": False,
            "censored": True, "restricted_latency": int(values.size)}
