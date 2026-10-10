"""File/link/note form composed with the unchanged prepared-draft window."""
import sys,copy
import authoring_presenter as p
import desktop

class Window(desktop.Window):
    def __init__(self,root,backend):
        self.form=None;self.form_controls=[];self.prepare_button=None;self.cancel_button=None;self.form_status=None
        super().__init__(root,backend);self.model=p.Model();root.title('Research Bank — создание материалов');root.geometry('1100x860')
        outer=root.winfo_children()[0];bar=self.ttk.LabelFrame(root,text='Создать или открыть подготовленный материал',padding=8);bar.pack(fill='x',padx=16,pady=(8,0),before=outer)
        self.button(bar,'new','Новый материал',self.new_form).grid(row=0,column=0,padx=3)
        self.button(bar,'author_list','Подготовленные записи',lambda:self.submit('author_list',{})).grid(row=0,column=1,padx=3)
        self.intent_choice=self.tk.StringVar();self.intent_combo=self.ttk.Combobox(bar,textvariable=self.intent_choice,state='readonly',width=45);self.intent_combo.grid(row=0,column=2,padx=3);self.intent_combo.bind('<<ComboboxSelected>>',self.choose_intent)
        self.button(bar,'author_next','Ещё записи',self.next_intents).grid(row=0,column=3,padx=3)
        self.button(bar,'author_finish','Завершить подготовку',lambda:self.transaction('author_finish')).grid(row=0,column=4,padx=3)
        self.txentry.configure(state='readonly');self.footer.configure(text='Файл, ссылка или самостоятельная заметка. Ссылка сохраняется без скачивания. Подготовка, публикация и запись в Bank показаны отдельно.')
    def render_result(self,result):return p.display(result,technical=self.technical_enabled(),labels=self.model.labels)
    def clear_panels(self):
        self.pubstatus.set('Пакет: ещё не проверен');self.savestatus.set('Bank: сохранение не выполнялось');self.show_result({'status':'OK','code':'Выбрана другая запись; проверь её состояние'})
    def set_busy(self,busy):
        super().set_busy(busy);self.txentry.configure(state='disabled' if busy else 'readonly')
        if hasattr(self,'intent_combo'):self.intent_combo.configure(state='disabled' if busy else 'readonly')
        for c in self.form_controls:
            try:
                if isinstance(c,self.ttk.Combobox):c.configure(state='disabled' if busy else 'readonly')
                elif isinstance(c,self.tk.Text):c.configure(state='disabled' if busy else 'normal')
                else:c.configure(state='disabled' if busy else 'normal')
            except self.tk.TclError:pass
        if self.prepare_button:self.prepare_button.state(['disabled'] if busy else ['!disabled'])
        if self.cancel_button:self.cancel_button.state(['!disabled'] if busy and self.model.active and self.model.active[0]=='author_prepare' and not self.model.closing else ['disabled'])
    def submit(self,action,args,tab=None):
        if self.model.busy or self.model.closing:return False
        if action=='author_prepare':self.bridge.backend.cancel.clear()
        started=super().submit(action,args,tab)
        if started and action=='author_prepare':self.tx.set('');self.clear_panels()
        return started
    def transaction(self,action):
        tx=self.model.transaction_id
        if not tx:self.status.set('Сначала создай или выбери подготовленную запись');return
        args=self.model.receipt_args(tx) if action=='receipt' else {'transaction_id':tx};self.submit(action,args)
    def choose_intent(self,event=None):
        i=self.intent_combo.current()
        if i<0 or i>=len(self.model.intents):return
        tx=self.model.intents[i]['transaction_id']
        if self.model.select_transaction(tx):self.tx.set(tx);self.clear_panels();self.submit('author_load',{'transaction_id':tx})
    def next_intents(self):
        if not self.model.intent_page.get('has_more'):self.status.set('Следующей страницы нет');return
        self.submit('author_list',{'after':self.model.intent_page['next_after']})
    def new_form(self):
        if self.model.busy or self.model.closing:return
        if self.form and self.form.winfo_exists():self.form.lift();return
        t=self.tk;tt=self.ttk;self.form=t.Toplevel(self.root);self.form.title('Новый материал');self.form.geometry('650x690');self.form.minsize(600,620);self.form.protocol('WM_DELETE_WINDOW',self.close_form);self.form_controls=[]
        f=tt.Frame(self.form,padding=16);f.pack(fill='both',expand=True);tt.Label(f,text='Новый материал',style='Heading.TLabel').pack(anchor='w')
        self.input_mode=t.StringVar(value='auto');self.kind=t.StringVar(value='note');self.title=t.StringVar();self.path=t.StringVar();self.uri=t.StringVar();self.author=t.StringVar(value='unknown');self.identity=t.StringVar();self.model_name=t.StringVar();self.content_format=t.StringVar(value='plain_text');self.form_status=t.StringVar(value='Подготовка создаёт новую запись. Для проверки старой выбери её в основном окне.')
        line=tt.Frame(f);line.pack(fill='x',pady=5);tt.Label(line,text='Вид материала').pack(side='left');self.kind_combo=tt.Combobox(line,textvariable=self.kind,values=['note','file','url'],state='readonly',width=12);self.kind_combo.pack(side='left',padx=8);self.kind_combo.bind('<<ComboboxSelected>>',lambda e:self.kind_changed());self.form_controls.append(self.kind_combo)
        tt.Label(f,text='Название').pack(anchor='w');title_entry=tt.Entry(f,textvariable=self.title);title_entry.pack(fill='x',pady=(0,8));self.form_controls.append(title_entry)
        self.file_frame=tt.Frame(f);tt.Label(self.file_frame,text='Файл (копируется в Bank, исходник сохраняется)').pack(anchor='w');file_line=tt.Frame(self.file_frame);file_line.pack(fill='x');entry=tt.Entry(file_line,textvariable=self.path);entry.pack(side='left',fill='x',expand=True);choose=tt.Button(file_line,text='Выбрать…',command=self.choose_file);choose.pack(side='left',padx=5);self.form_controls.extend([entry,choose]);mode=tt.Combobox(self.file_frame,textvariable=self.input_mode,values=['auto','utf8_text','binary'],state='readonly');mode.pack(anchor='w',pady=5);self.form_controls.append(mode);tt.Label(self.file_frame,text='auto: .txt/.md как UTF-8; остальные как binary. До 4 МиБ текст ищется по содержимому.',wraplength=590).pack(anchor='w')
        self.url_frame=tt.Frame(f);tt.Label(self.url_frame,text='Ссылка — содержимое не скачивается').pack(anchor='w');entry=tt.Entry(self.url_frame,textvariable=self.uri);entry.pack(fill='x');self.form_controls.append(entry)
        self.note_frame=tt.Frame(f);tt.Label(self.note_frame,text='Текст заметки').pack(anchor='w');self.body=t.Text(self.note_frame,height=12,wrap='word',font=('Segoe UI',10));self.body.pack(fill='both',expand=True);self.form_controls.append(self.body)
        for label,var,values in [('Автор',self.author,['unknown','user','ai']),('Формат',self.content_format,['plain_text','markdown'])]:
            row=tt.Frame(self.note_frame);row.pack(fill='x',pady=4);tt.Label(row,text=label,width=12).pack(side='left');c=tt.Combobox(row,textvariable=var,values=values,state='readonly',width=18);c.pack(side='left');self.form_controls.append(c)
        for label,var in [('Имя автора (если известно)',self.identity),('Модель AI (если известна)',self.model_name)]:
            row=tt.Frame(self.note_frame);row.pack(fill='x',pady=3);tt.Label(row,text=label,width=29).pack(side='left');c=tt.Entry(row,textvariable=var);c.pack(side='left',fill='x',expand=True);self.form_controls.append(c)
        tt.Label(f,textvariable=self.form_status,wraplength=600).pack(side='bottom',fill='x',pady=8);actions=tt.Frame(f);actions.pack(side='bottom',fill='x',pady=6);self.prepare_button=tt.Button(actions,text='Подготовить новую запись',command=self.prepare_form);self.prepare_button.pack(side='left');self.cancel_button=tt.Button(actions,text='Отменить подготовку',command=self.cancel_prepare,state='disabled');self.cancel_button.pack(side='left',padx=6)
        self.kind_changed();title_entry.focus_set()
    def kind_changed(self):
        for frame in [self.file_frame,self.url_frame,self.note_frame]:frame.pack_forget()
        {'file':self.file_frame,'url':self.url_frame,'note':self.note_frame}[self.kind.get()].pack(fill='both',expand=True,pady=5)
    def choose_file(self):
        if self.model.busy:return
        from tkinter import filedialog
        selected=filedialog.askopenfilename(parent=self.form,title='Выбрать файл для Bank')
        if selected:self.path.set(selected)
    def prepare_form(self):
        if self.model.busy:return
        fields={'kind':self.kind.get(),'title':self.title.get()}
        if fields['kind']=='file':fields.update(path=self.path.get(),input_mode=self.input_mode.get())
        elif fields['kind']=='url':fields['uri']=self.uri.get()
        else:fields.update(body=self.body.get('1.0','end-1c'),author_kind=self.author.get(),identity=self.identity.get() or None,model=self.model_name.get() or None,content_format=self.content_format.get())
        # Bound before crossing the worker seam too; never truncate input.
        try:self.bridge.backend.workspace.fields(fields)
        except Exception as e:self.form_status.set('Проверь ввод: '+getattr(e,'code','INVALID_INPUT'));return
        self.form_status.set('Подготовка выполняется…');self.submit('author_prepare',{'fields':fields})
    def cancel_prepare(self):
        if self.model.busy and self.model.active[0]=='author_prepare':self.bridge.backend.cancel.set();self.form_status.set('Запрошена отмена подготовки; ожидаем результат')
    def close_form(self):
        if self.model.busy:self.form_status.set('Ожидаем результат текущей операции. Для подготовки доступна отмена.');return
        if self.form:self.form.destroy();self.form=None
        self.form_controls=[];self.prepare_button=None;self.cancel_button=None;self.form_status=None
    def poll(self):
        self.poll_id=None;result=self.bridge.poll()
        if result is not None:
            action=self.model.active[0];refresh=self.model.finish(result);self.events.append({'event':'outcome','action':action,'transaction_id':self.model.transaction_id,'status':result.get('status'),'code':result.get('code')});self.set_busy(False);self.status.set(self.model.status)
            if self.model.transaction_id:self.tx.set(self.model.transaction_id)
            if action=='author_prepare':
                self.clear_panels()
                if self.form_status:self.form_status.set(p.display(result).split('\n')[0])
                if result.get('status')=='PREPARED':self.close_form()
            if action=='author_list' and result.get('status')=='OK':
                self.intent_combo.configure(values=p.base.intent_labels(self.model.intents));self.intent_choice.set('')
            if self.model.publication:self.pubstatus.set('Пакет: '+self.model.publication['status']+' / '+self.model.publication.get('code',''))
            if self.model.save:self.savestatus.set('Bank: '+self.model.save['status']+' / '+self.model.save.get('code',''))
            if self.model.last_receipt:self.savestatus.set('Bank: сохранение подтверждено квитанцией')
            for tab,rows in self.model.rows.items():
                tree=self.trees[tab];tree.delete(*tree.get_children())
                for i,row in enumerate(rows):ref=row['ref'];tree.insert('','end',iid=str(i),values=p.base.row_values(row))
            self.show_result(self.model.result)
            if self.model.closed:self.root.destroy();return
            if refresh:self.set_tab('Bank');self.refresh_id=self.root.after(0,self.refresh_after)
        if not self.model.closed:self.poll_id=self.root.after(30,self.poll)

def main(argv=None):
    parser=p.base.commands.Parser(description='Local creation-only Research Bank; existing configured private roots.')
    for role in sorted(p.a.ROLES):parser.add_argument('--'+role+'-root',required=True)
    try:
        args=parser.parse_args(argv);roots={role:getattr(args,role+'_root') for role in p.a.ROLES};backend=p.Backend(roots);backend.config();import tkinter as tk
        root=tk.Tk();window=Window(root,backend);root.after(0,window.refresh);root.mainloop();return 0
    except Exception:sys.stdout.write('{"status":"ERROR","code":"UI_UNAVAILABLE"}\n');return 2
if __name__=='__main__':sys.exit(main())
