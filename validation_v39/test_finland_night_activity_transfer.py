"""v39 synthetic exact group, composition, scaling and six-label tests."""
import unittest,math
import numpy as np
from finland_night_activity_transfer import (
    source_nights,features,predict,losses,exact_sign,evaluate,summary,transfer
)
def one_night(year,region="North",temperature=10.,ns=None):
    ns=ns if ns is not None else [12,5,3,7]
    obs=[]
    for i,(label,n) in enumerate(zip(("1","2","3","4","BSS","ASR"),ns+[0,0])):
        obs.append({"quartiles":label,"n":str(n),"period":"summer",
                    "mean_temp":str(temperature),"night_length":"8",
                    "sum_rain":"0","mean_wind":"2"})
    return (region,"L1","D1",str(year),str(year)+"-06-01"),obs
def records(years=7,each=80):
    out=[]
    for y in range(years):
        for j in range(each):
            temp=0.0 if j%2 else 20.
            counts=[8,4,2,1] if temp<10 else [1,2,4,8]
            key,obs=one_night(2017+y,"North" if j%3 else "South",temp,counts)
            group,_=source_nights({key:obs})
            out.extend(group)
    return out
class Tests(unittest.TestCase):
    def test_twilight_does_not_enter_four_dark_quartiles(self):
        key,obs=one_night(2020,ns=[1,2,3,4])
        obs[-2]["n"]="9999";obs[-1]["n"]="9999"
        rows,exc=source_nights({key:obs})
        np.testing.assert_allclose(rows[0]["share"],[.1,.2,.3,.4])
        self.assertEqual(exc,{})
    def test_invalid_night_without_darkness_activity_is_excluded(self):
        key,obs=one_night(2021,ns=[0,0,0,0])
        rows,exc=source_nights({key:obs})
        self.assertEqual(len(rows),0)
        self.assertEqual(exc["no_activity_in_sunset_to_sunrise_quartiles"],1)
    def test_train_only_features_independent_of_future_response(self):
        rows=records(years=4,each=5)
        a,b=features(rows[:-3],rows[-3:])
        altered=[dict(r,count=np.array([1.,1.,500.,1.]),share=np.array([.1,.1,.7,.1]))
                 for r in rows[-3:]]
        aa,bb=features(rows[:-3],altered)
        np.testing.assert_allclose(a,aa)
        np.testing.assert_allclose(b,bb)
    def test_synthetic_warm_cold_rule_predictable_across_year(self):
        rows=records(years=7,each=80)
        train=[r for r in rows if r["year"]!="2023"]
        test=[r for r in rows if r["year"]=="2023"]
        s=losses(train,test)
        self.assertLess(s["M1"],s["M0"])
        self.assertTrue(all(math.isfinite(v) for v in s.values()))
    def test_exact_sign_and_support_independent_years(self):
        self.assertEqual(exact_sign(7,7),1/128)
        x=summary([.1]*7,[1]*7,[.9]*7)
        self.assertTrue(x["primary_positive_gate"])
        self.assertEqual(evaluate({})["status"],"NIGHT_SOURCE_SUPPORT_STOP")
if __name__=="__main__":unittest.main()
