import unittest
from .marais_annual_transfer_v4 import source_grammar_amendment
class TestOriginalDomainAmendment(unittest.TestCase):
 def test_two_documented_anomalies_and_entire_site18_exclusion(self):
  good=[(2,{0:'Survey_ID'}),(3,{0:'2018_18'}),(4,{0:'2018_17'})]
  for i,k in enumerate(['2019_18','2020_18'],start=5):
   row={0:k,58:100.}
   for j in range(10,58):row[j]=0.
   row[56]=.5
   good.append((i,row))
  out,bad=source_grammar_amendment(good)
  self.assertEqual(len(bad),2)
  self.assertEqual([r[1][0] for r in out if 0 in r[1]],['Survey_ID','2018_17'])
 def test_anomaly_not_silently_ignored(self):
  with self.assertRaises(ValueError):source_grammar_amendment([(3,{0:'2018_18'})])
if __name__=='__main__':unittest.main()
