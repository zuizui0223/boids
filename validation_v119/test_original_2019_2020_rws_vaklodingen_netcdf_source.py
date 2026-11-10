"""v119 synthetic known truths for TRUE metadata, never field biology."""
from __future__ import annotations
import tempfile,unittest
from pathlib import Path
import numpy as np
from netCDF4 import Dataset
import original_2019_2020_rws_vaklodingen_netcdf_source as q

class HistoricalRWSBathymetrySourceTruth(unittest.TestCase):
    def test_fixed_exact_original_2019_2020_archive_URL_ID_and_expected_bytes(self):
        self.assertEqual(q.NATIVE_ORIGINAL['2019'],('20190712_vaklodingen.nc',3594788))
        self.assertEqual(q.NATIVE_ORIGINAL['2020'],('20200717_vaklodingen.nc',3991532))
        self.assertEqual(len(q.NATIVE_ORIGINAL),2)
        self.assertIn('Vaklodingen',q.PREFIX)
        with self.assertRaisesRegex(ValueError,'UNFROZEN'):
            q.download_original_snapshot('2025_positive_sediment.nc',1000,'unused')
    def test_original_CF_and_native_EPSG_NAP_can_identify_valid_fixed_geographies(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'known_truth.nc'
            with Dataset(path,'w',format='NETCDF4') as d:
                d.createDimension('x',3);d.createDimension('y',3)
                x=d.createVariable('x','f4',('x',))
                y=d.createVariable('y','f4',('y',))
                z=d.createVariable('z','f4',('y','x'),fill_value=-9999.)
                x[:]=[35000,40500,46000]
                y[:]=[400000,405000,415000]
                z[:]=np.ones((3,3))
                d.crs='EPSG:28992'
                d.vertical_datum='NAP'
                x.units='m';y.units='m';z.units='m'
            out=q.geo_source_first(path,'2019')
            geo=out['geographical_datum_source_QA']
            self.assertTrue(geo['source_native_CRS_verified_EPSG28992'])
            self.assertTrue(geo['source_vertical_NAP_string_present_in_native_metadata'])
            self.assertTrue(geo['native_public_landmark_geographic_bbox_assessment'][
                'Roggenplaat shoal']['source_fixed_locus_within_original_raw_NC_coordinate_BBOX_only'])
            self.assertEqual(out['candidate_bed_elevation_or_depth_source_variables_PRIORITY_BEFORE_DATA_VALUES'][0]['native_variable_name'],'z')
    def test_NAP_CRS_unspecified_cannot_be_grafted_onto_native_XY(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'no_crs.nc'
            with Dataset(path,'w',format='NETCDF4') as d:
                d.createDimension('x',2);d.createDimension('y',2)
                d.createVariable('x','f4',('x',))[:]=[35e3,45e3]
                d.createVariable('y','f4',('y',))[:]=[404e3,410e3]
                d.createVariable('z','f4',('y','x'))[:]=np.ones((2,2))
            out=q.geo_source_first(path,'2020')
            geo=out['geographical_datum_source_QA']
            self.assertFalse(geo['source_native_CRS_verified_EPSG28992'])
            self.assertEqual(geo['native_public_landmark_geographic_bbox_assessment'][
                  'Roggenplaat shoal']['source_status'],'NO_CERTIFIED_NATIVE_GEOREFERENCE')
    def test_original_source_missing_coords_cannot_be_zero_bathymetry(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'missing.nc'
            with Dataset(path,'w',format='NETCDF4') as d:
                d.createDimension('sample',2)
                d.createVariable('depth','f4',('sample',))[:]=[1.,2.]
            out=q.geo_source_first(path,'2020')
            geo=out['geographical_datum_source_QA']
            self.assertEqual(geo['native_public_landmark_geographic_bbox_assessment'],{})
            self.assertEqual(out['source_data_quality_status'],'TRUE_ORIGINAL_NETCDF_METADATA_ADMITTED')
    def test_no_biological_claims_from_rws_netcdf_source(self):
        self.assertIn('NOT a filled Zeeland coastline',q.__doc__)
        self.assertTrue(q.NO_ECOLOGICAL_USED_AVAILABLE_BEHAVIOR)
if __name__=="__main__":unittest.main()
