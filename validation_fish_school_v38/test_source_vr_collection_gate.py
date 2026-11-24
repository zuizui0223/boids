"""v38 original Figshare fish VR six-speed source-only source identity fixtures."""
import json
import unittest
from validation_fish_school_v38.source_vr_collection_gate import (
    author_article_manifest,author_collection_manifest,decode_json_bytes,SourceStop,COLLECTION
)
def article(a=29097605):
    return {"id":a,"title":"Test authentic original fish VR dataset",
            "doi":f"10.6084/m9.figshare.{a}.v1",
            "files":[{"id":11,"name":"experiment_trial_ids.csv","size":12000,
                     "supplied_md5":"0"*32,"computed_md5":"0"*32,
                     "download_url":"https://ndownloader.figshare.com/files/11"}]}
def coll():
    return {"id":COLLECTION,"title":"Six-speed fish original public supplementary",
            "doi":f"10.6084/m9.figshare.c.{COLLECTION}.v1","is_public":True}
def items():
    return [{"id":555,"title":"Original condition session data","doi":"10.6084/m9.figshare.555"}]
class PublisherOriginalSourceOnly(unittest.TestCase):
    def test_true_author_article_metadata_is_only_manifest(self):
        r=author_article_manifest(article(),29097605)
        self.assertEqual(r["status"],"ORIGINAL_PUBLISHER_FIGSHARE_ARTICLE_METADATA_VERIFIED")
        self.assertEqual(r["n_original_published_files"],1)
        self.assertTrue(r["original_animals_sessions_and_trails_NOT_verified"])
        self.assertFalse(r["original_provider_filename_MD5_size_manifest"][0]["original_fish_data_file_content_read"])
    def test_original_article_doi_or_id_must_match(self):
        a=article();a["doi"]="10.6084/m9.figshare.500.v1"
        with self.assertRaises(SourceStop):author_article_manifest(a,29097605)
        a=article();a["id"]=501
        with self.assertRaises(SourceStop):author_article_manifest(a,29097605)
    def test_original_author_collection_source_ids_only(self):
        r=author_collection_manifest(coll(),items())
        self.assertEqual(r["original_member_article_IDs"],[555])
        self.assertTrue(r["collection_member_full_original_file_manifests_NOT_ACCESSED"])
    def test_original_author_collection_doi_not_ambiguous(self):
        a=coll();a["doi"]="10.6084/m9.figshare.c.999"
        with self.assertRaises(SourceStop):author_collection_manifest(a,items())
    def test_more_than_50_articles_hard_stop(self):
        big=[{"id":i+1,"title":f"Article{i}"} for i in range(51)]
        with self.assertRaises(SourceStop):author_collection_manifest(coll(),big)
    def test_api_error_html_or_message_stop(self):
        with self.assertRaises(SourceStop):decode_json_bytes(b"<html>Authentication</html>")
        with self.assertRaises(SourceStop):decode_json_bytes(json.dumps({"message":"not authorized"}).encode())
    def test_original_supplement_video_not_misidentified_as_Fortran_source(self):
        original=article()
        original["files"][0]["name"]="rspb20260146_si_003.mov"
        video=author_article_manifest(original,29097605)
        self.assertEqual(video["original_provider_filename_MD5_size_manifest"][0]["potential_role_FROM_FILENAME_ONLY"],
                         "PUBLISHED_VIDEO_OR_MOVIE_NOT_ORIGINAL_TRACKING_ROWS")
        original["files"][0]["name"]="rspb20260146_si_001.pdf"
        pdf=author_article_manifest(original,29097605)
        self.assertEqual(pdf["original_provider_filename_MD5_size_manifest"][0]["potential_role_FROM_FILENAME_ONLY"],
                         "PUBLISHED_PDF_SUPPLEMENT_NOT_INDIVIDUAL_FISH_DATA")

    def test_invalid_published_source_file_md5_stops(self):
        a=article();a["files"][0]["supplied_md5"]="BAD"
        with self.assertRaises(SourceStop):author_article_manifest(a,29097605)
if __name__=="__main__":unittest.main()
