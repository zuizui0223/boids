"""Synthetic statistical tests only; none are field results."""
import unittest
from datetime import datetime, timedelta, timezone
import numpy as np
from matched_strata import matched_analysis

VALID = 'C_AHN2_VALID'
MASKED = 'C_SELECTED_CELL_AHN2_MISSING'
OUTSIDE = 'C_OUTSIDE_2010_SELECTED_CELLS'

def fixture(composition_only=False, effect=.16):
    rows, losses, labels, cells = [], [], [], []
    for bird in range(3):
        for month in range(1,7):
            for cell in range(2):
                for group in (VALID,MASKED):
                    n = (24 if ((group==VALID)==(cell==0)) else 6) if composition_only else 6
                    gain = (.02 if cell==0 else .20) if composition_only else (.04 if group==VALID else .04+effect)
                    for k in range(n):
                        stamp = datetime(2011,month,1,12,tzinfo=timezone.utc)+timedelta(days=k,hours=group==MASKED)
                        rows.append({'id':str(bird),'t':stamp,'phase':1 if k%2 else -1})
                        losses.append([.5,.5*(1-gain)])
                        labels.append(group); cells.append((85+cell,300))
    return rows,np.array(losses),labels,cells

class MatchedStrataTests(unittest.TestCase):
    def test_fixed_matching_removes_pure_cell_composition_contrast(self):
        args=fixture(composition_only=True)
        _,errors,labels,_=args
        v=errors[np.array(labels)==VALID].mean(0); m=errors[np.array(labels)==MASKED].mean(0)
        self.assertGreater((1-m[1]/m[0])-(1-v[1]/v[0]),.05)
        result=matched_analysis(*args,draws=120)
        self.assertEqual(result.get('admission'),'ADMITTED_MATCHED_CONDITIONAL_COMPARISON')
        self.assertAlmostEqual(result['relative_skill']['masked_minus_valid'],0.,places=12)
        self.assertEqual(result['support']['matched_birds'],3)
        self.assertEqual(result['support']['matched_strata'],36)
    def test_true_within_stratum_difference_and_paired_bootstrap(self):
        result=matched_analysis(*fixture(),draws=120)
        self.assertEqual(result.get('admission'),'ADMITTED_MATCHED_CONDITIONAL_COMPARISON')
        self.assertAlmostEqual(result['relative_skill']['valid'],.04,places=12)
        self.assertAlmostEqual(result['relative_skill']['masked'],.20,places=12)
        self.assertAlmostEqual(result['relative_skill']['masked_minus_valid'],.16,places=12)
        self.assertTrue(np.allclose(result['relative_skill']['paired_bird_CI95'],[.16,.16]))
        self.assertAlmostEqual(result['absolute_gain']['masked_minus_valid'],.08,places=12)
        self.assertEqual(result['positive_birds'],3)
        self.assertTrue(np.allclose(result['leave_one_bird_out_gap_range'],[.16,.16]))
    def test_unmatched_condition_cannot_influence_effect(self):
        args=list(fixture()); before=matched_analysis(*args,draws=60)
        args[0]=args[0]+[{'id':'0','t':datetime(2011,9,1,18,tzinfo=timezone.utc),'phase':1}]*40
        args[1]=np.vstack([args[1],np.tile([10.,0.],(40,1))])
        args[2]=args[2]+[MASKED]*40; args[3]=args[3]+[(85,300)]*40
        after=matched_analysis(*args,draws=60)
        self.assertEqual(after.get('admission'),'ADMITTED_MATCHED_CONDITIONAL_COMPARISON')
        self.assertEqual(before['support']['matched_episodes'],after['support']['matched_episodes'])
        self.assertEqual(before['relative_skill'],after['relative_skill'])
    def test_phase_sensitivity_requires_same_phase_in_each_stratum(self):
        rows,loss,labels,cells=fixture()
        for r,g in zip(rows,labels): r['phase']=1 if g==VALID else -1
        primary=matched_analysis(rows,loss,labels,cells,draws=80)
        self.assertEqual(primary.get('admission'),'ADMITTED_MATCHED_CONDITIONAL_COMPARISON')
        sensitivity=matched_analysis(rows,loss,labels,cells,phase_conditioned=True,draws=80)
        self.assertEqual(sensitivity.get('admission'),'NOT_ADMITTED_INSUFFICIENT_COMMON_SUPPORT')
        self.assertEqual(sensitivity['support']['matched_strata'],0)
        self.assertNotIn('relative_skill',sensitivity)
    def test_bird_support_gate_and_no_threshold_relaxation(self):
        rows,loss,labels,cells=fixture(); keep=[i for i,r in enumerate(rows) if r['id']!='2']
        result=matched_analysis([rows[i] for i in keep],loss[keep],[labels[i] for i in keep],[cells[i] for i in keep],draws=60)
        self.assertEqual(result.get('admission'),'NOT_ADMITTED_INSUFFICIENT_COMMON_SUPPORT')
        self.assertNotIn('relative_skill',result)
        self.assertIn('fewer_than_3_birds',result['failed_gates'])
    def test_phase_matched_positive_fixture_preserves_common_weights(self):
        result=matched_analysis(*fixture(),phase_conditioned=True,draws=120)
        self.assertEqual(result.get('admission'),'ADMITTED_MATCHED_CONDITIONAL_COMPARISON')
        self.assertEqual(result['support']['matched_strata'],72)
        self.assertAlmostEqual(result['relative_skill']['masked_minus_valid'],.16,places=12)
    def test_bad_loss_or_alignment_is_rejected(self):
        rows,loss,labels,cells=fixture()
        with self.assertRaises(ValueError): matched_analysis(rows,loss[:-1],labels,cells)
        loss[0,0]=float('nan')
        with self.assertRaises(ValueError): matched_analysis(rows,loss,labels,cells)
    def test_empty_input_reports_source_stop_not_zero_effect(self):
        result=matched_analysis([],np.empty((0,2)),[],[],draws=60)
        self.assertEqual(result.get('admission'),'NOT_ADMITTED_INSUFFICIENT_COMMON_SUPPORT')
        self.assertNotIn('relative_skill',result)

class SourceReplayTests(unittest.TestCase):
    def test_source_download_failure_or_hash_drift_is_not_missing_habitat(self):
        from run_matched_mask import verify_source_replay,TILE_SHA,PARTITION,PREVIOUS_GAP
        for site in TILE_SHA:
            verify_source_replay(site,TILE_SHA[site],PARTITION[site],PREVIOUS_GAP[site])
            with self.assertRaisesRegex(ValueError,'BYTES_DRIFT'):
                verify_source_replay(site,TILE_SHA[site][:-1],PARTITION[site],PREVIOUS_GAP[site])
            with self.assertRaisesRegex(ValueError,'PARTITION_DRIFT'):
                verify_source_replay(site,TILE_SHA[site],[0,0,0],PREVIOUS_GAP[site])
            with self.assertRaisesRegex(ValueError,'CONTRAST_NOT_REPLAYED'):
                verify_source_replay(site,TILE_SHA[site],PARTITION[site],PREVIOUS_GAP[site]+.1)

if __name__=='__main__': unittest.main()
