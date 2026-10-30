"""Synthetic known-truth tests only; no original new GPS outcomes read."""
import csv
import datetime as dt
import json
import math
from pathlib import Path
import tempfile
import unittest

import cross_study_forecast as m

DAY=dt.date(2020,1,1)
def synthetic_events(ids=16, ndays=25):
    days={}
    for k,study in enumerate(m.STUDIES):
        for i in range(ids):
            bird=(f"source-study-{k}",f"secret-bird-{k}-{i}")
            for d in range(ndays):
                date=DAY+dt.timedelta(days=d)
                days[bird,date]={"study":study, "taxon":("taxon-A" if i<ids//2 else "taxon-B"),
                                "y": 0.2+k*0.3+i*0.002+(d%3)*0.04}
    return days

class KnownTruth(unittest.TestCase):
    def test_only_four_original_non_Bangladesh_regions(self):
        self.assertEqual(len(m.STUDIES),4)
        self.assertEqual(sum(m.KNOWN_ID_COUNTS.values()),123)
        self.assertNotIn("Bangladesh", "\n".join(m.STUDIES))

    def test_duplicate_original_ID_UTC_records_removed_instead_of_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"synthetic.csv"
            fields=list(m.source.SOURCE_COLS)
            bird_fields={"study.name":m.STUDIES[0],"study.id":"A","individual.id":"secret",
                         "individual.taxon.canonical.name":"taxon-A","location.lat":"25",
                         "location.long":"80","gps.hdop":"2","ground.speed":"1"}
            with path.open("w",newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
                for h in (0,2,4,6,8,10):
                    r=dict(bird_fields,timestamp=f"2020-01-01 {h:02d}:00:00")
                    writer.writerow(r)
                    if h==2:writer.writerow(r)
            daily,quality=m.parse_gps(path)
            self.assertEqual(len(daily),0) # 7 original rows; both duplicate records removed => five
            self.assertEqual(quality["study_source_quality"][m.STUDIES[0]]
                ["duplicate_original_GPS_rows_discarded"],2)

    def test_exact_calendar_day_t_minus_one_requires_complete_day(self):
        days=synthetic_events(ids=1,ndays=9)
        bird=next(iter(days))[0]
        days.pop((bird,DAY+dt.timedelta(days=4)))
        events,_=m.make_events(days)
        dates={x["date"] for x in events}
        self.assertNotIn(DAY+dt.timedelta(days=5),dates)
        self.assertIn(DAY+dt.timedelta(days=6),dates)
        self.assertNotIn(DAY+dt.timedelta(days=4),dates)

    def test_same_date_embargo_and_exclusion_of_focal_bird(self):
        days=synthetic_events(ids=16,ndays=18)
        events,_=m.make_events(days)
        records,_=m.predict(events,days)
        assert records
        # Altering all observations of a later day must not change earlier predictions.
        modified={key:dict(value) for key,value in days.items()}
        for (bird,date),r in modified.items():
            if date==DAY+dt.timedelta(days=17):
                r["y"]=9999.
        earlier, _=m.predict([e for e in events if e["date"]<DAY+dt.timedelta(days=17)], days)
        later, _=m.predict([e for e in events if e["date"]<DAY+dt.timedelta(days=17)], modified)
        self.assertEqual(earlier,later)

    def test_external_mean_excludes_self_and_weights_birds_equally(self):
        source={"focal":[1000.,1000.],"a":[0.],"b":[6.,6.,6.]}
        mean,birds,rows=m.external_mean(source,"focal")
        self.assertEqual((mean,birds,rows),(3.,2,4))

    def test_taxon_fallback_and_all_studies_stop(self):
        days=synthetic_events(ids=16,ndays=25)
        records,audit=m.predict(m.make_events(days)[0],days)
        outcome=m.summarize(records)
        self.assertEqual(outcome["status"],"EXPLORATORY_ALL_FOUR_STUDY_HOLDOUT")
        self.assertEqual(outcome["total_forecast_birds"],64)
        self.assertEqual(outcome["model_order"],list(m.MODELS))
        self.assertEqual(list(outcome["frozen_comparisons"]),[
            "primary_MS_minus_MP","secondary_MP_minus_MI",
            "secondary_MP_minus_MH","descriptive_M0_minus_MS"])
        # Eight per taxon means species external history can eventually pass.
        self.assertTrue(all(a["same_taxon_fallbacks"]>0 for a in audit.values()))
        smaller=m.summarize([r for r in records if r["study"]!=m.STUDIES[0]])
        self.assertEqual(smaller["status"],"NOT_ADMITTED_FOUR_STUDY_SUPPORT")
        self.assertFalse(smaller["any_predictive_score_exported"])
        self.assertNotIn("frozen_comparisons",smaller)

    def test_equal_study_aggregation_and_not_equal_day_weighting(self):
        data=[]
        for k,study in enumerate(m.STUDIES):
            n=8 if k==0 else 16
            for i in range(n):
                for d in range(100 if k==0 else 12):
                    # means MP by study: 1 for 1st, 9 for other 3
                    errors=[9.,9.,9.,(1. if k==0 else 9.),4.]
                    data.append({"study":study,"bird":(str(k),str(i)),
                         "taxon":"A","errors":errors,"same_taxon_fallback":False})
        # total birds 56 < threshold => fixed STOP; add four more in one study
        self.assertEqual(m.summarize(data)["status"],"NOT_ADMITTED_FOUR_STUDY_SUPPORT")
        for i in range(16,20):
            for d in range(12):
                data.append({"study":m.STUDIES[1],"bird":("1",str(i)),
                         "taxon":"A","errors":[9.,9.,9.,9.,4.],
                         "same_taxon_fallback":False})
        out=m.summarize(data)
        self.assertEqual(out["status"],"EXPLORATORY_ALL_FOUR_STUDY_HOLDOUT")
        self.assertEqual(out["equal_study_absolute_MSE"][3],7.)
        self.assertEqual(out["frozen_comparisons"]["primary_MS_minus_MP"]
            ["equal_study_mean_MSE_gain"],2.)
        self.assertEqual(out["frozen_comparisons"]["primary_MS_minus_MP"]
            ["study_signs_positive"],1)

    def test_aggregate_omits_private_IDs_and_daily_raw_values(self):
        records,_=m.predict(m.make_events(synthetic_events())[0],synthetic_events())
        output=json.dumps(m.summarize(records),sort_keys=True)
        self.assertNotIn("secret-bird-",output)
        self.assertNotIn("2020-01-",output)
        self.assertNotIn('"bird"',output)
        self.assertNotIn('"y"',output)
        self.assertIn("study_absolute_MSE",output)

    def test_exact_four_study_sign_probability_lower_bound(self):
        self.assertEqual(m._sign_tail(4,4),1/16)
        self.assertEqual(m._sign_tail(0,4),1.)
        self.assertEqual(m._sign_tail(0,0),1.)

if __name__=="__main__":
    unittest.main()
