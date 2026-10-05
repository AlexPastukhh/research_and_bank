from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from .future import call_feature, tree_digest

class EmptyRootCase(unittest.TestCase):
    def setUp(self):
        self._td=tempfile.TemporaryDirectory(); self.addCleanup(self._td.cleanup); self.root=Path(self._td.name)/'project'
    def feature(self,module,request,*,now=None,**kwargs): return call_feature(module,self.root,request,now=now,**kwargs)

class ProjectCase(EmptyRootCase):
    def setUp(self):
        super().setUp()
        self.feature('research_system.features.project.start',{'project_id':'p1','research_day_timezone':'UTC'},now='2026-10-01T00:00:00+00:00')
    def digest(self): return tree_digest(self.root)
