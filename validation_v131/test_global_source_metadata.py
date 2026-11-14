"""v131 pure tests. Synthetic metadata is NOT observed biological evidence."""
from __future__ import annotations
from copy import deepcopy
import json
import unittest
import run_source_metadata_and_literature as m

class GlobalMetaSourceAndLiteratureKnownTruth(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads(m.SOURCE_FILE.read_text())
        self.src=next(x for x in self.registry['entries'] if x['id']=='O_VLIELAND')

    def test_candidate_registry_has_geographical_and_taxonomic_scope_without_false_meta(self):
        info=m.validate_registry(self.registry)
        self.assertEqual(info['raw_effects_currently_admitted_to_global_meta'],0)
        self.assertEqual(info['previous_known_source_backed_2018_Vlieland_single_site'],1)
        self.assertGreaterEqual(info['source_register_seed_n'],10)
        self.assertIn('crustacean',info['candidate_functional_groups'])
        self.assertIn('fish',info['candidate_functional_groups'])
        self.assertIn('East Asian Pacific',info['candidate_regions_metadata_not_global_biological_replication'])

    def test_no_unverified_source_can_be_marked_as_previous_effect(self):
        x=deepcopy(self.registry)
        other=next(z for z in x['entries'] if z['id']=='HG_TEXEL')
        other['candidate_status']='previous_single_site_field_effect_observed'
        with self.assertRaisesRegex(ValueError,'UNSEEN_FIELD_EFFECT'):
            m.validate_registry(x)
        x=deepcopy(self.registry)
        x['entries'].append(deepcopy(x['entries'][0]))
        with self.assertRaisesRegex(ValueError,'DUPLICATED_SOURCE_ID'):
            m.validate_registry(x)

    def test_real_firstparty_manifest_shape_must_contain_expected_native_files(self):
        raw={'id':10053988,'metadata':{'title':'O_VLIELAND - original'},'files':[
          {'key':'O_VLIELAND-gps-2018.csv.gz','size':121,'checksum':'md5:'+'a'*32},
          {'key':'O_VLIELAND-accessory-measurements-2018.csv.gz','size':55,'checksum':'md5:'+'b'*32}]}
        x=m.audit_zenodo_record(self.src,raw,'cafecafe')
        self.assertEqual(x['status'],'TRUE_ORIGINAL_ZENODO_SOURCE_METADATA_ADMITTED')
        self.assertEqual(x['native_catalog_original_GPS_yearfiles'],1)
        self.assertEqual(x['native_catalog_original_behavior_class_yearfiles'],1)
        self.assertNotIn('individual',str(x))
        r=deepcopy(raw);r['id']=999
        with self.assertRaisesRegex(ValueError,'WRONG_ZENODO_RECORD_ID'):
            m.audit_zenodo_record(self.src,r,'cafecafe')
        r=deepcopy(raw);r['files']=r['files'][:1]
        with self.assertRaisesRegex(ValueError,'CLASSIFIED_BEHAVIOR_FILE_NOT_PRESENT'):
            m.audit_zenodo_record(self.src,r,'cafecafe')
        r=deepcopy(raw);r['files'][1]['checksum']='NO_PROVIDER_MD5'
        with self.assertRaisesRegex(ValueError,'MD5_SIZE_INVALID'):
            m.audit_zenodo_record(self.src,r,'cafecafe')

    def test_gps_only_source_not_converted_to_assumed_behavior_classifier(self):
        x=next(z for z in self.registry['entries'] if z['id']=='DELTATRACK')
        raw={'id':10209521,'metadata':{'title':'DELTATRACK'},'files':[
          {'key':'DELTATRACK-gps-2020.csv.gz','checksum':'md5:'+'f'*32,'size':800}]}
        row=m.audit_zenodo_record(x,raw,'1234')
        self.assertEqual(row['native_catalog_original_behavior_class_yearfiles'],0)
        self.assertTrue(row['source_catalog_only_no_raw_rows_or_biological_effect'])

    def test_bibliographic_dedup_uses_article_doi_not_multiple_sources_as_replication(self):
        a={'resultList':{'result':[
          {'title':'Tide and crabs','doi':'https://doi.org/10.1000/CRAB','pubYear':'2022','pmid':'111'},
          {'title':'Solar shorebird movement','doi':'10.1000/bird','pubYear':'2025'}]}}
        b={'resultList':{'result':[
          {'title':'Tide and crabs','doi':'10.1000/crab','pubYear':'2022'},
          {'title':'Future report','doi':'10.1000/future','pubYear':'2027'}]}}
        one=m.harvest_europepmc_query('crab','q',a)
        two=m.harvest_europepmc_query('general','q',b)
        merged=m.dedup_literature_queries({'crab':one,'general':two})
        self.assertEqual(len(merged),2)
        first=next(x for x in merged if x['doi']=='10.1000/crab')
        self.assertEqual(first['query_groups'],['crab','general'])
        self.assertTrue(first['metadata_only_no_fulltext_eligibility_or_effect'])

    def test_known_reviews_or_metadata_not_automatically_eligible_field_effect(self):
        self.assertEqual(m.SEARCH_CUTOFF,2026)
        self.assertGreaterEqual(len(m.QUERIES),6)
        self.assertEqual(len({x['independence_group'] for x in self.registry['entries']}),
                         len(self.registry['entries']))
        x=next(z for z in self.registry['entries'] if z['id']=='ARCTIC_CHAR_LAKE_TROUT_CONTROL')
        self.assertIn('solar_only',x['candidate_status'])
        self.assertNotEqual(x['region'],'European Atlantic')

if __name__=='__main__':
    unittest.main()
