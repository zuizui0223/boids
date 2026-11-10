"""Scientific source-only gate: no paper figure or cloud listing becomes area estimate."""
import unittest
import real_intertidal2019_publisher_source as s
def fixture():
    return {'id':19334465,'title':'Murray Global Intertidal Change Classification v1.2 (1999-2019)',
       'doi':'10.6084/m9.figshare.19334465',
       'files':[{'name':'intertidal_2017-2019.tif','id':101,'size':3000,
                 'download_url':'https://springernature.figshare.com/ndownloader/files/101','computed_md5':'a'*32},
                {'name':'qa_2017-2019.tif','id':102,'size':400,
                 'download_url':'https://springernature.figshare.com/ndownloader/files/102'}]}
class NativeHabitatCatalogKnownTruth(unittest.TestCase):
    def test_true_2017_2019_source_raster_not_habitat_effect(self):
        r=s.genuine_figshare_file_manifest(fixture())
        self.assertEqual(r['original_files_n'],2)
        self.assertEqual(r['raster_file_count'],2)
        self.assertEqual(r['original_2019_temporal_candidate_files'],2)
        self.assertTrue(r['original_publisher_files'][1]['is_qa_or_mask_candidate'])
    def test_original_article_identity_must_not_drift(self):
        f=fixture();f['id']=19334466
        with self.assertRaisesRegex(ValueError,'ID_MISMATCH'):
            s.genuine_figshare_file_manifest(f)
    def test_wrong_year_product_must_not_pass(self):
        f=fixture();f['title']='Murray global intertidal v1.1 1984–2016'
        with self.assertRaisesRegex(ValueError,'NOT_CORRECT'):
            s.genuine_figshare_file_manifest(f)
    def test_untrusted_external_download_url_fails(self):
        f=fixture();f['files'][0]['download_url']='https://untrusted.example.net/fictional.tif'
        with self.assertRaisesRegex(ValueError,'NOT_AUTHENTICATED'):
            s.genuine_figshare_file_manifest(f)
    def test_do_not_request_random_sources(self):
        with self.assertRaisesRegex(ValueError,'UNAUTHORIZED'):
            s.fetch_json('https://example.org/untrusted')
if __name__=="__main__":unittest.main()
