"""v66 synthetic sources only. No actual wildlife movement effects in tests."""
from __future__ import annotations
import unittest
from datetime import datetime,timedelta,timezone
from copy import deepcopy

from watlas_official_rws_phase_check import (
    request_body,validate_official_rws,_official_phase_at,
    compare_original_source_with_RWS,reassemble_original_source_episodes,
    _closest_official_time,VALIDATION_SHIFTS_MIN,RWS_STATION
)
from test_watlas_original_slope_source import known_original_like
from watlas_original_slope_source import audit_slope_source_only

def fake_response(n=5,bad_unit=False,bad_datum=False,bad_station=False):
    t=datetime.fromisoformat("2018-08-01T00:00:00+01:00")
    return {
        "Succesvol":True,
        "WaarnemingenLijst":[{
            "Locatie":{"Code": "other_station" if bad_station else RWS_STATION},
            "AquoMetadata":{
                "Grootheid":{"Code":"WATHTE"},
                "Eenheid":{"Code":"m" if bad_unit else "cm"},
                "Hoedanigheid":{"Code":"MSL" if bad_datum else "NAP"}},
            "MetingenLijst":[{
                "Tijdstip":(t+timedelta(minutes=10*i)).isoformat(),
                "Meetwaarde":{"Waarde_Numeriek":20+10*i}}
                for i in range(n)]}]}

class ActualRwsSourceCodeTests(unittest.TestCase):
    def test_original_frozen_request_and_fixed_plus01_to_real_UTC(self):
        body=request_body()
        self.assertEqual(body["Locatie"]["Code"],"terschelling.west")
        self.assertEqual(body["Periode"]["Begindatumtijd"],"2018-08-01T00:00:00.000+01:00")
        src=validate_official_rws(fake_response(),body,expected_count=5)
        vals=src["original_UTC_second_to_cm_NAP"]
        start=round(datetime.fromisoformat("2018-08-01T00:00:00+01:00").timestamp())
        self.assertEqual(sorted(vals),[start+600*i for i in range(5)])
        self.assertEqual(list(vals.values()),[20,30,40,50,60])
        self.assertEqual(src["source_manifest"]["original_fixed_RWS_timezone"],"+01:00")

    def test_official_source_units_datum_station_and_completeness_fail_closed(self):
        body=request_body()
        for kw in ({"bad_unit":True},{"bad_datum":True},{"bad_station":True}):
            with self.subTest(kw=kw),self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
                validate_official_rws(fake_response(**kw),body,expected_count=5)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            validate_official_rws(fake_response(n=4),body,expected_count=5)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            validate_official_rws(fake_response(),{"Locatie":{"Code":"other"}},expected_count=5)

    def test_close_original_ten_minute_values_and_physical_phase(self):
        t=3600
        vals={t-1800:0.,t+1800:40.}
        times=sorted(vals)
        self.assertEqual(_official_phase_at(t,vals,times,0),"rising")
        self.assertEqual(_official_phase_at(t,{k:-v for k,v in vals.items()},times,0),"falling")
        self.assertEqual(_official_phase_at(t,{k:20. for k in vals},times,0),"slack")
        self.assertEqual(_official_phase_at(3600,{1800:0.},[1800],0),"unbracketed")
        self.assertEqual(VALIDATION_SHIFTS_MIN,(0,-30,30))
        self.assertEqual(_closest_official_time([300,900],600),300)

    def test_confusion_is_by_actual_phase_and_cannot_select_a_favorable_lag(self):
        base=3600
        vals={base-1800:0.,base+1800:60.}
        src={"original_UTC_second_to_cm_NAP":vals}
        real=[
            ("unpublished_bird1","t1",base,"rising"),
            ("unpublished_bird2","t2",base,"falling")
        ]
        report=compare_original_source_with_RWS(real,src,shift_minutes=0)
        self.assertEqual(report["official_phase_agree"],1)
        self.assertEqual(report["official_phase_disagree"],1)
        self.assertEqual(report["source_phase_vs_independently_observed_RWS_2x4"][
            "source_falling"]["rising"],1)
        self.assertFalse(report["fixed_prior_source_eligibility_satisfied"])
        self.assertNotIn("unpublished_bird",str(report))
        for minutes in (25,-25,60):
            with self.subTest(minutes=minutes),self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
                compare_original_source_with_RWS(real,src,shift_minutes=minutes)

    def test_reassemble_original_v65_source_unmodified_and_no_heading_leak(self):
        original=known_original_like(cycles=2,birds=3,minutes=241)
        extra=known_original_like(cycles=2,birds=3,minutes=241,extra_heading=True)
        pairs,stages=reassemble_original_source_episodes(original)
        extra_pairs,extra_stages=reassemble_original_source_episodes(extra)
        self.assertEqual(pairs,extra_pairs)
        self.assertEqual(stages,extra_stages)
        old=audit_slope_source_only(original)
        self.assertEqual(len(pairs),old["non_slack_bracketed_original_moving_triples"])
        self.assertEqual(stages["same_original_published_tide_metadata"],
                         old["eligible_moving_stage_counts"][
                             "original_waterlevel_and_tidaltime_present"])
        self.assertEqual(len({tag for tag,tid,t,phase in pairs}),3)

if __name__=="__main__":
    unittest.main()
