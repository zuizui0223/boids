"""Execute the frozen v14 synthetic follow-up; no parameter or seed search."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import tempfile

import numpy as np
import scipy
from scipy.spatial import ConvexHull, QhullError

from analysis import (contrast_summary, difference_in_differences,
                      first_high_window, paired_summary, window_mean)
from geometry import geometry_diagnostic
from simulation import simulate

ROOT = Path(__file__).resolve().parent
SEEDS = tuple(range(1000, 1024))
STEPS, N, CUT = 16000, 32, 1040
SNAPSHOTS = (1000, 1040, 4000, 16000)
MECHANISMS = {'intact': (5., 3.), 'motor_cut': (0., 3.),
              'hearing_cut': (5., 0.), 'both_cut': (0., 0.)}
TIMINGS = ('none', 'pulse')
WINDOWS = {'immediate_post': (1040, 1240), 'v13_terminal': (3000, 4000),
           'middle': (7000, 8000), 'terminal': (12000, 16000)}
FIELDS = ('call_fraction', 'hull_area', 'cue', 'snapshot_pos',
          'snapshot_velocity', 'snapshot_calling')
PROTOCOL_COMMIT = 'd56e0de00d2a1bc11da434aedda00251049f0418'
PREDECESSOR_COMMIT = 'f558b7f5de63e3b3e712b92a0b2239a08663264f'
V13_TRACE_SHA256 = '1673d018c97b467dc31aa9199ace86f420f8810eeaf57435e7bb2c947097ddeb'


def _shape(field):
    if field in ('call_fraction', 'hull_area', 'cue'):
        return (len(SEEDS), STEPS)
    if field == 'snapshot_calling':
        return (len(SEEDS), len(SNAPSHOTS), N)
    return (len(SEEDS), len(SNAPSHOTS), N, 2)


def validate_trace_arrays(arrays):
    expected = {f'{m}__{t}__{f}' for m in MECHANISMS for t in TIMINGS for f in FIELDS}
    if set(arrays) != expected:
        raise ValueError('Trace keys do not match the frozen v14 experiment')
    for key, values in arrays.items():
        _, timing, field = key.split('__')
        a = np.asarray(values)
        if a.shape != _shape(field) or a.dtype.kind not in 'fiu' or not np.isfinite(a).all():
            raise ValueError(f'Invalid shape or values for {key}')
        if field == 'call_fraction' and (np.any(a < 0) or np.any(a > 1)):
            raise ValueError(f'Call fractions outside [0,1]: {key}')
        if field == 'call_fraction' and np.any(a * N != np.rint(a * N)):
            raise ValueError(f'Call fractions are not multiples of 1/{N}: {key}')
        if field == 'hull_area' and np.any(a <= 0):
            raise ValueError(f'Nonpositive hull areas: {key}')
        if field == 'snapshot_calling' and np.any((a != 0) & (a != 1)):
            raise ValueError(f'Nonbinary calling snapshots: {key}')
        if field == 'cue':
            wanted = np.zeros(STEPS)
            if timing == 'pulse':
                wanted[1000:1040] = .8
            if not np.array_equal(a, np.broadcast_to(wanted, a.shape)):
                raise ValueError(f'Playback differs from the frozen timing: {key}')
    for mechanism in MECHANISMS:
        for timing in TIMINGS:
            prefix = f'{mechanism}__{timing}__'
            calls = arrays[prefix + 'snapshot_calling'].mean(axis=2)
            if not np.array_equal(calls, arrays[prefix + 'call_fraction'][:, np.array(SNAPSHOTS) - 1]):
                raise ValueError('Snapshot calling disagrees with its completed-step trace')
            positions = arrays[prefix + 'snapshot_pos']
            for i in range(len(SEEDS)):
                for j, step in enumerate(SNAPSHOTS):
                    try:
                        area = ConvexHull(positions[i, j]).volume
                    except QhullError as exc:
                        raise ValueError('A snapshot has no nondegenerate planar hull') from exc
                    if not np.isclose(area, arrays[prefix + 'hull_area'][i, step - 1],
                                      rtol=1e-12, atol=1e-9):
                        raise ValueError('Snapshot hull disagrees with its completed-step trace')


def verify_invariants(arrays):
    for timing in TIMINGS:
        for mechanism in MECHANISMS:
            for field in ('call_fraction', 'hull_area'):
                expected = arrays[f'intact__{timing}__{field}'][:, :CUT]
                actual = arrays[f'{mechanism}__{timing}__{field}'][:, :CUT]
                if not np.array_equal(actual, expected):
                    raise AssertionError('A continuation changed the pre-intervention history')
            for field in ('snapshot_pos', 'snapshot_velocity', 'snapshot_calling'):
                if not np.array_equal(arrays[f'{mechanism}__{timing}__{field}'][:, :2],
                                      arrays[f'intact__{timing}__{field}'][:, :2]):
                    raise AssertionError('A continuation changed a pre-cut snapshot')
    for field in ('call_fraction', 'hull_area'):
        if not np.array_equal(arrays[f'intact__none__{field}'][:, :1000],
                              arrays[f'intact__pulse__{field}'][:, :1000]):
            raise AssertionError('The playback history differed before playback began')
    reference_calls = arrays['hearing_cut__none__call_fraction'][:, CUT:]
    for mechanism in ('hearing_cut', 'both_cut'):
        for timing in TIMINGS:
            if not np.array_equal(arrays[f'{mechanism}__{timing}__call_fraction'][:, CUT:],
                                  reference_calls):
                raise AssertionError('Post-cut iid calling does not share the expected random stream')
    return {'pre_cut_histories_identical': True, 'pre_pulse_histories_identical': True,
            'hearing_cut_iid_calls_identical': True}


def save_trace_archive(path, arrays):
    validate_trace_arrays(arrays)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.npz', delete=False) as stream:
            temporary = Path(stream.name)
            np.savez_compressed(stream, seeds=np.array(SEEDS),
                                snapshot_steps=np.array(SNAPSHOTS), **arrays)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json(path, value):
    content = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def capture_source_hashes(paths, base):
    return {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def verify_source_hashes(expected, base):
    try:
        current = capture_source_hashes([base / p for p in expected], base)
    except OSError as exc:
        raise RuntimeError('An execution source disappeared during the run') from exc
    if current != expected:
        raise RuntimeError('Execution sources changed during the run; refusing output provenance')


def store_trace(arrays, task, trace):
    if set(trace) != set(FIELDS) | {'snapshot_steps'}:
        raise ValueError('Worker trace keys differ from the simulation contract')
    schedule = np.asarray(trace['snapshot_steps'])
    if (schedule.shape != (len(SNAPSHOTS),) or schedule.dtype.kind not in 'iu'
            or not np.array_equal(schedule, SNAPSHOTS)):
        raise ValueError('Worker snapshot schedule differs from the frozen schedule')
    for field in FIELDS:
        values = np.asarray(trace[field])
        if (values.shape != _shape(field)[1:] or values.dtype.kind not in 'fiu'
                or not np.isfinite(values).all()):
            raise ValueError(f'Worker returned invalid shape or values for {field}')
    mechanism, timing, seed = task
    for field in FIELDS:
        arrays[f'{mechanism}__{timing}__{field}'][SEEDS.index(seed)] = trace[field]


def simulate_task(task):
    mechanism, timing, seed = task
    audio, heard = MECHANISMS[mechanism]
    pulse = None if timing == 'none' else 1000
    trace = simulate(seed, steps=STEPS, pulse_start=pulse, intervention_step=CUT,
                     audio_weight_after=audio, heard_weight_after=heard,
                     n=N, snapshot_steps=SNAPSHOTS)
    if not np.array_equal(trace['snapshot_steps'], SNAPSHOTS):
        raise AssertionError('Simulator snapshot schedule mismatch')
    if mechanism == 'intact':
        source = ROOT.parent / 'validation_fish_boids_v13' / 'simulation.py'
        spec = importlib.util.spec_from_file_location('v13_prefix_replay', source)
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
        old = legacy.simulate(seed, steps=4000, pulse_start=pulse)
        for field in ('call_fraction', 'hull_area', 'cue'):
            if not np.array_equal(trace[field][:4000], old[field]):
                raise AssertionError(f'Exact v13 prefix replay failed: {task}, {field}')
    return task, trace


def execute(workers):
    tasks = [(m, t, seed) for m in MECHANISMS for t in TIMINGS for seed in SEEDS]
    arrays = {f'{m}__{t}__{f}': np.empty(_shape(f))
              for m in MECHANISMS for t in TIMINGS for f in FIELDS}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(simulate_task, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), 1):
            task, trace = future.result()
            store_trace(arrays, task, trace)
            if completed % 8 == 0:
                print(f'Completed {completed}/{len(tasks)} frozen trajectories', flush=True)
    validate_trace_arrays(arrays)
    return arrays


def compare_archived_v13(arrays, archive):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != V13_TRACE_SHA256:
        raise ValueError('The supplied v13 reference is not the recorded raw-trace archive')
    with np.load(archive, allow_pickle=False) as old:
        if not np.array_equal(old['seeds'], SEEDS):
            raise AssertionError('Archived v13 seed order differs')
        for timing, old_timing in (('none', 'none'), ('pulse', 'warmup')):
            for field in ('call_fraction', 'hull_area'):
                if not np.array_equal(arrays[f'intact__{timing}__{field}'][:, :4000],
                                      old[f'full__{old_timing}__{field}']):
                    raise AssertionError('Archived v13 prefix differs')
    return {'matched': True, 'sha256': V13_TRACE_SHA256, 'seed_pairs': 24}


def summarize(arrays):
    indices = np.random.default_rng(20261122).integers(0, len(SEEDS), (10000, len(SEEDS)))
    contrasts, cut_effects = {}, {}
    for mechanism in MECHANISMS:
        contrasts[mechanism] = {}
        for window, (a, b) in WINDOWS.items():
            contrasts[mechanism][window] = {'steps': [a, b]}
            for field in ('call_fraction', 'hull_area'):
                off = window_mean(arrays[f'{mechanism}__none__{field}'], a, b)
                on = window_mean(arrays[f'{mechanism}__pulse__{field}'], a, b)
                contrasts[mechanism][window][field] = paired_summary(off, on, indices)
    for mechanism in ('motor_cut', 'hearing_cut', 'both_cut'):
        cut_effects[mechanism] = {}
        for window in WINDOWS:
            cut_effects[mechanism][window] = {}
            for field in ('call_fraction', 'hull_area'):
                intact = contrasts['intact'][window][field]
                cut = contrasts[mechanism][window][field]
                values = difference_in_differences(intact['per_seed_no_pulse'],
                    intact['per_seed_pulse'], cut['per_seed_no_pulse'], cut['per_seed_pulse'])
                cut_effects[mechanism][window][field] = contrast_summary(values, indices)
    factorial = {}
    for field in ('call_fraction', 'hull_area'):
        values = [np.array(contrasts[m]['terminal'][field]['per_seed_difference']) for m in MECHANISMS]
        factorial[field] = contrast_summary(values[0] - values[1] - values[2] + values[3], indices)
    return contrasts, cut_effects, factorial


def arrival_diagnostics(arrays):
    records, summaries = [], {}
    pre = window_mean(arrays['intact__none__call_fraction'], 800, 1000)
    indices = np.random.default_rng(20261122).integers(0, len(SEEDS), (10000, len(SEEDS)))
    for threshold in (.80, .90, .95):
        by_timing = {}
        for timing in TIMINGS:
            rows = []
            for i, seed in enumerate(SEEDS):
                found = first_high_window(arrays[f'intact__{timing}__call_fraction'][i],
                                          CUT, 200, threshold)
                row = {'seed': seed, 'timing': timing, 'threshold': threshold,
                       'baseline_call_fraction': float(pre[i]),
                       'baseline_high': bool(pre[i] >= threshold), **found}
                records.append(row)
                rows.append(row)
            by_timing[timing] = rows
        off = np.array([r['restricted_latency'] for r in by_timing['none']])
        on = np.array([r['restricted_latency'] for r in by_timing['pulse']])
        below = np.flatnonzero(pre < threshold)
        summaries[str(threshold)] = {
            'baseline_high_count': int(np.count_nonzero(pre >= threshold)),
            'no_pulse_events': sum(r['event_observed'] for r in by_timing['none']),
            'pulse_events': sum(r['event_observed'] for r in by_timing['pulse']),
            'restricted_latency_pulse_minus_none': paired_summary(off, on, indices),
            'below_baseline_threshold': {
                'seeds': [SEEDS[i] for i in below], 'n': int(below.size),
                'no_pulse_events': sum(by_timing['none'][i]['event_observed'] for i in below),
                'pulse_events': sum(by_timing['pulse'][i]['event_observed'] for i in below),
                'mean_restricted_latency_difference': float((on - off)[below].mean()) if below.size else None,
            },
        }
    return records, summaries


def geometry_diagnostics(arrays):
    records = []
    for timing in TIMINGS:
        positions = arrays[f'intact__{timing}__snapshot_pos']
        calls = arrays[f'intact__{timing}__snapshot_calling']
        for i, seed in enumerate(SEEDS):
            for j, step in enumerate(SNAPSHOTS):
                result = geometry_diagnostic(positions[i, j])
                records.append({'seed': seed, 'timing': timing, 'completed_steps': step,
                    'observed_instantaneous_call_fraction': float(calls[i, j].mean()), **result})
    summary = {}
    for timing in TIMINGS:
        summary[timing] = {}
        for step in SNAPSHOTS:
            rows = [r for r in records if r['timing'] == timing and r['completed_steps'] == step]
            summary[timing][str(step)] = {
                'classifications': dict(Counter(r['classification'] for r in rows)),
                'low_endpoint_mean_across_seeds': float(np.mean([r['low_mean'] for r in rows])),
                'high_endpoint_mean_across_seeds': float(np.mean([r['high_mean'] for r in rows])),
                'max_bracket_gap': max(r['max_gap'] for r in rows),
                'max_residual': max(max(r['low_residual'], r['high_residual']) for r in rows),
                'max_iterations': max(r['iterations'] for r in rows),
                'max_local_spectral_radius': max(max(r['low_spectral_radius'], r['high_spectral_radius']) for r in rows),
            }
    return records, summary


def write_csv(path, rows):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'results')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--v13-reference', type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be 1..16')
    args.output.mkdir(parents=True, exist_ok=True)
    source_paths = [ROOT / name for name in ('simulation.py', 'analysis.py', 'geometry.py', 'run_audit.py')]
    source_paths += [ROOT.parent / 'validation_fish_boids_v13' / 'simulation.py',
                     ROOT.parent / 'docs' / 'V14_ACOUSTIC_MAINTENANCE_PROTOCOL.md']
    source_hashes = capture_source_hashes(source_paths, ROOT.parent)
    arrays = execute(args.workers)
    invariants = verify_invariants(arrays)
    archived = compare_archived_v13(arrays, args.v13_reference) if args.v13_reference else None
    contrasts, cut_effects, factorial = summarize(arrays)
    arrivals, arrival_summary = arrival_diagnostics(arrays)
    geometry, geometry_summary = geometry_diagnostics(arrays)
    verify_source_hashes(source_hashes, ROOT.parent)
    trace_path = args.output / 'full_traces.npz'
    save_trace_archive(trace_path, arrays)
    receipt = {'file': trace_path.name, 'bytes': trace_path.stat().st_size,
               'sha256': hashlib.sha256(trace_path.read_bytes()).hexdigest(),
               'protocol_commit': PROTOCOL_COMMIT}
    result = {
        'status': 'SYNTHETIC_ONLY_NOT_FIELD_RESULT', 'version': 'v14_post_pulse_maintenance',
        'protocol_commit': PROTOCOL_COMMIT, 'predecessor_commit': PREDECESSOR_COMMIT,
        'fitted_to_fish_data': False, 'same_v13_seeds_followed_up': True,
        'seeds': list(SEEDS), 'individuals': N, 'steps': STEPS, 'dt': .06,
        'trajectories': 192, 'pulse': {'amplitude': .8, 'steps': [1000, 1040]},
        'post_pulse_cut_step': CUT, 'post_cut_weights': MECHANISMS,
        'time_units': 'arbitrary model time, not calibrated fish seconds',
        'bootstrap': {'replicates': 10000, 'seed': 20261122, 'unit': 'paired simulator seed',
                      'interval': 'percentile 95%, descriptive and unadjusted'},
        'v13_prefix_replay': {'matched': True, 'seed_pairs': 24, 'steps': 4000,
                              'metrics': ['call_fraction', 'hull_area', 'cue']},
        'archived_v13_comparison': archived, 'invariants': invariants,
        'contrasts': contrasts, 'cut_effect_on_pulse_contrast': cut_effects,
        'terminal_factorial_interaction': factorial,
        'arrival_summary': arrival_summary, 'geometry_summary': geometry_summary,
        'trace_receipt': receipt,
        'source_sha256': source_hashes,
        'source_hashes_captured_before_execution_and_verified_after': True,
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
    }
    rows = []
    for mechanism, windows in contrasts.items():
        for window, values in windows.items():
            for metric in ('call_fraction', 'hull_area'):
                for i, seed in enumerate(SEEDS):
                    s = values[metric]
                    rows.append({'mechanism': mechanism, 'window': window, 'start': values['steps'][0],
                        'end': values['steps'][1], 'metric': metric, 'seed': seed,
                        'no_pulse': s['per_seed_no_pulse'][i], 'pulse': s['per_seed_pulse'][i],
                        'difference': s['per_seed_difference'][i]})
    write_csv(args.output / 'per_seed_windows.csv', rows)
    write_csv(args.output / 'arrival_records.csv', arrivals)
    write_json(args.output / 'geometry_diagnostics.json', {
        'interpretation': 'Deterministic mean-probability closure at frozen geometry, not exact stochastic expectations',
        'records': geometry})
    write_json(args.output / 'trace_receipt.json', receipt)
    write_json(args.output / 'audit_result.json', result)
    summary = {k: v for k, v in result.items() if k not in ('contrasts', 'cut_effect_on_pulse_contrast')}
    summary['terminal'] = {m: result['contrasts'][m]['terminal'] for m in MECHANISMS}
    summary['terminal_cut_effect'] = {m: v['terminal'] for m, v in cut_effects.items()}
    summary['window_means'] = {m: {w: {metric: {k: values[metric][k] for k in
        ('no_pulse_mean', 'pulse_mean', 'mean_difference', 'bootstrap_95_interval')}
        for metric in ('call_fraction', 'hull_area')} for w, values in windows.items()}
        for m, windows in contrasts.items()}
    write_json(args.output / 'summary.json', summary)
    print(json.dumps({'status': result['status'], 'trace_receipt': receipt, 'source_sha256': source_hashes,
        'terminal': {m: {metric: {
        'difference': contrasts[m]['terminal'][metric]['mean_difference'],
        'interval': contrasts[m]['terminal'][metric]['bootstrap_95_interval']}
        for metric in ('call_fraction', 'hull_area')} for m in MECHANISMS},
        'arrival_threshold_0.9': arrival_summary['0.9'],
        'geometry': geometry_summary}, indent=2), flush=True)


if __name__ == '__main__':
    main()
