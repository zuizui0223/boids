"""Frozen independent-seed state-transplant audit; synthetic outcomes only."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import tempfile

import numpy as np
import scipy
from scipy.spatial import ConvexHull, QhullError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from validation_fish_boids_v15 import simulation as sim
from validation_fish_boids_v15.analysis import decompose_counts, bootstrap_indices, summarize, arrival_record
from validation_fish_boids_v14.simulation import simulate as reference_simulate

PROTOCOL_COMMIT = '3fcbdfc157ca362cad4560bf3b2400ec4ee7e7e0'
BASE_COMMIT = '7295d885b587d808cb74fbae11163819ed8cf22d'
SEEDS = np.arange(2000, 2096, dtype=np.int64)
N, SPLIT, HORIZON = 32, 1040, 6000
PRIMARY_WINDOW = (1040, 4040)
SOURCE_STEPS = np.array([1000, 1040], dtype=np.int64)
CONTINUATION_STEPS = np.array([1040, 1240, 4040, 6000], dtype=np.int64)
SOURCE_LABELS = ('source__none', 'source__pulse')
ARMS = tuple(f'intact__{mask:03b}' for mask in range(8)) + tuple(
    f'motor_cut__{mask:03b}' for mask in (0, 3, 4, 7))
FIELDS = ('call_fraction', 'hull_area', 'cue', 'snapshot_pos', 'snapshot_velocity', 'snapshot_calling')
WINDOWS = {'immediate': (1040, 1240), 'primary': PRIMARY_WINDOW, 'late': (5000, 6000)}
BOOTSTRAP = {'replicates': 10000, 'seed': 2026112205, 'unit': 'paired simulator seed',
             'interval': 'percentile95%, descriptive and unadjusted'}
SOURCE_FILES = (
    'docs/V15_STATE_TRANSPLANT_PROTOCOL.md',
    'validation_fish_boids_v14/simulation.py',
    'validation_fish_boids_v15/simulation.py',
    'validation_fish_boids_v15/analysis.py',
    'validation_fish_boids_v15/run_audit.py',
)


def _layout(label):
    if label in SOURCE_LABELS:
        cue = np.zeros(SPLIT)
        if label == 'source__pulse':
            cue[1000:1040] = .8
        return SPLIT, 0, SOURCE_STEPS, cue
    if label in ARMS:
        return HORIZON-SPLIT, SPLIT, CONTINUATION_STEPS, np.zeros(HORIZON-SPLIT)
    raise ValueError('Unknown source or continuation label')


def _shapes(length, n, k):
    return {'call_fraction': (length,), 'hull_area': (length,), 'cue': (length,),
            'snapshot_pos': (k, n, 2), 'snapshot_velocity': (k, n, 2),
            'snapshot_calling': (k, n)}


def validate_block(block, sample_count, n, snapshot_steps, offset, expected_cue):
    """Validate one worker segment before any assignment can broadcast it."""
    if not isinstance(block, dict) or set(block) != set(FIELDS):
        raise ValueError('Segment fields must match the exact trace schema')
    shapes = _shapes(sample_count, n, len(snapshot_steps))
    for field, shape in shapes.items():
        a = np.asarray(block[field])
        if a.shape != shape or a.dtype.kind != 'f' or a.dtype.itemsize != 8 or not np.isfinite(a).all():
            raise ValueError(f'Invalid shape, dtype, or finite values for {field}')
    calls = block['call_fraction']
    if np.any(calls < 0) or np.any(calls > 1) or not np.array_equal(calls*n, np.rint(calls*n)):
        raise ValueError('Call fractions must be realizable integer individual counts')
    if np.any(block['hull_area'] <= 0):
        raise ValueError('Hull areas must be positive')
    if not np.array_equal(block['cue'], expected_cue):
        raise ValueError('Playback cue differs from the fixed schedule')
    if not np.isin(block['snapshot_calling'], (0., 1.)).all():
        raise ValueError('Snapshot calling must be binary')
    for j, step in enumerate(snapshot_steps):
        pos = block['snapshot_pos'][j]
        try:
            area = float(ConvexHull(pos).volume)
        except QhullError as exc:
            raise ValueError('Snapshot hull is degenerate') from exc
        if not np.isfinite(area) or area <= 0:
            raise ValueError('Snapshot hull is not positive and finite')
        if step > offset:
            trace_index = int(step-offset-1)
            if not 0 <= trace_index < sample_count:
                raise ValueError('Snapshot lies outside its segment')
            if block['snapshot_calling'][j].mean() != calls[trace_index]:
                raise ValueError('Snapshot calling disagrees with the completed-step trace')
            if not np.isclose(area, block['hull_area'][trace_index], rtol=1e-12, atol=1e-12):
                raise ValueError('Snapshot hull disagrees with the completed-step trace')


def _validate_rng_text(value):
    if not isinstance(value, (str, np.str_)) or not value or len(value) > 512:
        raise ValueError('RNG state must be a nonempty JSON string of at most512 characters')
    try:
        state = json.loads(str(value))
        return sim._copy_rng_state(state)
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError('Invalid saved PCG64 state') from exc


def expected_rng_states(seed):
    """Independently bind saved streams to the original seed and update count."""
    rng = np.random.default_rng(int(seed))
    rng.normal(size=(N, 2))
    rng.uniform(-np.pi, np.pi, N)
    rng.binomial(1, .08, N)
    # Every model update uses exactly N double-precision uniforms. The legacy
    # initialization is performed literally before PCG64 jump-ahead is used.
    rng.bit_generator.advance(SPLIT * N)
    split = rng.bit_generator.state
    rng.bit_generator.advance((HORIZON - SPLIT) * N)
    return {'split_rng_state_json': split, 'end_rng_state_json': rng.bit_generator.state}


def _validate_rng_pair(values, seed):
    for key, expected in expected_rng_states(seed).items():
        if _validate_rng_text(values[key]) != expected:
            raise ValueError('Saved RNG state does not match its seed and completed-update count')


def allocate_arrays():
    arrays = {'seeds': SEEDS.copy(), 'source_snapshot_steps': SOURCE_STEPS.copy(),
              'continuation_snapshot_steps': CONTINUATION_STEPS.copy(),
              'continuation_offset': np.array(SPLIT, dtype=np.int64),
              'split_rng_state_json': np.full(len(SEEDS), '', dtype='U512'),
              'end_rng_state_json': np.full(len(SEEDS), '', dtype='U512')}
    for label in SOURCE_LABELS + ARMS:
        length, _, steps, _ = _layout(label)
        for field, shape in _shapes(length, N, len(steps)).items():
            arrays[label+'__'+field] = np.empty((len(SEEDS),)+shape, dtype=float)
    return arrays


def _validate_state_origins(blocks):
    a, b = blocks['source__none'], blocks['source__pulse']
    for field in ('call_fraction', 'hull_area', 'cue'):
        if not np.array_equal(a[field][:1000], b[field][:1000]):
            raise ValueError('Paired source prefixes differ before playback')
    for field in ('snapshot_pos', 'snapshot_velocity', 'snapshot_calling'):
        if not np.array_equal(a[field][0], b[field][0]):
            raise ValueError('Pre-playback source snapshots differ')
    for label in ARMS:
        mask = int(label.rsplit('__', 1)[1], 2)
        for bit, field in ((4, 'snapshot_pos'), (2, 'snapshot_velocity'), (1, 'snapshot_calling')):
            wanted = (b if mask & bit else a)[field][-1]
            if not np.array_equal(blocks[label][field][0], wanted):
                raise ValueError('Initial continuation snapshot has wrong component provenance')
    for mask in (0, 1, 4, 5):
        left = blocks[f'intact__{mask:03b}']['call_fraction'][0]
        right = blocks[f'intact__{mask+2:03b}']['call_fraction'][0]
        if left != right:
            raise ValueError('First resumed calling changed with velocity provenance alone')


def store_worker(arrays, index, worker):
    """Admit every worker field before mutating any destination array."""
    keys = {'seed', 'blocks', 'split_rng_state_json', 'end_rng_state_json', 'reference_matched'}
    if (not isinstance(worker, dict) or set(worker) != keys or worker['seed'] != int(SEEDS[index])
            or worker['reference_matched'] is not True
            or set(worker['blocks']) != set(SOURCE_LABELS+ARMS)):
        raise ValueError('Worker identity, reference replay, or block schema is invalid')
    for label in SOURCE_LABELS + ARMS:
        length, offset, steps, cue = _layout(label)
        validate_block(worker['blocks'][label], length, N, steps, offset, cue)
    _validate_rng_pair(worker, worker['seed'])
    _validate_state_origins(worker['blocks'])
    for label, block in worker['blocks'].items():
        for field, values in block.items():
            arrays[label+'__'+field][index] = values
    for key in ('split_rng_state_json', 'end_rng_state_json'):
        arrays[key][index] = worker[key]


def validate_arrays(arrays):
    """Admit the exact fixed experiment, not a shape-compatible other archive."""
    metadata = {'seeds', 'source_snapshot_steps', 'continuation_snapshot_steps',
                'continuation_offset', 'split_rng_state_json', 'end_rng_state_json'}
    expected = metadata | {label+'__'+field for label in SOURCE_LABELS+ARMS for field in FIELDS}
    if not isinstance(arrays, dict) or set(arrays) != expected:
        raise ValueError('Archive keys do not match the fixed experiment')
    for key, value in [('seeds', SEEDS), ('source_snapshot_steps', SOURCE_STEPS),
                       ('continuation_snapshot_steps', CONTINUATION_STEPS),
                       ('continuation_offset', np.array(SPLIT, dtype=np.int64))]:
        a = np.asarray(arrays[key])
        if not np.issubdtype(a.dtype, np.integer) or a.shape != value.shape or not np.array_equal(a, value):
            raise ValueError('Invalid seed, snapshot, or time-offset manifest')
    for label in SOURCE_LABELS + ARMS:
        length, _, steps, _ = _layout(label)
        for field, shape in _shapes(length, N, len(steps)).items():
            a = np.asarray(arrays[label+'__'+field])
            if a.shape != (len(SEEDS),)+shape:
                raise ValueError('Archive array has an incorrect exact shape')
    for key in ('split_rng_state_json', 'end_rng_state_json'):
        a = np.asarray(arrays[key])
        if a.shape != (len(SEEDS),) or a.dtype.kind != 'U':
            raise ValueError('Invalid RNG-state archive array')
    for i in range(len(SEEDS)):
        _validate_rng_pair({key: arrays[key][i] for key in
                            ('split_rng_state_json', 'end_rng_state_json')}, SEEDS[i])
        blocks = {}
        for label in SOURCE_LABELS + ARMS:
            block = {field: arrays[label+'__'+field][i] for field in FIELDS}
            length, offset, steps, cue = _layout(label)
            validate_block(block, length, N, steps, offset, cue)
            blocks[label] = block
        _validate_state_origins(blocks)
    return {'exact_schema': True, 'integer_call_counts': True, 'snapshot_consistency': True,
            'component_provenance': True, 'pre_pulse_pairing': True, 'first_call_V_invariance': True}


def capture_source_hashes(paths=None):
    paths = paths if paths is not None else {name: ROOT/name for name in SOURCE_FILES}
    return {name: hashlib.sha256(Path(path).read_bytes()).hexdigest() for name, path in paths.items()}


def verify_source_hashes(before, paths=None):
    try:
        after = capture_source_hashes(paths)
    except OSError as exc:
        raise RuntimeError('An execution source disappeared during calculation') from exc
    if before != after:
        raise RuntimeError('An execution source changed during calculation; refusing output')


def _rng_text(state):
    return json.dumps(state.rng_state, sort_keys=True, separators=(',', ':'))


def run_seed(seed):
    sources = {timing: sim.advance(sim.initialize(seed, N), SPLIT,
               pulse_start=1000 if timing == 'pulse' else None,
               snapshot_steps=SOURCE_STEPS) for timing in ('none', 'pulse')}
    none_state, pulse_state = (sources[t]['final_state'] for t in ('none', 'pulse'))
    if none_state.rng_state != pulse_state.rng_state:
        raise RuntimeError('Source random streams differ at the split')
    blocks = {'source__'+timing: {f: source[f] for f in FIELDS} for timing, source in sources.items()}
    endings = []
    for label in ARMS:
        mask = int(label.rsplit('__', 1)[1], 2)
        segment = sim.advance(sim.transplant(none_state, pulse_state, mask), HORIZON,
                    audio_weight=0. if label.startswith('motor_cut') else 5., heard_weight=3.,
                    snapshot_steps=CONTINUATION_STEPS)
        blocks[label] = {f: segment[f] for f in FIELDS}
        if not np.array_equal(segment['snapshot_steps'], CONTINUATION_STEPS):
            raise RuntimeError('Continuation omitted a prescribed snapshot')
        endings.append(_rng_text(segment['final_state']))
    if len(set(endings)) != 1:
        raise RuntimeError('Continuation random streams diverged')
    for timing, label in [('none', 'intact__000'), ('pulse', 'intact__111')]:
        ref = reference_simulate(seed, steps=HORIZON, pulse_start=1000 if timing == 'pulse' else None,
                                 snapshot_steps=(1000, 1040, 1240, 4040, 6000))
        source, post = blocks['source__'+timing], blocks[label]
        for field in ('call_fraction', 'hull_area', 'cue'):
            if not np.array_equal(np.concatenate((source[field], post[field])), ref[field]):
                raise RuntimeError(f'Exact v14 trace replay failed for seed{seed} {timing} {field}')
        for field in ('snapshot_pos', 'snapshot_velocity', 'snapshot_calling'):
            if (not np.array_equal(source[field], ref[field][:2])
                    or not np.array_equal(post[field], ref[field][1:])):
                raise RuntimeError(f'Exact v14 state replay failed for seed{seed} {timing} {field}')
    return {'seed': seed, 'blocks': blocks, 'split_rng_state_json': _rng_text(none_state),
            'end_rng_state_json': endings[0], 'reference_matched': True}


def _summarize(values, indices, seed_ids):
    s = summarize(values, indices)
    s['positive_concentration']['top_two_seeds'] = [int(seed_ids[i]) for i in s['positive_concentration']['top_two_indices']]
    return s


def _contrast_vectors(means):
    normal = means['intact__111'] - means['intact__000']
    insert = means['intact__100'] - means['intact__000']
    delete = means['intact__111'] - means['intact__011']
    cut_normal = means['motor_cut__111'] - means['motor_cut__000']
    cut_insert = means['motor_cut__100'] - means['motor_cut__000']
    cut_delete = means['motor_cut__111'] - means['motor_cut__011']
    return {'natural_history': normal, 'X_insertion_intact': insert, 'X_deletion_intact': delete,
            'natural_history_motor_cut': cut_normal, 'X_insertion_motor_cut': cut_insert,
            'X_deletion_motor_cut': cut_delete, 'motor_DID_total': cut_normal-normal,
            'motor_DID_X_insertion': cut_insert-insert, 'motor_DID_X_deletion': cut_delete-delete}


def analyze_arrays(arrays):
    """Pure fixed-statistic computation; callers first admit the complete archive."""
    baseline = arrays['source__none__call_fraction'][:, 800:1000].mean(axis=1)
    low = baseline < .90
    selections = {'all': np.arange(len(SEEDS)), 'baseline_low': np.flatnonzero(low)}
    boot = {cohort: bootstrap_indices(len(ix), BOOTSTRAP['replicates'], BOOTSTRAP['seed'])
            for cohort, ix in selections.items()}
    stats = {'cohorts': {name: {'n': len(ix), 'seeds': SEEDS[ix].tolist(), 'indices': ix.tolist()}
                        for name, ix in selections.items()}, 'windows': {}, 'arrivals': {}}
    window_rows, effect_rows, arrival_rows = [], [], []
    for window, (start, end) in WINDOWS.items():
        stats['windows'][window] = {'steps': [start, end], 'cohorts': {name: {} for name in selections}}
        for metric in ('call_fraction', 'hull_area'):
            if metric == 'call_fraction':
                denominator = N * (end-start)
                totals = {arm: (arrays[arm+'__'+metric][:, start-SPLIT:end-SPLIT] * N)
                          .astype(np.int64).sum(axis=1) for arm in ARMS}
                means = {arm: values / denominator for arm, values in totals.items()}
                vectors = {name: values / denominator for name, values in _contrast_vectors(totals).items()}
            else:
                means = {arm: arrays[arm+'__'+metric][:, start-SPLIT:end-SPLIT].mean(axis=1) for arm in ARMS}
                vectors = _contrast_vectors(means)
            if window == 'primary' and metric == 'call_fraction':
                full = decompose_counts(np.column_stack([totals[f'intact__{mask:03b}']
                                                          for mask in range(8)]), denominator)
            for arm in ARMS:
                window_rows.extend({'seed': int(seed), 'baseline_low': bool(low[i]), 'window': window,
                    'start': start, 'end': end, 'arm': arm, 'metric': metric, 'value': float(means[arm][i])}
                    for i, seed in enumerate(SEEDS))
            for cohort, ix in selections.items():
                summaries = {arm: _summarize(means[arm][ix], boot[cohort], SEEDS[ix]) for arm in ARMS}
                entry = {'arms': {arm: {k: summaries[arm][k] for k in ('n', 'mean', 'median', 'ci95')} for arm in ARMS},
                         'contrasts': {name: _summarize(v[ix], boot[cohort], SEEDS[ix]) for name, v in vectors.items()}}
                if window == 'primary' and metric == 'call_fraction':
                    errors = {kind: (float(np.max(np.abs((sum(full[kind].values())-full['total'])[ix])))
                                     if len(ix) else None)
                              for kind in ('mobius', 'shapley')}
                    if any(err is not None and err > 1e-12 for err in errors.values()):
                        raise RuntimeError('Factorial allocation closure failed')
                    entry['decomposition'] = {
                        kind: {name: _summarize(v[ix], boot[cohort], SEEDS[ix]) for name, v in full[kind].items()}
                        for kind in ('mobius', 'shapley')}
                    entry['decomposition'].update({
                        'shapley_X_minus_C': _summarize(full['shapley_X_minus_C'][ix], boot[cohort], SEEDS[ix]),
                        'max_mobius_closure_error': errors['mobius'], 'max_shapley_closure_error': errors['shapley']})
                    if cohort == 'all':
                        effects = {**vectors, **{'mobius_'+k: v for k, v in full['mobius'].items()},
                                   **{'shapley_'+k: v for k, v in full['shapley'].items()},
                                   'shapley_X_minus_C': full['shapley_X_minus_C']}
                        effect_rows.extend({'seed': int(seed), 'baseline_low': bool(low[i]), 'effect': name,
                                            'value': float(values[i])}
                                           for name, values in effects.items() for i, seed in enumerate(SEEDS))
                stats['windows'][window]['cohorts'][cohort][metric] = entry
    for threshold in (.80, .90, .95):
        records = {arm: [arrival_record(arrays[arm+'__call_fraction'][i], SPLIT, 200, threshold, N)
                         for i in range(len(SEEDS))] for arm in ARMS}
        stats['arrivals'][str(threshold)] = {'cohorts': {}}
        for arm in ARMS:
            arrival_rows.extend({'seed': int(seed), 'baseline_low': bool(low[i]), 'arm': arm,
                                 'threshold': threshold, **records[arm][i]} for i, seed in enumerate(SEEDS))
        latencies = {arm: np.array([r['restricted_latency'] for r in records[arm]], dtype=float) for arm in ARMS}
        for cohort, ix in selections.items():
            arms = {arm: {'n': len(ix), 'events': sum(records[arm][i]['event_observed'] for i in ix),
                          'censored': sum(records[arm][i]['censored'] for i in ix),
                          'mean_restricted_latency': float(latencies[arm][ix].mean()) if len(ix) else None}
                    for arm in ARMS}
            stats['arrivals'][str(threshold)]['cohorts'][cohort] = {'arms': arms,
                'natural_latency_contrast': _summarize((latencies['intact__111']-latencies['intact__000'])[ix],
                                                     boot[cohort], SEEDS[ix])}
    return stats, window_rows, effect_rows, arrival_rows


def save_arrays(path, arrays):
    validate_arrays(arrays)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            np.savez_compressed(f, **{key: arrays[key] for key in sorted(arrays)})
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return {'file': path.name, 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def _atomic_text(path, content):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _write_json(path, value):
    _atomic_text(path, json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def _write_csv(path, rows):
    import io
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    _atomic_text(path, out.getvalue())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent/'results')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error('--workers must be positive')
    sources = capture_source_hashes()
    arrays = allocate_arrays()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_seed, int(seed)): i for i, seed in enumerate(SEEDS)}
        for completed, future in enumerate(as_completed(futures), 1):
            store_worker(arrays, futures[future], future.result())
            if completed % 4 == 0:
                print(f'Completed {completed}/{len(SEEDS)} fixed seeds ({completed*len(ARMS)} continuations)', flush=True)
    validation = validate_arrays(arrays)
    stats, windows, effects, arrivals = analyze_arrays(arrays)
    verify_source_hashes(sources)
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = save_arrays(args.output/'full_traces.npz', arrays)
    result = {'version': 'v15_state_transplant', 'status': 'SYNTHETIC_ONLY_NOT_FIELD_RESULT',
              'protocol_commit': PROTOCOL_COMMIT, 'predecessor_commit': BASE_COMMIT,
              'seeds': SEEDS.tolist(), 'n': N, 'split_step': SPLIT, 'steps': HORIZON,
              'trajectories': len(SEEDS)*len(ARMS), 'source_histories': 2*len(SEEDS),
              'primary_window': list(PRIMARY_WINDOW), 'bootstrap': BOOTSTRAP,
              'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
              'source_sha256': sources, 'source_hashes_captured_before_execution_and_verified_after': True,
              'validations': {**validation, 'exact_v14_natural_seed_pairs': len(SEEDS),
                              'common_rng_at_split_and_end': True},
              'trace_receipt': receipt, **stats}
    for name in ('summary.json', 'audit_result.json'):
        _write_json(args.output/name, result)
    _write_json(args.output/'trace_receipt.json', receipt)
    _write_csv(args.output/'per_seed_windows.csv', windows)
    _write_csv(args.output/'per_seed_effects.csv', effects)
    _write_csv(args.output/'arrival_records.csv', arrivals)
    print(json.dumps({'status': result['status'], 'trace_receipt': receipt, 'source_sha256': sources,
                      'cohorts': stats['cohorts'], 'primary': stats['windows']['primary'],
                      'arrival_threshold_0.9': stats['arrivals']['0.9']}, indent=2, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
