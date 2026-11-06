import unittest
from datetime import datetime, timezone
import numpy as np
from run_bearing_audit import check_replay, require_original

class OriginalReplayTests(unittest.TestCase):
    def fixture(self):
        n=4678
        rows=[{'id':str(i%5),'t':datetime(2011,6,1,tzinfo=timezone.utc)} for i in range(n)]
        truth=np.tile([1.,0.],(n,1))
        a=np.tile([1-np.sqrt(2*.5107931836556263),0.],(n,1))
        b=np.tile([1-np.sqrt(2*.43464618382116776),0.],(n,1))
        return rows,truth,a,b
    def test_exact_full_cohort_replay_passes(self):
        rows,y,a,b=self.fixture()
        r=check_replay(rows,y,a,b,site='ameland',train_count=3753)
        self.assertTrue(r['original_v43_replay_verified'])
    def test_changed_original_count_loss_or_year_stops(self):
        rows,y,a,b=self.fixture()
        for rr,yy,aa,bb,train in [(rows[:-1],y[:-1],a[:-1],b[:-1],3753),
                                (rows,y,a,b+.001,3753),(rows,y,a,b,3752)]:
            with self.assertRaises(ValueError):
                check_replay(rr,yy,aa,bb,site='ameland',train_count=train)
        rows[0]['t']=datetime(2010,6,1,tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            check_replay(rows,y,a,b,site='ameland',train_count=3753)
    def test_authentic_checksum_and_provider_verification_both_required(self):
        m={'provider_original_md5_matched':True,'original_sha256':'c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c'}
        self.assertTrue(require_original(m,'ameland',2010))
        for bad in [{**m,'provider_original_md5_matched':False},{**m,'original_sha256':'0'*64}]:
            with self.assertRaises(ValueError): require_original(bad,'ameland',2010)

if __name__=='__main__':unittest.main()
