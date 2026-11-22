"""Render static scientific figures from saved v14 values, without simulations."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from geometry import geometry_diagnostic
from run_audit import (SEEDS, SNAPSHOTS, PROTOCOL_COMMIT, validate_trace_arrays,
                       verify_invariants, summarize)

BLUE, ORANGE = '#266a9e', '#d56b35'
MECHANISMS = ('intact', 'motor_cut', 'hearing_cut', 'both_cut')
LABELS = ('Intact', 'Motor cut', 'Hearing cut', 'Both cut')
COLORS = ('#266a9e', '#258875', '#8b6ea8', '#69737c')
STAGES = (1000, 1040, 4000, 16000)
STAGE_COLORS = ('#38598b', '#168d97', '#9065a0', '#d56b35')


def style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.titleweight': 'bold', 'axes.labelcolor': '#263542',
        'xtick.color': '#43515d', 'ytick.color': '#43515d',
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
        'savefig.facecolor': 'white', 'pdf.fonttype': 42, 'ps.fonttype': 42})


def save(fig, directory, name):
    for extension in ('png', 'pdf'):
        fig.savefig(directory / f'{name}.{extension}', dpi=190, bbox_inches='tight')
    plt.close(fig)


def block_means(a, size=100):
    return np.asarray(a).reshape(*np.shape(a)[:-1], -1, size).mean(axis=-1)


def maintenance_figure(data, result, directory):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.3), gridspec_kw={'height_ratios': [1.15, 1]})
    times = np.arange(50, 16000, 100)
    for ax, mechanism, title in zip(axes[0], ('intact', 'motor_cut'),
            ('A  Intact acoustic links', 'B  Motor link removed after playback')):
        for timing, color, label in (('none', BLUE, 'No playback'), ('pulse', ORANGE, 'Playback')):
            values = block_means(data[f'{mechanism}__{timing}__call_fraction']).mean(axis=0)
            ax.plot(times, values, color=color, lw=2, label=label)
        ax.axvline(1040, color='#6b747c', lw=1, ls=':')
        ax.axvline(4000, color='#9ca6ae', lw=1, ls='--')
        ax.axvspan(12000, 16000, color='#e6edf3', alpha=.8, zorder=0)
        ax.set(xlim=(0,16000), ylim=(0,1.035), xlabel='Simulation step', ylabel='Mean calling fraction')
        ax.set_title(title, loc='left', fontsize=12)
        ax.grid(axis='y', alpha=.15)
        ax.legend(frameon=False, loc='lower right')
        ax.set_xticks((0, 4000, 8000, 12000, 16000))
    for ax, metric, title, xlabel in (
        (axes[1,0], 'call_fraction', 'C  Terminal playback effect', 'Pulse − no pulse (calling fraction)'),
        (axes[1,1], 'hull_area', 'D  Terminal area effect', 'Pulse − no pulse (arbitrary area units)')):
        for i, (mechanism, color) in enumerate(zip(MECHANISMS, COLORS)):
            row = result['contrasts'][mechanism]['terminal'][metric]
            mean = row['mean_difference']
            low, high = row['bootstrap_95_interval']
            ax.errorbar(mean, i, xerr=[[mean-low],[high-mean]], fmt='o', color=color,
                        markersize=6, capsize=4, lw=1.8)
        ax.axvline(0, color='#9ba6ae', lw=1)
        ax.set_yticks(range(4), LABELS)
        ax.invert_yaxis()
        ax.set_ylim(3.6,-.6)
        ax.set_xlabel(xlabel)
        ax.set_title(title, loc='left', fontsize=12)
        ax.grid(axis='x', alpha=.15)
        if metric == 'call_fraction':
            ax.ticklabel_format(axis='x', style='sci', scilimits=(0,0), useMathText=True)
    fig.suptitle('Acoustic Boids v14 | a long finite-horizon maintenance audit', fontsize=17, x=.05, ha='left')
    fig.text(.05,.035,'24 paired simulator seeds; cuts at step 1040; terminal window [12000,16000). '
             'Error bars: paired-seed percentile 95% intervals.\n'
             'Curves show 100-step display means. Dashed line: v13 horizon. Synthetic model; time and area are not calibrated to fish.',
             fontsize=9.3,color='#56636d')
    fig.subplots_adjust(left=.09,right=.98,top=.88,bottom=.17,hspace=.40,wspace=.30)
    save(fig,directory,'maintenance_audit')


def all_seed_figure(data, seeds, directory):
    fig, axes = plt.subplots(4,6,figsize=(16,10),sharex=True,sharey=True)
    times = np.arange(50,16000,100)
    for i, ax in enumerate(axes.flat):
        for timing,color in (('none',BLUE),('pulse',ORANGE)):
            ax.plot(times,block_means(data[f'intact__{timing}__call_fraction'][i]),color=color,lw=1.3)
        ax.axvline(1040,color='#9da7ad',lw=.7,ls=':')
        ax.axvline(4000,color='#b8c1c7',lw=.7,ls='--')
        ax.axvspan(12000,16000,color='#edf2f5',zorder=0)
        ax.set_title(f'Seed {seeds[i]}',loc='left',fontsize=10)
        ax.set(xlim=(0,16000),ylim=(-.025,1.025))
        ax.set_xticks((0,8000,16000),('0','8000','16000'))
        ax.set_yticks((0,.5,1))
        ax.tick_params(labelsize=8)
        ax.grid(axis='y',alpha=.12)
    handles=[Line2D([0],[0],color=BLUE,lw=2,label='No playback'),
             Line2D([0],[0],color=ORANGE,lw=2,label='Playback at steps 1000–1039')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.51,.95),ncol=2,frameon=False)
    fig.suptitle('Every seed retained | intact acoustic links',fontsize=17,x=.05,ha='left',y=.995)
    fig.supxlabel('Simulation step',y=.055)
    fig.supylabel('Calling fraction (100-step display mean)',x=.018)
    fig.text(.05,.012,'All 24 original v13 seeds, continued to a fixed 16000-step horizon. '
             'Dotted line: playback end. Dashed line: v13 horizon. Shading: terminal window.\n'
             'Overlapping paths are retained. Similar late calling fractions do not establish a unique stationary distribution.',
             fontsize=9,color='#56636d')
    fig.subplots_adjust(left=.06,right=.99,top=.88,bottom=.12,wspace=.16,hspace=.35)
    save(fig,directory,'all_seed_continuations')


def geometry_figure(records,directory):
    fig, axes=plt.subplots(1,2,figsize=(12.7,5.7))
    axes[0].plot((0,1),(0,1),ls='--',color='#abb4bb',lw=1,zorder=0)
    for step,color in zip(STAGES,STAGE_COLORS):
        for timing,marker in (('none','o'),('pulse','^')):
            rows=[r for r in records if r['completed_steps']==step and r['timing']==timing]
            axes[0].scatter([r['low_mean'] for r in rows],[r['high_mean'] for r in rows],
                            color=color,marker=marker,s=38,alpha=.65,edgecolor='white',linewidth=.35)
            for r in rows:
                axes[1].plot([r['weighted_degree_mean']]*2,[r['low_mean'],r['high_mean']],
                             color=color,alpha=.45,lw=1)
            axes[1].scatter([r['weighted_degree_mean'] for r in rows], [r['low_mean'] for r in rows],
                            marker=marker,color=color,s=30,alpha=.65,edgecolor='white',linewidth=.3)
            axes[1].scatter([r['weighted_degree_mean'] for r in rows], [r['high_mean'] for r in rows],
                            marker=marker,facecolor='none',edgecolor=color,s=40,alpha=.65,linewidth=.8)
    axes[0].set(xlim=(-.025,1.025),ylim=(-.025,1.025),xlabel='Mean lower closure endpoint',ylabel='Mean upper closure endpoint')
    axes[0].set_title('A  Lower and upper numerical bounds',loc='left',fontsize=12)
    axes[1].set(ylim=(-.025,1.025),xlabel='Mean effective hearing degree (row sum of A)',ylabel='Mean closure endpoint')
    axes[1].set_title('B  Actual geometry and closure response',loc='left',fontsize=12)
    for ax in axes:
        ax.grid(alpha=.12)
    handles=[Line2D([0],[0],marker='o',color='none',markerfacecolor=c,markeredgecolor='none',label=f'Step {s}')
             for s,c in zip(STAGES,STAGE_COLORS)]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.905),ncol=4,frameon=False)
    separated=sum(r['classification']=='separated_fixed_points' for r in records)
    unresolved=sum(r['classification']=='unresolved' for r in records)
    fig.suptitle('Frozen-geometry calling closure | supplementary diagnostic',fontsize=16,x=.05,ha='left',y=.99)
    fig.text(.05,.028,f'{len(records)} geometry records: {len(records)-separated-unresolved} collapsed brackets, '
             f'{separated} separated records, {unresolved} unresolved. Circles: no playback; triangles: playback. In B: filled lower, open upper.\n'
             'Pre-pulse pairs duplicate the same geometry. The probability closure is not the exact stochastic expectation or the full moving system.',
             fontsize=9,color='#56636d')
    fig.subplots_adjust(left=.08,right=.98,top=.76,bottom=.21,wspace=.28)
    save(fig,directory,'geometry_closure')


def load_inputs(directory):
    result=json.loads((directory/'audit_result.json').read_text())
    expected={'status':'SYNTHETIC_ONLY_NOT_FIELD_RESULT','version':'v14_post_pulse_maintenance',
              'seeds':list(SEEDS),'individuals':32,'steps':16000,'trajectories':192,
              'protocol_commit':PROTOCOL_COMMIT}
    if any(result.get(key)!=value for key,value in expected.items()):
        raise ValueError('Result metadata differs from the fixed v14 experiment')
    trace_path=directory/'full_traces.npz'
    if hashlib.sha256(trace_path.read_bytes()).hexdigest()!=result['trace_receipt']['sha256']:
        raise ValueError('Trace archive checksum does not match the result receipt')
    with np.load(trace_path,allow_pickle=False) as archive:
        if not np.array_equal(archive['seeds'],SEEDS) or not np.array_equal(archive['snapshot_steps'],SNAPSHOTS):
            raise ValueError('Trace seed or snapshot order differs from the fixed experiment')
        data={k:archive[k] for k in archive.files if k not in ('seeds','snapshot_steps')}
        seeds=archive['seeds']
    validate_trace_arrays(data)
    verify_invariants(data)
    computed,_,_=summarize(data)
    for mechanism in MECHANISMS:
        for metric in ('call_fraction','hull_area'):
            for field in ('mean_difference','bootstrap_95_interval'):
                if not np.allclose(result['contrasts'][mechanism]['terminal'][metric][field],
                                   computed[mechanism]['terminal'][metric][field],rtol=1e-12,atol=1e-12):
                    raise ValueError('Plotted terminal estimates disagree with the archived trajectories')
    geometry=json.loads((directory/'geometry_diagnostics.json').read_text())['records']
    expected_records={(seed,timing,step) for seed in SEEDS for timing in ('none','pulse') for step in SNAPSHOTS}
    actual_records={(r['seed'],r['timing'],r['completed_steps']) for r in geometry}
    if len(geometry)!=192 or actual_records!=expected_records:
        raise ValueError('Geometry records do not match the fixed seed and snapshot panel')
    for record in geometry:
        i=SEEDS.index(record['seed'])
        j=SNAPSHOTS.index(record['completed_steps'])
        pos=data[f"intact__{record['timing']}__snapshot_pos"][i,j]
        expected_geometry=geometry_diagnostic(pos)
        for field,value in expected_geometry.items():
            actual=record.get(field)
            if isinstance(value,(str,bool,int)):
                matches=actual==value
            else:
                matches=actual is not None and np.allclose(actual,value,rtol=1e-10,atol=1e-10)
            if not matches:
                raise ValueError('Geometry diagnostics disagree with the archived positions')
    return data,seeds,result,geometry


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',type=Path,default=Path(__file__).resolve().parent/'results')
    args=parser.parse_args()
    data,seeds,result,geometry=load_inputs(args.results)
    directory=args.results/'figures'
    directory.mkdir(exist_ok=True)
    style()
    maintenance_figure(data,result,directory)
    all_seed_figure(data,seeds,directory)
    geometry_figure(geometry,directory)
    print('Rendered three figures as PNG and PDF from saved values.')


if __name__=='__main__':
    main()
