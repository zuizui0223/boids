"""v21: pressure/particle-motion phase observability counterexample.

This is an analytic/constructed known-truth fixture, NOT observed fish data.
It does not estimate a biological sensing rule from Veith et al. (2024).
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SoundField:
    """Single-frequency complex sound pressure and axial particle velocity.

    P and U are complex Fourier amplitudes. This is deliberately a *local*
    signal, not a complete calibrated field or an acoustic propagation model.
    """

    pressure: complex
    particle_velocity: complex

    def __post_init__(self) -> None:
        for name, value in (("pressure", self.pressure), ("particle_velocity", self.particle_velocity)):
            try:
                z = complex(value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"{name} must be a finite complex amplitude") from exc
            if not (math.isfinite(z.real) and math.isfinite(z.imag)):
                raise ValueError(f"{name} must be a finite complex amplitude")
            object.__setattr__(self, name, z)

    def phase_blind_signature(self) -> tuple[float, float]:
        """Sound pressure magnitude^2 and particle velocity magnitude^2 only."""
        return (abs(self.pressure)**2, abs(self.particle_velocity)**2)

    def directional_cross_term(self) -> float:
        """Illustrative active axial acoustic flux proxy Re[P * conjugate(U)].

        NOT a measured sensory filter or fish steering law. Its sign is
        phase sensitive whereas phase_blind_signature is not.
        """
        return (self.pressure * self.particle_velocity.conjugate()).real

    def counterphase(self) -> SoundField:
        """Invert particle motion while keeping both channel magnitudes."""
        return SoundField(self.pressure, -self.particle_velocity)


def constructed_pair(seed: int = 20261122, n_pairs: int = 1000) -> dict:
    """Show the irreducible balanced sign error for phase-blind observations.

    Every matched pair has identical phase-blind inputs, but opposite
    *constructed* labels (the sign of the cross term). Thus no classifier
    based only on the phase-blind signature can beat 1/2 accuracy when
    matched pairs have identical weights. No wild-fish inference is made.
    """
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a nonnegative int")
    if not isinstance(n_pairs, int) or isinstance(n_pairs, bool) or n_pairs < 1:
        raise ValueError("n_pairs must be a positive int")
    rng = random.Random(seed)
    matched = 0
    sign_flips = 0
    scalar_correct = 0
    phase_correct = 0
    for _ in range(n_pairs):
        p_mag = rng.uniform(.1, 2.)
        u_mag = rng.uniform(.1, 2.)
        theta = rng.uniform(-math.pi, math.pi)
        phase = complex(math.cos(theta), math.sin(theta))
        a = SoundField(p_mag * phase, u_mag * phase)
        b = a.counterphase()
        assert a.phase_blind_signature() == b.phase_blind_signature()
        matched += 1
        a_label = 1 if a.directional_cross_term() > 0 else 0
        b_label = 1 if b.directional_cross_term() > 0 else 0
        assert a_label != b_label
        sign_flips += 1
        # Any fixed scalar-only prediction makes exactly one correct label.
        scalar_prediction = 1
        scalar_correct += int(scalar_prediction == a_label) + int(scalar_prediction == b_label)
        phase_correct += int(a_label == 1) + int(b_label == 0)
    return {
        "status": "CONSTRUCTED_IDENTIFIABILITY_COUNTEREXAMPLE_NOT_FIELD_EVIDENCE",
        "seed": seed,
        "matched_pairs": matched,
        "total_constructed_cases": 2 * matched,
        "equal_phase_blind_pairs": matched,
        "opposite_phase_cross_term_pairs": sign_flips,
        "phase_blind_balanced_accuracy_bound": scalar_correct / (2 * matched),
        "phase_aware_constructed_label_accuracy": phase_correct / (2 * matched),
        "scope": "Same pressure and particle-motion amplitudes; relative phase is inverted. "
                 "Illustrative frequency-domain proxy only, not a fitted fish response model.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261122)
    parser.add_argument("--pairs", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = constructed_pair(args.seed, args.pairs)
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
