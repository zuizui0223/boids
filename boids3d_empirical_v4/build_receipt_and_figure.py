#!/usr/bin/env python3
"""Produce human-readable research receipt and figure from aggregate bat-browser audit.

Embedded aggregate values were computed against the complete 9,873-row public annotated
CSV via a page-content reader; the raw dataset is not repackaged here. Running
empirical_transition_benchmark.py --download independently regenerates result metrics
and verifies the source's pinned checksum in a network-enabled environment.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from math import comb

DIR=Path(__file__).resolve().parent
individuals={
 'Bat1_3D6001852B958':[-1.0758112005136857,-1.0618459363554111,-1.0602667216652404,-1.0599894342823029],
 'Bat2_3D6001852B95D':[-1.1176207494793466,-1.0867179986554065,-1.0890190338416386,None],
 'Bat3_3D6001852B978':[-1.0838754246887825,-1.0781301789952127,-1.0776103673677475,-1.1006263544363646],
 'Bat4_3D6001852B980':[-1.080395495385785,-1.0667346414828183,-1.0673588790825612,-1.0696237779825535],
 'Bat5_3D6001852B98C':[-1.0948808776369838,-1.066016027540372,-1.0666360895315206,-1.0595212437477062],
 'Bat6_3D6001852B98E':[-1.0802417172313286,-1.0704300985365045,-1.073061971707668,-1.0769919369853835],
 'Bat7_3D6001852B9A3':[-1.0718717634530972,-1.0610568103072653,-1.0612034187026382,-1.0734757142366325],
 'Bat8':[-1.0911979444596567,-1.0943158647783724,-1.0990910763313466,-1.129105114743992]
}
np.random.seed(20261026)
raw=np.array([x for x in individuals.values()],dtype=object)
contrast={}
for k,a,b in [('inertia_gain',1,0),('wind_additional_gain',2,1),('individual_history_gain',3,2)]:
    v=np.array([float(x[a])-float(x[b]) for x in individuals.values() if x[a] is not None])
    rng=np.random.default_rng(20261026+len(v)+a)
    means=np.mean(rng.choice(v,size=(20000,len(v)),replace=True),axis=1)
    contrast[k]={
        'n_individuals':len(v),
        'mean_nats_per_transition':float(v.mean()),
        'bootstrap_95pct_percentile_CI':[float(np.quantile(means,.025)),float(np.quantile(means,.975))],
        'individual_positive_count':int(np.sum(v>0)),
        'individual_values':v.tolist(),
        'one_sided_sign_p_ge_positive':float(sum(comb(len(v),i) for i in range(int(np.sum(v>0)),len(v)+1))/(2**len(v)))
    }
receipt={
    'id':'boids3d-realdata-transition-benchmark-v4',
    'date':'2026-10-26',
    'status':'completed exploratory bat transition validation and cadence gate; full social-Boids validation blocked by data scale',
    'provenance':{
        'dataset':'Tadarida teniotis annotated GPS + derived wind',
        'doi':'10.5441/001/1.52nn82r9',
        'archive_bitstream':'a6a6db33-0aca-4902-a58d-f32980c1a3e1',
        'expected_md5_from_batter':'e0f6faedfd1f21bac222d9da430ea5d8',
        'expected_size_from_batter':3630088,
        'source_text_length_observed':3630088,
        'source_rows':9873,
        'local_raw_file_available':False,
        'md5_verified_in_this_environment':False,
        'method':'Source CSV fetched into remote content-extraction runtime, reduced to counts and model scores, no raw GPS tracks transferred to local files',
    },
    'eligibility':{'candidate_sessions':16,'eligible_sessions':16,'eligible_individuals':8,'repeat_individuals':7,'transition_triplets':9587,'gps_events_used_for_synchronous_audit':9829},
    'methods':{'primary_speed_threshold_m_s':.5,'primary_wind_threshold_m_s':.05,'two_consecutive_gaps_s':'15 to 75','min_transition_triplets_per_night':30,
        'split':'leave-one-individual-x-BatDay-session-out; independent individual-only holdout for M0/M1/M2',
        'replicate':'session mean followed by equal-individual mean',
        'personal_history_comparison':'M3-M2 paired within 7 evaluable individuals',
        'permutation_unit':'whole night; shuffle individual session labels 199 times preserving label counts'},
    'heldout_session_equal_individual_log_score':{'M0':-1.0869868966060832,'M1':-1.0731559445814205,'M2':-1.074280944778795,'M3_unmatched_subset':-1.0813333680592765},
    'heldout_new_individual_equal_individual_log_score':{'M0':-1.0867083258087016,'M1':-1.0732401769055044,'M2':-1.07442348267165},
    'contrasts':contrast,
    'personal_policy_night_label_null':{'replicates':199,'observed_M3_minus_M2':-0.009157864575173166,'null_mean':-0.01149266536058751,'null_sd':0.00486823757549729,'calibrated_excess':-0.009157864575173166-(-0.01149266536058751),'one_sided_p_ge_observed':0.32},
    'fixed_threshold_sensitivity':[
        {'vertical_m_s':.5,'wind_m_s':.05,'M2_minus_M1':-.0011250001973746038,'M3_minus_M2_matched':-.009157864575173166},
        {'vertical_m_s':1.,'wind_m_s':.05,'M2_minus_M1':-.00032974731950441427,'M3_minus_M2_matched':-.009924959134995455},
        {'vertical_m_s':.5,'wind_m_s':.15,'M2_minus_M1':-.0005108224828604957,'M3_minus_M2_matched':-.008765915277445493},
    ],
    'simultaneity_gate':{'recorded_cross_individual_pairs_within_5sec':15676,'within_5sec_and_3d_distance_le100m':0,
        'within_15sec_and_3d_distance_le500m':39,'decision':'FAIL: neighbor-level force coefficients not inferable from this dataset'},
    'external_species_cadence_gate':{'species':'Eidolon helvum','doi':'10.5441/001/1.k8n02jn8',
        'observed_csv_length':4497472,'gps_rows':18154,'n_individuals':63,'gap_q10_seconds':147,
        'gap_median_seconds':273,'gap_q90_seconds':1786,'two_consecutive_valid_15_75s_triplets':0,
        'decision':'FAIL: no events for the fixed short-horizon transition benchmark; do not adjust rule after seeing failure'},
    'claim_boundary':[
        'One-step climb class is modestly predictable from previous class, averaged equally by individual.',
        'No improvement demonstrated from the archived modelled vertical wind at this horizon and feature design.',
        'No calibrated evidence of a repeatable individualized short-step policy beyond pooled predictors (p=0.32).',
        'Not a full separation/alignment/cohesion coefficient fit; synchronized close neighbors were not observed at required scale.',
        'Does not contradict prior repeatable individual centered-height distribution in other fruit-bat panels.',
        'Source already used for other ecological questions; this is exploratory and cannot be called independent confirmatory evidence.'
    ],
    'per_individual_scores':individuals
}
(DIR/'EMPIRICAL_RESULT_V4.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

labels=['Previous state vs marginal','+ estimated wind vs inertia','+ self history vs pooled']
cols=['inertia_gain','wind_additional_gain','individual_history_gain']
ys=[contrast[k]['mean_nats_per_transition'] for k in cols]
lo=[contrast[k]['bootstrap_95pct_percentile_CI'][0] for k in cols]
hi=[contrast[k]['bootstrap_95pct_percentile_CI'][1] for k in cols]
fig,ax=plt.subplots(figsize=(9.1,4.4))
xx=np.arange(3)
ax.axhline(0,color='0.4',linewidth=1)
ax.errorbar(xx,ys,yerr=[np.array(ys)-np.array(lo),np.array(hi)-np.array(ys)],fmt='o',capsize=7,markersize=8,elinewidth=2)
ax.set_xticks(xx,labels)
ax.set_ylabel('Held-out log-score difference (nats / transition)')
ax.set_title('Observed bat tracks: vertical transition prediction')
ax.text(.01,.02,'Equal-individual estimates; 95% individual bootstrap percentile intervals\nM3 matched: 7/8 individuals; observational model, not full social Boids',transform=ax.transAxes,fontsize=9,va='bottom')
fig.tight_layout()
fig.savefig(DIR/'bat_vertical_prediction_v4.png',dpi=180)
plt.close(fig)
print(json.dumps({'contrasts':contrast,'written':['EMPIRICAL_RESULT_V4.json','bat_vertical_prediction_v4.png']},indent=2))
