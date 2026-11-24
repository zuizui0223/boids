"""Restartable state transplants in the unchanged synthetic v14 Boids model.

SYNTHETIC_ONLY_NOT_FIELD_RESULT. A State retains fish order, absolute positions,
velocities, previous binary calls, the completed-update count, and the complete
PCG64 state. No state component is a separate latent biological memory variable.
Trace sample zero is the update at the input completed count; snapshots instead
record the state after the indicated absolute number of completed updates.
"""
from __future__ import annotations

from copy import deepcopy
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


def _copy_real_array(name: str, value) -> np.ndarray:
    try:
        source = np.asarray(value)
        if source.dtype.kind not in "biuf":
            raise ValueError("not real numeric data")
        result = np.array(source, dtype=float, copy=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain finite real numbers") from exc
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain finite real numbers")
    return result


def _copy_rng_state(value: dict) -> dict:
    """Admit the exact PCG64 schema, including a possible uint32 draw cache."""
    keys = {"bit_generator", "state", "has_uint32", "uinteger"}
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("rng_state must be an exact PCG64 state dictionary")
    if not isinstance(value["bit_generator"], str) or value["bit_generator"] != "PCG64":
        raise ValueError("rng_state bit_generator must be PCG64")
    inner = value["state"]
    if not isinstance(inner, dict) or set(inner) != {"state", "inc"}:
        raise ValueError("rng_state must contain exactly state and inc in its state dictionary")
    for name, number, maximum in (
        ("state", inner["state"], 2**128 - 1),
        ("inc", inner["inc"], 2**128 - 1),
        ("has_uint32", value["has_uint32"], 1),
        ("uinteger", value["uinteger"], 2**32 - 1),
    ):
        _check_integer(f"rng_state {name}", number, 0)
        if number > maximum:
            raise ValueError(f"rng_state {name} exceeds its PCG64 range")
    if inner["inc"] % 2 != 1:
        raise ValueError("rng_state inc must be odd")
    return deepcopy(value)


class State:
    """An independent, validated copy of one complete microscopic state.

    Positions and velocities have exact shape ``(N, 2)``; calls have exact shape
    ``(N,)`` and values zero or one, with N >= 3. Arrays are finite float64.
    ``completed_steps`` is a nonnegative integer. ``rng_state`` is an exact
    NumPy PCG64 state dictionary, copied recursively. Public fields may be
    inspected or serialized directly; advance/transplant revalidate them.
    """

    def __init__(self, pos, velocity, calling, completed_steps, rng_state):
        _check_integer("completed_steps", completed_steps, 0)
        copied_pos = _copy_real_array("pos", pos)
        if copied_pos.ndim != 2 or copied_pos.shape[1:] != (2,) or copied_pos.shape[0] < 3:
            raise ValueError("pos must have exact shape (N, 2), with N >= 3")
        n = copied_pos.shape[0]
        copied_velocity = _copy_real_array("velocity", velocity)
        if copied_velocity.shape != (n, 2):
            raise ValueError("velocity must have exact shape (N, 2), matching pos")
        copied_calling = _copy_real_array("calling", calling)
        if copied_calling.shape != (n,):
            raise ValueError("calling must have exact shape (N,), matching pos")
        if not np.isin(copied_calling, (0., 1.)).all():
            raise ValueError("calling must contain only binary zero/one values")
        copied_rng = _copy_rng_state(rng_state)
        self.pos = copied_pos
        self.velocity = copied_velocity
        self.calling = copied_calling
        self.completed_steps = int(completed_steps)
        self.rng_state = copied_rng


def _copy_state(state: State) -> State:
    if not isinstance(state, State):
        raise ValueError("state must be a State instance")
    return State(state.pos, state.velocity, state.calling,
                 state.completed_steps, state.rng_state)


def _snapshot_schedule(snapshot_steps, start: int, stop: int) -> np.ndarray:
    try:
        requested = tuple(snapshot_steps)
    except TypeError as exc:
        raise ValueError("snapshot_steps must contain nonnegative integers") from exc
    for completed_steps in requested:
        _check_integer("snapshot_steps entries", completed_steps, 0)
    if len(set(requested)) != len(requested):
        raise ValueError("snapshot_steps must not contain duplicates")
    return np.asarray(sorted(s for s in requested if start <= s <= stop), dtype=np.int64)


def initialize(seed: int, n: int = 32) -> State:
    """Use the original position, heading, then binomial-call draw order."""
    _check_integer("seed", seed, 0)
    _check_integer("n", n, 3)
    rng = np.random.default_rng(seed)
    pos = rng.normal(size=(n, 2)) * 4.
    headings = rng.uniform(-np.pi, np.pi, n)
    velocity = np.stack((np.cos(headings), np.sin(headings)), 1) * 1.7
    calling = rng.binomial(1, .08, n).astype(float)
    return State(pos, velocity, calling, 0, rng.bit_generator.state)


def advance(
    state: State,
    stop_step: int,
    pulse_start: int | None = None,
    pulse_duration: int = 40,
    audio_weight: float = 5.,
    heard_weight: float = 3.,
    snapshot_steps=(),
) -> dict:
    """Continue a copy of state to the absolute completed count ``stop_step``.

    The weights apply starting with the first resumed update. The cue is 0.8
    for absolute update indices in ``[pulse_start, pulse_start+pulse_duration)``;
    None disables it. One ``rng.random(N)`` draw is consumed per update in all
    arms. No initialization or reseeding occurs at the continuation boundary.

    Traces cover updates ``[state.completed_steps, stop_step)`` and contain no
    fabricated prefix. Unique nonnegative snapshot counts are sorted and
    filtered to the inclusive interval ``[state.completed_steps, stop_step]``.
    Returned snapshot arrays have shapes ``(K,N,2)``, ``(K,N,2)``, and ``(K,N)``.
    A zero-length continuation returns empty traces, requested boundary state,
    and an independent final_state. All input/output state buffers are copied.
    """
    current = _copy_state(state)
    start = current.completed_steps
    _check_integer("stop_step", stop_step, start)
    _check_integer("pulse_duration", pulse_duration, 1)
    if pulse_start is not None:
        _check_integer("pulse_start", pulse_start, 0)
    _check_weight("audio_weight", audio_weight)
    _check_weight("heard_weight", heard_weight)
    saved_steps = _snapshot_schedule(snapshot_steps, start, stop_step)

    bit_generator = np.random.PCG64()
    bit_generator.state = current.rng_state
    rng = np.random.Generator(bit_generator)
    pos, velocity, calling = current.pos, current.velocity, current.calling
    n = pos.shape[0]
    dt = .06
    steps = stop_step - start
    call_fraction = np.empty(steps, dtype=float)
    hull_area = np.empty(steps, dtype=float)
    cues = np.empty(steps, dtype=float)
    snapshot_pos = np.empty((len(saved_steps), n, 2), dtype=float)
    snapshot_velocity = np.empty((len(saved_steps), n, 2), dtype=float)
    snapshot_calling = np.empty((len(saved_steps), n), dtype=float)
    snapshot_index = 0
    if len(saved_steps) and saved_steps[0] == start:
        snapshot_pos[0] = pos
        snapshot_velocity[0] = velocity
        snapshot_calling[0] = calling
        snapshot_index = 1

    for t in range(start, stop_step):
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
        trace_index = t - start
        call_fraction[trace_index] = float(calling.mean())
        hull_area[trace_index] = float(ConvexHull(pos).volume)
        cues[trace_index] = cue
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
        "final_state": State(pos, velocity, calling, stop_step, rng.bit_generator.state),
    }


def transplant(none_state: State, pulse_state: State, mask: int) -> State:
    """Copy corner X/V/C from paired states; mask bits are X=4, V=2, C=1."""
    _check_integer("mask", mask, 0)
    if mask > 7:
        raise ValueError("mask must be an integer from 0 through 7")
    none = _copy_state(none_state)
    pulse = _copy_state(pulse_state)
    if none.completed_steps != pulse.completed_steps:
        raise ValueError("paired states must have equal completed_steps")
    if none.pos.shape != pulse.pos.shape:
        raise ValueError("paired states must have equal shapes")
    if none.rng_state != pulse.rng_state:
        raise ValueError("paired states must have equal rng_state")
    return State(
        pulse.pos if mask & 4 else none.pos,
        pulse.velocity if mask & 2 else none.velocity,
        pulse.calling if mask & 1 else none.calling,
        none.completed_steps,
        none.rng_state,
    )
