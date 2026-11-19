"""v38b known-truth no-outcome, four-quartile night-key source tests."""
import io,zipfile,unittest
from finland_six_bin_source import audit,scan

HEADER=["species","region","period","location","device","year","startdate","quartiles","mean_temp","night_length","total_nightly_activity","n","prop_activity"]
HOUR=["species","region","period","location","device","year","startdate","hours_after_sunset_group","mean_temp","night_length","total_nightly_activity","prop_activity"]
NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
def worksheet(names,groups=2,dup=False):
    def cell(idx,txt):
        # Inline strings in categorical source; numerical response is never read by gate.
        col=chr(65+idx)
        return f'<c r="{col}1" t="inlineStr"><is><t>{txt}</t></is></c>'
    top='<row r="1">'+''.join(cell(i,n) for i,n in enumerate(names))+'</row>'
    rows=[top]; j=2
    for night in range(groups):
        for quartile in range(6):
            row={"species":"Eptesicus","region":"North" if night%2 else "South",
                 "period":"Summer","location":"L1","device":"D1",
                 "year":str(2020+night),"startdate":"2020-06-"+str(night+1),
                 "quartiles":str(quartile+1),"hours_after_sunset_group":str(quartile+1),
                 "mean_temp":"9999999","night_length":"-999",
                 "total_nightly_activity":"999","prop_activity":"0.99","n":"3"}
            if dup and night==0 and quartile==5:row[names[7]]="1"
            rowtxt='<row r="'+str(j)+'">'
            for i,k in enumerate(names):
                col=chr(65+i)
                if k in ("mean_temp","night_length","total_nightly_activity","prop_activity","n"):
                    rowtxt+=f'<c r="{col}{j}"><v>{row[k]}</v></c>'
                else:
                    rowtxt+=f'<c r="{col}{j}" t="inlineStr"><is><t>{row[k]}</t></is></c>'
            rowtxt+='</row>';rows.append(rowtxt);j+=1
    return '<worksheet xmlns="'+NS+'"><sheetData>'+''.join(rows)+'</sheetData></worksheet>'
def fake(night_n=2,dup=False):
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,'w') as z:
        z.writestr('xl/workbook.xml','<workbook xmlns="'+NS+'"><sheets><sheet name="Quartiles" sheetId="1"/><sheet name="Hours" sheetId="2"/></sheets></workbook>')
        z.writestr('xl/worksheets/sheet1.xml',worksheet(HEADER,night_n,dup))
        z.writestr('xl/worksheets/sheet2.xml',worksheet(HOUR,night_n,dup))
    return blob.getvalue()
class Gates(unittest.TestCase):
    def test_quartile_keys(self):
        r=audit(fake())
        q=r["files"]["xl/worksheets/sheet1.xml"]
        self.assertEqual(q["rows"],12)
        self.assertEqual(q["source_night_keys"],2)
        self.assertEqual(q["source_nights_with_exactly_6_distinct_bins"],2)
        self.assertEqual(q["source_original_bin_labels"],["1","2","3","4","5","6"])
        self.assertEqual(q["nights_with_6_bins_and_all_nonempty_n_and_prop_activity"],2)
        self.assertFalse(r["raw_bat_activity_weather_values_opened"])
        self.assertNotIn("9999999",str(r))
    def test_duplicate_prevents_admission(self):
        r=audit(fake(dup=True))
        q=r["files"]["xl/worksheets/sheet1.xml"]
        self.assertEqual(q["source_duplicate_night_bin_keys"],1)
        self.assertEqual(r["admission"],"V38C_SIX_BIN_SOURCE_SUPPORT_STOP")
    def test_six_bin_rule_hard_threshold(self):
        r=audit(fake())
        self.assertFalse(r["predeclared_conditions"]["one_thousand_unique_nights"])
    def test_hour_groups_separate_from_quartile_bins(self):
        r=audit(fake())
        q=r["files"]["xl/worksheets/sheet2.xml"]
        self.assertEqual(q["source_night_keys"],2)
        self.assertIn("hours_after_sunset_group",q["original_header_columns"])
if __name__=="__main__":unittest.main()
