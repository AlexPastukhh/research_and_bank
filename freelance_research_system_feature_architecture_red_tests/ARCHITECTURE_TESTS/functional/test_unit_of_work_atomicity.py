import tempfile, unittest
from pathlib import Path
from ARCHITECTURE_TESTS.support.future import require_symbol

class UnitOfWorkAtomicityTests(unittest.TestCase):
    def test_multi_aggregate_commit_is_all_or_nothing_under_fault(self):
        """PROPOSAL driven by AX13 crash-window: infrastructure transaction is functional-tested separately."""
        U=require_symbol('research_system.infrastructure.filesystem.unit_of_work','FilesystemUnitOfWork')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'a.json').write_text('{"v":1}',encoding='utf-8'); (root/'b.json').write_text('{"v":1}',encoding='utf-8')
            try:
                with U(root,fault_at='after_first_replace') as u:
                    u.write_json('a.json',{'v':2}); u.write_json('b.json',{'v':2}); u.commit()
            except Exception:
                pass
            U.recover(root)
            a=(root/'a.json').read_text(); b=(root/'b.json').read_text(); self.assertTrue((a=='{"v":1}' and b=='{"v":1}') or ('"v": 2' in a and '"v": 2' in b),f'partial commit: {a} / {b}')
