"""Private bounded UI projection; does not extend canonical BANK_QUERY/DDL."""
from pathlib import Path
import json,sqlite3,sys
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'EXPERIMENTS/local_command_adapter'))
import commands
read=commands.read;im=commands.im
PROTOCOL='local-bank-ui-list/1'
class Discovery:
    def __init__(self,bank_root,*,_limits=None,_hook=None):
        self.root=Path(bank_root);self.limits={**read.ReadAPI(self.root).limits,**json.loads((Path(__file__).parent/'LIMITS.json').read_text()),**(_limits or {})};self.hook=_hook;self.contracts=im.Contracts();self.result_validator=Draft202012Validator(json.loads((Path(__file__).parent/'discovery_result.schema.json').read_text()),format_checker=FormatChecker());self.validator=Draft202012Validator(json.loads((Path(__file__).parent/'discovery.schema.json').read_text()))
    def execute(self,q):
        seq=None;budget=read.Budget(self.limits)
        try:
            read.need(isinstance(q,dict) and len(im.encoded(q))<=16384,'INVALID_REQUEST');read.need(next(self.validator.iter_errors(q),None)is None,'INVALID_REQUEST')
            for k in ['limit','snapshot_sequence']:read.need(q[k] is None or type(q[k])is int,'INVALID_REQUEST')
            read.need(self.root.is_absolute() and '..' not in self.root.parts,'BANK_UNAVAILABLE')
            with im.Store(self.root,contracts=self.contracts) as store,read.ReadSession(store,budget,self.hook) as session:
                seq=session.snapshot if q['snapshot_sequence'] is None else q['snapshot_sequence'];read.need(seq<=session.snapshot,'SNAPSHOT_NOT_AVAILABLE')
                if seq:read.need(session.c.execute('SELECT 1 FROM commits WHERE commit_sequence=?',(seq,)).fetchone() is not None,'SNAPSHOT_NOT_AVAILABLE')
                after=q['after_object_id'] or '';items=[];candidates=0
                while len(items)<=q['limit']:
                    budget.tick();next_id=session.c.execute('SELECT object_id FROM revisions WHERE object_id>? ORDER BY object_id LIMIT 1',(after,)).fetchone()
                    if next_id is None:break
                    after=next_id[0];read.need(isinstance(after,str) and bool(im.reader.UUID.fullmatch(after)),'INTEGRITY_ERROR');candidates+=1;read.need(candidates<=self.limits['candidate_seeks'],'LIMIT_EXCEEDED')
                    row=session.c.execute('SELECT revision_id,object_id,object_type,commit_sequence,document_path FROM revisions WHERE object_id=? AND commit_sequence<=? ORDER BY commit_sequence DESC LIMIT 1',(after,seq)).fetchone()
                    if row is None:continue
                    read.need(row[2] in read.TYPES,'INTEGRITY_ERROR')
                    if row[2] not in q['object_types']:continue
                    d,commit=session.document(row);items.append({'ref':read.ref(d),'title':d['title'],'commit_sequence':row[3],'accepted_at':commit['row'][3]})
                more=len(items)>q['limit'];items=items[:q['limit']];result={'protocol':PROTOCOL,'status':'OK','code':'OK','snapshot_sequence':seq,'items':items,'has_more':more,'next_after_object_id':items[-1]['ref']['object_id'] if more else None};read.need(next(self.result_validator.iter_errors(result),None)is None,'INTEGRITY_ERROR');read.need(len(im.encoded(result))<=self.limits['list_response_bytes'],'LIMIT_EXCEEDED');budget.tick();return result
        except read.ReadError as e:code=e.code
        except im.Problem as e:code='BANK_UNAVAILABLE' if e.code in ['STORE_CLOSED','UNTRUSTED_TEST_ROOT','UNTRUSTED_TEST_PARENT'] else 'INTEGRITY_ERROR'
        except sqlite3.Error as e:code='LIMIT_EXCEEDED' if budget.exceeded else ('BANK_BUSY' if (getattr(e,'sqlite_errorcode',0) or 0)&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED] else 'INTEGRITY_ERROR')
        except (im.reader.Rejected,ValueError,KeyError,TypeError,UnicodeError):code='INTEGRITY_ERROR'
        except (OSError,im.native.SafetyError):code='BANK_UNAVAILABLE'
        return {'protocol':PROTOCOL,'status':'ERROR','code':code,'snapshot_sequence':seq,'items':[],'has_more':False,'next_after_object_id':None}
