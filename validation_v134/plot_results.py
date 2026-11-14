"""Render the reviewed exploratory comparison without a pooled-effect graphic."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    directory = Path(__file__).resolve().parent
    result = json.loads((directory / 'results/penguin_analysis_results.json').read_text())
    primary = result['scenarios'][0]
    scores = primary['scores']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.spines.left': False, 'axes.edgecolor': '#bec5ce',
                         'axes.labelcolor': '#243247', 'xtick.color': '#44536a',
                         'ytick.color': '#243247', 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1, 2, figsize=(15.2, 8.7), gridspec_kw={'width_ratios': [1.08, 1]})
    fig.patch.set_facecolor('white')
    navy, blue, teal, orange = '#182c48', '#6b85a3', '#087e8b', '#b8642d'
    configurations = [
        ('Constant 0.5 (diagnostic)', 'diagnostic_constant_half'),
        ('Training prevalence (diagnostic)', 'diagnostic_training_prevalence'),
        ('M0: clock + animal + space', 'M0'), ('M1: M0 + solar', 'M1'),
        ('M2: actual current', 'current_+0h'),
    ] + [(f'Shifted current: {shift:+d} h', f'current_{shift:+d}h') for shift in (-24, -18, -12, -6, 6, 12, 18, 24)]
    ax = axes[0]
    for y, (label, key) in enumerate(configurations):
        value = scores[key]['cross_entropy']
        color = teal if key == 'current_+0h' else orange if key.startswith('diagnostic') else blue
        ax.scatter(value, y, color=color, s=72 if key == 'current_+0h' else 44,
                   marker='D' if key == 'current_+0h' else 'o', zorder=3)
        ax.text(value + .0022, y, f'{value:.4f}', va='center', fontsize=9, color=color)
    ax.set_yticks(np.arange(len(configurations)), [x[0] for x in configurations])
    ax.invert_yaxis()
    ax.set_xlim(.68, .827)
    ax.set_xticks([.69, .72, .75, .78, .81])
    ax.grid(axis='x', color='#e4e9ef', linewidth=.7)
    ax.set_xlabel('Held-out fractional cross-entropy (nats)\nLower is better', labelpad=13)
    ax.set_title('A  Primary held-out losses', loc='left', fontweight='bold', fontsize=11, pad=18)
    ax.tick_params(axis='y', length=0, pad=10)
    ax.axhline(1.5, color='#d7dee7', lw=1)
    ax.axhline(4.5, color='#d7dee7', lw=1)

    labels = {'primary': 'Primary: depth > 2 m', 'threshold_1m': 'Depth > 1 m',
              'threshold_5m': 'Depth > 5 m', 'clock_minus3h': 'Animal clock -3 h',
              'clock_plus3h': 'Animal clock +3 h', 'nearest_hour': 'Nearest model hour',
              'floor_hour': 'Floored model hour', 'retain_original_zero_nodes': 'Retain original zero nodes',
              'ridge_0.001': 'Ridge penalty 0.001', 'ridge_0.1': 'Ridge penalty 0.1'}
    ax = axes[1]
    for y, scenario in enumerate(result['scenarios']):
        ax.scatter(scenario['delta_current'], y - .13, s=48, marker='o', color=blue,
                   label='Current versus M1' if y == 0 else None, zorder=3)
        ax.scatter(scenario['delta_phase'], y + .13, s=48, marker='D', color=teal,
                   label='Real versus best shifted current' if y == 0 else None, zorder=3)
    ax.axvline(0, color=navy, lw=1)
    ax.set_xlim(-.022, .08)
    ax.set_yticks(np.arange(10), [labels[x['scenario']] for x in result['scenarios']])
    ax.invert_yaxis()
    ax.set_xticks([-.02, 0, .02, .04, .06, .08])
    ax.grid(axis='x', color='#e4e9ef', linewidth=.7)
    ax.set_xlabel('Loss reduction (nats)\nPositive favors the real-current model', labelpad=13)
    ax.set_title('B  Prespecified sensitivities', loc='left', fontweight='bold', fontsize=11, pad=18)
    ax.tick_params(axis='y', length=0, pad=8)
    handles, legend_labels = ax.get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc='upper right', bbox_to_anchor=(.975, .935), frameon=False, fontsize=9)

    fig.suptitle('An exploratory current–diel test does not establish tide specificity',
                 x=.04, y=.975, ha='left', color=navy, fontsize=18, fontweight='bold')
    fig.text(.04, .925, '27 Magellanic penguins  |  1 colony/coast  |  2 held-out calendar weeks  |  3,334 primary 15-minute bins',
             color='#546278', fontsize=11)
    fig.text(.04, .06,
             'Scores average animals within weeks, then weeks. Points are settings/models, not independent studies or confidence intervals.\n'
             'The original naive animal clock is interpreted using author metadata. Scalar-speed controls shifted by ±6 h correlate ≈0.991 with real speed.\n'
             'Failure to distinguish these similar clocks does not imply absence of tidal influence. The eight-week confirmatory gate is unmet.',
             color='#46546a', fontsize=10, linespacing=1.6)
    fig.text(.04, .016, 'Source: Gunner et al. (2025), DOI 10.1371/journal.pbio.3002981; Figshare v1. Boids v134 prefit exploratory reanalysis.',
             color='#657186', fontsize=9)
    fig.subplots_adjust(left=.225, right=.97, top=.825, bottom=.255, wspace=.88)
    output = directory / 'figures'
    output.mkdir(exist_ok=True)
    for extension in ('png', 'svg'):
        fig.savefig(output / f'penguin_current_diel_validation.{extension}', dpi=180, facecolor='white')
    svg = output / 'penguin_current_diel_validation.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)


if __name__ == '__main__':
    main()
