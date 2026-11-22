"""Render static v15 figures only after admitting the complete saved output."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import tempfile

import numpy as np
import scipy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D


REPOSITORY = Path(__file__).resolve().parents[1]
if str(REPOSITORY) not in sys.path:
    sys.path.insert(0, str(REPOSITORY))

SEEDS = np.arange(2000, 2096, dtype=np.int64)
PROTOCOL_COMMIT = "3fcbdfc157ca362cad4560bf3b2400ec4ee7e7e0"
ARMS = tuple(f"intact__{mask:03b}" for mask in range(8)) + (
    "motor_cut__000", "motor_cut__011", "motor_cut__100", "motor_cut__111",
)
BOOTSTRAP = {
    "replicates": 10000,
    "seed": 2026112205,
    "unit": "paired simulator seed",
    "interval": "percentile95%, descriptive and unadjusted",
}
PINNED_RUNTIME = {"numpy": "2.3.5", "scipy": "1.17.0", "matplotlib": "3.10.8"}
STATISTICAL_KEYS = ("cohorts", "windows", "arrivals")
PRIMARY_DENOMINATOR = 32 * 3000
BLUE, LOW, GRAY, INK = "#28679c", "#b16b2f", "#85929d", "#243641"
MOBIUS_TERMS = ("X", "V", "C", "XV", "XC", "VC", "XVC")
MOTOR_CONTRASTS = (
    ("X_insertion_intact", "Insert X · intact"),
    ("X_insertion_motor_cut", "Insert X · motor cut"),
    ("X_deletion_intact", "Delete X · intact"),
    ("X_deletion_motor_cut", "Delete X · motor cut"),
    ("motor_DID_total", "Cut − intact · total"),
    ("motor_DID_X_insertion", "Cut − intact · insert X"),
    ("motor_DID_X_deletion", "Cut − intact · delete X"),
)


def assert_same_statistics(saved, computed, path):
    """Reject missing keys, nonfinite numbers, and changed values at any depth.

    The analysis is deterministic under the pinned numerical runtime; saved JSON
    floats are compared exactly after the JSON round trip, without a tolerance
    that could conceal a changed small signed effect.
    """
    if isinstance(computed, np.generic):
        computed = computed.item()
    if isinstance(computed, dict):
        if not isinstance(saved, dict) or set(saved) != set(computed):
            raise ValueError(f"Saved statistics disagree with raw arrays at {path}: keys differ")
        for key, value in computed.items():
            assert_same_statistics(saved[key], value, f"{path}.{key}")
        return
    if isinstance(computed, (list, tuple)):
        if not isinstance(saved, (list, tuple)) or len(saved) != len(computed):
            raise ValueError(f"Saved statistics disagree with raw arrays at {path}: sequence differs")
        for index, value in enumerate(computed):
            assert_same_statistics(saved[index], value, f"{path}[{index}]")
        return
    if isinstance(computed, bool) or computed is None or isinstance(computed, str):
        matches = type(saved) is type(computed) and saved == computed
    elif isinstance(computed, (int, float)):
        matches = (
            isinstance(saved, (int, float)) and not isinstance(saved, bool)
            and math.isfinite(saved) and math.isfinite(computed) and saved == computed
        )
    else:
        raise ValueError(f"Unsupported statistical value at {path}")
    if not matches:
        raise ValueError(f"Saved statistics disagree with raw arrays at {path}")


def _read_json(path):
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path.name}")
    return value


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inputs(directory):
    """Admit complete saved arrays and recompute every published statistic.

    The runner import is deliberately delayed until receipts and manifests pass.
    This function has no writes, and never calls a simulation entry point.
    """
    directory = Path(directory)
    result = _read_json(directory / "audit_result.json")
    summary = _read_json(directory / "summary.json")
    expected = {
        "status": "SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "protocol_commit": PROTOCOL_COMMIT,
        "seeds": SEEDS.tolist(),
        "n": 32,
        "steps": 6000,
        "split_step": 1040,
        "trajectories": 1152,
        "primary_window": [1040, 4040],
        "bootstrap": BOOTSTRAP,
    }
    for document in (result, summary):
        if any(document.get(key) != value for key, value in expected.items()):
            raise ValueError("Result metadata differs from the fixed v15 experiment")
    receipt = _read_json(directory / "trace_receipt.json")
    if result.get("trace_receipt") != receipt or summary.get("trace_receipt") != receipt:
        raise ValueError("Trace receipts disagree across the saved result files")
    if (
        set(receipt) != {"file", "bytes", "sha256"}
        or receipt["file"] != "full_traces.npz"
        or type(receipt["bytes"]) is not int or receipt["bytes"] <= 0
        or not isinstance(receipt["sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"]) is None
    ):
        raise ValueError("Invalid trace receipt metadata")
    trace = directory / receipt["file"]
    if trace.stat().st_size != receipt["bytes"]:
        raise ValueError("Trace archive byte count does not match the result receipt")
    if _sha256(trace) != receipt["sha256"]:
        raise ValueError("Trace archive checksum does not match the result receipt")
    with np.load(trace, allow_pickle=False) as archive:
        if "seeds" not in archive or not np.array_equal(archive["seeds"], SEEDS):
            raise ValueError("Trace seed order differs from the fixed v15 experiment")
        arrays = {key: archive[key] for key in archive.files}

    # All metadata must agree, including provenance and the raw receipt, before
    # expensive validation/analysis; the three statistical sections are checked
    # again below against fresh values rather than trusting their agreement.
    assert_same_statistics(summary, result, "summary_vs_audit")
    runtime = result.get("runtime", {})
    if any(runtime.get(key) != PINNED_RUNTIME[key] for key in ("numpy", "scipy")):
        raise ValueError("Saved numerical runtime differs from the pinned v14/v15 versions")
    if not isinstance(runtime.get("python"), str):
        raise ValueError("Saved runtime has no Python version")
    _check_runtime()

    from validation_fish_boids_v15.run_audit import (
        BASE_COMMIT, analyze_arrays, capture_source_hashes, validate_arrays,
    )

    if (result.get("predecessor_commit") != BASE_COMMIT
            or type(result.get("source_histories")) is not int or result["source_histories"] != 192
            or result.get("source_hashes_captured_before_execution_and_verified_after") is not True):
        raise ValueError("Saved execution history differs from the fixed v15 audit")
    sources = capture_source_hashes()
    if result.get("source_sha256") != sources:
        raise ValueError("Computational source provenance disagrees with the saved result")
    expected_validations = {
        "exact_schema": True, "integer_call_counts": True, "snapshot_consistency": True,
        "component_provenance": True, "pre_pulse_pairing": True, "first_call_V_invariance": True,
        "common_rng_at_split_and_end": True, "exact_v14_natural_seed_pairs": 96,
    }
    try:
        assert_same_statistics(result.get("validations"), expected_validations, "validations")
        if type(result["validations"]["exact_v14_natural_seed_pairs"]) is not int:
            raise ValueError("Natural seed-pair replay count must be an integer")
    except ValueError as exc:
        raise ValueError("Saved replay/validation evidence differs from the fixed v15 audit") from exc

    validate_arrays(arrays)
    stats, _window_rows, _effect_rows, arrival_rows = analyze_arrays(arrays)
    for key in STATISTICAL_KEYS:
        if key not in result or key not in summary or key not in stats:
            raise ValueError(f"Missing saved statistical section: {key}")
        assert_same_statistics(result[key], stats[key], f"audit_result.{key}")
        assert_same_statistics(summary[key], stats[key], f"summary.{key}")
    if capture_source_hashes() != sources:
        raise ValueError("Computational sources changed while admitting plotted results")
    return arrays, stats, arrival_rows


def factorial_values(counts, denominator):
    """Difference integer calling totals before scaling displayed allocations."""
    from validation_fish_boids_v15.analysis import decompose_counts

    return decompose_counts(counts, denominator)


def _check_runtime():
    actual = {"numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__}
    if actual != PINNED_RUNTIME:
        raise ValueError(f"Use the pinned v14/v15 plotting runtime: {PINNED_RUNTIME}")


def _style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.3,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "bold", "axes.labelcolor": INK,
        "text.color": INK, "xtick.color": "#43515d", "ytick.color": "#43515d",
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.formatter.useoffset": False,
    })


def _primary_counts(arrays):
    # Continuations start at global1040: [1040,4040) is local[0,3000).
    # The archive validator has already admitted the exact 1/32 calling grid.
    return {arm: np.rint(arrays[f"{arm}__call_fraction"][:, :3000] * 32).astype(np.int64).sum(axis=1)
            for arm in ARMS}


def _indices(stats, cohort):
    return np.asarray(stats["cohorts"][cohort]["indices"], dtype=int)


def _endpoint_stats(stats, cohort):
    return stats["windows"]["primary"]["cohorts"][cohort]["call_fraction"]


def _cohort_label(stats, cohort):
    n = stats["cohorts"][cohort]["n"]
    if cohort == "all":
        return f"All {n} seeds"
    suffix = "; no estimate" if n == 0 else "; no interval" if n == 1 else "; descriptive"
    return f"Baseline-low subset (n={n}{suffix})"


def _estimate_text(row, digits=4):
    if row["n"] == 0:
        return "no estimate (n=0)"
    mean = f"{row['mean']:.{digits}g}"
    interval = row["ci95"]
    if interval is None:
        return f"{mean}; no interval (n=1)"
    return f"{mean} [{interval[0]:.{digits}g}, {interval[1]:.{digits}g}]"


def _summary_extent(row):
    values = [] if row["mean"] is None else [row["mean"]]
    return values + ([] if row["ci95"] is None else list(row["ci95"]))


def _limits(values, *, include_zero=True):
    finite = np.asarray(values, dtype=float).reshape(-1)
    finite = finite[np.isfinite(finite)]
    if include_zero:
        finite = np.append(finite, 0.0)
    if not finite.size:
        return (-0.01, 0.01)
    lo, hi = float(finite.min()), float(finite.max())
    pad = (hi - lo) * 0.10
    if pad == 0:
        pad = max(abs(lo) * 0.04, 0.01)
    return lo - pad, hi + pad


def _empty_panel(ax):
    ax.text(0.5, 0.5, "No baseline-low seeds\nNo estimate or interval", transform=ax.transAxes,
            ha="center", va="center", color="#687784", fontsize=11,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 6})


def _draw_estimate(ax, row, y, color):
    """Draw interval endpoints directly, even when the mean is outside them."""
    if row["mean"] is None:
        return
    if row["ci95"] is not None:
        lo, hi = row["ci95"]
        ax.hlines(y, lo, hi, color=color, linewidth=2.2, zorder=4)
        ax.vlines((lo, hi), y - 0.075, y + 0.075, color=color, linewidth=1.2, zorder=4)
    ax.plot(row["mean"], y, marker="D", color=color, markeredgecolor="white",
            markeredgewidth=0.6, markersize=6.8, zorder=5, linestyle="none")


def _effect_panel(ax, keys, labels, summaries, vectors, selected, color, limits):
    n = len(selected)
    jitter = np.linspace(-0.17, 0.17, n) if n > 1 else np.zeros(n)
    for y, key in enumerate(keys):
        if n:
            ax.scatter(vectors[key][selected], y + jitter, s=13 if n > 10 else 27,
                       color=GRAY, alpha=0.45 if n > 10 else 0.7, edgecolors="none", zorder=2)
        _draw_estimate(ax, summaries[key], y, color)
    ax.axvline(0, color="#a3adb5", linewidth=0.9, zorder=0)
    ax.set(yticks=range(len(keys)), yticklabels=labels, ylim=(len(keys) - 0.45, -0.55), xlim=limits)
    ax.grid(axis="x", alpha=0.16)
    ax.ticklabel_format(axis="x", style="sci", scilimits=(-3, 3), useMathText=True)
    if not n:
        _empty_panel(ax)


def _primary_figure(values, counts, stats):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.7), gridspec_kw={"width_ratios": [1.15, 1]})
    difference = (counts["intact__111"] - counts["intact__000"]) / PRIMARY_DENOMINATOR
    low_indices = set(_indices(stats, "baseline_low").tolist())
    extent = list(difference)
    for cohort in ("all", "baseline_low"):
        extent.extend(_summary_extent(_endpoint_stats(stats, cohort)["contrasts"]["natural_history"]))
    limits = _limits(extent)
    for row, cohort in enumerate(("all", "baseline_low")):
        selected = _indices(stats, cohort)
        n = len(selected)
        color = BLUE if cohort == "all" else LOW
        result = _endpoint_stats(stats, cohort)
        summary = result["contrasts"]["natural_history"]
        left, right = axes[row]
        if n:
            left.scatter(SEEDS[selected], difference[selected], s=29,
                         c=[LOW if i in low_indices else BLUE for i in selected],
                         linewidths=0.45, edgecolors="white", zorder=3)
        if summary["ci95"] is not None:
            left.axhspan(*summary["ci95"], color=color, alpha=0.12, zorder=0)
        if summary["mean"] is not None:
            left.axhline(summary["mean"], color=color, linewidth=1.5, linestyle="--", zorder=2)
        left.axhline(0, color="#9eabb3", linewidth=0.9, zorder=1)
        left.set(xlim=(1997, 2098), ylim=limits, xlabel="Simulator seed",
                 ylabel="111 − 000 (call-fraction units)", xticks=(2000, 2020, 2040, 2060, 2080, 2095))
        left.grid(axis="y", alpha=0.15)
        left.tick_params(axis="x", labelsize=9)
        left.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3), useMathText=True)
        prefix = "A  Primary contrast" if row == 0 else "C  Secondary contrast"
        left.set_title(f"{prefix} | {_cohort_label(stats, cohort)}", loc="left", fontsize=11.5, pad=15)
        left.text(0.02, 0.97, f"Mean [95% interval]: {_estimate_text(summary)}", transform=left.transAxes,
                  ha="left", va="top", fontsize=9.1, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85})
        if n == 0:
            _empty_panel(left)
        if row == 0:
            left.legend(handles=[
                Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, markeredgecolor="white", label="Other retained seeds"),
                Line2D([0], [0], marker="o", color="none", markerfacecolor=LOW, markeredgecolor="white", label="Baseline-low seeds"),
            ], loc="lower right", fontsize=8.6, frameon=True, edgecolor="none", framealpha=0.85)

        corner_extent = []
        for index, arm in enumerate(ARMS[:8]):
            _draw_estimate(right, result["arms"][arm], index, color)
            corner_extent.extend(_summary_extent(result["arms"][arm]))
        right.set(yticks=range(8), yticklabels=[f"{mask:03b}" for mask in range(8)], ylim=(7.55, -0.55),
                  xlabel="Mean call fraction over [1040, 4040)", ylabel="Intact corner (X V C)",
                  xlim=_limits(corner_extent, include_zero=False))
        right.grid(axis="x", alpha=0.15)
        right.ticklabel_format(axis="x", style="plain", useOffset=False)
        right.set_title(f"{'B' if row == 0 else 'D'}  Eight intact corners | {'all seeds' if row == 0 else 'secondary subset'}",
                        loc="left", fontsize=11.5, pad=15)
        if n == 0:
            _empty_panel(right)
    fig.suptitle("Acoustic Boids v15 | primary-window state transplants", x=0.055, ha="left", fontsize=17, y=0.98)
    fig.text(0.055, 0.925, "All 96 independent seeds retained.  X: positions; V: velocities; C: previous binary calling.  "
             "Bit 1 selects the playback source.", fontsize=10, color="#596974")
    fig.text(0.055, 0.025,
             "SYNTHETIC_ONLY_NOT_FIELD_RESULT. Model steps are uncalibrated; these state swaps do not establish biological memory.\n"
             "Bands/whiskers: 95% percentile intervals of the paired-seed mean (10,000 whole-seed replicates), descriptive and unadjusted.\n"
             "Baseline-low: shared pre-pulse mean over [800, 1000) < 0.90; fixed secondary subset. Hybrid panels use continuation data only.",
             fontsize=9.2, color="#596974", linespacing=1.45)
    fig.subplots_adjust(left=0.075, right=0.975, top=0.86, bottom=0.16, hspace=0.50, wspace=0.30)
    return fig


def _component_figure(counts, stats):
    corners = np.column_stack([counts[arm] for arm in ARMS[:8]])
    terms = factorial_values(corners, PRIMARY_DENOMINATOR)
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.5), gridspec_kw={"height_ratios": [0.80, 1.25]})
    for row, kind, keys in ((0, "shapley", ("X", "V", "C")), (1, "mobius", MOBIUS_TERMS)):
        extent = np.concatenate([terms[kind][key] for key in keys]).tolist()
        for cohort in ("all", "baseline_low"):
            summary = _endpoint_stats(stats, cohort)["decomposition"][kind]
            for key in keys:
                extent.extend(_summary_extent(summary[key]))
        limits = _limits(extent)
        for col, cohort in enumerate(("all", "baseline_low")):
            ax = axes[row, col]
            color = BLUE if cohort == "all" else LOW
            decomposition = _endpoint_stats(stats, cohort)["decomposition"]
            _effect_panel(ax, keys, keys, decomposition[kind], terms[kind], _indices(stats, cohort), color, limits)
            label = "Shapley allocations" if kind == "shapley" else "Möbius terms"
            ax.set_title(f"{'ABCD'[row * 2 + col]}  {label} | {'all 96 seeds' if cohort == 'all' else 'baseline-low subset'}",
                         loc="left", fontsize=11.6, pad=13)
            ax.set_xlabel("Signed contribution (call-fraction units)")
            if row == 0:
                ax.text(0, 1.025, _cohort_label(stats, cohort), transform=ax.transAxes, fontsize=9, color="#687784")
                ax.text(0.01, 0.025, "Paired φX − φC: " + _estimate_text(decomposition["shapley_X_minus_C"]),
                        transform=ax.transAxes, fontsize=8.9, color="#4d5b67", ha="left", va="bottom",
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.87})
    fig.suptitle("Acoustic Boids v15 | component allocations and interactions", x=0.055, ha="left", fontsize=17, y=0.98)
    fig.text(0.055, 0.923, "Intact factorial, endpoint [1040, 4040). Both rows sum within each seed to 111 − 000. "
             "Gray dots retain every seed; diamonds show means.", fontsize=10, color="#596974")
    fig.text(0.055, 0.025,
             "SYNTHETIC_ONLY_NOT_FIELD_RESULT. Signed units are retained; Shapley allocates interactions by convention, not by a unique physical mechanism.\n"
             "Whiskers: 95% percentile intervals of the paired-seed mean (10,000 whole-seed replicates), descriptive and unadjusted; none for n < 2.\n"
             "Baseline-low is a fixed secondary subset. The four motor-cut anchors do not identify a motor-cut Shapley decomposition. Model time is uncalibrated.",
             fontsize=9.1, color="#596974", linespacing=1.45)
    fig.subplots_adjust(left=0.075, right=0.975, top=0.85, bottom=0.16, hspace=0.55, wspace=0.18)
    return fig


def _motor_vectors(values):
    intact_total = values["intact__111"] - values["intact__000"]
    cut_total = values["motor_cut__111"] - values["motor_cut__000"]
    intact_insert = values["intact__100"] - values["intact__000"]
    cut_insert = values["motor_cut__100"] - values["motor_cut__000"]
    intact_delete = values["intact__111"] - values["intact__011"]
    cut_delete = values["motor_cut__111"] - values["motor_cut__011"]
    return {"X_insertion_intact": intact_insert, "X_insertion_motor_cut": cut_insert,
            "X_deletion_intact": intact_delete, "X_deletion_motor_cut": cut_delete,
            "motor_DID_total": cut_total - intact_total,
            "motor_DID_X_insertion": cut_insert - intact_insert,
            "motor_DID_X_deletion": cut_delete - intact_delete}


def _arrival_panel(ax, stats, arrival_rows):
    selected_seeds = stats["cohorts"]["baseline_low"]["seeds"]
    selected_set = set(selected_seeds)
    rows = {(int(row["seed"]), row["arm"]): row for row in arrival_rows
            if int(row["seed"]) in selected_set and float(row["threshold"]) == 0.9
            and row["arm"] in ("intact__000", "intact__111")}
    for index, seed in enumerate(selected_seeds):
        natural = [rows[(seed, arm)] for arm in ("intact__000", "intact__111")]
        ax.plot([record["restricted_latency"] for record in natural], [index - 0.12, index + 0.12],
                color="#c3ccd2", linewidth=0.9, zorder=1)
        for record, dy, color in zip(natural, (-0.12, 0.12), (BLUE, LOW)):
            observed = bool(record["event_observed"])
            ax.scatter(record["restricted_latency"], index + dy, marker="o" if observed else ">",
                       s=40 if len(selected_seeds) < 30 else 23, facecolors=color if observed else "white",
                       edgecolors=color, linewidths=1.1, zorder=3)
    ax.axvline(4960, color="#a3adb5", linewidth=0.9, linestyle="--", zorder=0)
    ax.set(xlim=(0, 5230), xlabel="Restricted latency after split (model steps)", ylabel="Simulator seed",
           xticks=(200, 1240, 2480, 3720, 4960))
    if selected_seeds:
        stride = max(1, math.ceil(len(selected_seeds) / 24))
        tick_positions = list(range(0, len(selected_seeds), stride))
        if len(selected_seeds) - 1 not in tick_positions:
            tick_positions.append(len(selected_seeds) - 1)
        ax.set(yticks=tick_positions, yticklabels=[selected_seeds[i] for i in tick_positions],
               ylim=(len(selected_seeds) - 0.45, -0.65))
    else:
        ax.set(yticks=[], ylim=(0.6, -0.6))
        _empty_panel(ax)
    ax.grid(axis="x", alpha=0.16)
    ax.set_title(f"A  Natural arrivals, threshold 0.90\nBaseline-low subset (n={len(selected_seeds)}; secondary)",
                 loc="left", fontsize=11.5, pad=15, linespacing=1.5)
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, markeredgecolor=BLUE, label="000: no-playback source"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=LOW, markeredgecolor=LOW, label="111: playback source"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=GRAY, markeredgecolor=GRAY, label="Filled circle: observed event"),
        Line2D([0], [0], marker=">", color="none", markerfacecolor="white", markeredgecolor=GRAY, label="Open triangle: censored"),
    ], loc="upper left", bbox_to_anchor=(0, -0.08), frameon=False, fontsize=9, borderaxespad=0)


def _arrival_motor_figure(counts, stats, arrival_rows):
    fig = plt.figure(figsize=(14.6, 10.3))
    grid = fig.add_gridspec(2, 2, width_ratios=(1, 1.2), height_ratios=(1, 1))
    arrivals_ax = fig.add_subplot(grid[:, 0])
    _arrival_panel(arrivals_ax, stats, arrival_rows)
    vectors = {key: vector / PRIMARY_DENOMINATOR for key, vector in _motor_vectors(counts).items()}
    keys, labels = zip(*MOTOR_CONTRASTS)
    extent = np.concatenate([vectors[key] for key in keys]).tolist()
    for cohort in ("all", "baseline_low"):
        for key in keys:
            extent.extend(_summary_extent(_endpoint_stats(stats, cohort)["contrasts"][key]))
    limits = _limits(extent)
    for row, cohort in enumerate(("all", "baseline_low")):
        ax = fig.add_subplot(grid[row, 1])
        _effect_panel(ax, keys, labels, _endpoint_stats(stats, cohort)["contrasts"], vectors,
                      _indices(stats, cohort), BLUE if cohort == "all" else LOW, limits)
        ax.axhline(3.5, color="#dce3e8", linewidth=0.9)
        ax.set_title(f"{'B' if row == 0 else 'C'}  {_cohort_label(stats, cohort)}", loc="left", fontsize=11.5, pad=13)
        ax.set_xlabel("Primary-window contrast (call-fraction units)")
        ax.tick_params(axis="y", labelsize=9.2)
    all_latency = stats["arrivals"]["0.9"]["cohorts"]["all"]["natural_latency_contrast"]
    low_latency = stats["arrivals"]["0.9"]["cohorts"]["baseline_low"]["natural_latency_contrast"]
    fig.suptitle("Acoustic Boids v15 | arrival timing and motor-cut anchors", x=0.055, ha="left", fontsize=17, y=0.98)
    fig.text(0.055, 0.925,
             "Secondary diagnostics. Restricted-latency difference (111 − 000), model steps; mean [95% interval]:\n"
             f"All 96: {_estimate_text(all_latency, 5)}.   Baseline-low: {_estimate_text(low_latency, 5)}. "
             "Negative values indicate earlier confirmation for 111.", fontsize=9.7, color="#596974", linespacing=1.45)
    fig.text(0.055, 0.025,
             "SYNTHETIC_ONLY_NOT_FIELD_RESULT. Model time is uncalibrated. Arrival: first completed 200-update window at or above the threshold; 200-step floor.\n"
             "At latency 4960, a filled circle confirms at step 6000; an open triangle has no event by the fixed horizon. Confirmation is not absorbing.\n"
             "Insert X = 100 − 000; delete X = 111 − 011. Cut − intact is paired within seed. Motor cuts start at 1040 and retain only four anchors.\n"
             "Gray dots: every seed; diamonds: means. Whiskers: descriptive, unadjusted paired-seed 95% bootstrap intervals (10,000 replicates); none for n < 2.",
             fontsize=8.9, color="#596974", linespacing=1.45)
    fig.subplots_adjust(left=0.075, right=0.975, top=0.825, bottom=0.255, hspace=0.43, wspace=0.56)
    return fig


def build_figures(arrays, stats, arrival_rows):
    """Build figures from values already admitted by ``load_inputs``."""
    _check_runtime()
    _style()
    counts = _primary_counts(arrays)
    values = {arm: count / PRIMARY_DENOMINATOR for arm, count in counts.items()}
    return {
        "primary_state_transplants": _primary_figure(values, counts, stats),
        "component_interactions": _component_figure(counts, stats),
        "arrival_and_motor_controls": _arrival_motor_figure(counts, stats, arrival_rows),
    }


def render_figures(directory, arrays, stats, arrival_rows):
    """Render all six files to staging before replacing any existing figure."""
    directory = Path(directory)
    figures = {}
    try:
        figures = build_figures(arrays, stats, arrival_rows)
        with tempfile.TemporaryDirectory(prefix=".v15_figures_", dir=directory) as tmp:
            staging = Path(tmp)
            for name, fig in figures.items():
                for extension in ("png", "pdf"):
                    fig.savefig(staging / f"{name}.{extension}", dpi=190)
            output = directory / "figures"
            output.mkdir(exist_ok=True)
            for path in staging.iterdir():
                path.replace(output / path.name)
    finally:
        for fig in figures.values():
            plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path(__file__).resolve().parent / "results")
    args = parser.parse_args()
    arrays, stats, arrival_rows = load_inputs(args.results)
    render_figures(args.results, arrays, stats, arrival_rows)
    print("Rendered three v15 figures as PNG and PDF from fully validated saved values.")


if __name__ == "__main__":
    main()
