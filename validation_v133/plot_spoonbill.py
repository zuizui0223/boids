"""Scientific display of source-extracted contrasts, without pooling."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'results/spoonbill_tide_diel_contrasts.json').read_text())
stages = ['high tide', 'ebbing tide', 'low tide', 'rising tide']
rows = [next(r for r in data['day_night_feeding_effects']
             if r['conditioning'] == 'tidal_stage=' + stage) for stage in stages]
or_values = np.array([r['derived_odds_ratio'] for r in rows])
bounds = np.exp(np.array([r['derived_unadjusted_normal_95_log_interval'] for r in rows]))
interaction = data['ria_low_vs_high_diel_interaction']
ratio = interaction['ratio_of_day_night_odds_ratios']
envelope = interaction['rounding_sensitivity']['ratio_envelope']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.spines.left': False})
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 6.6), sharex=True,
                              gridspec_kw={'height_ratios': [3.2, 1.3]})
fig.subplots_adjust(left=.24, right=.94, top=.80, bottom=.19, hspace=.35)
fig.suptitle('Day–night feeding contrast varies with tidal stage', x=.06, y=.96, ha='left',
             fontsize=18, fontweight='bold')
fig.text(.06, .895, 'Eurasian spoonbill · Ria Formosa, Portugal · 25 juveniles · one study', fontsize=12)
y = np.arange(3, -1, -1)
ax.errorbar(or_values, y, xerr=np.vstack((or_values-bounds[:,0], bounds[:,1]-or_values)),
            fmt='o', markersize=8, capsize=4, color='#15697c', lw=2)
ax.set_yticks(y, ['High tide', 'Ebbing tide', 'Low tide', 'Rising tide'])
ax.set_ylim(-.55, 3.55)
for value, yy in zip(or_values, y):
    ax.text(1.19, yy, f'{value:.2f}', ha='right', va='center', fontweight='bold')
ax.set_title('Day / night odds ratio of ACC-classified feeding', loc='left', fontsize=12, pad=13)
ax2.errorbar([ratio], [0], xerr=[[ratio-envelope[0]], [envelope[1]-ratio]],
             fmt='D', markersize=8, color='#303846', lw=3, capsize=5)
ax2.set_yticks([0], ['Low / high ratio of\nday–night odds ratios'])
ax2.set_ylim(-.7, .7)
ax2.text(1.19, 0, f'{ratio:.3f}', ha='right', va='center', fontweight='bold')
ax2.set_title('Derived interaction: covariance and rounding sensitivity', loc='left', fontsize=11, pad=9)
for a in (ax, ax2):
    a.set_xscale('log')
    a.set_xlim(.2, 1.25)
    a.axvline(1, color='#7a8793', ls='--', lw=1)
    a.grid(axis='x', alpha=.18)
    a.tick_params(axis='y', length=0, pad=12)
ax2.set_xticks([.2, .3, .5, 1], ['0.2', '0.3', '0.5', '1.0'])
ax2.xaxis.set_minor_formatter(NullFormatter())
ax2.set_xlabel('Odds-ratio scale (log axis); values below 1 indicate a stronger nighttime bias', labelpad=9)
fig.text(.06, .09, 'Upper intervals: unadjusted normal approximations from printed SEs; not Tukey intervals.', fontsize=9, color='#485462')
fig.text(.06, .058, 'Lower interval: conservative envelope [0.266, 0.401]; exact contrast covariance unavailable.', fontsize=9, color='#485462')
fig.text(.06, .026, 'Source: Rodrigues et al. (2025), DOI 10.1007/s12237-025-01598-x, Table S8. No meta-analysis pooling.', fontsize=9, color='#485462')
out = ROOT / 'figures'
out.mkdir(exist_ok=True)
fig.savefig(out / 'spoonbill_tide_diel_effects.png', dpi=180, facecolor='white')
fig.savefig(out / 'spoonbill_tide_diel_effects.svg', facecolor='white')
svg = out / 'spoonbill_tide_diel_effects.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
