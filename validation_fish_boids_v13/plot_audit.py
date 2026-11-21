"""Render scientific figures directly from saved v13 arrays and summaries."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, default=Path(__file__).parent / 'results')
    args = parser.parse_args()
    result = json.loads((args.results / 'audit_result.json').read_text())
    target = args.results / 'figures'
    target.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.titleweight': 'bold', 'savefig.facecolor': 'white'})
    colors = {'none': '#34495E', 'early': '#D55E00', 'warmup': '#0072B2'}
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.7))
    with np.load(args.results / 'full_traces.npz', allow_pickle=False) as data:
        for ax, metric, ylabel, title in (
                (axes[0, 0], 'call_fraction', 'Fraction calling', 'A  Full mechanism: calling'),
                (axes[0, 1], 'hull_area', 'Convex-hull area (arbitrary units²)', 'B  Full mechanism: group area')):
            for timing, label in [('none', 'No pulse'), ('early', 'Early pulse'), ('warmup', 'Pulse after warmup')]:
                values = data[f'full__{timing}__{metric}'].mean(0)
                # Non-overlapping 20-step means; every input point contributes once.
                y = values.reshape(-1, 20).mean(1)
                x = (np.arange(y.size) * 20 + 10) * result['dt']
                ax.plot(x, y, label=label, color=colors[timing], lw=1.8)
            ax.axvspan(80 * .06, 120 * .06, color=colors['early'], alpha=.12)
            ax.axvspan(1000 * .06, 1040 * .06, color=colors['warmup'], alpha=.12)
            ax.axvspan(3000 * .06, 4000 * .06, color='#7F8C8D', alpha=.08)
            ax.set(xlabel='Model time (arbitrary; not fish seconds)', ylabel=ylabel, title=title)
            ax.grid(alpha=.18)
            ax.set_xlim(0, 240)
            if metric == 'call_fraction':
                ax.set_ylim(-.02, 1.02)
                ax.legend(loc='lower right', frameon=False, fontsize=9)
    rows = [('full_early', 'Full / early pulse'), ('full_warmup', 'Full / warmup pulse'),
            ('no_motor_warmup', 'No acoustic steering'), ('no_hearing_warmup', 'No hearing → calling'),
            ('neither_warmup', 'Neither acoustic link')]
    for ax, metric, title, xlabel in (
            (axes[1, 0], 'call_fraction', 'C  Terminal calling contrast', 'Pulse − no pulse (fraction)'),
            (axes[1, 1], 'hull_area', 'D  Terminal area contrast', 'Pulse − no pulse (area units²)')):
        for y, (key, _) in enumerate(rows):
            item = result['contrasts'][key]['windows']['terminal'][metric]
            mean = item['mean_difference']
            lo, hi = item['bootstrap_95_interval']
            ax.hlines(y, lo, hi, color='#0072B2', lw=2)
            ax.plot(mean, y, 'o', color='#0072B2', ms=5)
        ax.axvline(0, color='#555555', lw=.9, ls='--')
        ax.set_yticks(range(len(rows)), [r[1] for r in rows])
        ax.invert_yaxis()
        ax.set(xlabel=xlabel, title=title)
        ax.grid(axis='x', alpha=.18)
    fig.suptitle('Acoustic Boids v13  |  Persistence and mechanism audit', fontsize=17, fontweight='bold', x=.04, ha='left')
    fig.text(.04, .925, 'SYNTHETIC ONLY • 24 matched seeds • unchanged v12 equations • 4,000 steps', fontsize=11, color='#555555')
    fig.text(.04, .025, 'Top: seed means in 20-step bins; shaded pulses and terminal window (steps 3000–3999). All ablations use the warmup pulse.\nBottom: paired mean differences and 95% bootstrap intervals over simulator seeds; no animal-population inference.', fontsize=9, color='#555555')
    fig.tight_layout(rect=[.02, .07, .99, .90], h_pad=2.8, w_pad=3.2)
    for extension in ('png', 'pdf'):
        fig.savefig(target / f'persistence_audit.{extension}', dpi=220)
    plt.close(fig)

    terminal = result['contrasts']['full_warmup']['windows']['terminal']['call_fraction']
    seeds = np.asarray(result['seeds'])
    differences = np.asarray(terminal['per_seed_difference'])
    no_pulse = np.asarray(terminal['per_seed_no_pulse'])
    pulse = np.asarray(terminal['per_seed_pulse'])
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 6.8))
    y = np.arange(len(seeds))
    axes[0].hlines(y, 0, differences, color='#0072B2', lw=1.5)
    axes[0].scatter(differences, y, color='#0072B2', s=22)
    axes[0].set_yticks(y, seeds, fontsize=8)
    axes[0].invert_yaxis()
    axes[0].axvline(0, color='#555555', lw=.8)
    axes[0].set(title='A  Every paired seed', xlabel='Terminal pulse − no-pulse call fraction', ylabel='Simulator seed')
    axes[1].plot([0, 1], [0, 1], ls='--', color='#777777', lw=1, label='Equal terminal calling')
    axes[1].scatter(no_pulse, pulse, s=38, color='#0072B2', alpha=.7)
    for i in np.argsort(differences)[-2:]:
        axes[1].annotate(str(seeds[i]), (no_pulse[i], pulse[i]), xytext=(8, -20),
                         textcoords='offset points', fontsize=10)
    axes[1].set(title='B  Terminal levels in the two arms', xlabel='No-pulse call fraction',
                ylabel='Warmup-pulse call fraction', xlim=(-.03, 1.05), ylim=(-.03, 1.05))
    axes[1].set_aspect('equal', adjustable='box')
    for ax in axes:
        ax.grid(alpha=.15)
    fig.suptitle('Delayed-pulse average is concentrated in a few trajectories', fontsize=14, fontweight='bold')
    fig.text(.06, .025, 'SYNTHETIC ONLY • Full mechanism • 24 paired seeds • Terminal average over steps 3000–3999\nAll seed outcomes shown; individual points are simulator replicates, not fish or independent biological groups.', fontsize=9, color='#555555')
    fig.tight_layout(rect=[.02, .10, .99, .92], w_pad=3)
    for extension in ('png', 'pdf'):
        fig.savefig(target / f'terminal_seed_heterogeneity.{extension}', dpi=220)
    plt.close(fig)

    from meanfield_audit import equilibria, stability
    mf = result['meanfield']
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.1))
    ax = axes[0]
    theta = np.linspace(-4.5, -1.5, 401)
    stable_t, stable_p, unstable_t, unstable_p = [], [], [], []
    for h in theta:
        for p in equilibria(6., float(h)):
            if stability(p)['classification'] == 'stable':
                stable_t.append(h); stable_p.append(p)
            else:
                unstable_t.append(h); unstable_p.append(p)
    ax.scatter(stable_t, stable_p, s=5, color='#0072B2', label='Stable equilibria')
    ax.scatter(unstable_t, unstable_p, s=5, color='#888888', label='Unstable equilibria')
    ax.set(title='A  Exact equilibrium structure', xlabel='Baseline calling intercept θ', ylabel='Equilibrium call probability p')
    ax.legend(frameon=False, loc='upper left', fontsize=9)
    ax = axes[1]
    for name, label, color in [('increasing', 'Increasing θ', '#D55E00'), ('decreasing', 'Decreasing θ', '#0072B2')]:
        points = mf['sweeps'][name]
        ax.plot([x['theta'] for x in points], [x['p'] for x in points], label=label, color=color, lw=2)
    ax.set(title='B  Converged two-state continuation', xlabel='Baseline calling intercept θ', ylabel='Settled call probability p')
    ax.legend(frameon=False, loc='upper left', fontsize=9)
    for ax in axes:
        for bound in (mf['folds']['h_lower'], mf['folds']['h_upper']):
            ax.axvline(bound, color='#555555', ls='--', lw=.8)
        ax.set(xlim=(-4.5, -1.5), ylim=(-.02, 1.02))
        ax.grid(alpha=.15)
    fig.suptitle('Mean-field hysteresis is a property of the stipulated equations', fontsize=14, fontweight='bold')
    fig.text(.06, .025, 'L = 6, α = 0.65; fold bounds θ = −3.41509 and −2.58491. This is not a fitted threshold for fish.\nθ changes intrinsic calling propensity; this sweep is not a sweep of nonnegative playback amplitude.', fontsize=9, color='#555555')
    fig.tight_layout(rect=[.02, .12, .99, .91], w_pad=2)
    for extension in ('png', 'pdf'):
        fig.savefig(target / f'meanfield_bifurcation.{extension}', dpi=220)
    plt.close(fig)
    print(f'Rendered six plot files in {target}')


if __name__ == '__main__':
    main()
