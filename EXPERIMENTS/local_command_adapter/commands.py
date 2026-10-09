"""Synthetic local entrypoint. Existing package/query protocols and sources unchanged."""
from pathlib import Path
from contextlib import ExitStack
import argparse,json,os,sqlite3,stat,sys,uuid
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'EXPERIMENTS/lexical_search'))
import search
read=search.read;im=search.im
sys.path.insert(0,str(ROOT/'EXPERIMENTS/first_bank'))
import attempts
STATES=['ACCEPTED','REPLAY','CONFLICT','REJECTED','INCOMPLETE','INTEGRITY_ERROR','IO_ERROR','RETRYABLE_BUSY','UNKNOWN','CANCELLED']
class ConfigurationError(Exception):pass
class Parser(argparse.ArgumentParser):
    def error(self,message):raise ConfigurationError('INVALID_CLI')
def valid_tx(value):return isinstance(value,str) and bool(im.reader.UUID.fullmatch(value))
def code_text(value,fallback):
    # Never disclose paths, payloads or exception text as diagnostics.
    return value if isinstance(value,str) and 0<len(value)<=64 and value[0].isupper() and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in value) else fallback
class Controller:
    def __init__(self,bank_root,*,intake_root=None,stage_root=None,cache_root=None,output_root=None,contracts=None,_transport=None,_store_factory=None,_hook=None,_read_limits=None,_search_limits=None,_limits=None):
        self.roots={k:Path(v) if v is not None else None for k,v in [('bank',bank_root),('intake',intake_root),('stage',stage_root),('cache',cache_root),('output',output_root)]};self.contracts=contracts or im.Contracts();self.transport=_transport or im.reader.read_package;self.store_factory=_store_factory or im.Store;self.hook=_hook;self.closed=False
        folder=Path(__file__).parent;self.limits=json.loads((folder/'LIMITS.json').read_text());self.limits.update(_limits or {});self.validator=Draft202012Validator(json.loads((folder/'save_result.schema.json').read_text()))
        self.reader=read.ReadAPI(self.roots['bank'],self.roots['output'],contracts=self.contracts,_limits=_read_limits)
        # With no cache configured this object is used only for its unchanged
        # pure validator, never for execute/rebuild or any filesystem access.
        self.search=search.SearchAPI(self.roots['bank'],self.roots['cache'] or self.roots['bank'],_limits=_search_limits)
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
    def close(self):
        self.closed=True
        try:self.reader.close()
        finally:self.search.close()
    def _event(self,name,value=None):
        if self.hook:self.hook(name,value)
    def _configuration(self):
        if self.closed:raise ConfigurationError('CONTROLLER_CLOSED')
        paths=[p for p in self.roots.values() if p is not None]
        if any(not p.is_absolute() or '..' in p.parts for p in paths):raise ConfigurationError('INVALID_ROOT_CONFIGURATION')
        for i,p in enumerate(paths):
            for q in paths[i+1:]:
                if p.is_relative_to(q) or q.is_relative_to(p):raise ConfigurationError('ROOT_OVERLAP')
    def _root(self,p):
        if p is None:raise ConfigurationError('ROOT_NOT_CONFIGURED')
        if os.name=='nt':return im.native.configured_root(p)
        # Portable fixture evidence only; native production path is above.
        st=p.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)&0o077 or any(x.is_symlink() for x in [p,*p.parents]):raise ConfigurationError('UNTRUSTED_PORTABLE_ROOT')
        return ExitStack()
    def _result(self,operation,state,code,tx=None,digest=None,receipt=None,cleanup='not_needed',diagnostic=None):
        r={'result_kind':'local_bank_command_outcome','result_version':1,'operation':operation if operation in ['bank.save','collection.save'] else None,'status':state,'code':code_text(code,'COMMAND_ERROR'),'transaction_id':tx if valid_tx(tx) else None,'manifest_sha256':digest,'receipt':receipt,'cleanup_status':cleanup,'diagnostic':code_text(diagnostic or code,'COMMAND_ERROR')}
        correlated=receipt is None or (receipt.get('status')==state and receipt.get('code')==code and receipt.get('transaction_id')==r['transaction_id'] and receipt.get('manifest_sha256')==digest)
        if not correlated or next(self.validator.iter_errors(r),None)is not None or len(im.encoded(r))>self.limits['save_response_bytes']:
            # Result conformance/output loss must not negate a possible commit.
            r.update(status='UNKNOWN',code='OUTPUT_OUTCOME_UNCERTAIN',receipt=None,diagnostic='OUTPUT_OUTCOME_UNCERTAIN')
            if next(self.validator.iter_errors(r),None)is not None:raise RuntimeError('INVALID_INTERNAL_OUTCOME')
        return r
    def save(self,operation,transaction_id):
        state='REJECTED';code='INVALID_REQUEST';receipt=None;digest=None;tx=transaction_id if valid_tx(transaction_id) else None;snapshot=None;entered=False;cleanup='not_needed';diagnostic=None
        try:
            if operation not in ['bank.save','collection.save'] or tx is None:return self._result(operation,state,code,tx)
            self._configuration()
            with ExitStack() as stack:
                for role in ['intake','stage']:stack.enter_context(self._root(self.roots[role]))
                store=stack.enter_context(self.store_factory(self.roots['bank'],contracts=self.contracts))
                # Fail unavailable/unknown existing Bank before consuming intake.
                c=store._connect(False);c.close()
                transport=self.transport(self.roots['intake'],tx,self.roots['stage'],policy_bytes=self.contracts.policy.raw,schema=self.contracts.env)
                snapshot=transport.snapshot
                if snapshot is None:
                    state=transport.status if transport.status in STATES else 'IO_ERROR';code=code_text(transport.code,'TRANSPORT_ERROR')
                    if state in ['REJECTED','INCOMPLETE']:receipt=store._receipt(state,code,str(uuid.uuid4()),tx)
                else:
                    cleanup='complete';digest=snapshot.manifest_sha256
                    manifest=im.reader.strict_json(snapshot.manifest_bytes,self.contracts.policy['manifest_bytes'],self.contracts.policy['json_container_depth'])
                    self.contracts.envelope(manifest)
                    if operation=='collection.save' and any(o['type']!='Collection' for o in manifest['operations']):
                        code='COLLECTION_ONLY_REQUIRED';receipt=store._receipt('REJECTED',code,str(uuid.uuid4()),tx,digest)
                    else:
                        self._event('before_import',snapshot);entered=True;outcome=store.import_snapshot(snapshot);self._event('after_import',outcome)
                        state=outcome.state if outcome.state in STATES else 'UNKNOWN';code=code_text(outcome.code,'IMPORT_OUTCOME_UNKNOWN');receipt=outcome.receipt
        except (ConfigurationError,im.reader.ConfigurationError) as e:state='IO_ERROR';code=code_text(str(e),'INVALID_CONFIGURATION');receipt=None
        except KeyboardInterrupt:state='UNKNOWN' if entered else 'CANCELLED';code='COMMAND_OUTCOME_UNKNOWN' if entered else 'CANCELLED';receipt=None
        except (im.Problem,im.reader.Rejected,im.native.SafetyError) as e:
            state='UNKNOWN' if entered else 'REJECTED';code='COMMAND_OUTCOME_UNKNOWN' if entered else code_text(getattr(e,'code',str(e)),'VALIDATION_ERROR');receipt=None
        except sqlite3.Error as e:
            n=getattr(e,'sqlite_errorcode',0) or 0;state='UNKNOWN' if entered else ('RETRYABLE_BUSY' if n&255 in [sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED] else 'IO_ERROR');code='COMMAND_OUTCOME_UNKNOWN' if entered else ('WRITER_BUSY' if state=='RETRYABLE_BUSY' else 'BANK_UNAVAILABLE');receipt=None
        except Exception:state='UNKNOWN' if entered else 'IO_ERROR';code='COMMAND_OUTCOME_UNKNOWN' if entered else 'BANK_UNAVAILABLE';receipt=None
        finally:
            if snapshot is not None:
                try:snapshot.close()
                except Exception:cleanup='failed';diagnostic='SNAPSHOT_CLEANUP_FAILED'
        result=self._result(operation,state,code,tx,digest,receipt,cleanup,diagnostic)
        result['diagnostic_attempt']=attempts.record(self.roots['bank'],result)
        return result
    def query(self,raw):
        q={}
        try:
            q=self.reader.parse(raw)
            if q.get('protocol')==attempts.QUERY or q.get('operation')=='attempt.get':
                self._configuration();return attempts.query(self.roots['bank'],q)
            if q.get('operation')=='bank.search':
                self.search.validate(raw,search.Budget(self.search.limits));self._configuration()
                if self.roots['cache'] is None:return self.reader.error(q,'INDEX_UNAVAILABLE')
                return self.search.execute(raw)
            self.reader.validate(q);self._configuration();return self.reader.execute(raw)
        except (read.ReadError,search.SearchError) as e:return self.reader.error(q,e.code)
        except Exception:return self.reader.error(q,'BANK_UNAVAILABLE')
    def rebuild(self):
        try:
            self._configuration()
            if self.roots['cache'] is None:raise ConfigurationError('ROOT_NOT_CONFIGURED')
            return self.search.rebuild()
        except Exception:return {'status':'ERROR','code':'INVALID_CONFIGURATION'}
