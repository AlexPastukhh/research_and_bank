from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.queries.trend'
class TrendQueryTests(ProjectCase):
    def test_trend_is_read_only_uses_existing_metric_and_represents_missing_windows(self):
        before=self.digest(); r=self.feature(M,{'metric_id':'budget:svc1','scope':'market:x','grain':'day','from':'2026-10-01','to':'2026-10-07'},now='2026-10-08T08:00:00+00:00'); self.assertEqual(self.digest(),before)
        for k in ['series_id','metric_id','scope','grain','from','to','points','trend_stats']: self.assertIn(k,r)
        self.assertIn('missing_windows',r); self.assertFalse(r.get('measurement_created',False))
