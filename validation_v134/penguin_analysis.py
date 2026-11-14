"""Prefit, matched whole-week exploratory submergence/current analysis.

See docs/V134_PENGUIN_PREFIT_ANALYSIS.md. No global or confirmatory inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from validation_v134.penguin_source import (
    CLOCKS, ORIGIN, ORIGINALS, SHIFTS, CurrentGrid, aggregate_observations,
    join_windows, read_current_grid, speed_column, verify_source,
)


def local_week(seconds):
    return pd.to_datetime(np.asarray(seconds) - 3 * 3600, unit='s', utc=True).strftime('%G-W%V').to_numpy()


def week_folds(weeks):
    weeks = np.asarray(weeks)
    levels = np.unique(weeks)
    if len(levels) < 2:
        raise ValueError('FEWER_THAN_TWO_WEEKS')
    return [(week, weeks != week, weeks == week) for week in levels]


def solar_sine(seconds, longitude, latitude):
    """Sine of solar-center elevation, NOAA fractional-year approximation."""
    t = pd.to_datetime(np.asarray(seconds), unit='s', utc=True)
    hour = t.hour.to_numpy() + t.minute.to_numpy() / 60 + t.second.to_numpy() / 3600
    year_days = np.where(t.is_leap_year, 366., 365.)
    gamma = 2 * np.pi / year_days * (t.dayofyear.to_numpy() - 1 + (hour - 12) / 24)
    equation = 229.18 * (.000075 + .001868 * np.cos(gamma) - .032077 * np.sin(gamma)
                         - .014615 * np.cos(2 * gamma) - .040849 * np.sin(2 * gamma))
    declination = (.006918 - .399912 * np.cos(gamma) + .070257 * np.sin(gamma)
                   - .006758 * np.cos(2 * gamma) + .000907 * np.sin(2 * gamma)
                   - .002697 * np.cos(3 * gamma) + .00148 * np.sin(3 * gamma))
    solar_minutes = (hour * 60 + equation + 4 * np.asarray(longitude)) % 1440
    angle = np.radians(solar_minutes / 4 - 180)
    lat = np.radians(latitude)
    return np.clip(np.sin(lat) * np.sin(declination) + np.cos(lat) * np.cos(declination) * np.cos(angle), -1, 1)


def fractional_objective(beta, design, outcome, weights, penalty):
    eta = design @ beta
    loss = np.sum(weights * (np.logaddexp(0, eta) - outcome * eta)) + penalty * np.dot(beta[1:], beta[1:]) / 2
    gradient = design.T @ (weights * (expit(eta) - outcome))
    gradient[1:] += penalty * beta[1:]
    return float(loss), gradient


def fit_predict(train_x, test_x, outcome, animal_ids, penalty, names):
    animal_ids = np.asarray(animal_ids)
    _, inv, counts = np.unique(animal_ids, return_inverse=True, return_counts=True)
    weights = 1 / counts[inv]
    weights /= weights.sum()
    continuous = np.array([not name.startswith('animal:') for name in names])
    means = np.sum(weights[:, None] * train_x, axis=0)
    scales = np.sqrt(np.sum(weights[:, None] * (train_x - means) ** 2, axis=0))
    # Indicators retain their original 0/1 coding. Constant numeric features
    # provide no training information and are zero in both design matrices.
    constant = (scales < 1e-12) & continuous
    means[~continuous] = 0
    scales[~continuous] = 1
    scales[constant] = 1
    a = (train_x - means) / scales
    b = (test_x - means) / scales
    a[:, constant] = 0; b[:, constant] = 0
    a = np.column_stack([np.ones(len(a)), a])
    b = np.column_stack([np.ones(len(b)), b])
    initial = np.zeros(a.shape[1])
    mean_y = np.clip(np.dot(weights, outcome), 1e-6, 1 - 1e-6)
    initial[0] = np.log(mean_y / (1 - mean_y))
    fitted = minimize(fractional_objective, initial, args=(a, outcome, weights, penalty), jac=True,
                      method='L-BFGS-B', options={'maxiter': 1000, 'ftol': 1e-12, 'gtol': 1e-8})
    if not fitted.success:
        raise RuntimeError('FRACTIONAL_MODEL_DID_NOT_CONVERGE: ' + str(fitted.message))
    return expit(b @ fitted.x), {'converged': True, 'iterations': int(fitted.nit),
                                'maximum_gradient': float(np.max(np.abs(fitted.jac))),
                                'training_animals': len(counts), 'training_windows': len(a)}


def design_features(frame, model, clock=0, shift=0, mode='linear'):
    seconds = frame.time_seconds.to_numpy() + clock * 3600
    hour = ((seconds - 3 * 3600) % 86400) / 3600
    lon, lat = frame.longitude.to_numpy(), frame.latitude.to_numpy()
    features = {
        'clock_sin24': np.sin(2 * np.pi * hour / 24), 'clock_cos24': np.cos(2 * np.pi * hour / 24),
        'clock_sin12': np.sin(2 * np.pi * hour / 12), 'clock_cos12': np.cos(2 * np.pi * hour / 12),
        'elapsed_days': (seconds - ORIGIN) / 86400, 'trip_elapsed_hours': frame.elapsed_hours.to_numpy(),
        'observation_fraction': frame.n_seconds.to_numpy() / 900,
        'longitude': lon, 'latitude': lat, 'longitude_squared': lon ** 2,
        'latitude_squared': lat ** 2, 'longitude_latitude': lon * lat,
    }
    if model != 'M0':
        sun = solar_sine(seconds, lon, lat)
        night = (sun < np.sin(np.radians(-.833))).astype(float)
        features.update(solar_sine=sun, positive_solar_sine=np.maximum(sun, 0), night=night)
    if model == 'M2':
        speed = frame[speed_column(clock, shift, mode)].to_numpy()
        features.update(current_speed=speed, current_speed_squared=speed ** 2, current_speed_night=speed * night)
    for animal in sorted(frame.ID.unique()):
        features['animal:' + animal] = (frame.ID.to_numpy() == animal).astype(float)
    return np.column_stack(list(features.values())), list(features)


def hierarchical_score(frame, value):
    individual_week = frame.groupby(['week', 'ID'], observed=True)[value].mean()
    return float(individual_week.groupby(level='week').mean().mean())


def run_scenario(inputs, name, threshold=2, clock=0, mode='linear', include_static_zero=False, penalty=.01):
    selected = inputs.common_support.to_numpy(dtype=bool, copy=True)
    if not include_static_zero:
        selected &= inputs.static_zero_vertices.to_numpy() == 0
    frame = inputs.loc[selected].copy().reset_index(drop=True)
    frame['week'] = local_week(frame.time_seconds.to_numpy() + clock * 3600)
    y = frame[f'depth_gt_{threshold}'].to_numpy() / frame.n_seconds.to_numpy()
    sun = solar_sine(frame.time_seconds.to_numpy() + clock * 3600, frame.longitude.to_numpy(), frame.latitude.to_numpy())
    frame['night'] = sun < np.sin(np.radians(-.833))
    if frame.ID.nunique() < 2 or frame.night.nunique() != 2:
        raise ValueError('INSUFFICIENT_ANIMALS_OR_DAY_NIGHT_COVERAGE')
    folds = week_folds(frame.week.to_numpy())
    predictions = {}
    convergence, fold_records = [], []
    configurations = [('M0', 'M0', 0), ('M1', 'M1', 0)] + [(f'current_{shift:+d}h', 'M2', shift) for shift in SHIFTS]
    for label, model, shift in configurations:
        x, names = design_features(frame, model, clock, shift, mode)
        prediction = np.full(len(frame), np.nan)
        for week, train, test in folds:
            prediction[test], fit = fit_predict(x[train], x[test], y[train], frame.ID.to_numpy()[train], penalty, names)
            convergence.append({'model': label, 'held_out_week': week, **fit})
            if label == 'M0':
                train_ids, test_ids = set(frame.ID[train]), set(frame.ID[test])
                fold_records.append({'held_out_week': week, 'train_windows': int(train.sum()), 'test_windows': int(test.sum()),
                                     'train_animals': len(train_ids), 'test_animals': len(test_ids),
                                     'animals_in_both': len(train_ids & test_ids),
                                     'test_night_windows': int(frame.night[test].sum()),
                                     'test_day_windows': int((~frame.night[test]).sum())})
        if not np.isfinite(prediction).all():
            raise ValueError('MISSING_HELD_OUT_PREDICTION')
        predictions[label] = prediction
    # Postfit calibration diagnostic, added transparently after observing that
    # the prefit model losses exceed log(2). It does not change any prefit model,
    # mask, hyperparameter, shift, ranking or scientific decision rule.
    predictions['diagnostic_constant_half'] = np.full(len(frame), .5)
    prevalence_prediction = np.full(len(frame), np.nan)
    for _, train, test in folds:
        train_frame = pd.DataFrame({'ID': frame.ID.to_numpy()[train], 'y': y[train]})
        prevalence_prediction[test] = train_frame.groupby('ID').y.mean().mean()
    predictions['diagnostic_training_prevalence'] = prevalence_prediction
    scored = frame[['ID', 'week', 'n_seconds', 'night']].copy()
    metrics = {}
    for label, prediction in predictions.items():
        p = np.clip(prediction, 1e-12, 1 - 1e-12)
        scored[label] = -(y * np.log(p) + (1 - y) * np.log1p(-p))
        scored[label + '_brier'] = (y - p) ** 2
        metrics[label] = {'cross_entropy': hierarchical_score(scored, label),
                          'squared_share_error': hierarchical_score(scored, label + '_brier')}
    real = metrics['current_+0h']['cross_entropy']
    wrong = {k: v['cross_entropy'] for k, v in metrics.items() if k.startswith('current_') and k != 'current_+0h'}
    best_wrong = min(wrong, key=wrong.get)
    individual_week = scored.groupby(['ID', 'week'], observed=True)[list(predictions)].mean().reset_index()
    details = {'scenario': name, 'threshold_m': threshold, 'clock_shift_hours': clock, 'time_interpolation': mode,
               'include_static_zero_nodes': include_static_zero, 'ridge_penalty': penalty,
               'windows': len(frame), 'animals': frame.ID.nunique(), 'weeks': frame.week.nunique(),
               'observed_seconds': int(frame.n_seconds.sum()), 'night_windows': int(frame.night.sum()),
               'day_windows': int((~frame.night).sum()), 'folds': fold_records,
               'scores': metrics, 'best_wrong_clock': best_wrong,
               'delta_solar': metrics['M0']['cross_entropy'] - metrics['M1']['cross_entropy'],
               'delta_current': metrics['M1']['cross_entropy'] - real,
               'delta_phase': wrong[best_wrong] - real,
               'real_clock_rank_of_9': 1 + sum(value < real for value in wrong.values()),
               'all_fits_converged': all(x['converged'] for x in convergence),
               'largest_final_gradient': max(x['maximum_gradient'] for x in convergence),
               'postfit_calibration_diagnostic': 'Both an unfit p=0.5 comparator and animal-balanced training-only prevalence; no model selection or revision based on these diagnostics.',
               'confirmatory_eight_week_gate': frame.week.nunique() >= 8}
    return details, individual_week


def conditional_bootstrap(individual_week, draws=2000, seed=134):
    rng = np.random.default_rng(seed)
    animals = np.sort(individual_week.ID.unique())
    weeks = np.sort(individual_week.week.unique())
    models = [c for c in individual_week if c not in ('ID', 'week')]
    cube = np.full((len(animals), len(weeks), len(models)), np.nan)
    for _, row in individual_week.iterrows():
        cube[np.searchsorted(animals, row.ID), np.searchsorted(weeks, row.week)] = row[models].to_numpy(dtype=float)
    indexes = {name: models.index(name) for name in models}
    wrong_indexes = [i for i, label in enumerate(models) if label.startswith('current_') and label != 'current_+0h']
    values = []
    while len(values) < draws:
        sampled = cube[rng.integers(len(animals), size=len(animals))]
        if np.any(np.all(np.isnan(sampled[:, :, 0]), axis=0)):
            continue
        scores = np.nanmean(sampled, axis=0).mean(axis=0)
        real = scores[indexes['current_+0h']]
        values.append([scores[indexes['M0']] - scores[indexes['M1']], scores[indexes['M1']] - real,
                       min(scores[wrong_indexes]) - real])
    intervals = np.quantile(values, [.025, .975], axis=0)
    return {'draws': draws, 'seed': seed, 'type': 'animal-cluster conditional resampling interval; fitted folds not refit; two observed weeks fixed',
            'not_a_meta_analysis_standard_error': True,
            'intervals': {label: [float(intervals[0, i]), float(intervals[1, i])]
                          for i, label in enumerate(('delta_solar', 'delta_current', 'delta_phase'))}}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def run(source_directory, output_directory, prepared=None):
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    spec = Path(__file__).resolve().parents[1] / 'docs/V134_PENGUIN_PREFIT_ANALYSIS.md'
    spec_hash = hashlib.sha256(spec.read_bytes()).hexdigest()
    if prepared:
        inputs = pd.read_csv(prepared)
        source_audit = {'mode': 'derived-input replay', 'prepared_input_sha256': hashlib.sha256(Path(prepared).read_bytes()).hexdigest()}
    else:
        source = Path(source_directory)
        receipts = {name: verify_source(source / name) for name in ORIGINALS}
        original = pd.read_csv(source / 'Penguins.csv')
        windows, aggregation = aggregate_observations(original)
        del original
        print('AGGREGATED', json.dumps(aggregation), flush=True)
        grid = read_current_grid(source / 'Ocean_Currents.csv')
        inputs, join = join_windows(windows, grid)
        del grid
        prepared_path = output / 'penguin_15min_matched_inputs.csv.gz'
        inputs.to_csv(prepared_path, index=False, float_format='%.12g', compression={'method': 'gzip', 'mtime': 0})
        # Analyze the exact serialized inputs that will be replayed and reviewed.
        inputs = pd.read_csv(prepared_path)
        source_audit = {'original_sources': receipts, 'aggregation': aggregation, 'current_join': join,
                        'prepared_input_sha256': hashlib.sha256(prepared_path.read_bytes()).hexdigest(),
                        'license': 'CC BY 4.0; Gunner et al. 2025, Figshare 10.6084/m9.figshare.28517873.v1',
                        'timezone_qualification': 'Naive Timestamp localized using author metadata for renamed DateTime=UTC; +/-3h sensitivity retained.'}
        write_json(output / 'penguin_analysis_source_audit.json', source_audit)
    configurations = [
        ('primary', {}), ('threshold_1m', {'threshold': 1}), ('threshold_5m', {'threshold': 5}),
        ('clock_minus3h', {'clock': -3}), ('clock_plus3h', {'clock': 3}),
        ('nearest_hour', {'mode': 'nearest'}), ('floor_hour', {'mode': 'floor'}),
        ('retain_original_zero_nodes', {'include_static_zero': True}),
        ('ridge_0.001', {'penalty': .001}), ('ridge_0.1', {'penalty': .1}),
    ]
    scenarios = []
    primary_scores = None
    for name, options in configurations:
        result, individual_week = run_scenario(inputs, name, **options)
        scenarios.append(result)
        if name == 'primary':
            primary_scores = individual_week
            individual_week.to_csv(output / 'penguin_primary_animal_week_scores.csv', index=False, float_format='%.12g')
        print('SCENARIO', name, {k: result[k] for k in ('windows', 'animals', 'weeks', 'delta_current', 'delta_phase', 'real_clock_rank_of_9')}, flush=True)
    result = {'version': 'v134-prefit-penguin-submergence-1', 'spec_sha256': spec_hash,
              'source_input_sha256': source_audit['prepared_input_sha256'],
              'independent_studies': 1, 'independent_coasts': 1, 'taxa': ['Spheniscus magellanicus'],
              'status': 'EXPLORATORY_CONDITIONAL_ON_SOURCE_CLOCK; NOT_CONFIRMATORY; NOT_GLOBAL_META_ANALYSIS',
              'endpoint': 'Observed pressure-depth submergence share, not prey capture',
              'scenarios': scenarios, 'primary_conditional_intervals': conditional_bootstrap(primary_scores)}
    write_json(output / 'penguin_analysis_results.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-directory')
    parser.add_argument('--output-directory', required=True)
    parser.add_argument('--prepared')
    args = parser.parse_args()
    if not args.prepared and not args.source_directory:
        parser.error('supply --source-directory or --prepared')
    run(args.source_directory, args.output_directory, args.prepared)
