"""Saved-output admission must finish before a verified figure is replaced."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings

import numpy as np


SCRIPT = Path(__file__).with_name("plot_audit.py")
PROTOCOL_COMMIT = "3fcbdfc157ca362cad4560bf3b2400ec4ee7e7e0"
BASE_COMMIT = "7295d885b587d808cb74fbae11163819ed8cf22d"
SOURCE_FILES = (
    "docs/V15_STATE_TRANSPLANT_PROTOCOL.md",
    "validation_fish_boids_v14/simulation.py",
    "validation_fish_boids_v15/simulation.py",
    "validation_fish_boids_v15/analysis.py",
    "validation_fish_boids_v15/run_audit.py",
)


def fixture_metadata(root, *, seeds=None, wrong_hash=False):
    """Deliberately incomplete arrays: admission must stop before array analysis."""
    seeds = list(range(2000, 2096)) if seeds is None else seeds
    trace = root / "full_traces.npz"
    np.savez_compressed(trace, seeds=np.asarray(seeds, dtype=np.int64))
    receipt = {
        "file": "full_traces.npz",
        "bytes": trace.stat().st_size,
        "sha256": "0" * 64 if wrong_hash else hashlib.sha256(trace.read_bytes()).hexdigest(),
    }
    metadata = {
        "status": "SYNTHETIC_ONLY_NOT_FIELD_RESULT",
        "protocol_commit": PROTOCOL_COMMIT,
        "predecessor_commit": BASE_COMMIT,
        "seeds": seeds,
        "n": 32,
        "steps": 6000,
        "split_step": 1040,
        "trajectories": 1152,
        "source_histories": 192,
        "primary_window": [1040, 4040],
        "bootstrap": {
            "replicates": 10000,
            "seed": 2026112205,
            "unit": "paired simulator seed",
            "interval": "percentile95%, descriptive and unadjusted",
        },
        "runtime": {"python": "3.12.0", "numpy": "2.3.5", "scipy": "1.17.0"},
        "source_sha256": {name: hashlib.sha256((SCRIPT.resolve().parents[1] / name).read_bytes()).hexdigest()
                          for name in SOURCE_FILES},
        "source_hashes_captured_before_execution_and_verified_after": True,
        "validations": {"exact_schema": True, "integer_call_counts": True, "snapshot_consistency": True,
                        "component_provenance": True, "pre_pulse_pairing": True, "first_call_V_invariance": True,
                        "common_rng_at_split_and_end": True, "exact_v14_natural_seed_pairs": 96},
        "trace_receipt": receipt,
    }
    for name in ("audit_result.json", "summary.json"):
        (root / name).write_text(json.dumps(metadata), encoding="utf-8")
    (root / "trace_receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    return metadata


class PlotInputTests(unittest.TestCase):
    def assert_rejected_without_replacing(self, root, expected_message):
        directory = root / "figures"
        directory.mkdir()
        previous = directory / "primary_state_transplants.png"
        previous.write_bytes(b"previous verified figure")
        done = subprocess.run(
            [sys.executable, str(SCRIPT), "--results", str(root)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(done.returncode, 0)
        self.assertIn(expected_message, done.stderr)
        self.assertEqual(previous.read_bytes(), b"previous verified figure")
        self.assertEqual(sorted(path.name for path in directory.iterdir()), [previous.name])

    def test_bad_trace_receipt_preserves_existing_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture_metadata(root, wrong_hash=True)
            self.assert_rejected_without_replacing(root, "Trace archive checksum does not match")

    def test_wrong_seed_manifest_preserves_existing_figure_with_valid_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture_metadata(root, seeds=[1999] + list(range(2001, 2096)))
            self.assert_rejected_without_replacing(root, "Result metadata differs from the fixed v15 experiment")

    def test_wrong_receipt_byte_count_preserves_existing_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = fixture_metadata(root)
            metadata["trace_receipt"]["bytes"] += 1
            for name in ("audit_result.json", "summary.json"):
                (root / name).write_text(json.dumps(metadata), encoding="utf-8")
            (root / "trace_receipt.json").write_text(json.dumps(metadata["trace_receipt"]), encoding="utf-8")
            self.assert_rejected_without_replacing(root, "Trace archive byte count does not match")

    def test_raw_seed_order_cannot_disagree_with_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = fixture_metadata(root, seeds=list(reversed(range(2000, 2096))))
            metadata["seeds"] = list(range(2000, 2096))
            for name in ("audit_result.json", "summary.json"):
                (root / name).write_text(json.dumps(metadata), encoding="utf-8")
            self.assert_rejected_without_replacing(root, "Trace seed order differs from the fixed v15 experiment")

    def test_nested_secondary_statistic_tampering_is_rejected(self):
        plot = importlib.import_module("validation_fish_boids_v15.plot_audit")
        saved = {"late": {"cohorts": {"baseline_low": {"hull_area": {"mean": 0.125}}}}}
        computed = {"late": {"cohorts": {"baseline_low": {"hull_area": {"mean": 0.25}}}}}
        with self.assertRaisesRegex(ValueError, "late.cohorts.baseline_low.hull_area.mean"):
            plot.assert_same_statistics(saved, computed, "windows")

    def test_no_interval_is_not_equivalent_to_a_zero_interval(self):
        plot = importlib.import_module("validation_fish_boids_v15.plot_audit")
        with self.assertRaisesRegex(ValueError, "ci95"):
            plot.assert_same_statistics({"ci95": [0, 0]}, {"ci95": None}, "singleton")

    def test_wrong_source_key_preserves_existing_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = fixture_metadata(root)
            metadata["source_sha256"]["unrelated.py"] = metadata["source_sha256"].pop(SOURCE_FILES[-1])
            for name in ("audit_result.json", "summary.json"):
                (root / name).write_text(json.dumps(metadata), encoding="utf-8")
            self.assert_rejected_without_replacing(root, "Computational source provenance disagrees")

    def test_wrong_source_hash_preserves_existing_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = fixture_metadata(root)
            metadata["source_sha256"][SOURCE_FILES[-1]] = "0" * 64
            for name in ("audit_result.json", "summary.json"):
                (root / name).write_text(json.dumps(metadata), encoding="utf-8")
            self.assert_rejected_without_replacing(root, "Computational source provenance disagrees")

    def test_false_replay_evidence_preserves_existing_figure(self):
        invalid = (
            ("common_rng_at_split_and_end", False),
            ("exact_v14_natural_seed_pairs", 95),
            ("exact_v14_natural_seed_pairs", 96.0),
            ("first_call_V_invariance", 1),
        )
        for key, value in invalid:
            with self.subTest(field=key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                metadata = fixture_metadata(root)
                metadata["validations"][key] = value
                for name in ("audit_result.json", "summary.json"):
                    (root / name).write_text(json.dumps(metadata), encoding="utf-8")
                self.assert_rejected_without_replacing(root, "Saved replay/validation evidence differs")

    def test_wrong_execution_history_metadata_preserves_existing_figure(self):
        invalid = (
            ("predecessor_commit", "0" * 40),
            ("source_histories", 191),
            ("source_hashes_captured_before_execution_and_verified_after", False),
        )
        for key, value in invalid:
            with self.subTest(field=key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                metadata = fixture_metadata(root)
                metadata[key] = value
                for name in ("audit_result.json", "summary.json"):
                    (root / name).write_text(json.dumps(metadata), encoding="utf-8")
                self.assert_rejected_without_replacing(root, "Saved execution history differs")


def figure_fixture(low_n):
    """Analytical constants for rendering edge cases, never a simulated seed run."""
    seeds = list(range(2000, 2096))
    cohort = {
        "all": {"n": 96, "seeds": seeds, "indices": list(range(96))},
        "baseline_low": {"n": low_n, "seeds": seeds[:low_n], "indices": list(range(low_n))},
    }
    arms = tuple(f"intact__{mask:03b}" for mask in range(8)) + (
        "motor_cut__000", "motor_cut__011", "motor_cut__100", "motor_cut__111",
    )
    # Every toy corner is equal: all signed effects are exactly zero. The one
    # member subset tests a point estimate with no interval; an empty subset
    # tests absence of both. This fixture never passes the saved-data admission.
    arrays = {f"{arm}__call_fraction": np.broadcast_to(np.array(0.5), (96, 4960)) for arm in arms}
    arrays["seeds"] = np.asarray(seeds)

    def summary(value, n):
        return {"n": n, "mean": value if n else None, "median": value if n else None,
                "ci95": [value, value] if n > 1 else None}

    contrasts = (
        "natural_history", "X_insertion_intact", "X_deletion_intact", "natural_history_motor_cut",
        "X_insertion_motor_cut", "X_deletion_motor_cut", "motor_DID_total",
        "motor_DID_X_insertion", "motor_DID_X_deletion",
    )
    stats = {"cohorts": cohort, "windows": {"primary": {"steps": [1040, 4040], "cohorts": {}}},
             "arrivals": {"0.9": {"cohorts": {}}}}
    for name, data in cohort.items():
        n = data["n"]
        stats["windows"]["primary"]["cohorts"][name] = {"call_fraction": {
            "arms": {arm: summary(0.5, n) for arm in arms},
            "contrasts": {key: summary(0.0, n) for key in contrasts},
            "decomposition": {
                "shapley": {key: summary(0.0, n) for key in ("X", "V", "C")},
                "mobius": {key: summary(0.0, n) for key in ("X", "V", "C", "XV", "XC", "VC", "XVC")},
                "shapley_X_minus_C": summary(0.0, n),
                "max_mobius_closure_error": 0.0,
                "max_shapley_closure_error": 0.0,
            },
        }}
        stats["arrivals"]["0.9"]["cohorts"][name] = {
            "natural_latency_contrast": summary(0.0, n),
            "arms": {arm: {"n": n, "events": n, "censored": 0, "mean_restricted_latency": 4960 if n else None}
                     for arm in arms},
        }
    arrivals = []
    for i, seed in enumerate(seeds):
        for arm in ("intact__000", "intact__111"):
            observed = arm == "intact__000"
            arrivals.append({"seed": seed, "baseline_low": i < low_n, "arm": arm, "threshold": 0.9,
                             "confirmation_step": 6000 if observed else None,
                             "event_observed": observed, "censored": not observed, "restricted_latency": 4960})
    return arrays, stats, arrivals


class FigureEdgeCaseTests(unittest.TestCase):
    def test_empty_and_singleton_subsets_render_all_three_figures(self):
        plot = importlib.import_module("validation_fish_boids_v15.plot_audit")
        for low_n in (0, 1):
            with self.subTest(low_n=low_n), tempfile.TemporaryDirectory() as tmp:
                arrays, stats, arrivals = figure_fixture(low_n)
                with warnings.catch_warnings():
                    warnings.simplefilter("error", RuntimeWarning)
                    figures = plot.build_figures(arrays, stats, arrivals)
                self.assertEqual(set(figures), {
                    "primary_state_transplants", "component_interactions", "arrival_and_motor_controls",
                })
                first = figures["primary_state_transplants"]
                # A lost high-state seed would change this visible point count.
                self.assertEqual(len(first.axes[0].collections[0].get_offsets()), 96)
                low_panel = first.axes[2]
                low_offsets = [item.get_offsets() for item in low_panel.collections
                               if isinstance(item, plot.PathCollection)]
                self.assertEqual(sum(len(points) for points in low_offsets), low_n)
                for name, fig in figures.items():
                    for extension in ("png", "pdf"):
                        path = Path(tmp) / f"{name}.{extension}"
                        fig.savefig(path)
                        self.assertGreater(path.stat().st_size, 1000)
                    plot.plt.close(fig)

    def test_factorial_display_values_use_xvc_bit_order_and_signed_interactions(self):
        plot = importlib.import_module("validation_fish_boids_v15.plot_audit")
        first = np.asarray([0, 1, 2, 4, 3, 6, 8, 16], dtype=np.int64)
        corners = np.stack((first, 32 - first))
        terms = plot.factorial_values(corners, 32)
        expected = {"X": 3 / 32, "V": 2 / 32, "C": 1 / 32, "XV": 3 / 32,
                    "XC": 2 / 32, "VC": 1 / 32, "XVC": 4 / 32}
        for key, value in expected.items():
            np.testing.assert_allclose(terms["mobius"][key], [value, -value], rtol=0, atol=1e-15)
        for key, value in {"X": 41 / 192, "V": 1 / 6, "C": 23 / 192}.items():
            np.testing.assert_allclose(terms["shapley"][key], [value, -value], rtol=0, atol=1e-15)

    def test_component_points_keep_additive_integer_interactions_exactly_zero(self):
        plot = importlib.import_module("validation_fish_boids_v15.plot_audit")
        arrays, stats, arrivals = figure_fixture(1)
        # Counts 1..8 are exactly additive (X=4,V=2,C=1). Dividing each
        # corner by 96000 before differencing creates false signed roundoff.
        for mask in range(8):
            trace = np.zeros(4960)
            trace[0] = (mask + 1) / 32
            arrays[f"intact__{mask:03b}__call_fraction"] = np.broadcast_to(trace, (96, 4960))
        figures = plot.build_figures(arrays, stats, arrivals)
        try:
            for axis in figures["component_interactions"].axes[2:]:
                points = [item for item in axis.collections if isinstance(item, plot.PathCollection)]
                self.assertEqual(len(points), 7)
                for item in points[3:]:
                    np.testing.assert_array_equal(np.asarray(item.get_offsets())[:, 0], 0.0)
        finally:
            for figure in figures.values():
                plot.plt.close(figure)


if __name__ == "__main__":
    unittest.main()
