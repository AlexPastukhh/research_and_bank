from ARCHITECTURE_TESTS.support.integration import ProjectCase
from ARCHITECTURE_TESTS.support.future import assert_error_code
M='research_system.features.measurement.measure'
class MeasureFeatureTests(ProjectCase):
    def test_one_atomic_measurement_contains_one_unit_scope_metric_method_coverage_and_missingness(self):
        r=self.feature(M,{'service_unit_id':'svc1','scope':'market:x','metric_type':'budget','method_id':'budget-v1','method_version':'1','source_route_ids':['s1'],'observation_window':['2026-09-01','2026-09-30'],'values':[10,20,None]},now='2026-10-01T02:00:00+00:00')
        for k in ['measurement_id','metric_type','method_id','method_version','coverage_status','missingness','limitations']: self.assertIn(k,r)
        self.assertEqual(r['metric_type'],'budget')
    def test_request_for_multiple_metrics_is_rejected(self):
        assert_error_code(self,'one_metric_per_measurement',lambda:self.feature(M,{'service_unit_id':'svc1','scope':'market:x','metric_type':['budget','competition'],'method_id':'m','method_version':'1'},now='2026-10-01T02:00:00+00:00'))
    def test_effective_rate_is_not_fabricated_when_required_inputs_are_missing(self):
        r=self.feature(M,{'service_unit_id':'svc1','scope':'market:x','metric_type':'effective_rate','method_id':'econ-v1','method_version':'1','inputs':{'payout':100}},now='2026-10-01T02:00:00+00:00')
        self.assertIn(r['coverage_status'],{'partial','failed'}); self.assertIsNone(r.get('value'))
