import unittest
from comparative_state.usgs_wetland_cv_transfer_v6e import normalize_years,EXPECTED

class TestYearOnlyAmendment(unittest.TestCase):
    def audit(self):return {'status':'SOURCE_YEAR_GRAMMAR_ADMITTED',
          'year_token_to_calendar_year_counts':EXPECTED,'date_format_counts':{'%m/%d/%Y':240}}
    def good_rows(self):return [{'Study year':'Year1','Date':'2/2/2022'} for _ in range(136)]+[
                      {'Study year':'Year2','Date':'2/2/2023'} for _ in range(104)]
    def test_exact_grammar(self):
        rows=normalize_years(self.good_rows(),self.audit())
        self.assertEqual([rows[0]['Study year'],rows[-1]['Study year']],['2022','2023'])
    def test_unknown_label_stop(self):
        rows=self.good_rows();rows[0]['Study year']='Year0'
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_YEAR_TOKEN'):normalize_years(rows,self.audit())
    def test_bad_year_mapping_stop(self):
        a=self.audit();a['year_token_to_calendar_year_counts']={'Year1':{'2023':136},'Year2':{'2022':104}}
        with self.assertRaisesRegex(ValueError,'YEAR_MAPPING'):normalize_years(self.good_rows(),a)
    def test_bad_rows_stop(self):
        with self.assertRaisesRegex(ValueError,'ROW_COUNT'):normalize_years(self.good_rows()[:-1],self.audit())

if __name__=='__main__':unittest.main()
