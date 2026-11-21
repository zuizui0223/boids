"""Long-duration replay of the synthetic v12 microscopic acoustic Boids model.

This is a synthetic model, not a fit to fish data. The equations, random
draws, and update order are unchanged from v12. This extension adds configurable
pulse timing, a longer default run, and array outputs. All returned samples
are recorded after that step's movement and call update, as in v12.
"""
from __future__ import annotations

from numbers import Integral

import numpy as np
from scipy.special import expit
from scipy.spatial import ConvexHull


def _check_integer(name: str, value: int, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def simulate(
    seed: int,
    steps: int = 4000,
    pulse_start: int | None = 1000,
    pulse_duration: int = 40,
    audio_weight: float = 5.0,
    heard_weight: float = 3.0,
    n: int = 32,
) -> dict[str, np.ndarray]:
    """Return call fraction, convex-hull area, and cue arrays of shape ``(steps,)``.

    ``pulse_start=None`` disables playback. Otherwise the cue is 0.8 on the
    half-open interval ``[pulse_start, pulse_start + pulse_duration)`` and zero
    elsewhere. Pulses beyond the end of a run are permitted. Duration must
    be positive even when playback is disabled. Seed and pulse start are
    nonnegative integers, steps is positive, and at least three fish are needed.

    A seed consumes the same initialization draws and one ``rng.random(n)``
    draw per step in every arm, including when either acoustic weight is zero.
    Geometry and perceived sound use the previous calling state; movement is
    updated before drawing the current step's calls. The timestep remains 0.06.
    """
    _check_integer("seed", seed, 0)
    _check_integer("steps", steps, 1)
    _check_integer("n", n, 3)
    _check_integer("pulse_duration", pulse_duration, 1)
    if pulse_start is not None:
        _check_integer("pulse_start", pulse_start, 0)

    rng = np.random.default_rng(seed)
    dt = .06
    pos = rng.normal(size=(n, 2)) * 4.
    headings = rng.uniform(-np.pi, np.pi, n)
    velocity = np.stack((np.cos(headings), np.sin(headings)), 1) * 1.7
    calling = rng.binomial(1, .08, n).astype(float)
    call_fraction = np.empty(steps, dtype=float)
    hull_area = np.empty(steps, dtype=float)
    cues = np.empty(steps, dtype=float)

    for t in range(steps):
        diff = pos[None, :, :] - pos[:, None, :]
        dist = np.linalg.norm(diff, axis=2)
        mask_eye = np.eye(n, dtype=bool)
        neigh = (dist < 7.) & (~mask_eye)
        counts = np.maximum(neigh.sum(1), 1)
        delta_v = velocity[None, :, :] - velocity[:, None, :]
        separation = np.sum(np.where(((dist < 1.2) & (~mask_eye))[:, :, None],
                            -diff / np.maximum(dist[:, :, None] ** 2, .05), 0.),
                            1) / counts[:, None]
        cohesion = np.sum(neigh[:, :, None] * diff, 1) / counts[:, None]
        alignment = np.sum(neigh[:, :, None] * delta_v, 1) / counts[:, None]
        hearing = np.exp(-dist / 5) * (~mask_eye)
        perceived = (hearing @ calling) / (n / 4)
        toward_callers = (hearing[:, :, None] * calling[None, :, None] * diff /
                          np.maximum(dist[:, :, None], .5)).sum(1) / n
        r = np.linalg.norm(pos, axis=1, keepdims=True)
        wall = -np.maximum(r - 10., 0.) * pos / np.maximum(r, 1.)
        force = (8 * separation + .012 * cohesion + .8 * alignment
                 + audio_weight * toward_callers + 2 * wall)
        velocity += dt * force
        speed = np.linalg.norm(velocity, axis=1, keepdims=True)
        velocity = velocity / np.maximum(speed, .001) * np.clip(speed, .6, 3.)
        pos += dt * velocity
        cue = (.8 if pulse_start is not None
               and pulse_start <= t < pulse_start + pulse_duration else 0.)
        probabilities = expit(-2.8 + heard_weight * perceived + cue)
        calling = (rng.random(n) < probabilities).astype(float)
        call_fraction[t] = float(calling.mean())
        hull_area[t] = float(ConvexHull(pos).volume)
        cues[t] = cue

    return {"call_fraction": call_fraction, "hull_area": hull_area, "cue": cues}
