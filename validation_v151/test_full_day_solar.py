"""v151 original-independent bitset and decompositions."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from v151_full_day_solar import score_bits,source_date_scores,PAIRS

class TestV151(unittest.TestCase):
    def test_boundary_seam_and_central_partition(self):
        a=1<<23
        b=1<<23
        assert score_bits(a,b,tuple(range(24)),True)[0]==1
        assert score_bits(a,b,tuple(range(2,22)),False)[0]==0
        assert score_bits(a,b,(0,1,22,23),True)[0]==1
    def test_all_days_must_partition_light_classes(self):
        flags=[False]*24
        for i in range(8,16):flags[i]=True
        h=list(range(24))
        by={typ:0 for z in PAIRS for typ in z}
        by["Bocaccio"]=sum(1<<i for i in range(8,17))
        by["UF440"]=sum(1<<i for i in range(8,17))
        p, opportunities=source_date_scores("synthetic",h,by,flags)
        self.assertEqual(opportunities["full24_cyclic"],24)
        self.assertEqual(opportunities["central20_no_wrap"],20)
        self.assertEqual(opportunities["midnight_wrap_four_hours"],4)
        self.assertEqual(opportunities["solar_stable_no_wrap"]+opportunities["solar_transition_adjacent_no_wrap"],20)
    def test_focal_hour_safe_2h_shifts(self):
        with self.assertRaises(ValueError):score_bits(1,1,[0],False)
        self.assertEqual(score_bits(1<<10,1<<10,[10],False),[1,0,0,0,0])
        self.assertEqual(score_bits(1<<23,1<<23,[23],True)[0],1)

if __name__=="__main__":unittest.main()
