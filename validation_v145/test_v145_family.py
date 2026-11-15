import unittest
from v145_family import holm_adjust

class HolmKnownTruth(unittest.TestCase):
    def test_ordered_and_indifferent_to_input_order(self):
        self.assertEqual(holm_adjust([.4,.01,.02]),[.4,.03,.04])
        self.assertEqual(holm_adjust([.01,.02,.4]),[.03,.04,.4])
    def test_ties_retained(self):
        self.assertEqual(holm_adjust([.0005,.0005,.0005]),[.0015,.0015,.0015])
    def test_empty(self):
        self.assertEqual(holm_adjust([]),[])
if __name__=="__main__":unittest.main()
