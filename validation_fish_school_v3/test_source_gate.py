"""Source gate known-truth structural tests. These do not download field data."""
import io,unittest,zipfile
from dryad_source_gate import SourceStop,zip_structure,receiver_structure,numeric_id,collection

class GateTests(unittest.TestCase):
    def test_exact_five_receivers(self):
        x=b"x,y,z\n1,2,A\n2,2,B\n3,2,C\n4,2,D\n5,2,E\n"
        self.assertEqual(receiver_structure(x)["receiver_coordinate_rows"],5)
    def test_insufficient_receivers_stop(self):
        with self.assertRaises(SourceStop):receiver_structure(b"x,y,z\n1,2,A\n")
    def test_zip_valid(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as z:z.writestr("data.csv","header\n")
        self.assertEqual(zip_structure(b.getvalue())["n_zip_members"],1)
    def test_zip_unsafe_name_stop(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as z:z.writestr("../bad.csv","header\n")
        with self.assertRaises(SourceStop):zip_structure(b.getvalue())
    def test_id_and_hypermedia(self):
        x={"_embedded":{"stash:versions":[{"id":12,"versionNumber":1}]}}
        self.assertEqual(numeric_id(collection(x,"version")[0],"versions"),12)

if __name__=="__main__":unittest.main()
