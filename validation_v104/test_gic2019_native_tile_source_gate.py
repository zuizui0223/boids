import unittest
import gic2019_native_tile_source_gate as m
class True2019Source(unittest.TestCase):
    def test_exact_provider_year_prefix(self):
        self.assertEqual(len(m.TARGET_SUFFIXES),4)
        self.assertIn('2019',m.source_url(m.TARGET_SUFFIXES[0]))
        with self.assertRaisesRegex(ValueError,'NOT_FROZEN'):
            m.source_url('favorable-positive-ecology')
    def test_original_bucket_object_different_from_site_habitat(self):
        pref=m.TARGET_SUFFIXES[0]
        doc={'items':[{'name':m.FIXED_BASE+pref+'0000000000-0000000000.tif',
                        'contentType':'image/tiff','size':'28606510','generation':'1'}]}
        rows=m.original_objects(doc,pref)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['size_bytes'],28606510)
        self.assertTrue(rows[0]['source_URL_unmodified'].startswith('https://storage.googleapis.com/gic-archive/'))
    def test_other_raster_gain_type_cannot_be_t7_probability(self):
        p=m.TARGET_SUFFIXES[0]
        data={'items':[{'name':m.FIXED_BASE+'murray-gic-v1.0.1-gain-0000000000-0000000000.tif',
                        'contentType':'image/tiff','size':'1000'}]}
        self.assertEqual(m.original_objects(data,p),[])
    def test_not_a_raster_mimetype_protection(self):
        p=m.TARGET_SUFFIXES[0]
        doc={'items':[{'name':m.FIXED_BASE+p+'tile.tif','contentType':'text/plain','size':'0'}]}
        with self.assertRaisesRegex(ValueError,'MIME'):
            m.original_objects(doc,p)
if __name__=='__main__':unittest.main()
