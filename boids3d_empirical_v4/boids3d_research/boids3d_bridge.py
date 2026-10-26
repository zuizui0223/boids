"""A small, explicitly synthetic 3D Boids-to-niche research prototype.

Nothing here estimates parameters of wild bats or birds.  Local interaction,
movement/environment response, and scoring are separate modules so that
future empirical work can test models on held-out individuals/nights.

Requires: numpy. Python 3.10+.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Rules:
    dt: float = 0.5                    # seconds
    min_speed: float = 3.0             # airspeed, m/s (illustrative)
    max_speed: float = 13.0
    max_climb_rate: float = 3.0        # m/s (illustrative)
    max_accel: float = 5.0            # m/s^2
    neighbor_radius: float = 55.0     # m, metric neighbourhood
    topological_k: int = 6
    separation_radius: float = 11.0
    separation_weight: float = 2.0
    alignment_weight: float = 0.15
    cohesion_weight: float = 0.012
    patch_weight: float = 0.017
    vertical_damping: float = 0.75
    noise_sd: float = 0.25
    z_min: float = 5.0
    z_max: float = 200.0


def neighbors(pos: np.ndarray, method: str, rules: Rules) -> np.ndarray:
    """Boolean directed interaction graph; self never interacts with self."""
    dist = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=-1)
    np.fill_diagonal(dist, np.inf)
    if method == "metric":
        out = dist < rules.neighbor_radius
    elif method == "topological":
        k = min(rules.topological_k, max(0, len(pos) - 1))
        out = np.zeros_like(dist, dtype=bool)
        if k:
            nearest = np.argpartition(dist, k - 1, axis=1)[:, :k]
            out[np.arange(len(pos))[:, None], nearest] = True
    else:
        raise ValueError("method must be 'metric' or 'topological'")
    np.fill_diagonal(out, False)
    return out


def _clip_magnitude(vec: np.ndarray, maximum: float) -> np.ndarray:
    norm = np.linalg.norm(vec, axis=1, keepdims=True)
    return vec * np.minimum(1.0, maximum / np.maximum(norm, 1e-9))


def step(pos: np.ndarray, air_vel: np.ndarray, t: float, gains: np.ndarray,
         rng: np.random.Generator, *, model: str = "boids_personal",
         method: str = "metric", rules: Rules = Rules()):
    """One synchronous Euler step. Wind shifts *ground* motion, not airspeed."""
    n = len(pos)
    accel = np.zeros_like(pos)
    if model in {"boids_shared", "boids_personal"}:
        nb = neighbors(pos, method, rules)
        # Always apply short-range physical collision repulsion; not just k-NN.
        delta = pos[:, None, :] - pos[None, :, :]
        dist = np.linalg.norm(delta, axis=-1)
        close = (dist < rules.separation_radius) & (dist > 1e-7)
        sep = np.where(close[..., None], delta / np.maximum(dist[..., None] ** 2, 1e-6), 0).sum(axis=1)
        accel += rules.separation_weight * sep
        n_nb = nb.sum(axis=1, keepdims=True)
        sum_v = (nb[..., None] * air_vel[None, :, :]).sum(axis=1)
        sum_p = (nb[..., None] * pos[None, :, :]).sum(axis=1)
        mean_v = np.divide(sum_v, n_nb, out=np.copy(air_vel), where=n_nb > 0)
        mean_p = np.divide(sum_p, n_nb, out=np.copy(pos), where=n_nb > 0)
        accel += rules.alignment_weight * (mean_v - air_vel)
        accel += rules.cohesion_weight * (mean_p - pos)
    elif model != "independent_shared":
        raise ValueError("model must be independent_shared, boids_shared or boids_personal")

    # Environment known to all individuals: one moving feeding patch plus a
    # common height field (NOT personal target heights).
    patch = np.array([45.0 * np.sin(0.011 * t), 45.0 * np.cos(0.009 * t)])
    accel[:, :2] += rules.patch_weight * (patch - pos[:, :2])
    resource_height = (95.0 + 19.0 * np.sin(0.045 * t)
                       + 19.0 * np.sin(pos[:, 0] / 65.0)
                       + 11.0 * np.cos(pos[:, 1] / 50.0))
    accel[:, 2] += gains * (resource_height - pos[:, 2]) - rules.vertical_damping * air_vel[:, 2]
    accel += rng.normal(0.0, rules.noise_sd, size=(n, 3))
    accel = _clip_magnitude(accel, rules.max_accel)

    vel = air_vel + rules.dt * accel
    # Illustrative flight envelope.  Used in all treatment arms identically.
    vel[:, 2] = np.clip(vel[:, 2], -rules.max_climb_rate, rules.max_climb_rate)
    speed = np.linalg.norm(vel, axis=1, keepdims=True)
    vel *= np.clip(speed, rules.min_speed, rules.max_speed) / np.maximum(speed, 1e-9)
    wind = np.zeros_like(vel)
    wind[:, 0] = 0.55 + 0.18 * np.sin(t / 41.0)
    wind[:, 1] = 0.25 * np.cos(t / 55.0)
    new_pos = pos + rules.dt * (vel + wind)

    # Soft numerical safeguard: bounce if hitting the vertical domain edge.
    low = new_pos[:, 2] < rules.z_min
    high = new_pos[:, 2] > rules.z_max
    new_pos[:, 2] = np.clip(new_pos[:, 2], rules.z_min, rules.z_max)
    vel[low, 2] = abs(vel[low, 2]); vel[high, 2] = -abs(vel[high, 2])
    return new_pos, vel


def simulate(*, model: str, method: str, seed: int = 17, n: int = 14,
             nights: int = 4, steps: int = 1800, burn: int = 350,
             thin: int = 5, rules: Rules = Rules(),
             swap_personal_between_nights: bool = False):
    """Return nights x individuals x time x 3, plus population gain vector.

    swap_personal_between_nights severs persistent gain-to-identity mapping
    while retaining the same set of individual gains within every night.
    """
    if n < 2 or nights < 2 or steps <= burn or thin <= 0:
        raise ValueError("need >=2 agents/nights and a nonempty retained interval")
    rng = np.random.default_rng(seed)
    gains = (np.linspace(0.018, 0.45, n)
             if model == "boids_personal" else np.repeat(0.17, n))
    samples = []
    for night in range(nights):
        night_gains = gains[rng.permutation(n)] if swap_personal_between_nights else gains
        p = np.column_stack([rng.normal(0, 17, size=n),
                             rng.normal(0, 17, size=n),
                             rng.normal(95, 8, size=n)])
        heading = rng.normal(0, 1, size=(n, 3))
        heading[:, 2] *= 0.10
        v = 7.0 * heading / np.linalg.norm(heading, axis=1, keepdims=True)
        frames = []
        for j in range(steps):
            p, v = step(p, v, t=j * rules.dt, gains=night_gains, rng=rng,
                        model=model, method=method, rules=rules)
            if j >= burn and (j - burn) % thin == 0:
                frames.append(p.copy())
        samples.append(np.stack(frames).transpose(1, 0, 2))
    return np.stack(samples), gains


def centered_height_histories(traces: np.ndarray, edges=None):
    """One center-per-session histogram, not raw (altitude-confounded) height."""
    if edges is None:
        edges = np.array([-np.inf, -70., -40., -20., -10., 10., 20., 40., 70., np.inf])
    centered = traces[..., 2] - np.median(traces[..., 2], axis=-1, keepdims=True)
    h = np.zeros((*centered.shape[:2], len(edges) - 1), dtype=float)
    for a in range(centered.shape[0]):
        for b in range(centered.shape[1]):
            h[a, b] = np.histogram(centered[a, b], bins=edges)[0]
    return h


def heldout_shape_gain(histories: np.ndarray, labels: np.ndarray | None = None,
                       pseudocount: float = 0.5) -> float:
    """Self-vs-peer log score, leave-one-night-out, individual-equal weighted.

    labels: nights x original_individual -> identity, distinct within night.
    """
    nights, n, bins = histories.shape
    if labels is None:
        labels = np.broadcast_to(np.arange(n), (nights, n))
    heldout = np.empty((nights, n), dtype=float)
    for t in range(nights):
        training = np.arange(nights) != t
        for i in range(n):
            lab = labels[t, i]
            self_train = histories[training][labels[training] == lab].sum(axis=0)
            peer_train = histories[training][labels[training] != lab].sum(axis=0)
            p_self = (self_train + pseudocount) / (self_train.sum() + bins * pseudocount)
            p_peer = (peer_train + pseudocount) / (peer_train.sum() + bins * pseudocount)
            heldout[t, i] = np.dot(histories[t, i], np.log(p_self / p_peer)) / histories[t, i].sum()
    return float(heldout.mean())


def permutation_calibration(histories: np.ndarray, seed: int = 770, reps: int = 199):
    """Whole-night-agent label shuffles; contrast against its own nonzero null."""
    if reps < 1:
        raise ValueError("reps must be >=1")
    observed = heldout_shape_gain(histories)
    rng = np.random.default_rng(seed)
    nights, n, _ = histories.shape
    shuffled = np.empty(reps)
    for j in range(reps):
        labels = np.stack([rng.permutation(n) for _ in range(nights)])
        shuffled[j] = heldout_shape_gain(histories, labels)
    return {
        "raw_gain_nats_per_fix": observed,
        "null_mean_nats_per_fix": float(shuffled.mean()),
        "calibrated_excess_nats_per_fix": float(observed - shuffled.mean()),
        "permutation_p_one_sided": float((1 + (shuffled >= observed).sum()) / (reps + 1)),
        "reps": reps,
    }


def mean_horizontal_overlap(traces: np.ndarray, extent: float = 210.0,
                            nbins: int = 7) -> float:
    """Mean pairwise Bhattacharyya coefficient of coarse x-y occupancy [0,1]."""
    n = traces.shape[1]
    edges = np.linspace(-extent, extent, nbins + 1)
    profile = []
    for i in range(n):
        xy = traces[:, i, :, :2].reshape(-1, 2)
        histogram, _, _ = np.histogram2d(xy[:, 0], xy[:, 1], bins=(edges, edges))
        histogram = histogram + 0.5
        profile.append(histogram.ravel() / histogram.sum())
    ps = np.stack(profile)
    similarity = np.sqrt(ps[:, None, :] * ps[None, :, :]).sum(axis=-1)
    return float(similarity[np.triu_indices(n, k=1)].mean())


def benchmark(seed: int, reps: int, n: int = 14, steps: int = 1800):
    result = {}
    for model in ["independent_shared", "boids_shared", "boids_personal",
                  "boids_personal_swapped"]:
        synthetic_model = ("boids_personal" if model == "boids_personal_swapped"
                           else model)
        traces, gains = simulate(model=synthetic_model, method="topological", seed=seed,
                                 n=n, steps=steps, burn=max(50, steps // 5),
                                 swap_personal_between_nights=(model == "boids_personal_swapped"))
        h = centered_height_histories(traces)
        summary = permutation_calibration(h, seed=seed + 101, reps=reps)
        summary["horizontal_Bhattacharyya_overlap"] = mean_horizontal_overlap(traces)
        summary["gain_min"] = float(gains.min())
        summary["gain_max"] = float(gains.max())
        summary["observed_agents"] = n
        summary["nights"] = traces.shape[0]
        summary["height_sample_count_per_night"] = traces.shape[2]
        result[model] = summary
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--reps", type=int, default=199)
    parser.add_argument("--agents", type=int, default=14)
    parser.add_argument("--steps", type=int, default=1800)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.seed, args.reps, args.agents, args.steps), indent=2))
