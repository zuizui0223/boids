"""Original observations and conservative spatial/temporal current joins."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import Delaunay

ORIGIN = pd.Timestamp('2019-11-22T01:00:00Z').timestamp()
SHIFTS = (-24, -18, -12, -6, 0, 6, 12, 18, 24)
CLOCKS = (-3, 0, 3)
ORIGINALS = {
    'Penguins.csv': {'bytes': 336457626, 'md5': '35096032cf31d99d4de59adbad047f1c',
                     'sha256': '567c1c41b98f358d0421f7804d9869f2bcf60210fe6300c763ea562a5ba79706',
                     'url': 'https://ndownloader.figshare.com/files/52709456'},
    'Ocean_Currents.csv': {'bytes': 595255770, 'md5': '821597f7a6e0b73cec090f61daac604f',
                         'sha256': '202770385d4aba6ca1fb7335d10281f6805ae01748ff09fd57c4053207e96e69',
                         'url': 'https://ndownloader.figshare.com/files/52709309'},
}


def verify_source(path: Path) -> dict:
    expected = ORIGINALS[path.name]
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            md5.update(block); sha.update(block)
    actual = {'bytes': path.stat().st_size, 'md5': md5.hexdigest(), 'sha256': sha.hexdigest()}
    if any(actual[k] != expected[k] for k in actual):
        raise ValueError(f'ORIGINAL_SOURCE_HASH_MISMATCH: {path.name}')
    return {**expected, 'verified_locally': True}


def aggregate_observations(frame: pd.DataFrame, minimum_seconds=720):
    """Aggregate only unique, finite, actually observed original seconds."""
    original_n = len(frame)
    unique = frame.drop_duplicates().copy()
    removed = original_n - len(unique)
    timestamps = pd.to_datetime(unique.Timestamp, format='mixed', utc=True, errors='raise')
    unique['second'] = timestamps.astype('int64') // 10**9
    if unique.duplicated(['ID', 'second']).any():
        raise ValueError('CONFLICTING_ID_TIMESTAMP_DUPLICATES')
    first = unique.groupby('ID', observed=True).second.min()
    valid = np.isfinite(unique[['Depth_sm', 'DR_longitude', 'DR_latitude']].to_numpy()).all(axis=1)
    invalid_n = int((~valid).sum())
    unique = unique.loc[valid, ['ID', 'second', 'Depth_sm', 'DR_longitude', 'DR_latitude']].copy()
    unique['window_start_seconds'] = (unique.second // 900) * 900
    unique['elapsed_hours'] = (unique.second - unique.ID.map(first)) / 3600
    for threshold in (1, 2, 5):
        unique[f'depth_gt_{threshold}'] = unique.Depth_sm > threshold
    grouped = unique.groupby(['ID', 'window_start_seconds'], observed=True, sort=True)
    windows = grouped.agg(n_seconds=('second', 'size'), time_seconds=('second', 'mean'),
                          longitude=('DR_longitude', 'mean'), latitude=('DR_latitude', 'mean'),
                          longitude_min=('DR_longitude', 'min'), longitude_max=('DR_longitude', 'max'),
                          latitude_min=('DR_latitude', 'min'), latitude_max=('DR_latitude', 'max'),
                          elapsed_hours=('elapsed_hours', 'mean'),
                          depth_gt_1=('depth_gt_1', 'sum'), depth_gt_2=('depth_gt_2', 'sum'),
                          depth_gt_5=('depth_gt_5', 'sum')).reset_index()
    if (windows.n_seconds > 900).any():
        raise ValueError('MORE_THAN_900_UNIQUE_SECONDS_IN_15_MINUTES')
    audit = {'original_rows': original_n, 'exact_duplicate_rows_removed': removed,
             'unique_rows_before_missingness': original_n - removed,
             'nonfinite_required_rows_excluded': invalid_n,
             'unique_observed_seconds': int(windows.n_seconds.sum()),
             'observed_windows': len(windows), 'empty_windows_inserted': 0,
             'minimum_observed_seconds': minimum_seconds,
             'low_coverage_windows_excluded': int((windows.n_seconds < minimum_seconds).sum())}
    windows = windows.loc[windows.n_seconds >= minimum_seconds].reset_index(drop=True)
    windows['ID'] = windows.ID.astype(str)
    audit.update(eligible_windows=len(windows), eligible_animals=windows.ID.nunique(),
                 eligible_observed_seconds=int(windows.n_seconds.sum()))
    return windows, audit


class CurrentGrid:
    def __init__(self, coordinates, uv, origin_seconds=ORIGIN):
        self.coordinates = np.asarray(coordinates, dtype=float)
        self.uv = np.asarray(uv, dtype=float)
        if self.uv.shape[0] != len(self.coordinates) or self.uv.shape[2] != 2 or not np.isfinite(self.uv).all():
            raise ValueError('INVALID_CURRENT_GRID')
        self.origin = float(origin_seconds)
        self.triangulation = Delaunay(self.coordinates)
        self.static_zero = np.all(self.uv == 0, axis=(1, 2))

    def sample(self, locations, seconds, mode='linear', exclude_static_zero=True):
        locations = np.asarray(locations, dtype=float)
        hours = (np.asarray(seconds, dtype=float) - self.origin) / 3600
        simplex = self.triangulation.find_simplex(locations)
        safe_simplex = np.maximum(simplex, 0)
        transform = self.triangulation.transform[safe_simplex]
        first_weights = np.einsum('nij,nj->ni', transform[:, :2], locations - transform[:, 2])
        weights = np.column_stack([first_weights, 1 - first_weights.sum(axis=1)])
        vertices = self.triangulation.simplices[safe_simplex]
        zero_count = self.static_zero[vertices].sum(axis=1)
        valid = (simplex >= 0) & np.isfinite(hours) & (hours >= 0) & (hours <= self.uv.shape[1] - 1)
        if exclude_static_zero:
            valid &= zero_count == 0
        safe_hours = np.clip(np.nan_to_num(hours), 0, self.uv.shape[1] - 1)
        if mode == 'linear':
            low = np.floor(safe_hours).astype(int)
            high = np.minimum(low + 1, self.uv.shape[1] - 1)
            fraction = safe_hours - low
        elif mode in ('floor', 'nearest'):
            low = np.floor(safe_hours + (.5 if mode == 'nearest' else 0)).astype(int)
            high, fraction = low, np.zeros_like(safe_hours)
        else:
            raise ValueError('UNKNOWN_TIME_INTERPOLATION')
        left = np.einsum('ni,nij->nj', weights, self.uv[vertices, low[:, None]])
        right = np.einsum('ni,nij->nj', weights, self.uv[vertices, high[:, None]])
        velocity = left * (1 - fraction[:, None]) + right * fraction[:, None]
        speed = np.hypot(velocity[:, 0], velocity[:, 1])
        speed[~valid] = np.nan
        zero_count = np.where(simplex >= 0, zero_count, -1)
        return speed, valid, zero_count


def read_current_grid(path: Path):
    coordinates, velocities = [], []
    for frame in pd.read_csv(path, chunksize=240000):
        if len(frame) % 240:
            raise ValueError('INCOMPLETE_CURRENT_GRID_NODE')
        n = len(frame) // 240
        hours = frame.Hours.to_numpy().reshape(n, 240)
        if not np.array_equal(hours, np.broadcast_to(np.arange(240), hours.shape)):
            raise ValueError('INVALID_CURRENT_HOUR_ORDER')
        for time_column in ('Time', 'TS'):
            seconds = pd.to_datetime(frame[time_column], format='mixed', utc=True).astype('int64').to_numpy() // 10**9
            if not np.array_equal(seconds, ORIGIN + hours.ravel() * 3600):
                raise ValueError('CURRENT_TIME_ORIGIN_MISMATCH')
        xy = frame[['Lon', 'Lat']].to_numpy().reshape(n, 240, 2)
        if not np.all(xy == xy[:, :1]):
            raise ValueError('CHANGING_CURRENT_NODE_COORDINATES')
        coordinates.append(xy[:, 0])
        velocities.append(frame[['U_comp', 'V_comp']].to_numpy().reshape(n, 240, 2))
    coords, uv = np.concatenate(coordinates), np.concatenate(velocities)
    if len(np.unique(coords, axis=0)) != len(coords):
        raise ValueError('DUPLICATE_CURRENT_NODES')
    return CurrentGrid(coords, uv)


def speed_column(clock, shift, mode='linear'):
    return f'speed_clock{clock}_shift{shift}_{mode}'


def join_windows(windows: pd.DataFrame, grid: CurrentGrid):
    """Keep every planned clock on the same temporal/spatial support."""
    result = windows.copy()
    locations = result[['longitude', 'latitude']].to_numpy()
    common = np.ones(len(result), dtype=bool)
    columns = {}
    zero = None
    for clock in CLOCKS:
        for shift in SHIFTS:
            for mode in ('linear', 'floor', 'nearest'):
                speed, valid, zero = grid.sample(locations, result.time_seconds.to_numpy() + (clock + shift) * 3600,
                                                 mode=mode, exclude_static_zero=False)
                common &= valid
                columns[speed_column(clock, shift, mode)] = speed
    result = pd.concat([result, pd.DataFrame(columns, index=result.index)], axis=1)
    result['static_zero_vertices'] = zero
    result['common_support'] = common
    return result, {
        'current_grid_nodes': len(grid.coordinates), 'current_hours': grid.uv.shape[1],
        'static_all_hour_zero_nodes': int(grid.static_zero.sum()),
        'candidate_windows': len(result), 'outside_common_support': int((~common).sum()),
        'common_support_windows': int(common.sum()),
        'common_support_touching_static_zero_node': int((common & (zero > 0)).sum()),
        'conservative_primary_windows': int((common & (zero == 0)).sum()),
        'ghost_offsets_hours': list(SHIFTS), 'clock_sensitivities_hours': list(CLOCKS),
        'matched_clocks_are_not_independent_studies': True,
    }
