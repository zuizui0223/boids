"""Fixed seed-paired estimands and explicitly censored high-window times."""
from __future__ import annotations
from numbers import Integral, Real
import numpy as np


def _integer(value, minimum=0):
    return not isinstance(value, bool) and isinstance(value, Integral) and value >= minimum


def _vectors(*values):
    arrays = [np.asarray(x, dtype=float) for x in values]
    if (not arrays or arrays[0].ndim != 1 or arrays[0].size == 0
            or any(a.shape != arrays[0].shape or not np.isfinite(a).all() for a in arrays)):
        raise ValueError('Expected equally shaped, nonempty finite paired vectors')
    return arrays


def contrast_summary(differences, indices):
    (d,) = _vectors(differences)
    ix = np.asarray(indices)
    if (ix.ndim != 2 or ix.shape[0] < 1 or ix.shape[1] != d.size
            or not np.issubdtype(ix.dtype, np.integer)
            or np.any(ix < 0) or np.any(ix >= d.size)):
        raise ValueError('Bootstrap indices must resample whole paired seeds')
    resampled = d[ix].mean(axis=1)
    return {
        'n_seed_pairs': int(d.size),
        'mean_difference': float(d.mean()),
        'median_difference': float(np.median(d)),
        'bootstrap_95_interval': np.quantile(resampled, [.025, .975]).tolist(),
        'positive_seed_pairs': int(np.count_nonzero(d > 0)),
        'negative_seed_pairs': int(np.count_nonzero(d < 0)),
        'zero_seed_pairs': int(np.count_nonzero(d == 0)),
        'per_seed_difference': d.tolist(),
    }


def paired_summary(no_pulse, pulse, indices):
    a, b = _vectors(no_pulse, pulse)
    return {**contrast_summary(b - a, indices),
            'no_pulse_mean': float(a.mean()), 'pulse_mean': float(b.mean()),
            'per_seed_no_pulse': a.tolist(), 'per_seed_pulse': b.tolist()}


def difference_in_differences(intact_none, intact_pulse, cut_none, cut_pulse):
    a, b, c, d = _vectors(intact_none, intact_pulse, cut_none, cut_pulse)
    return (d - c) - (b - a)


def window_mean(values, start, end):
    a = np.asarray(values, dtype=float)
    if (a.ndim != 2 or not _integer(start) or not _integer(end, 1)
            or not 0 <= start < end <= a.shape[1] or not np.isfinite(a).all()):
        raise ValueError('Expected finite seed-by-time values and a nonempty valid window')
    return a[:, start:end].mean(axis=1)


def first_high_window(values, start=1040, window=200, threshold=.90):
    """Find a completed high-mean window, retaining a right-censoring flag.

    Confirmation s+window means samples s,...,s+window-1 met the criterion.
    A confirmation exactly at the horizon is observed; an absent event has
    the same restricted latency but is explicitly censored. This diagnostic
    does not identify an absorbing transition or a stationary high state.
    """
    (a,) = _vectors(values)
    if (not _integer(start) or not _integer(window, 1) or start + window > a.size
            or isinstance(threshold, bool) or not isinstance(threshold, Real)
            or not np.isfinite(threshold) or not 0 <= threshold <= 1
            or np.any(a < 0) or np.any(a > 1)):
        raise ValueError('Invalid call fractions, search window or high-activity threshold')
    cumulative = np.concatenate(([0.], np.cumsum(a[start:])))
    totals = cumulative[window:] - cumulative[:-window]
    matches = np.flatnonzero(totals >= threshold * window)
    confirmation = int(start + matches[0] + window) if matches.size else None
    return {
        'confirmation_step': confirmation,
        'event_observed': confirmation is not None,
        'censored': confirmation is None,
        'restricted_latency': int((confirmation if confirmation is not None else a.size) - start),
    }
