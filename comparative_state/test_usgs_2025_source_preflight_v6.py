import unittest
from comparative_state.usgs_2025_source_preflight_v6 import validate_provider_manifest, ITEM_ID

class TestSourcePreflight(unittest.TestCase):
    def good(self):
        return {'id': ITEM_ID,
                'title':'Habitat Features and Waterbird Abundance and Diversity on Managed Wetlands Enrolled in the California Waterfowl Habitat Program',
                'files':[{'name':'bird_visit.csv','size':100,'downloadUri':'https://www.sciencebase.gov/catalog/file/get/test'}]}

    def test_valid_data_inventory_is_source_only(self):
        r=validate_provider_manifest(self.good())
        self.assertEqual(r['status'],'SOURCE_FILE_INVENTORY_ADMITTED')
        self.assertFalse(r['original_numeric_outcomes_opened'])

    def test_wrong_item_hard_stop(self):
        x=self.good();x['id']='other'
        self.assertEqual(validate_provider_manifest(x)['status'],'SOURCE_STOP_BAD_ITEM_ID')

    def test_wrong_title_hard_stop(self):
        x=self.good();x['title']='random unrelated'
        self.assertEqual(validate_provider_manifest(x)['status'],'SOURCE_STOP_UNEXPECTED_TITLE')

    def test_no_tabular_hard_stop(self):
        x=self.good();x['files']=[{'name':'paper.pdf'}]
        self.assertEqual(validate_provider_manifest(x)['status'],'SOURCE_STOP_NO_TABULAR_SOURCE')

    def test_untrusted_download_not_emitted(self):
        x=self.good();x['files'][0]['downloadUri']='https://evil.example.org/a.csv'
        self.assertIsNone(validate_provider_manifest(x)['plausible_original_data_files'][0]['downloadUri'])

if __name__ == '__main__':unittest.main()
