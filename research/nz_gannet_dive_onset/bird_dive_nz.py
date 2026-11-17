"""Recalculate the Fig 1 comparison from the 37 curve transcriptions.

Source: https://doi.org/10.1111/j.1748-7692.2009.00317.x
Arrows identify the start of a two-minute interval containing first diving.
Time is snapped to nominal readings only if within 0.12 min (plot resolution).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

folder = Path(__file__).resolve().parent
# x coordinate of each arrow on the enlarged author figure crops.
arrows = dict(A6=116, A10=1040, C4=810, D5=1047, D6=178, D8=569, D9=943)
panels = pd.read_csv(folder / 'depth_nz_figure1.csv')
rows = []
curves = {}


def window(segs, start, end):
    for t, z in segs:
        if t[0] <= start and t[-1] >= end:
            x = np.r_[start, t[(start < t) & (t < end)], end]
            d = np.interp(x, t, z)
            values = {'start_depth_m': d[0], 'end_depth_m': d[-1],
                      'mean_depth_m': sum(np.diff(x) * (d[:-1] + d[1:]) / 2) / (end - start)}
            for cutoff in (3, 4, 5, 6, 8, 10):
                duration = 0.
                for dt, a, b in zip(np.diff(x), d[:-1], d[1:]):
                    if max(a,b) <= cutoff:
                        duration += dt
                    elif min(a,b) < cutoff:
                        duration += dt * (cutoff - min(a,b)) / abs(b-a)
                values[f'within_{cutoff}m_seconds'] = 60 * duration
            return values
    return {}


for panel in panels.itertuples():
    row = {'panel': panel.panel, 'trajectory_class': panel.panel[0], 'marked': panel.panel in arrows}
    if row['marked']:
        segments = []
        for piece in panel.trace_xy.split('|'):
            xy = np.array([pair.split(':') for pair in piece.split()], dtype=float)
            t = (xy[:, 0] - arrows[panel.panel]) * 5 / panel.pixels_per_5min
            nominal = np.rint(t / 2) * 2
            t = np.where(abs(t - nominal) < 0.12, nominal, t)
            z = (xy[:, 1] - panel.axis_top) * 20 / (panel.axis_bottom - panel.axis_top)
            segments.append((t, z))
        curves[panel.panel] = segments
        for name, lo, hi in [('before', -2, 0), ('onset_bin', 0, 2)]:
            w = window(segments, lo, hi)
            row[name + '_covered'] = bool(w)
            row.update({name + '_' + key: value for key, value in w.items()})
    rows.append(row)
data = pd.DataFrame(rows)
assert len(data) == 37 and data.marked.sum() == 7
paired = data.dropna(subset=['before_end_depth_m', 'onset_bin_end_depth_m'])
assert paired.panel.tolist() == ['D9']
data.to_csv(folder / 'bird_dive_nz_all37.csv', index=False)
print(data[data.marked][['panel','before_covered','onset_bin_covered',
                         'onset_bin_start_depth_m','onset_bin_end_depth_m']].to_string(index=False))
print(paired.filter(regex='panel|mean_depth|within_[45]m').to_string(index=False))

# Descriptive pseudo-onsets in unmarked schools: first 2-min sampling boundary
# with the entire preceding curve in the shallow band and a recorded next bin.
# An unmarked school may still have occasional dives. Do not treat as no-attack.
reference = []
for panel in panels[~panels.panel.isin(arrows)].itertuples():
    pieces = [np.array([v.split(':') for v in s.split()], float) for s in panel.trace_xy.split('|')]
    segments = []
    for xy in pieces:
        t = (xy[:,0] - pieces[0][0,0]) * 5 / panel.pixels_per_5min
        nominal = np.rint(t / 2) * 2
        t = np.where(abs(t - nominal) < .12, nominal, t)
        segments.append((t, (xy[:,1]-panel.axis_top) * 20 / (panel.axis_bottom-panel.axis_top)))
    for band in (1, 2, 3):
        for t in np.arange(2, segments[-1][0][-1], 2):
            pre = window(segments, t-2, t)
            post = window(segments, t, t+2)
            if not pre or not post:
                continue
            pre_curve = next((x, z) for x, z in segments if x[0] <= t-2 and x[-1] >= t)
            x, z = pre_curve
            interior = z[(x > t-2) & (x < t)]
            if max([pre['start_depth_m'], pre['end_depth_m'], *interior]) > band:
                continue
            reference.append((panel.panel, band, t, post['end_depth_m'] - post['start_depth_m'],
                              post['within_4m_seconds'] - pre['within_4m_seconds']))
            break
ref = pd.DataFrame(reference, columns=['panel','pre_band_m','pseudo_onset_min',
                                       'next_depth_change_m','change_within_4m_s'])
ref.to_csv(folder / 'bird_dive_nz_reference.csv',index=False)
print(ref.groupby('pre_band_m').agg({'panel':'count','change_within_4m_s':['min','max']}))

fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True, layout='constrained')
for ax, panel_id in zip(axes, ['D6', 'D9']):
    ax.axvspan(0, 2, color='#fae3cc', label='First dive falls in this interval')
    ax.axhspan(0, 4, color='#d4e8ed', alpha=.68)
    ax.axhline(4, color='#508893', linestyle='--', linewidth=1)
    for t, z in curves[panel_id]:
        ax.plot(t, z, '.-', color='#213e51', linewidth=1.8)
    ax.set(title=f'School {panel_id}', xlabel='Minutes from marked interval start', ylim=(12, -.6))
    ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('School centre depth (m)')
axes[1].legend(fontsize=8, loc='lower left')
fig.savefig(folder / 'bird_dive_nz_windows.png', dpi=180)
