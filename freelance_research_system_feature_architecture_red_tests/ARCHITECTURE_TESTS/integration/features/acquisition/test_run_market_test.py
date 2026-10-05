from ARCHITECTURE_TESTS.support.integration import ProjectCase
M='research_system.features.acquisition.run_market_test'
class MarketAcquisitionFeatureTests(ProjectCase):
    def test_records_declared_exposure_cost_period_and_responses_without_claiming_global_demand(self):
        r=self.feature(M,{'service_unit_id':'svc1','channel_id':'c1','offer':'offer','attempt_count':10,'exposure':100,'cost':5,'period':['2026-10-01','2026-10-07'],'responses':2},now='2026-10-08T00:00:00+00:00')
        for k in ['channel_id','attempt_count','exposure','cost','period','responses']: self.assertIn(k,r)
        self.assertNotIn('global_demand',r); self.assertNotIn('passive_job_frequency',r)
