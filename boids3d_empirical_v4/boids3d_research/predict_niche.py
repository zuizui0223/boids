"""Predict *synthetic model* aggregate niche patterns from explicit rule strengths.
NOT a wild bat/bird predictor. Uses only the frozen archived 90-world simulator grid.
Forecast range: preference 0..0.30, depletion 0..0.30, tracking 0..0.80.
"""
import argparse,json
from pathlib import Path
from forward_prediction_validation import ROOT, fit_interpolators

LABELS={
 'I_species_XY':'species_horizontal_niche_information_nats',
 'I_species_Z_given_XY':'species_vertical_information_given_XY_nats',
 'buffering':'experienced_environmental_state_buffering_index',
 'uptake':'simulated_mean_resource_uptake'
}


def forecast(preference:float,depletion:float,tracking:float):
    inputs={'preference':float(preference),'depletion':float(depletion),'tracking':float(tracking)}
    support={'preference':(0,.30),'depletion':(0,.30),'tracking':(0,.80)}
    for name,value in inputs.items():
        lo,hi=support[name]
        if not lo<=value<=hi:raise ValueError(f'{name}={value} outside trained domain [{lo},{hi}]')
    rows=json.loads((ROOT/'cross_repo_phase_scan.json').read_text())['raw']
    fits=fit_interpolators(rows)
    calibration=json.loads((ROOT/'prediction_uncertainty_revalidation.json').read_text())
    x=list(inputs.values())
    measures={}
    for name,fit in fits.items():
        p=float(fit['linear'](x).item())
        q=calibration['scores'][name]['calibration_abs_error_quantile_90pct']
        measures[LABELS[name]]={
           'prediction':p,
           'empirically_calibrated_error_band':[p-q,p+q],
           'error_band_half_width':q,
           'second_synthetic_test_coverage':calibration['scores'][name]['coverage_24_new_worlds']
        }
    return {'model':'mechanistic_BOIDS_inspired_simulator_surrogate',
            'intended_use':'synthetic within-domain niche-index forecast (NOT wild-animal forecast)',
            'inputs':inputs,'metrics':measures,
            'training':{'worlds':90,'original_seeds':5,'original_parameter_grid':'3x3x2'},
            'error_calibration':'24 synthetic worlds distinct from training, 24 further worlds for revalidation',
            'limits':['Fixed 4x4 horizontal grid and 8 vertical states',
                      'Synthetic flight units and environment not calibrated to real taxa',
                      'Error bands are heuristic and lack formal coverage without scenario exchangeability',
                      'Resource preference/strength known here; wild inference would require fitting and uncertainty propagation',
                      'No seasonal population prediction or colony breeding-site forecast implied']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preference',type=float,required=True)
    parser.add_argument('--depletion',type=float,required=True)
    parser.add_argument('--tracking',type=float,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=forecast(args.preference,args.depletion,args.tracking)
    content=json.dumps(report,indent=2,ensure_ascii=False)
    print(content)
    if args.output:args.output.write_text(content,encoding='utf-8')

if __name__=='__main__':main()
