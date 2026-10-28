"""v15 pre-outcome no-leakage, source clock, structural and scoring tests."""
from __future__ import annotations
import datetime as dt
import math
import random
import unittest
import numpy as np
import forecast as v


def nmea_sentence(instant:dt.datetime,lat:str="5120.0000",lon:str="00010.0000",
                  speed:str="21.0",course:str="90.0",status:str="A") -> bytes:
    time=instant.strftime("%H%M%S.%f")[:-4]
    date=instant.strftime("%d%m%y")
    payload=f"GNRMC,{time},{status},{lat},N,{lon},W,{speed},{course},{date},,"
    x=0
    for c in payload:
        x^=ord(c)
    return ("$"+payload+"*"+f"{x:02X}\n").encode()


def artificial_event(trial:str,bird:str,current:float,stale:float,target:float,
                     ghost:float|None=None) -> v.Event:
    own=(0.,0.,1.,0.,0.,0.,0.,0.)
    sf=lambda x:(x,0.,0.,0.,1.,0.)
    return v.Event(trial,bird,own,sf(current),sf(stale),sf(ghost) if ghost is not None else None,target)


class RawContract(unittest.TestCase):
    def test_source_digest_and_fixed_design(self):
        self.assertEqual(v.SOURCE_SHA256,"756eed718ad13c14233e60b19009ce0916f183eb540b1262ba030ebc25a0ab03")
        self.assertEqual(v.SOURCE_BYTES,126588691)
        self.assertEqual(v.SOURCE_TRIALS,("analysis_trial_01","analysis_trial_02","analysis_trial_03"))
        self.assertEqual(v.RIDGE_ALPHA,30.)
        self.assertEqual(v.ANCHOR_STRIDE_MS,5000)
        self.assertEqual(v.COFIX_TOLERANCE_MS,200)

    def test_nmea_parser_time_heading_speed_and_crc(self):
        tm=dt.datetime(2026,7,1,12,1,2,300000)
        text=nmea_sentence(tm).decode()
        tag,fix=v.parse_original_rmc(text)
        self.assertEqual(tag,"valid")
        self.assertEqual(fix.time_ms,tm.date().toordinal()*86400000+((12*3600+60+2)*1000+300))
        self.assertAlmostEqual(fix.speed,21*v.SPEED_KNOT_M_S)
        self.assertAlmostEqual(fix.heading,math.pi/2)
        broken=text[:-3]+("00" if not text.endswith("00\n") else "FF")+"\n"
        self.assertEqual(v.parse_original_rmc(broken)[0],"bad_checksum")

    def test_invalid_record_does_not_become_airborne_fix(self):
        tm=dt.datetime(2026,7,1,12,1,2)
        self.assertEqual(v.parse_original_rmc(nmea_sentence(tm,status="V").decode())[0],"invalid_status")
        self.assertEqual(v.parse_original_rmc(nmea_sentence(tm,speed="").decode())[0],"invalid_fields")
        self.assertEqual(v.parse_original_rmc("not original RMC")[0],"non_rmc")

    def test_utc_duplicate_rows_break_run_and_all_discarded(self):
        base=dt.datetime(2026,7,1,12)
        lines=[nmea_sentence(base+dt.timedelta(milliseconds=100*i)) for i in range(400)]
        lines.insert(350,lines[350])
        fixes,qc=v.raw_runs(lines,51.333333,-.16666667)
        self.assertEqual(qc["duplicate_utc_rows_discarded"],2)
        self.assertTrue(all(f.time_ms != (base+dt.timedelta(seconds=35)).date().toordinal()*86400000+12*3600*1000+35000 for f in fixes))
        self.assertGreater(qc["accepted_flight_segments"],0)

    def test_true_flight_speed_and_gap_segment_control(self):
        base=dt.datetime(2026,7,1,12)
        seg1=[nmea_sentence(base+dt.timedelta(milliseconds=100*i)) for i in range(310)]
        seg2=[nmea_sentence(base+dt.timedelta(seconds=40,milliseconds=100*i)) for i in range(310)]
        fixes,qc=v.raw_runs(seg1+seg2,51.333333,-.16666667)
        self.assertEqual(qc["accepted_flight_segments"],2)
        self.assertEqual(len(fixes),620)
        self.assertEqual(len({f.run for f in fixes}),2)

    def test_nearest_partner_excludes_future_observations(self):
        future=v.Fix(1050,0,0,10,0,run=1)
        before=v.Fix(900,0,0,10,0,run=1)
        tr=v.Track("B",[before,future],[900,1050],{1:(0,1)}, {})
        self.assertIs(v.nearest(tr,1000),future)
        self.assertIs(v.nearest_past(tr,1000),before)
        self.assertIsNone(v.nearest_past(tr,1000,same_run=2))
        self.assertIsNone(v.nearest_past(tr,1300))

    def test_partners_use_same_age_geometry_not_stale_x_vs_current_a(self):
        a=v.Fix(20000,0,0,11.,math.pi/2,x=100,y=10)
        b=v.Fix(20000,0,0,12.,math.pi/2,x=110,y=10)
        ap=v.Fix(10000,0,0,11.,math.pi/2,x=-500,y=10)
        bp=v.Fix(10000,0,0,12.,math.pi/2,x=-490,y=10)
        self.assertAlmostEqual(v.relative_partner(a,b)[0],v.relative_partner(ap,bp)[0])
        self.assertAlmostEqual(v.relative_partner(a,b)[1],0.)


