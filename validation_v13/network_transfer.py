#!/usr/bin/env python3
"""v13: predeclared synthetic 3D social-network rewiring and niche forecast.

All agents and data are simulated. Reuses frozen v12 motion/choice primitives
without changing original observed bat/pigeon failures or v12 receipts.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validation_v12"))
import emergent_preferences as v12  # noqa: E402

N = v12.N
OLD = np.repeat(np.arange(2), v12.N_PER_SPECIES)
NEW = np.array([0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1], dtype=int)
SEED_START = 20270101
N_SEEDS = 30
BOOT = 5000
PSEUDO = .5
POST_TRAIN = slice(4, 6)
POST_TEST = slice(6, 8)
BEFORE_TRAIN = slice(0, 4)
IMMEDIATE_TEST = slice(4, 6)
GRADIENT = np.array([.25, .25, 1., 1.])

@dataclass(frozen=True)
class Condition:
    name: str
    network: str = "stable"  # stable, rewired, or mixed starting on day 5
    gradient: bool = False
    learning: bool = True
    reset_on_day5: bool = False
    motor_boids: bool = False

CONDITIONS = (
    Condition("stable_uniform"),
    Condition("rewired_uniform", network="rewired"),
    Condition("mixed_uniform", network="mixed"),
    Condition("rewired_no_learning", network="rewired", learning=False),
    Condition("rewired_reset", network="rewired", reset_on_day5=True),
    Condition("stable_gradient", gradient=True),
    Condition("rewired_gradient", network="rewired", gradient=True),
    Condition("rewired_boids", network="rewired", motor_boids=True),
)

def check_partition(labels: np.ndarray) -> None:
    if labels.shape != (N,) or set(labels.tolist()) != {0, 1}:
        raise ValueError("Membership must be two fixed groups")
    if not np.array_equal(np.bincount(labels), [6, 6]):
        raise ValueError("Groups must be balanced, six agents each")

def social_fractions(chosen: np.ndarray, labels: np.ndarray | None) -> np.ndarray:
    """Prior-step choices of connected OTHER agents; never self/target choice."""
    if chosen.shape != (N,) or np.any((chosen < 0) | (chosen >= 4)):
        raise ValueError("Invalid prior-choice vector")
    if labels is not None:
        check_partition(labels)
    fractions = np.empty((N, 4), dtype=float)
    for i in range(N):
        linked = (np.arange(N) != i)
        if labels is not None:
            linked &= (labels == labels[i])
        fractions[i] = np.bincount(chosen[linked], minlength=4) / linked.sum()
    return fractions

def active_network(condition: Condition, day: int) -> np.ndarray | None:
    if day < 4 or condition.network == "stable":
        return OLD
    if condition.network == "rewired":
        return NEW
    if condition.network == "mixed":
        return None
    raise ValueError("Unknown network scenario")

def simulate(condition: Condition, seed: int) -> dict:
    """Same v12 eight-day algorithm; intervention is fixed at day-five boundary."""
    if condition.network not in ("stable", "rewired", "mixed"):
        raise ValueError("Invalid condition network")
    rng = np.random.default_rng(seed)
    q = np.zeros((N, 4), dtype=float)
    shape = (v12.N_DAYS, v12.N_BLOCKS - v12.BURN_BLOCKS, N)
    choices = np.empty(shape, dtype=int)
    xyz = np.empty(shape + (3,), dtype=float)
    daily_q = []
    for day in range(v12.N_DAYS):
        if day == 4 and condition.reset_on_day5:
            q.fill(0.)
        network = active_network(condition, day)
        reward_map = GRADIENT if (day >= 4 and condition.gradient) else np.ones(4)
        x = rng.normal(0., .4, size=(N, 3))
        v = np.zeros((N, 3), dtype=float)
        chosen = rng.integers(0, 4, size=N)
        for block in range(v12.N_BLOCKS):
            distance = np.linalg.norm(x[:, None, :] - v12.PATCHES[None, :, :], axis=-1)
            utility = 3.6 * q + .50 * reward_map[None, :] - .006 * distance
            utility += 2.0 * social_fractions(chosen, network)
            next_choice = v12.sample_categorical(rng, utility)
            reward = reward_map[next_choice]
            if condition.learning:
                q *= .94
                idx = np.arange(N)
                q[idx, next_choice] = .45 * reward + .55 * q[idx, next_choice]
            chosen = next_choice
            x, v = v12.move(x, v, chosen, rng, alpha=1., social_on=condition.motor_boids)
            if block >= v12.BURN_BLOCKS:
                j = block - v12.BURN_BLOCKS
                choices[day, j] = chosen
                xyz[day, j] = x
        daily_q.append(q.copy())
    if not np.isfinite(xyz).all():
        raise AssertionError("Non-finite movement")
    return {"choices": choices, "xyz": xyz, "daily_q": np.asarray(daily_q)}

def _choice_counts(choices: np.ndarray, days: slice) -> np.ndarray:
    if choices.shape != (8, 21, N):
        raise ValueError("Unexpected choice array")
    part = choices[days]
    return np.stack(
        [np.bincount(part[:, :, i].ravel(), minlength=4) for i in range(N)]
    ).astype(float)

def patch_scores(choices: np.ndarray, labels: np.ndarray,
                 train_days: slice = POST_TRAIN, test_days: slice = POST_TEST) -> dict:
    """Same training/test events for all models; balanced individual prior mass."""
    check_partition(labels)
    train = _choice_counts(choices, train_days)
    test = _choice_counts(choices, test_days)
    pool = train.sum(axis=0)
    p_population = (pool + N * PSEUDO) / (pool.sum() + 4 * N * PSEUDO)
    group_log, group_vs_pool, self_vs_group = [], [], []
    for i in range(N):
        members = np.flatnonzero(labels == labels[i])
        count = train[members].sum(axis=0)
        p_group = (count + len(members) * PSEUDO) / (
            count.sum() + 4 * len(members) * PSEUDO
        )
        personal = train[i]
        p_self = (personal + PSEUDO) / (personal.sum() + 4 * PSEUDO)
        n = test[i].sum()
        if n <= 0:
            raise ValueError("No test decisions for one agent")
        group_log.append(float(test[i] @ np.log(p_group) / n))
        group_vs_pool.append(float(test[i] @ np.log(p_group / p_population) / n))
        self_vs_group.append(float(test[i] @ np.log(p_self / p_group) / n))
    return {
        "group_logscore": float(np.mean(group_log)),
        "group_vs_population": float(np.mean(group_vs_pool)),
        "individual_vs_group": float(np.mean(self_vs_group))
    }

def height_scores(xyz: np.ndarray, labels: np.ndarray,
                  train_days: slice = POST_TRAIN, test_days: slice = POST_TEST) -> dict:
    """P(z|x,y,group) versus pooled model; score ALL held-out 3D positions."""
    check_partition(labels)
    categorical = v12.categorical_xyz(xyz, v12.PRIMARY_GRAIN)
    nx, ny, nz = [len(v12.PRIMARY_GRAIN[a]) + 1 for a in ("x", "y", "z")]
    def make_counts(days: slice) -> np.ndarray:
        return np.stack([
            np.bincount(categorical[days, :, i].ravel(), minlength=nx*ny*nz)
              .reshape(nx*ny, nz)
            for i in range(N)
        ]).astype(float)
    train, test = make_counts(train_days), make_counts(test_days)
    common = train.sum(axis=0)
    p_population = (common + N*PSEUDO) / (
        common.sum(axis=1, keepdims=True) + nz*N*PSEUDO
    )
    g_log, g_gain = [], []
    for i in range(N):
        members = np.flatnonzero(labels == labels[i])
        part = train[members].sum(axis=0)
        p_group = (part + len(members)*PSEUDO) / (
            part.sum(axis=1, keepdims=True) + nz*len(members)*PSEUDO
        )
        total = test[i].sum()
        g_log.append(float((test[i] * np.log(p_group)).sum() / total))
        g_gain.append(float((test[i] * np.log(p_group / p_population)).sum() / total))
    return {"group_logscore": float(np.mean(g_log)),
            "group_vs_population": float(np.mean(g_gain))}

def evaluate(condition: Condition, seed: int) -> dict:
    data = simulate(condition, seed)
    active = NEW if condition.network == "rewired" else OLD
    counterfactual = OLD if condition.network == "rewired" else NEW
    a = patch_scores(data["choices"], active)
    b = patch_scores(data["choices"], counterfactual)
    za = height_scores(data["xyz"], active)
    zb = height_scores(data["xyz"], counterfactual)
    early = patch_scores(data["choices"], OLD, BEFORE_TRAIN, IMMEDIATE_TEST)
    return {
        "seed": seed,
        "network": condition.network,
        "patch_topology_advantage": a["group_logscore"]-b["group_logscore"],
        "post_group_vs_population": a["group_vs_population"],
        "post_individual_vs_group": a["individual_vs_group"],
        "height_topology_advantage": za["group_logscore"]-zb["group_logscore"],
        "post_height_group_vs_population": za["group_vs_population"],
        "early_old_group_vs_population": early["group_vs_population"],
        "mean_q_concentration": float(np.mean(data["daily_q"][-1].max(axis=1) -
                                                data["daily_q"][-1].mean(axis=1))),
    }

METRICS = (
    "patch_topology_advantage",
    "post_group_vs_population",
    "post_individual_vs_group",
    "height_topology_advantage",
    "post_height_group_vs_population",
    "early_old_group_vs_population",
    "mean_q_concentration",
)

def bootstrap_summary(values: np.ndarray, indices: np.ndarray) -> dict:
    means = values[indices].mean(axis=1)
    lo, hi = np.quantile(means, (.025, .975))
    return {
        "mean": float(values.mean()),
        "bootstrap_95": [float(lo), float(hi)],
        "positive_worlds": int((values > 0).sum()),
        "n_worlds": len(values),
    }

def experiment(seeds: int = N_SEEDS) -> dict:
    if not (3 <= seeds <= 1000):
        raise ValueError("Require 3..1000 worlds")
    if not np.array_equal(OLD[:6], np.zeros(6, int)):
        raise AssertionError("Original partition changed")
    check_partition(OLD)
    check_partition(NEW)
    if int(((OLD == 0) & (NEW == 0)).sum()) != 3:
        raise AssertionError("Orthogonal rewiring contract changed")
    seed_list = list(range(SEED_START, SEED_START+seeds))
    rows = {c.name: [evaluate(c, seed) for seed in seed_list] for c in CONDITIONS}
    rng = np.random.default_rng(131313)
    boot_indices = rng.integers(0, seeds, size=(BOOT, seeds))
    stats = {name: {
        metric: bootstrap_summary(
            np.asarray([row[metric] for row in values], dtype=float), boot_indices
        ) for metric in METRICS
    } for name, values in rows.items()}
    def diff(condition1: str, condition2: str, metric: str) -> dict:
        v1 = np.asarray([r[metric] for r in rows[condition1]], dtype=float)
        v2 = np.asarray([r[metric] for r in rows[condition2]], dtype=float)
        return bootstrap_summary(v1 - v2, boot_indices)

    contrasts = {
        "rewired_minus_no_learning_patch_topology":
          diff("rewired_uniform", "rewired_no_learning", "patch_topology_advantage"),
        "rewired_minus_mixed_group_gain":
          diff("rewired_uniform", "mixed_uniform", "post_group_vs_population"),
        "rewired_gradient_minus_uniform_topology":
          diff("rewired_gradient", "rewired_uniform", "patch_topology_advantage"),
        "rewired_boids_minus_motor_off_topology":
          diff("rewired_boids", "rewired_uniform", "patch_topology_advantage"),
        "rewired_reset_minus_persist_topology":
          diff("rewired_reset", "rewired_uniform", "patch_topology_advantage"),
    }
    gate = (
        stats["rewired_uniform"]["patch_topology_advantage"]["bootstrap_95"][0] > 0
        and contrasts["rewired_minus_no_learning_patch_topology"]["bootstrap_95"][0] > 0
        and stats["stable_uniform"]["patch_topology_advantage"]["bootstrap_95"][0] > 0
    )
    return {
        "study": "boids-v13-predeclared-social-network-rewiring-synthetic-transfer",
        "status": "SYNTHETIC_ONLY_NOT_WILD_NICHE_EVIDENCE",
        "protocol": "docs/NETWORK_REWIRING_FORECAST_PROTOCOL_V13.md",
        "seed_start": SEED_START,
        "seeds": seed_list,
        "conditions": [asdict(c) for c in CONDITIONS],
        "design": {
            "days": 8, "decisions_per_day": 24, "burn_blocks": 3,
            "day5_network_intervention": True, "post_train_days": [5,6],
            "post_test_days": [7,8], "prior_per_training_agent_per_class": PSEUDO,
            "old_labels": OLD.tolist(), "rewired_labels": NEW.tolist(),
            "primary_social_imitation": 2.0, "alpha": 1.0,
            "primary_motor_boids": False,
            "post_gradient_rewards": GRADIENT.tolist(),
            "seed_bootstrap_samples": BOOT, "fixed_grain": v12.PRIMARY_GRAIN,
        },
        "registered_gate": {
            "membership_transfer_supported_in_simulator": bool(gate),
            "note": "A positive gate is a specified simulator result, not a wild-species rule."
        },
        "summary": stats,
        "paired_contrasts": contrasts,
        "per_seed": rows,
        "limitations": [
            "All choices, rewards, networks and positions are simulated; no real animals.",
            "Network labels are fixed ex ante and not inferred from spatial occupancy.",
            "Reward gradient is a stipulated uniform-to-asymmetric toy perturbation.",
            "Day-level RNG worlds, not decisions or individual fixes, are independent.",
            "The first four historical days are not a preregistered empirical dataset.",
            "Boids motor-on sensitivity retains original dyad partners despite rewiring choice contacts.",
            "Original v6 bat and v8 pigeon negative primary tests remain unchanged."
        ],
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=N_SEEDS)
    parser.add_argument("--out", type=Path,
                        default=Path("validation_v13/results/network_transfer_v13.json"))
    args = parser.parse_args()
    result = experiment(args.seeds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2,
                                    allow_nan=False) + "\n", encoding="utf-8")
    print("EXPLORATORY_SYNTHETIC_V13")
    print("Registered primary gate:",
          result["registered_gate"]["membership_transfer_supported_in_simulator"])
    for c in CONDITIONS:
        name = c.name
        patch = result["summary"][name]["patch_topology_advantage"]
        height = result["summary"][name]["height_topology_advantage"]
        print(name, "patch_topology_advantage", json.dumps(patch, sort_keys=True),
              "height_topology_advantage", json.dumps(height, sort_keys=True))
    print("paired contrasts:", json.dumps(result["paired_contrasts"], sort_keys=True))
    print("full_receipt:", args.out)

if __name__ == "__main__":
    main()
