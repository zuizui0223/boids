"""v51 pure conditional predictive comparison, never a causal habitat test.

The same frozen M0/M1 losses are standardized over common bird/cell/month/
6-hour clock strata. No original identifiers or source coordinates are returned.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import timezone
import numpy as np

VALID = 'C_AHN2_VALID'
MASKED = 'C_SELECTED_CELL_AHN2_MISSING'
OUTSIDE = 'C_OUTSIDE_2010_SELECTED_CELLS'
GROUPS = (VALID, MASKED)
MIN_EACH_STRATUM = 3
MIN_STRATA_PER_BIRD = 2
MIN_BIRDS = 3
MIN_ROWS_EACH = 200
MIN_WEEKS_EACH = 4
MIN_CELLS = 2
SEED = 20261106


def _contrasts(four):
    """Input order: valid M0/M1, masked M0/M1; preserve paired columns."""
    x = np.asarray(four, dtype=float)
    if x.shape[-1] != 4 or np.any(x[..., [0, 2]] <= 0):
        raise ValueError('Four losses with positive group baselines required')
    rv = 1 - x[..., 1] / x[..., 0]
    rm = 1 - x[..., 3] / x[..., 2]
    absolute = (x[..., 2] - x[..., 3]) - (x[..., 0] - x[..., 1])
    return np.stack((rv, rm, rm-rv, absolute), axis=-1)


def matched_analysis(rows, losses, labels, cells, *, phase_conditioned=False,
                     draws=10000):
    """Equal-stratum within bird, equal-bird matched source-domain contrast.

    Rows carry id, aware B-time t and true phase. Cells are destination RD
    cell keys, used only to match; neither source location nor id is exported.
    All frozen gates are applied to common support before outcome reporting.
    """
    errors = np.asarray(losses, dtype=float)
    n = len(rows)
    if errors.shape != (n, 2) or len(labels) != n or len(cells) != n:
        raise ValueError('Source rows, losses, groups and cells must align')
    if not np.isfinite(errors).all() or np.any(errors < 0):
        raise ValueError('Squared direction losses must be finite and nonnegative')
    if not isinstance(draws, int) or draws < 1:
        raise ValueError('Positive integer bootstrap count required')
    strata = defaultdict(lambda: {VALID: [], MASKED: []})
    time_utc = []
    input_counts = {g: 0 for g in (VALID, MASKED, OUTSIDE)}
    for i, (r, label, cell) in enumerate(zip(rows, labels, cells)):
        if label not in input_counts:
            raise ValueError('Unexpected historical source-observability label')
        t = r['t']
        if t.tzinfo is None or t.utcoffset() is None:
            raise ValueError('Timezone-aware original B timestamp required')
        t = t.astimezone(timezone.utc)
        if t.year != 2011:
            raise ValueError('Only frozen 2011 test source year is permitted')
        time_utc.append(t)
        input_counts[label] += 1
        if label == OUTSIDE:
            continue
        if cell is None or len(cell) != 2:
            raise ValueError('Selected destination cell required')
        key = (r['id'], tuple(cell), t.year, t.month, t.hour // 6)
        if phase_conditioned:
            if r['phase'] not in (-1, 1):
                raise ValueError('Frozen non-slack phase sign required')
            key += (int(r['phase']),)
        strata[key][label].append(i)

    common = [(k, v) for k, v in strata.items()
              if all(len(v[g]) >= MIN_EACH_STRATUM for g in GROUPS)]
    per_bird = defaultdict(list)
    for key, indices in common:
        per_bird[key[0]].append((key, indices))
    per_bird = {b: entries for b, entries in per_bird.items()
                if len(entries) >= MIN_STRATA_PER_BIRD}
    chosen = [entry for entries in per_bird.values() for entry in entries]
    kept = {g: [i for _, ix in chosen for i in ix[g]] for g in GROUPS}
    weeks = {g: len({time_utc[i].isocalendar()[:2] for i in kept[g]})
             for g in GROUPS}
    n_cells = len({k[1] for k, _ in chosen})
    support = {
        'source_test_rows': n,
        'source_group_episodes': input_counts,
        'candidate_strata': len(strata),
        'strata_with_at_least_three_each_before_bird_filter': len(common),
        'matched_strata': len(chosen),
        'matched_birds': len(per_bird),
        'matched_destination_cells': n_cells,
        'matched_episodes': {g: len(kept[g]) for g in GROUPS},
        'matched_ISO_weeks': weeks,
        'retained_fraction_by_group': {
            g: len(kept[g])/input_counts[g] if input_counts[g] else None
            for g in GROUPS},
    }
    failed = []
    if len(per_bird) < MIN_BIRDS: failed.append('fewer_than_3_birds')
    if n_cells < MIN_CELLS: failed.append('fewer_than_2_destination_cells')
    for g in GROUPS:
        if len(kept[g]) < MIN_ROWS_EACH: failed.append(g + '_fewer_than_200_rows')
        if weeks[g] < MIN_WEEKS_EACH: failed.append(g + '_fewer_than_4_weeks')
    report = {
        'admission': 'NOT_ADMITTED_INSUFFICIENT_COMMON_SUPPORT' if failed
                     else 'ADMITTED_MATCHED_CONDITIONAL_COMPARISON',
        'phase_composition_matched': bool(phase_conditioned),
        'support': support,
        'failed_gates': failed,
        'estimand': 'equal_bird_equal_common_stratum_ratio_of_mean_losses',
        'model_refit_by_source_group': False,
    }
    if failed:
        return report

    # Exactly the same set of conditions and weights on BOTH sides for each bird.
    bird_losses = []
    for bird in sorted(per_bird, key=str):
        pieces = [np.concatenate([errors[ix[g]].mean(axis=0) for g in GROUPS])
                  for _, ix in per_bird[bird]]
        bird_losses.append(np.mean(pieces, axis=0))
    bird_losses = np.asarray(bird_losses)
    point = _contrasts(bird_losses.mean(axis=0))
    rng = np.random.default_rng(SEED)
    index = rng.integers(len(bird_losses), size=(draws, len(bird_losses)))
    boot = _contrasts(bird_losses[index].mean(axis=1))
    individual = _contrasts(bird_losses)
    lo = [_contrasts(np.delete(bird_losses, j, axis=0).mean(axis=0))[2]
          for j in range(len(bird_losses))]
    report.update({
        'standardized_M0_M1_losses': {
            'valid': bird_losses.mean(axis=0)[:2].tolist(),
            'masked': bird_losses.mean(axis=0)[2:].tolist()},
        'relative_skill': {
            'valid': float(point[0]), 'masked': float(point[1]),
            'masked_minus_valid': float(point[2]),
            'paired_bird_CI95': np.quantile(boot[:, 2], [.025, .975]).tolist()},
        'absolute_gain': {
            'masked_minus_valid': float(point[3]),
            'paired_bird_CI95': np.quantile(boot[:, 3], [.025, .975]).tolist()},
        'positive_birds': int(np.sum(individual[:, 2] > 0)),
        'leave_one_bird_out_gap_range': [float(min(lo)), float(max(lo))],
        'bootstrap_draws': draws,
        'causal_or_intertidal_habitat_identity': 'NOT_IDENTIFIED',
    })
    return report