class ForecastContract(unittest.TestCase):
    def test_trial_balanced_known_truth_signal(self):
        rng=random.Random(2026)
        events=[]
        for k,trial in enumerate(v.SOURCE_TRIALS):
            for j in range(160):
                p=rng.uniform(-1,1)
                q=rng.uniform(-1,1)
                target=.45*p + rng.gauss(0,.035)
                events.append(artificial_event(trial,f"bird{j%5}",p,q,target,ghost=rng.uniform(-1,1)))
        qc={trial:{"n_primary_eligible":160} for trial in v.SOURCE_TRIALS}
        result=v.forecast(events,qc)
        self.assertEqual(result["status"],"EXPLORATORY_OBSERVED_3_TRIALS_NO_CONFIRMATORY_CLAIM")
        self.assertEqual(result["summary"]["primary_positive_trials"],3)
        self.assertEqual(result["30s_surrogate_secondary"]["status"],"MATCHED_RESTRICTED_SUBSET_EXPLORATORY")
        self.assertGreater(result["summary"]["equal_trial_mean_primary_stale_minus_current_rad2"],.03)

    def test_focal_target_does_not_enter_feature_matrix(self):
        events=[artificial_event("analysis_trial_01","b",.5,.1,.1)]
        first=v.design(events,"current")
        altered=[v.Event(events[0].trial,events[0].bird,events[0].x0,events[0].current,events[0].stale,None,-1.2)]
        np.testing.assert_array_equal(first,v.design(altered,"current"))

    def test_training_standardization_excludes_heldout_trial(self):
        events=[]
        for i,trial in enumerate(v.SOURCE_TRIALS):
            for j in range(65):
                events.append(artificial_event(trial,f"bird{j%5}",.01*j, .1*i, .03*j))
        train=[e for e in events if e.trial != v.SOURCE_TRIALS[2]]
        test=[e for e in events if e.trial == v.SOURCE_TRIALS[2]]
        before=v.fit_ridge(train,"current")
        extreme=[v.Event(e.trial,e.bird,e.x0,tuple(1e9 for _ in e.current),e.stale,None,2.0) for e in test]
        after=v.fit_ridge(train,"current")
        for b,a in zip(before[:3],after[:3]):
            np.testing.assert_array_equal(b,a)
        self.assertNotEqual(v.evaluate(train,test,"current"),v.evaluate(train,extreme,"current"))

    def test_insufficient_trial_stops_instead_of_tuning(self):
        records=[artificial_event(t,"A",.2,.3,.1) for t in v.SOURCE_TRIALS for _ in range(20)]
        result=v.forecast(records,{})
        self.assertEqual(result["status"],"NOT_ADMITTED")
        self.assertNotIn("per_trial",result)
        self.assertTrue(any("only_20_matched_anchors" in reason for reason in result["reasons"]))

    def test_surrogate_not_available_does_not_change_primary_rows(self):
        rng=random.Random(7)
        events=[]
        for trial in v.SOURCE_TRIALS:
            for j in range(100):
                p=rng.uniform(-1,1)
                events.append(artificial_event(trial,f"bird{j%4}",p,rng.uniform(-1,1),.2*p,None))
        d=v.forecast(events,{})
        self.assertEqual(d["30s_surrogate_secondary"]["status"],"NOT_ADMITTED_IN_ALL_THREE_TRIALS")
        self.assertEqual(d["status"],"EXPLORATORY_OBSERVED_3_TRIALS_NO_CONFIRMATORY_CLAIM")

    def test_wrap_angle_uses_circular_error(self):
        self.assertAlmostEqual(v.wrapped(2*math.pi-.1),-.1)
        self.assertAlmostEqual(v.wrapped(-2*math.pi+.1),+.1)


if __name__=="__main__":
    unittest.main()
