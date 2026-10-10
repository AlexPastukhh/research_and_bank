"""First local prepared-draft UI slice. Tk access stays on its main thread."""
import argparse,copy,json,sys
from pathlib import Path
import presenter as p
class Window:
    def __init__(self,root,backend):
        import tkinter as tk
        from tkinter import ttk
        self.tk=tk;self.ttk=ttk;self.root=root;self.model=p.Model();self.bridge=p.Bridge(backend);self.buttons={};self.events=[];self.trees={};self.poll_id=None;self.refresh_id=None
        root.title('Research Bank — локальный интерфейс');root.geometry('1100x760');root.minsize(900,620);root.protocol('WM_DELETE_WINDOW',self.close);root.bind('<Destroy>',self.destroyed,add='+')
        style=ttk.Style(root);style.configure('Heading.TLabel',font=('Segoe UI',18,'bold'));style.configure('TButton',padding=(8,5));style.configure('Treeview',rowheight=28)
        outer=ttk.Frame(root,padding=16);outer.pack(fill='both',expand=True);ttk.Label(outer,text='Research Bank',style='Heading.TLabel').pack(anchor='w');ttk.Label(outer,text='Материалы • коллекции • поиск').pack(anchor='w',pady=(0,10))
        self.status=tk.StringVar(value=self.model.status);self.pubstatus=tk.StringVar(value='Пакет: ещё не проверен');self.savestatus=tk.StringVar(value='Bank: сохранение не выполнялось');self.context=tk.StringVar(value='Выбери объект в списке')
        ttk.Label(outer,textvariable=self.status,wraplength=1040).pack(anchor='w');ttk.Label(outer,textvariable=self.pubstatus,wraplength=1040).pack(anchor='w');ttk.Label(outer,textvariable=self.savestatus,wraplength=1040).pack(anchor='w',pady=(0,8))
        transaction=ttk.LabelFrame(outer,text='Подготовленная запись',padding=8);transaction.pack(fill='x',pady=(0,10));self.txline=txline=ttk.Frame(transaction);self.tx=tk.StringVar();ttk.Label(txline,text='ID транзакции').pack(side='left');self.txentry=ttk.Entry(txline,textvariable=self.tx,width=40);self.txentry.pack(side='left',padx=8);actions=ttk.Frame(transaction);actions.pack(fill='x',pady=(6,0))
        for key,label in [('publish','Опубликовать'),('inspect','Проверить пакет'),('resume','Возобновить пакет'),('save','Сохранить в Bank'),('receipt','Квитанция')]:self.button(actions,key,label,lambda k=key:self.transaction(k)).pack(side='left',padx=2)
        toolbar=ttk.Frame(outer);toolbar.pack(fill='x',pady=(0,8))
        for key,label,fn in [('refresh','Обновить список',self.refresh),('next','Следующая страница',self.next_page),('detail','Открыть',lambda:self.selected_action('detail')),('history','История',lambda:self.selected_action('history')),('export','Выгрузить файл',lambda:self.selected_action('export')),('rebuild','Перестроить поиск',lambda:self.submit('rebuild',{}))]:self.button(toolbar,key,label,fn).pack(side='left',padx=(0,4))
        self.footer=ttk.Label(outer,text='Просматривайте материалы и выгружайте сохранённые файлы. Содержимое файлов не запускается автоматически.',wraplength=1040);self.footer.pack(side='bottom',fill='x',pady=(8,0));paned=ttk.Panedwindow(outer,orient='horizontal');paned.pack(fill='both',expand=True);left=ttk.Frame(paned);right=ttk.Frame(paned);paned.add(left,weight=1);paned.add(right,weight=1);self.tabs=ttk.Notebook(left);self.tabs.pack(fill='both',expand=True);self.tab_names={}
        self.search_text=tk.StringVar();self.search_mode=tk.StringVar(value='current');self.search_type=tk.StringVar(value='Все типы');self.field_vars={name:tk.BooleanVar(value=name in ['title','body','content']) for name in ['title','filename','uri','aliases','body','content']};self.search_controls=[]
        for name in ['Bank','Collections','History','Search']:
            frame=ttk.Frame(self.tabs,padding=4);self.tabs.add(frame,text={'Bank':'Материалы','Collections':'Коллекции','History':'История','Search':'Поиск'}[name]);self.tab_names[str(frame)]=name
            if name=='Search':
                sf=ttk.Frame(frame);sf.pack(fill='x');entry=ttk.Entry(sf,textvariable=self.search_text);entry.pack(fill='x',pady=4);entry.bind('<Return>',lambda e:self.search());self.search_controls.append(entry);modes=ttk.Checkbutton(sf,text='Включить историю',variable=self.search_mode,onvalue='all_revisions',offvalue='current');modes.pack(side='left');types=ttk.Combobox(sf,textvariable=self.search_type,values=['Все типы',*(p.type_label(x) for x in p.TYPES)],state='readonly',width=15);types.pack(side='left');self.search_controls.extend([modes,types]);self.button(sf,'search','Найти',self.search).pack(side='left');fields=ttk.Frame(frame);fields.pack(fill='x')
                for n,(field,var) in enumerate(self.field_vars.items()):cb=ttk.Checkbutton(fields,text=p.FIELD_LABELS[field],variable=var);cb.grid(row=n//3,column=n%3,sticky='w');self.search_controls.append(cb)
            tree=ttk.Treeview(frame,columns=('kind','title','when'),show='headings',height=12,selectmode='browse');tree.heading('kind',text='Тип');tree.heading('title',text='Название');tree.heading('when',text='Сохранено');tree.column('kind',width=85,stretch=False);tree.column('title',width=220);tree.column('when',width=160,stretch=False);scroll=ttk.Scrollbar(frame,orient='vertical',command=tree.yview);tree.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');tree.pack(fill='both',expand=True);tree.bind('<<TreeviewSelect>>',lambda e,n=name:self.choose(n));tree.bind('<Double-1>',lambda e:self.selected_action('detail'));self.trees[name]=tree
        self.tabs.hide(list(self.tab_names)[2])
        self.technical=tk.BooleanVar(value=False);self.view_result=None
        ttk.Checkbutton(right,text='Технические детали',variable=self.technical,command=self.toggle_technical).pack(anchor='w')
        ttk.Label(right,textvariable=self.context,wraplength=470).pack(anchor='w',pady=(0,6));self.details=tk.Text(right,wrap='word',font=('Consolas',10),height=24,state='disabled');scroll=ttk.Scrollbar(right,orient='vertical',command=self.details.yview);self.details.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');self.details.pack(fill='both',expand=True)
        self.poll_id=root.after(30,self.poll)
    def button(self,parent,key,label,command):
        b=self.ttk.Button(parent,text=label,command=lambda:(self.events.append({'event':'button','action':key}),command()));self.buttons[key]=b;return b
    def tab(self):return self.tab_names[self.tabs.select()]
    def set_tab(self,name):
        frame=list(self.tab_names)[list(self.trees).index(name)]
        if name=='History':self.tabs.add(frame)
        self.tabs.select(frame)
    def technical_enabled(self):return bool(getattr(self,'technical',None) and self.technical.get())
    def toggle_technical(self):
        if self.technical_enabled():self.txline.pack(fill='x',before=self.txline.master.winfo_children()[-1])
        else:self.txline.pack_forget()
        if self.view_result is not None:self.show_result(self.view_result)
        elif self.model.selected:self.context.set(self.selection_label())
    def selection_label(self):
        return json.dumps(self.model.selected,ensure_ascii=False) if self.technical_enabled() else self.model.ref_label(self.model.selected)
    def render_result(self,result):return p.display(result,technical=self.technical_enabled(),labels=self.model.labels)
    def show_result(self,result):
        self.view_result=copy.deepcopy(result)
        data=result.get('data',{});doc=data.get('document')
        if doc:self.context.set(json.dumps(data.get('ref') or p.read.ref(doc),ensure_ascii=False) if self.technical_enabled() else p.material_label(doc,doc.get('title')))
        elif result.get('transaction_id') or data.get('receipt') or result.get('receipt'):self.context.set('Подготовленная запись')
        else:self.context.set('Результат операции')
        self.details.configure(state='normal');self.details.delete('1.0','end');self.details.insert('1.0',self.render_result(result));self.details.configure(state='disabled')
    def submit(self,action,args,tab=None):
        tab=tab or self.tab()
        if not self.model.begin(action,args,tab):return False
        if not self.bridge.submit(action,args):self.model.finish({'status':'ERROR','code':'UI_BUSY'});return False
        self.set_busy(True);self.status.set(self.model.status);return True
    def set_busy(self,busy):
        for b in self.buttons.values():b.state(['disabled'] if busy else ['!disabled'])
        self.txentry.configure(state='disabled' if busy else 'normal')
        for c in self.search_controls:
            if isinstance(c,self.ttk.Combobox):c.configure(state='disabled' if busy else 'readonly')
            else:c.configure(state='disabled' if busy else 'normal')
        self.tabs.state(['disabled'] if busy else ['!disabled'])
    def refresh(self):
        tab=self.tab()
        if tab not in ['Bank','Collections']:self.status.set('Открой «Материалы» или «Коллекции» для обновления списка');return
        self.submit('list',{'protocol':p.discovery.PROTOCOL,'object_types':['Collection'] if tab=='Collections' else p.TYPES,'snapshot_sequence':None,'after_object_id':None,'limit':10},tab)
    def next_page(self):
        tab=self.tab();page=self.model.pages[tab]
        if not page.get('has_more'):self.status.set('Следующей страницы нет');return
        if tab in ['Bank','Collections']:self.submit('list',{'protocol':p.discovery.PROTOCOL,'object_types':['Collection'] if tab=='Collections' else p.TYPES,'snapshot_sequence':page['snapshot_sequence'],'after_object_id':page['after_object_id'],'limit':10},tab)
        elif tab=='History':self.submit('history',{'ref':page['ref'],'snapshot_sequence':page['snapshot_sequence'],'offset':page['offset']},tab)
        else:self.submit('search',{**page['query_args'],'snapshot_sequence':page['snapshot_sequence'],'offset':page['offset']},tab)
    def choose(self,tab):
        selection=self.trees[tab].selection()
        if selection and self.model.select(tab,int(selection[0])):self.context.set(self.selection_label())
    def selected_action(self,action):
        if not self.model.selected:self.status.set('Сначала выбери объект');return
        if action=='export' and self.model.selected['object_type']!='Asset':self.status.set('Файл можно выгрузить только у материала с сохранённым файлом или ссылкой');return
        if action=='history':self.set_tab('History')
        self.submit(action,{'ref':copy.deepcopy(self.model.selected)},'History' if action=='history' else self.tab())
    def transaction(self,action):
        tx=self.tx.get();args=self.model.receipt_args(tx) if action=='receipt' else {'transaction_id':tx};self.submit(action,args)
    def search(self):
        self.set_tab('Search');types=p.chosen_types(self.search_type.get());self.submit('search',{'query':self.search_text.get(),'revisions_mode':self.search_mode.get(),'object_types':types,'fields':[k for k,v in self.field_vars.items() if v.get()]},'Search')
    def destroyed(self,event):
        if event.widget is self.root:
            for name in ['poll_id','refresh_id']:
                token=getattr(self,name,None)
                if token is not None:self.root.after_cancel(token);setattr(self,name,None)
    def refresh_after(self):
        self.refresh_id=None;self.refresh()
    def poll(self):
        self.poll_id=None;result=self.bridge.poll()
        if result is not None:
            refresh=self.model.finish(result);self.events.append({'event':'outcome','status':result.get('status'),'code':result.get('code')});self.set_busy(False);self.status.set(self.model.status+(' • срез '+str(result['snapshot_sequence'])+' • строк '+str(len(result['items'])) if result.get('protocol')==p.discovery.PROTOCOL and result.get('status')=='OK' else ''))
            if self.model.publication:self.pubstatus.set('Пакет: '+self.model.publication['status']+' / '+self.model.publication.get('code','')+'; готовность пакета ещё не подтверждает запись в Bank')
            if self.model.save:self.savestatus.set('Bank: '+self.model.save['status']+' / '+self.model.save.get('code',''))
            for tab,rows in self.model.rows.items():
                tree=self.trees[tab];old=tree.selection();tree.delete(*tree.get_children())
                for i,row in enumerate(rows):ref=row['ref'];tree.insert('', 'end',iid=str(i),values=p.row_values(row))
            self.show_result(result)
            if self.model.closed:self.root.destroy();return
            if refresh:self.set_tab('Bank');self.refresh_id=self.root.after(0,self.refresh_after)
        if not self.model.closed:self.poll_id=self.root.after(30,self.poll)
    def close(self):
        self.model.close_request();self.status.set(self.model.status);self.set_busy(True)
        if self.model.closed:self.root.destroy()
def main(argv=None):
    parser=p.commands.Parser(description='First prepared-draft local Bank UI; existing configured roots only.')
    for role in ['bank','intake','source','stage','cache','output']:parser.add_argument('--'+role+'-root',required=True)
    try:
        args=parser.parse_args(argv);roots={role:getattr(args,role+'_root') for role in ['bank','intake','source','stage','cache','output']};backend=p.Backend(roots);backend.config();import tkinter as tk
        root=tk.Tk();app=Window(root,backend);root.after(0,app.refresh);root.mainloop();return 0
    except Exception:sys.stdout.write('{"status":"ERROR","code":"UI_UNAVAILABLE"}\n');return 2
if __name__=='__main__':sys.exit(main())
