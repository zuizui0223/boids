"""Timed interventions in the synthetic v13 microscopic acoustic Boids model.

This synthetic model is not a fit to fish data or a claim about real fish
mechanisms. The equations, random draws, and update order are unchanged from
v13. Individual previous calling states and positions are model memory;
velocity is also retained across updates. Interventions change only the two
acoustic weights, retaining all state. Trace samples follow movement and call
updates, while snapshots are indexed by the number of completed updates.
"""
from __future__ import annotations

from numbers import Integral, Real

import numpy as np
from scipy.special import expit
from scipy.spatial import ConvexHull


def _check_integer(name: str, value: int, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _check_weight(name: str, value: float) -> None:
    if not isinstance(value, Real) or not np.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


def _snapshot_schedule(snapshot_steps, steps: int) -> np.ndarray:
    try:
        requested = tuple(snapshot_steps)
    except TypeError as exc:
        raise ValueError("snapshot_steps must contain nonnegative integers") from exc
    for completed_steps in requested:
        _check_integer("snapshot_steps entries", completed_steps, 0)
    if len(set(requested)) != len(requested):
        raise ValueError("snapshot_steps must not contain duplicates")
    return np.asarray(sorted(s for s in requested if s <= steps), dtype=np.int64)


def simulate(
    seed: int,
    steps: int = 16000,
    pulse_start: int | None = 1000,
    pulse_duration: int = 40,
    intervention_step: int | None = None,
    audio_weight_after: float = 5.0,
    heard_weight_after: float = 3.0,
    n: int = 32,
    snapshot_steps=(1000, 1040, 4000, 16000),
) -> dict[str, np.ndarray]:
    """Return synthetic traces and snapshots without changing v13 dynamics.

    ``call_fraction``, ``hull_area``, and ``cue`` have shape ``(steps,)``.
    ``pulse_start=None`` disables playback. Otherwise the cue is 0.8 on the
    half-open interval ``[pulse_start, pulse_start + pulse_duration)`` and zero
    elsewhere. Pulses beyond the end of a run are permitted. Duration must
    be positive even when playback is disabled. Seed and pulse start are
    nonnegative integers, steps is positive, and at least three fish are needed.

    Weights are exactly 5.0 and 3.0 before ``intervention_step``. Starting with
    update ``t == intervention_step``, use ``audio_weight_after`` for movement
    toward callers and ``heard_weight_after`` for perceived-sound excitation.
    ``intervention_step=None`` leaves the weights unchanged throughout. A
    nonnegative intervention beyond the horizon is allowed. Both afterweights
    must be finite and nonnegative even when they will not be used.

    A seed consumes the same initialization draws and one ``rng.random(n)``
    draw per step in every arm, including when either acoustic weight is zero.
    Geometry and perceived sound use the previous individual calling state;
    movement is updated before drawing the current step's calls. The timestep
    remains 0.06. No state is reset when the weights change.

    ``snapshot_steps`` contains unique nonnegative integer completed-update
    counts. Its returned integer array is sorted and filtered to ``[0, steps]``.
    A snapshot at count ``s`` records the state after ``s`` completed updates,
    before update ``t == s``; count zero records initialization. Returned
    ``snapshot_pos`` and ``snapshot_velocity`` have shape ``(K, n, 2)``, and
    ``snapshot_calling`` has shape ``(K, n)``. All non-index arrays are float64.
    """
    _check_integer("seed", seed, 0)
    _check_integer("steps", steps, 1)
    _check_integer("n", n, 3)
    _check_integer("pulse_duration", pulse_duration, 1)
    if pulse_start is not None:
        _check_integer("pulse_start", pulse_start, 0)
    if intervention_step is not None:
        _check_integer("intervention_step", intervention_step, 0)
    _check_weight("audio_weight_after", audio_weight_after)
    _check_weight("heard_weight_after", heard_weight_after)
    saved_steps = _snapshot_schedule(snapshot_steps, steps)

    rng = np.random.default_rng(seed)
    dt = .06
    pos = rng.normal(size=(n, 2)) * 4.
    headings = rng.uniform(-np.pi, np.pi, n)
    velocity = np.stack((np.cos(headings), np.sin(headings)), 1) * 1.7
    calling = rng.binomial(1, .08, n).astype(float)
    call_fraction = np.empty(steps, dtype=float)
    hull_area = np.empty(steps, dtype=float)
    cues = np.empty(steps, dtype=float)
    snapshot_pos = np.empty((len(saved_steps), n, 2), dtype=float)
    snapshot_velocity = np.empty((len(saved_steps), n, 2), dtype=float)
    snapshot_calling = np.empty((len(saved_steps), n), dtype=float)
    snapshot_index = 0
    if len(saved_steps) and saved_steps[0] == 0:
        snapshot_pos[0] = pos
        snapshot_velocity[0] = velocity
        snapshot_calling[0] = calling
        snapshot_index = 1
    audio_weight, heard_weight = 5.0, 3.0

    for t in range(steps):
        if intervention_step is not None and t == intervention_step:
            audio_weight = audio_weight_after
            heard_weight = heard_weight_after
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
        if snapshot_index < len(saved_steps) and saved_steps[snapshot_index] == t + 1:
            snapshot_pos[snapshot_index] = pos
            snapshot_velocity[snapshot_index] = velocity
            snapshot_calling[snapshot_index] = calling
            snapshot_index += 1

    return {
        "call_fraction": call_fraction,
        "hull_area": hull_area,
        "cue": cues,
        "snapshot_steps": saved_steps,
        "snapshot_pos": snapshot_pos,
        "snapshot_velocity": snapshot_velocity,
        "snapshot_calling": snapshot_calling,
    }
