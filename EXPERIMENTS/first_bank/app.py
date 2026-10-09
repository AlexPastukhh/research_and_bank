"""First Bank window. All Tk calls stay on the user-opened main thread."""
import copy,json,sys,time
import integration as i
import authoring_ui
p=i.p
class Window(authoring_ui.Window):
    def __init__(self,root,backend):
        super().__init__(root,backend)
        self.flow=i.Flow(backend.context,backend.identity);self.observe_at=0;self.background=False
        self.observing=False;self.waiting_action=False
        root.title('Research Bank');self.sync_status=self.tk.StringVar(value='Bank: проверка подключения…')
        outer=root.winfo_children()[0];self.ttk.Label(outer,textvariable=self.sync_status,wraplength=1040).pack(anchor='w',before=self.footer)
        self.tools_area=self.ttk.Frame(outer);self.tools_area.pack(fill='x',before=self.footer)
        bar=self.ttk.Frame(self.tools_area,padding=(0,4));bar.pack(fill='x')
        self.button(bar,'attempts','Диагностика сохранения',lambda:self.transaction('attempts')).pack(side='left',padx=4)
        self.button(bar,'safeguard','Проверенная копия Bank',lambda:self.submit('safeguard',{})).pack(side='left',padx=4)
        self.footer.configure(text='Новый материал → Подготовить → Опубликовать → Сохранить. Поиск обновляется отдельной видимой операцией. Копия Bank — по кнопке.')
    def submit(self,action,args,tab=None):
        if action=='observe':
            if self.observing or self.model.busy or self.model.closing:return False
            if not self.bridge.submit(action,args):return False
            self.observing=True;return True
        if self.observing:
            # Keep one worker. Capture one user request while its read-only poll finishes.
            if not self.model.begin(action,args,tab or self.tab()):return False
            self.waiting_action=True;self.set_busy(True);self.status.set(self.model.status)
            if action=='author_prepare':
                self.bridge.backend.cancel.clear();self.tx.set('');self.clear_panels()
            return True
        return super().submit(action,args,tab)
    def update_sync_status(self):
        value=self.flow.notice or ('Bank подключён; поиск готов' if self.flow.index_ready else 'Bank подключён; поиск ожидает обновления')
        if self.sync_status.get()!=value:self.sync_status.set(value)
    def search(self):
        if self.model.busy or self.model.closing:return
        self.set_tab('Search');types=p.base.TYPES if self.search_type.get()=='Все типы' else [self.search_type.get()]
        args={'query':self.search_text.get(),'revisions_mode':self.search_mode.get(),'object_types':types,'fields':[k for k,v in self.field_vars.items() if v.get()]}
        self.flow.search(args)
        if not self.flow.index_ready:self.flow.rebuild_pending=True
        self.drive()
    def drive(self):
        if self.observing or self.model.busy or self.model.closing:return
        work=self.flow.next()
        if work:
            action,args,tab=work;self.background=action in ['list','rebuild'];self.submit(action,args,tab)
        elif time.monotonic()>=self.observe_at:
            self.observe_at=time.monotonic()+2;self.submit('observe',{})
    def paint_rows(self):
        for tab,rows in self.model.rows.items():
            tree=self.trees[tab];tree.delete(*tree.get_children())
            for n,row in enumerate(rows):
                ref=row['ref'];tree.insert('','end',iid=str(n),values=(ref['object_type'],row.get('title') or ref['object_id'],ref['revision_id']))
                if ref==self.model.selected:tree.selection_set(str(n))
    def poll(self):
        self.poll_id=None;result=self.bridge.poll()
        if result is not None:
            if self.observing:
                self.observing=False;self.flow.apply('observe',result);self.update_sync_status()
                self.events.append({'event':'outcome','action':'observe','status':result.get('status'),'code':result.get('code')})
                if self.waiting_action:
                    self.waiting_action=False;action,args,_=self.model.active
                    if self.bridge.submit(action,args):result=None
                    else:result={'status':'UNKNOWN' if action=='save' else 'ERROR','code':'UI_WORKER_ERROR'}
                elif self.model.closing:
                    self.model.closed=True;self.root.destroy();return
                else:result=None
        if result is not None:
            action=self.model.active[0];background=self.background;self.background=False
            # Observation must never replace the pinned detail/search/history panels.
            previous=self.model.result
            self.model.finish(result);self.flow.apply(action,result);self.set_busy(False)
            self.events.append({'event':'outcome','action':action,'status':result.get('status'),'code':result.get('code')})
            if action in ['observe'] or background:self.model.result=previous
            self.status.set(self.model.status)
            self.update_sync_status()
            if self.model.transaction_id:self.tx.set(self.model.transaction_id)
            if action=='author_prepare':
                self.clear_panels()
                if self.form_status:self.form_status.set(p.display(result).split('\n')[0])
                if result.get('status')=='PREPARED':self.close_form()
            if action=='author_list' and result.get('status')=='OK':
                self.intent_combo.configure(values=[x['title'][:32]+' — '+x['transaction_id'][:8] for x in self.model.intents]);self.intent_choice.set('')
            self.handle_extension_result(action,result)
            if self.model.publication:self.pubstatus.set('Пакет: '+self.model.publication['status']+' / '+self.model.publication.get('code',''))
            if self.model.save:
                diagnostic=self.model.save.get('diagnostic_attempt',{})
                self.savestatus.set('Bank: '+self.model.save['status']+' / '+self.model.save.get('code','')+(' — диагностика не записана' if diagnostic.get('availability')=='unavailable' else ''))
            if self.model.last_receipt:self.savestatus.set('Bank: подтверждено квитанцией '+self.model.last_receipt['transaction_id'])
            if action in ['list','history','search']:self.paint_rows()
            if not background and action!='observe':
                if action in ['attempts','safeguard']:self.show_private(result)
                else:self.show_result(result)
            if self.model.closed:self.flow.close();self.root.destroy();return
        if not self.model.closed:
            self.drive();self.poll_id=self.root.after(30,self.poll)
    def show_private(self,result):
        self.details.configure(state='normal');self.details.delete('1.0','end')
        text=json.dumps(result,ensure_ascii=False,indent=2)
        if result.get('operation')=='attempt.get':text='Диагностика попыток отдельно от принятой квитанции. Отсутствие записи не доказывает неудачу.\n\n'+text
        if result.get('code')=='VERIFIED_SQLITE_BACKUP':text='Проверенная копия создана. Сохрани её отдельно от рабочего диска; восстановление пока не принято.\n\n'+text
        raw=text.encode('utf-8');text=raw[:65536].decode('utf-8','ignore')+('\n\n[Предпросмотр сокращён; диагностика доступна по next_before_rowid.]' if len(raw)>65536 else '');self.details.insert('1.0',text);self.details.configure(state='disabled')
    def close(self):
        self.flow.close()
        if self.observing and not self.model.busy:
            self.model.closing=True;self.model.status='Закрытие: ожидаем завершения проверки Bank'
            self.status.set(self.model.status);self.set_busy(True);return
        super().close()
    def handle_extension_result(self,action,result):
        """Optional object forms share this window's existing worker and observation flow."""
        pass

def launch(roots,context):
    window_type=Window
    if 'object_authoring' in roots:
        sys.path.insert(0,str(i.runtime.ROOT/'EXPERIMENTS/object_authoring/runtime'))
        import object_authoring,object_ui
        backend=object_authoring.Backend(roots,context=context);window_type=object_ui.Window
    else:backend=i.Backend(roots,context=context)
    backend.config()
    import tkinter as tk
    root=tk.Tk();window_type(root,backend);root.mainloop();return 0
