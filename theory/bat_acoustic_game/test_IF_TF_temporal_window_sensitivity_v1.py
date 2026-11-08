"""Invented-only tests for the noncausal original-source time-window audit."""
import unittest
from IF_TF_temporal_window_sensitivity_v1 import (
    WINDOWS,filter_window,window_results
)


def invented_source(bat="invented",start_on=90,tf_on=47):
    rows=[]
    for level in (50,100,200,800,1600):
        for state,times in (
            ("0",(-.95,-.70,-.40,-.15)),
            ("1",(.10,.35,.60,.90))
        ):
            for t in times:
                rows.append({
                    "ID":bat,"Experiment":"IPIlow",
                    "Condition":str(level)+"ms",
                    "Var":"toy","jammingTF":"toy",
                    "isON":state,"time":str(t),
                    "IF":str(start_on if state=="1" else 90),
                    "TF":str(tf_on if state=="1" else 45)})
    return rows


class TestTimingWindowSourceOnly(unittest.TestCase):
    def test_fixed_three_policies(self):
        self.assertEqual(set(WINDOWS),{
            "near_one_second","symmetric_two_seconds","exclude_near_switch"})
        self.assertEqual(WINDOWS["near_one_second"]["off"],(-1.,0.))
        self.assertEqual(WINDOWS["near_one_second"]["on"],(0.,1.))
    def test_negative_and_positive_time(self):
        rows=invented_source()
        kept,excluded=filter_window(rows,*WINDOWS["near_one_second"].values())
        self.assertEqual(len(kept),len(rows))
        self.assertEqual(excluded,{})
    def test_source_near_switch_exclusion(self):
        rows=invented_source()
        a,b=filter_window(rows,*WINDOWS["exclude_near_switch"].values())
        self.assertEqual(len(a),len(rows)*.5)
        self.assertEqual(b["not_in_predeclared_window"],len(rows)*.5)
    def test_time_window_still_bat_unit(self):
        rows=sum((invented_source("invented"+str(i)) for i in range(5)),[])
        output=window_results(rows,WINDOWS["near_one_second"])
        assert output["medians"]["experiments"]["IPIlow"]["n_bats"]==5
        self.assertEqual(output["medians"]["experiments"]["IPIlow"]["n_bat_condition_cells"],25)
        self.assertEqual(output["medians"]["experiments"]["IPIlow"]["source_bats_favor_fixed_start"],5)
    def test_condition_support_is_not_rescued_if_sparse(self):
        sparse=invented_source()
        for row in sparse:
            row["time"]="100"
        outcome=window_results(sparse,WINDOWS["near_one_second"])
        item=outcome["medians"]["experiments"]["IPIlow"]
        self.assertEqual(item["n_bats"],0)
        self.assertEqual(item["source_condition_support_status"],"SOURCE_SUPPORT_STOP_LT_FIVE_BATS")
    def test_time_matching_does_not_discard_source_ID_within_memory(self):
        rows=invented_source("NOT_FOR_EXPORT")
        obj=window_results(rows,WINDOWS["near_one_second"])
        self.assertNotIn("NOT_FOR_EXPORT",str(obj))
    def test_same_windows_for_mean_median(self):
        d=window_results(invented_source(),WINDOWS["symmetric_two_seconds"])
        self.assertEqual(
            d["medians"]["experiments"]["IPIlow"]["n_bats"],
            d["means_sensitivity"]["experiments"]["IPIlow"]["n_bats"])


if __name__=="__main__":
    unittest.main()
