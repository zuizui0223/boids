"""Seed-paired summaries for a fixed synthetic experiment, never frame-level inference."""
from __future__ import annotations
import numpy as np


def window_mean(values, start, end):
    a = np.asarray(values, dtype=float)
    if (a.ndim != 2 or not 0 <= start < end <= a.shape[1]
            or not np.isfinite(a).all()):
        raise ValueError("Expected finite seed-by-time values and a valid nonempty window")
    return a[:, start:end].mean(axis=1)


def paired_summary(no_pulse, pulse, resampling_indices):
    a, b = np.asarray(no_pulse, dtype=float), np.asarray(pulse, dtype=float)
    if (a.ndim != 1 or a.size == 0 or a.shape != b.shape
            or not np.isfinite(a).all() or not np.isfinite(b).all()):
        raise ValueError("Expected equal nonempty finite vectors of paired seed outcomes")
    ix = np.asarray(resampling_indices)
    if (ix.ndim != 2 or ix.shape[0] < 1 or ix.shape[1] != a.size
            or not np.issubdtype(ix.dtype, np.integer) or np.any(ix < 0)
            or np.any(ix >= a.size)):
        raise ValueError("Bootstrap indices must resample whole paired seeds")
    difference = b - a
    bootstrap = difference[ix].mean(axis=1)
    return {
        "n_seed_pairs": int(a.size),
        "no_pulse_mean": float(a.mean()),
        "pulse_mean": float(b.mean()),
        "mean_difference": float(difference.mean()),
        "bootstrap_95_interval": np.quantile(bootstrap, [.025, .975]).tolist(),
        "positive_seed_pairs": int(np.count_nonzero(difference > 0)),
        "negative_seed_pairs": int(np.count_nonzero(difference < 0)),
        "zero_seed_pairs": int(np.count_nonzero(difference == 0)),
        "per_seed_no_pulse": a.tolist(),
        "per_seed_pulse": b.tolist(),
        "per_seed_difference": difference.tolist(),
    }


def interaction_contrast(full, no_motor, no_hearing, neither):
    arrays = [np.asarray(x, dtype=float) for x in (full, no_motor, no_hearing, neither)]
    if (arrays[0].ndim != 1 or arrays[0].size == 0
            or any(x.shape != arrays[0].shape or not np.isfinite(x).all()
                   for x in arrays)):
        raise ValueError("Interaction requires four matched finite seed vectors")
    return arrays[0] - arrays[1] - arrays[2] + arrays[3]

