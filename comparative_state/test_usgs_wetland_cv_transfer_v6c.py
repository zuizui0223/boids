import math
import random
import unittest
from comparative_state import usgs_wetland_cv_transfer_v6c as m

class TestOriginalV6CKnownTruth(unittest.TestCase):
    def build(self,nprop=18,visits=8):
        rows=[]
        for i in range(nprop):
            for k in range(visits):
                y=2022+(k%2);cv=0.25+0.07*((k*7+i*3)%10)
                r={x:'1' for x in m.ALL_COLS}
                r.update({'Region':'R'+str(i%3),'County':'County'+str(i%4),
                          'Property':'P'+str(i), 'Wetland unit':'Unit'+str(i)+'_'+str(k%5),
                          'Study year':str(y),'Wetland type year of survey':'seasonal',
                          'Date':f'{y}-03-{1+k:02d}',
                          'Water depth CV':str(cv),'Mean water depth':str(10+(i%4)),
                          'Number of shorebirds':str(int(round(2+80*cv))),
                          'Number of dabbling ducks':'10',
                          'Number of waterbirds':str(80+int(round(2+80*cv))),
                          'Number of wading birds':'3','Number of secretive marsh birds':'2',
                          'Number of species':'8'})
                rows.append(r)
        return rows

    def test_admit_complete_original_schema(self):
        qc,rows=m.parse_input(self.build())
        self.assertEqual(qc['status'],'SOURCE_DOMAIN_ADMITTED')
        self.assertEqual(len(rows),144)
        self.assertEqual(qc['original_properties'],18)
        self.assertGreaterEqual(qc['original_wetlands'],50)

    def test_non_integer_bird_count_is_stop(self):
        r=self.build();r[0]['Number of shorebirds']='1.5'
        qc,rows=m.parse_input(r)
        self.assertIsNone(rows)
        self.assertEqual(qc['status'],'SOURCE_DOMAIN_STOP')

    def test_missing_predictor_drops_identical_rows(self):
        r=self.build();r[0]['Water depth CV']=''
        qc,rows=m.parse_input(r)
        self.assertEqual(qc['status'],'SOURCE_DOMAIN_ADMITTED')
        self.assertEqual(len(rows),143)
        self.assertEqual(qc['missing_fields']['Water depth CV'],1)

    def test_unknown_year_does_not_fix_silently(self):
        r=self.build();r[0]['Study year']='2024'
        qc,rows=m.parse_input(r)
        self.assertEqual(qc['status'],'SOURCE_DOMAIN_STOP')

    def test_no_property_id_in_model_design(self):
        _,rows=m.parse_input(self.build())
        ns,x,c=m.design(rows,include_cv=True)
        self.assertNotIn('Property',ns)
        self.assertEqual(x.shape[0],len(rows))
        self.assertEqual(c.shape[1],3)

    def test_bootstrap_fixed_positive_and_negative(self):
        a=[{'property_nvisits':2,'gain':[1.0]*len(m.RESULT_NAMES)} for i in range(20)]
        x=m.bootstrap(a,repetitions=200,seed=2)
        self.assertEqual(x['primary_gate'],'PASS')
        a=[{'property_nvisits':2,'gain':[-1.0]*len(m.RESULT_NAMES)} for i in range(20)]
        self.assertEqual(m.bootstrap(a,repetitions=200,seed=2)['primary_gate'],'FAIL')

    def test_actual_synthetic_heldout_model(self):
        qc,rows=m.parse_input(self.build())
        outputs=m.property_holdout(rows)
        self.assertEqual(len(outputs),18)
        self.assertEqual(sum(x['property_nvisits'] for x in outputs),len(rows))
        self.assertTrue(all(len(x['gain'])==len(m.RESULT_NAMES) for x in outputs))

if __name__=='__main__':unittest.main()