def exit_code(result):
    s=result['status'];return 0 if s in ['OK','BUILT','ACCEPTED','REPLAY'] else (3 if s in ['RETRYABLE_BUSY'] else (4 if s=='UNKNOWN' else (130 if s=='CANCELLED' else 2)))
def main(argv=None):
    parser=Parser(description='Synthetic existing-Bank local commands; roots are trusted operator configuration.');parser.add_argument('action',choices=['save','collection-save','query','rebuild-search']);parser.add_argument('--bank-root',required=True);parser.add_argument('--intake-root');parser.add_argument('--stage-root');parser.add_argument('--cache-root');parser.add_argument('--output-root');parser.add_argument('--transaction-id')
    try:
        a=parser.parse_args(argv)
        if (a.action in ['save','collection-save'])!=(a.transaction_id is not None):raise ConfigurationError('INVALID_CLI')
        with Controller(a.bank_root,intake_root=a.intake_root,stage_root=a.stage_root,cache_root=a.cache_root,output_root=a.output_root) as app:
            if a.action in ['save','collection-save']:result=app.save('bank.save' if a.action=='save' else 'collection.save',a.transaction_id)
            elif a.action=='query':result=app.query(sys.stdin.buffer.read(max(app.reader.limits['request_bytes'],app.search.limits['request_bytes'])+1))
            else:result=app.rebuild()
    except ConfigurationError:result={'status':'ERROR','code':'INVALID_CLI'}
    except KeyboardInterrupt:result={'status':'UNKNOWN','code':'COMMAND_OUTCOME_UNKNOWN'}
    except Exception:result={'status':'ERROR','code':'INVALID_CONFIGURATION'}
    try:sys.stdout.buffer.write(im.encoded(result)+b'\n');sys.stdout.buffer.flush()
    except (OSError,KeyboardInterrupt):
        # Prevent a second shutdown flush from replacing UNKNOWN exit4 with
        # Python's exit120 on a broken pipe after a possible durable commit.
        try:sys.stdout.close()
        except OSError:pass
        return 4
    return exit_code(result)
if __name__=='__main__':sys.exit(main())
