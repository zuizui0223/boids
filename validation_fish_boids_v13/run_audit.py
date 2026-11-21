"""Replay v12 and execute the protocol-frozen v13 synthetic audit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import scipy

from analysis import interaction_contrast, paired_summary, window_mean
from simulation import simulate

ROOT = Path(__file__).resolve().parent
SEEDS = tuple(range(1000, 1024))
STEPS = 4000
MECHANISMS = {'full': (5., 3.), 'no_motor': (0., 3.),
              'no_hearing': (5., 0.), 'neither': (0., 0.)}
PROTOCOL_COMMIT = '2f57d64678c91e70f5bdfa3023184cf975de2a3b'


def replay_v12():
    reference = json.loads((ROOT / 'v12_reference.json').read_text())
    output = {}
    for key, metric, start, end in (
            ('call_postpulse', 'call_fraction', 130, 170),
            ('call_late', 'call_fraction', 240, 280),
            ('area_postpulse', 'hull_area', 130, 170),
            ('area_late', 'hull_area', 240, 280)):
        output[key] = []
    for seed in reference['seeds']:
        off = simulate(seed, steps=300, pulse_start=None)
        on = simulate(seed, steps=300, pulse_start=80)
        for key, metric, start, end in (
                ('call_postpulse', 'call_fraction', 130, 170),
                ('call_late', 'call_fraction', 240, 280),
                ('area_postpulse', 'hull_area', 130, 170),
                ('area_late', 'hull_area', 240, 280)):
            output[key].append(float(on[metric][start:end].mean() - off[metric][start:end].mean()))
    maximum_error = 0.
    for key, values in output.items():
        target = reference['differences'][key]['paired_difference_by_seed']
        error = float(np.max(np.abs(np.asarray(values) - target)))
        maximum_error = max(maximum_error, error)
        if error > 1e-10:
            raise AssertionError(f'v12 replay differs for {key}: {error}')
    return {'matched': True, 'max_abs_endpoint_error': maximum_error,
            'source_bundle_sha256': reference['source_bundle_sha256'],
            'source_json_sha256': reference['source_json_sha256'],
            'means': {key: float(np.mean(value)) for key, value in output.items()}}


def simulate_task(task):
    mechanism, timing, seed = task
    audio, heard = MECHANISMS[mechanism]
    pulse = {'none': None, 'early': 80, 'warmup': 1000}[timing]
    return task, simulate(seed, steps=STEPS, pulse_start=pulse,
                          audio_weight=audio, heard_weight=heard)


def execute(workers):
    tasks = [(mechanism, timing, seed)
             for mechanism in MECHANISMS
             for timing in ('none', 'warmup') for seed in SEEDS]
    tasks += [('full', 'early', seed) for seed in SEEDS]
    arrays = {}
    for mechanism, timing, _ in tasks:
        for metric in ('call_fraction', 'hull_area'):
            arrays.setdefault(f'{mechanism}__{timing}__{metric}', np.empty((len(SEEDS), STEPS)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(simulate_task, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), 1):
            (mechanism, timing, seed), trace = future.result()
            for metric in ('call_fraction', 'hull_area'):
                arrays[f'{mechanism}__{timing}__{metric}'][SEEDS.index(seed)] = trace[metric]
            if completed % 24 == 0:
                print(f'Completed {completed}/{len(tasks)} fixed trajectories', flush=True)
    validate_trace_arrays(arrays)
    return arrays


def validate_trace_arrays(arrays):
    expected = {f'{mechanism}__{timing}__{metric}'
                for mechanism in MECHANISMS
                for timing in ('none', 'warmup') + (('early',) if mechanism == 'full' else ())
                for metric in ('call_fraction', 'hull_area')}
    if set(arrays) != expected:
        raise ValueError('Trace keys do not match the fixed experiment')
    for key, values in arrays.items():
        a = np.asarray(values)
        if (a.shape != (len(SEEDS), STEPS) or a.dtype.kind not in 'fiu'
                or not np.isfinite(a).all()):
            raise ValueError(f'Invalid shape or values for {key}')
        if key.endswith('call_fraction') and (np.any(a < 0) or np.any(a > 1)):
            raise ValueError(f'Invalid call fractions for {key}')
        if key.endswith('hull_area') and np.any(a <= 0):
            raise ValueError(f'Nonpositive hull area for {key}')


def save_trace_archive(path, arrays):
    """Validate before writing; an interrupted write leaves the old file intact."""
    validate_trace_arrays(arrays)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.npz', delete=False) as stream:
            temporary = Path(stream.name)
            np.savez_compressed(stream, seeds=np.array(SEEDS), **arrays)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json(path, value):
    content = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def summarize(arrays):
    validate_trace_arrays(arrays)
    indices = np.random.default_rng(20261121).integers(0, len(SEEDS), (10000, len(SEEDS)))
    contrasts = {}
    pairs = [('full', 'early')] + [(mechanism, 'warmup') for mechanism in MECHANISMS]
    for mechanism, timing in pairs:
        start = 80 if timing == 'early' else 1000
        end = start + 40
        windows = {'pre': (max(0, start - 200), start), 'during': (start, end),
                   'immediate_post': (end + 10, end + 50),
                   'intermediate': (end + 120, end + 320),
                   'penultimate': (2000, 3000), 'terminal': (3000, 4000)}
        record = {'mechanism': mechanism, 'timing': timing, 'pulse_window': [start, end], 'windows': {}}
        for name, (a, b) in windows.items():
            record['windows'][name] = {'steps': [a, b]}
            for metric in ('call_fraction', 'hull_area'):
                off = window_mean(arrays[f'{mechanism}__none__{metric}'], a, b)
                on = window_mean(arrays[f'{mechanism}__{timing}__{metric}'], a, b)
                record['windows'][name][metric] = paired_summary(off, on, indices)
        contrasts[f'{mechanism}_{timing}'] = record
    interaction = {}
    for window in ('immediate_post', 'terminal'):
        interaction[window] = {}
        for metric in ('call_fraction', 'hull_area'):
            ds = [contrasts[f'{m}_warmup']['windows'][window][metric]['per_seed_difference'] for m in MECHANISMS]
            values = interaction_contrast(*ds)
            paired = paired_summary(np.zeros(len(SEEDS)), values, indices)
            interaction[window][metric] = {k: v for k, v in paired.items()
                if k not in ('no_pulse_mean', 'pulse_mean', 'per_seed_no_pulse', 'per_seed_pulse')}
    return contrasts, interaction


def write_seed_csv(path, contrasts):
    fields = ['contrast', 'window', 'start_step', 'end_step', 'metric', 'seed', 'no_pulse', 'pulse', 'difference']
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for name, contrast in contrasts.items():
            for window, values in contrast['windows'].items():
                for metric in ('call_fraction', 'hull_area'):
                    for i, seed in enumerate(SEEDS):
                        writer.writerow(dict(contrast=name, window=window,
                            start_step=values['steps'][0], end_step=values['steps'][1],
                            metric=metric, seed=seed,
                            no_pulse=values[metric]['per_seed_no_pulse'][i],
                            pulse=values[metric]['per_seed_pulse'][i],
                            difference=values[metric]['per_seed_difference'][i]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'results')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be 1..16')
    args.output.mkdir(parents=True, exist_ok=True)
    replay = replay_v12()
    print('Original v12 endpoint replay matched', flush=True)
    arrays = execute(args.workers)
    contrasts, interaction = summarize(arrays)
    from meanfield_audit import run_audit
    meanfield = run_audit()
    if not meanfield['checks']['all_sweep_points_converged']:
        raise ArithmeticError('Mean-field continuation failed to settle')
    trace_path = args.output / 'full_traces.npz'
    save_trace_archive(trace_path, arrays)
    receipt = {'file': trace_path.name, 'sha256': hashlib.sha256(trace_path.read_bytes()).hexdigest(),
               'bytes': trace_path.stat().st_size, 'protocol_commit': PROTOCOL_COMMIT}
    source_paths = list(ROOT.glob('*.py')) + [ROOT / 'v12_reference.json',
        ROOT.parent / 'validation_fish_boids_v12' / 'acoustic_feedback.py',
        ROOT.parent / 'docs' / 'V13_ACOUSTIC_FEEDBACK_AUDIT_PROTOCOL.md']
    result = {
        'status': 'SYNTHETIC_ONLY_NOT_FIELD_RESULT', 'version': 'v13_persistence_mechanism_audit',
        'protocol_commit': PROTOCOL_COMMIT, 'fitted_to_fish_data': False,
        'seed_unit': 'independent simulator initialization with paired random draws across arms',
        'seeds': list(SEEDS), 'n_individuals': 32, 'steps': STEPS, 'dt': .06,
        'time_units': 'arbitrary model time, not calibrated fish seconds',
        'trajectories': 216, 'mechanisms': MECHANISMS,
        'bootstrap': {'replicates': 10000, 'seed': 20261121, 'unit': 'paired seed',
                      'interval': 'percentile 95%; Monte Carlo uncertainty, no equivalence or biological test'},
        'v12_replay': replay, 'contrasts': contrasts, 'factorial_interaction': interaction,
        'trace_receipt': receipt,
        'meanfield': meanfield,
        'source_sha256': {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(source_paths)},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
    }
    csv_temporary = args.output / 'per_seed_windows.csv.tmp'
    write_seed_csv(csv_temporary, contrasts)
    csv_temporary.replace(args.output / 'per_seed_windows.csv')
    write_json(args.output / 'trace_receipt.json', receipt)
    write_json(args.output / 'audit_result.json', result)
    print(json.dumps({'status': result['status'], 'terminal': {
        k: {m: {'difference': v['windows']['terminal'][m]['mean_difference'],
                 'interval': v['windows']['terminal'][m]['bootstrap_95_interval']}
             for m in ('call_fraction', 'hull_area')} for k, v in contrasts.items()}}, indent=2))


if __name__ == '__main__':
    main()
