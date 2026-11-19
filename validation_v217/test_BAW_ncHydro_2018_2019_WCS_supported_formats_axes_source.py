import unittest
from validation_v217.BAW_ncHydro_2018_2019_WCS_supported_formats_axes_source import (
 FROZEN_WCS_CAP_SHA,FROZEN_COVERAGE_IDS,FROZEN_DESCRIBE_SHA,
 source_native_formats,source_native_description_axes,FROZEN_NATIVE_NIL
)

class TrulyAuthenticatedYearlyBAWWCSAxes(unittest.TestCase):
    def test_both_years_SHA_pinned_and_no_crop_in_source_layer(self):
        self.assertEqual(set(FROZEN_WCS_CAP_SHA),{"2018","2019"})
        self.assertEqual(set(FROZEN_COVERAGE_IDS),{"2018","2019"})
        self.assertEqual(set(FROZEN_DESCRIBE_SHA),{"2018","2019"})
        for year in ("2018","2019"):
            self.assertEqual(len(FROZEN_WCS_CAP_SHA[year]),64)
            self.assertEqual(len(FROZEN_DESCRIBE_SHA[year]),64)
            self.assertIn("sea_surface_height_2d",FROZEN_COVERAGE_IDS[year])

    def test_original_capabilities_native_formats_not_imputed(self):
        xml=b'''<wcs:Capabilities xmlns:wcs="http://www.opengis.net/wcs/2.0"
             xmlns:ows="http://www.opengis.net/ows/2.0" version="2.0.1">
           <ows:OperationsMetadata><ows:Operation name="GetCoverage"/></ows:OperationsMetadata>
           <wcs:ServiceMetadata><wcs:formatSupported>image/tiff</wcs:formatSupported>
             <wcs:formatSupported>application/x-netcdf</wcs:formatSupported>
           </wcs:ServiceMetadata></wcs:Capabilities>'''
        x=source_native_formats(xml)
        self.assertTrue(x["native_declared_GetCoverage"])
        self.assertEqual(x["native_explicit_NetCDF_output_format_if_any"],["application/x-netcdf"])
        self.assertEqual(x["native_explicit_GeoTIFF_output_format_if_any"],["image/tiff"])
        none=source_native_formats(xml.replace(b"application/x-netcdf",b"application/json"))
        self.assertEqual(none["native_explicit_NetCDF_output_format_if_any"],[])

    def test_true_coverage_envelope_grid_time_uom_nil_no_binary_claim(self):
        xml=f'''<wcs:CoverageDescriptions xmlns:wcs="http://www.opengis.net/wcs/2.0"
             xmlns:gml="http://www.opengis.net/gml/3.2"
             xmlns:swe="http://www.opengis.net/swe/2.0">
           <wcs:CoverageDescription>
             <wcs:CoverageId>{FROZEN_COVERAGE_IDS["2018"]}</wcs:CoverageId>
             <gml:boundedBy><gml:Envelope srsName="EPSG:4326" axisLabels="Lon Lat">
               <gml:lowerCorner>4 52</gml:lowerCorner><gml:upperCorner>10 56</gml:upperCorner>
             </gml:Envelope></gml:boundedBy>
             <gml:domainSet><gml:RectifiedGrid dimension="2">
               <gml:origin><gml:Point><gml:pos>4.0 52.0</gml:pos></gml:Point></gml:origin>
               <gml:offsetVector>0.005 0</gml:offsetVector>
               <gml:offsetVector>0 0.005</gml:offsetVector></gml:RectifiedGrid></gml:domainSet>
             <wcs:ServiceParameters/>
             <gml:rangeType><swe:DataRecord><swe:field name="Wasserstand">
               <swe:Quantity><swe:uom code="m"/>
               <swe:nilValues><swe:nilValue reason="unknown">{FROZEN_NATIVE_NIL}</swe:nilValue>
               </swe:nilValues></swe:Quantity></swe:field></swe:DataRecord></gml:rangeType>
           </wcs:CoverageDescription>
        </wcs:CoverageDescriptions>'''.encode()
        a=source_native_description_axes(xml,FROZEN_COVERAGE_IDS["2018"])
        self.assertEqual(a["source_native_envelopes"][0]["native_axisLabels"],"Lon Lat")
        self.assertEqual(a["source_native_grid_and_time_structure"][0]["native_tag"],"RectifiedGrid")
        self.assertEqual(len(a["source_native_grid_origins_offsets_limited"]),3)
        self.assertEqual(a["source_UOM_tags"][0]["native_uom_code"],"m")
        self.assertEqual(a["source_nil_values"][0]["native_literal"],FROZEN_NATIVE_NIL)
        self.assertTrue(a["model_WCS_service_metadata_not_original_NetCDF_variable_attrs"])

    def test_any_original_nil_or_uom_changed_must_stop(self):
        base=f'''<CoverageDescriptions><CoverageDescription><CoverageId>{FROZEN_COVERAGE_IDS["2019"]}</CoverageId>
           <rangeType><field name="Wasserstand"><uom code="m"/>
           <nilValue>{FROZEN_NATIVE_NIL}</nilValue></field></rangeType>
           </CoverageDescription></CoverageDescriptions>'''.encode()
        source_native_description_axes(base,FROZEN_COVERAGE_IDS["2019"])
        with self.assertRaisesRegex(ValueError,"NIL"):
            source_native_description_axes(base.replace(FROZEN_NATIVE_NIL.encode(),b"0"),FROZEN_COVERAGE_IDS["2019"])
        with self.assertRaisesRegex(ValueError,"UOM"):
            source_native_description_axes(base.replace(b'code="m"',b'code="cm"'),FROZEN_COVERAGE_IDS["2019"])
        with self.assertRaisesRegex(ValueError,"WRONG_OR_NONUNIQUE"):
            source_native_description_axes(base,FROZEN_COVERAGE_IDS["2018"])

if __name__=="__main__":
    unittest.main()
