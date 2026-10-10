"""Object transaction state mapped onto the existing one-worker authoring model."""
import copy
import object_authoring as o
p=o.first.p
MAP={'object_prepare':'author_prepare','object_load':'author_load','object_finish':'author_finish'}

class Model(p.Model):
    def __init__(self):
        super().__init__();self.object_intents=[];self.object_page={}
    def begin(self,action,args,tab):
        mapped=MAP.get(action,action)
        if not super().begin(mapped,args,tab):return False
        self.active=(action,self.active[1],self.active[2]);return True
    def finish(self,result):
        action,args,tab=self.active
        if action=='object_list' and result.get('status')=='OK':
            self.object_intents=copy.deepcopy(result['items']);self.object_page={k:result[k] for k in ['has_more','next_after']}
        self.active=(MAP.get(action,action),args,tab)
        return super().finish(result)

class Values:
    """Closed form edits; IDs/base come from a separate immutable captured context."""
    def __init__(self,workspace,typ,base=None,target=None):
        self.w=workspace;self.typ=typ;self.base=copy.deepcopy(base);self.replacement=None
        self.data=copy.deepcopy(base['document']['data']) if base else workspace.defaults(typ)
        if target and typ=='Annotation':self.data['targets']=[workspace.pin(target)]
        self.title=base['document']['title'] if base else ''
        self.provenance=copy.deepcopy(base['document']['provenance']) if base else {'origin_kind':'unknown','source_locator':None,'derived_from':[]}
    def add_ref(self,key,ref):
        ref=self.w.pin(ref)
        if key=='asset_refs':o.need(ref['object_type']=='Asset','ASSET_REFERENCE_REQUIRED')
        values=self.provenance['derived_from'] if key=='derived_from' else self.data[key]
        o.need(ref not in values,'DUPLICATE_REFERENCE');o.need(len(values)<self.w.limits['references_per_list'],'OBJECT_LIST_LIMIT');values.append(ref)
    def move(self,key,index,delta):
        values=self.provenance['derived_from'] if key=='derived_from' else self.data[key];other=index+delta
        if 0<=index<len(values) and 0<=other<len(values):values[index],values[other]=values[other],values[index]
    def fields(self):
        return {'object_type':self.typ,'title':self.title,'data':copy.deepcopy(self.data),
                'provenance':{k:copy.deepcopy(self.provenance[k]) for k in ['origin_kind','source_locator','derived_from']}}
    def has_changes(self):
        """Only editable content counts; creation and explicit file replacement always proceed."""
        if self.base is None or self.replacement is not None:return True
        original=self.base['document']
        before={k:copy.deepcopy(original[k]) for k in ['object_type','title','data']}
        before['provenance']={k:copy.deepcopy(original['provenance'][k]) for k in ['origin_kind','source_locator','derived_from']}
        return self.fields()!=before
    def args(self):
        return {'fields':self.fields(),'base_ref':copy.deepcopy(self.base['ref']) if self.base else None,'replacement':copy.deepcopy(self.replacement)}
