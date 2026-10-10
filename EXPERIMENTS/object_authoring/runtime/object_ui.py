"""Structured object forms in the existing user-opened Bank window. No GUI automation."""
import copy
import object_authoring as o
import object_model as m
import app as first_app

class Window(first_app.Window):
    def __init__(self,root,backend):
        self.object_form=None;self.object_controls=[];self.object_values=None;self.object_status=None
        self.object_vars={};self.object_lists={};self.object_body=None;self.object_prepare_button=None;self.object_cancel_button=None
        self.authoring_route='legacy'
        super().__init__(root,backend);self.model=m.Model()
        bar=self.ttk.Frame(self.tools_area,padding=(0,4));bar.pack(fill='x')
        for col in range(3):bar.columnconfigure(col,weight=1)
        for n,(key,label,callback) in enumerate([('new_entity','Новая сущность',lambda:self.open_object('Entity')),
            ('new_collection','Новая коллекция',lambda:self.open_object('Collection')),
            ('target_note','Добавить заметку',self.targeted_note),
            ('edit_object','Редактировать',self.edit_selected),
            ('object_list','Подготовленные объекты',lambda:self.submit('object_list',{}))]):
            self.button(bar,key,label,callback).grid(row=n//3,column=n%3,sticky='ew',padx=3,pady=2)
        row=self.ttk.Frame(self.tools_area,padding=(0,4));row.pack(fill='x')
        self.object_choice=self.tk.StringVar();self.object_combo=self.ttk.Combobox(row,textvariable=self.object_choice,state='readonly',width=38)
        self.object_combo.pack(side='left');self.object_combo.bind('<<ComboboxSelected>>',self.choose_object)
        self.button(row,'object_next','Ещё объекты',self.next_objects).pack(side='left',padx=5)
        self.button(row,'object_finish','Завершить подготовку объекта',lambda:self.transaction('object_finish')).pack(side='left',padx=5)
        self.footer.configure(text='Материалы и объекты сохраняются через подготовку → публикацию → запись в Bank. Предыдущие состояния и сохранённые файлы доступны через историю.')

    def submit(self,action,args,tab=None):
        if action in ['object_prepare','author_prepare']:
            self.bridge.backend.cancel.clear();self.authoring_route='object' if action=='object_prepare' else 'legacy'
        started=super().submit(action,args,tab)
        if started and action=='object_prepare':self.tx.set('');self.clear_panels()
        return started

    def set_busy(self,busy):
        super().set_busy(busy)
        if hasattr(self,'object_combo'):self.object_combo.configure(state='disabled' if busy else 'readonly')
        for control,editable in self.object_controls:
            try:control.configure(state='disabled' if busy else editable)
            except self.tk.TclError:pass
        if self.object_prepare_button:self.object_prepare_button.state(['disabled'] if busy else ['!disabled'])
        if self.object_cancel_button:
            cancellable=busy and self.model.active and self.model.active[0]=='object_prepare' and not self.model.closing
            self.object_cancel_button.state(['!disabled'] if cancellable else ['disabled'])

    def transaction(self,action):
        if action=='author_finish' and self.authoring_route=='object':action='object_finish'
        if action=='object_finish' and self.authoring_route!='object':self.status.set('Выбери подготовленный объект');return
        return super().transaction(action)

    def choose_intent(self,event=None):
        if not self.model.busy:self.authoring_route='legacy'
        return super().choose_intent(event)

    def choose_object(self,event=None):
        index=self.object_combo.current()
        if not 0<=index<len(self.model.object_intents):return
        tx=self.model.object_intents[index]['transaction_id']
        if self.model.select_transaction(tx):
            self.authoring_route='object';self.tx.set(tx);self.clear_panels();self.submit('object_load',{'transaction_id':tx})

    def next_objects(self):
        if self.model.object_page.get('has_more'):self.submit('object_list',{'after':self.model.object_page['next_after']})
        else:self.status.set('Следующей страницы нет')

    def handle_extension_result(self,action,result):
        if self.model.closing:return
        if action=='object_base' and result.get('status')=='OK':
            self.open_object(result['data']['document']['object_type'],base=result['data'])
        if action=='object_list' and result.get('status')=='OK':
            self.object_combo.configure(values=o.first.p.base.intent_labels(self.model.object_intents));self.object_choice.set('')
        if action=='object_prepare':
            self.clear_panels()
            if self.object_status:self.object_status.set(o.first.p.display(result).split('\n')[0])
            if result.get('status')=='PREPARED':self.close_object()
        if action=='save' and result.get('code')=='STALE_BASE':
            self.status.set('Материал уже изменён другим сохранением. Эта подготовка сохранена. Для новой правки открой актуальный материал в Bank; повтор продолжает эту же подготовку.')

    def toggle_technical(self):
        super().toggle_technical()
        if self.object_form and self.object_form.winfo_exists():
            if self.form_technical:
                if self.technical_enabled():self.form_technical.pack(anchor='w',pady=5)
                else:self.form_technical.pack_forget()
            for key in self.object_lists:self.paint_list(key)

    def targeted_note(self):
        if not self.model.selected:self.status.set('Выбери материал для заметки');return
        self.open_object('Annotation',target=copy.deepcopy(self.model.selected))

    def new_form(self):
        if self.object_form and self.object_form.winfo_exists():
            self.object_form.lift();self.status.set('Заверши или закрой форму объекта');return
        return super().new_form()

    def edit_selected(self):
        if not self.model.selected:self.status.set('Выбери материал для редактирования');return
        if self.object_form and self.object_form.winfo_exists():self.object_form.lift();return
        self.submit('object_base',{'ref':copy.deepcopy(self.model.selected)})

    def field(self,parent,key,label,value='',choices=None):
        self.ttk.Label(parent,text=label).pack(anchor='w',pady=(6,0))
        var=self.tk.StringVar(value='' if value is None else value);self.object_vars[key]=var
        c=self.ttk.Combobox(parent,textvariable=var,values=choices,state='readonly') if choices else self.ttk.Entry(parent,textvariable=var)
        c.pack(fill='x');self.object_controls.append((c,'readonly' if choices else 'normal'));return var

    def open_object(self,typ,base=None,target=None):
        if self.model.busy or self.model.closing:return
        if self.object_form and self.object_form.winfo_exists():self.object_form.lift();return
        if self.form and self.form.winfo_exists():self.status.set('Заверши или закрой форму нового материала');return
        self.object_values=m.Values(self.bridge.backend.objects,typ,base,target)
        self.object_vars={};self.object_lists={};self.object_controls=[];self.object_body=None
        t=self.tk;tt=self.ttk;top=t.Toplevel(self.root);self.object_form=top
        top.title(('Редактирование: ' if base else 'Создание: ')+o.first.p.base.type_label(typ));top.geometry('790x820');top.minsize(660,600);top.protocol('WM_DELETE_WINDOW',self.close_object)
        self.object_status=t.StringVar(value='Выбор другого материала в основном окне не меняет эту форму. Подготовка и сохранение подтверждаются отдельно.')
        bottom=tt.Frame(top,padding=12);bottom.pack(side='bottom',fill='x')
        tt.Label(bottom,textvariable=self.object_status,wraplength=720).pack(fill='x')
        buttons=tt.Frame(bottom);buttons.pack(fill='x',pady=8)
        self.object_prepare_button=tt.Button(buttons,text='Подготовить изменения' if base else 'Подготовить объект',command=self.prepare_object);self.object_prepare_button.pack(side='left')
        self.object_cancel_button=tt.Button(buttons,text='Отменить подготовку',command=self.cancel_object,state='disabled');self.object_cancel_button.pack(side='left',padx=8)
        container=tt.Frame(top);container.pack(fill='both',expand=True);canvas=t.Canvas(container,highlightthickness=0)
        scroll=tt.Scrollbar(container,orient='vertical',command=canvas.yview);scroll.pack(side='right',fill='y');canvas.configure(yscrollcommand=scroll.set);canvas.pack(side='left',fill='both',expand=True)
        f=tt.Frame(canvas,padding=16);item=canvas.create_window((0,0),window=f,anchor='nw')
        f.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda e:canvas.itemconfigure(item,width=e.width))
        tt.Label(f,text=o.first.p.base.type_label(typ),style='Heading.TLabel').pack(anchor='w')
        self.form_technical=None
        if base:
            self.model.remember({'ref':base['ref'],'title':base['document']['title'],'accepted_at':base.get('accepted_at','')})
            tt.Label(f,text=base['document']['title'] or 'Без названия',wraplength=710).pack(anchor='w',pady=5)
            ref=base['ref'];self.form_technical=tt.Label(f,text='Object: '+ref['object_id']+'\nБазовая revision: '+ref['revision_id'],wraplength=710)
            if self.technical_enabled():self.form_technical.pack(anchor='w',pady=5)
        self.field(f,'title','Название',self.object_values.title)
        d=self.object_values.data
        if typ=='Entity':
            self.field(f,'entity_kind','Вид сущности (например problem, algorithm, theory)',d['entity_kind'])
            self.list_field(f,'aliases','Альтернативные названия',mode='text')
            self.list_field(f,'external_ids','Внешние идентификаторы: пространство имён и значение',mode='external')
            self.list_field(f,'asset_refs','Связанные материалы')
        elif typ=='Collection':self.list_field(f,'members','Состав коллекции: порядок сохраняется')
        elif typ=='Annotation':
            self.field(f,'annotation_kind','Вид заметки',d['kind'],['note','tag','comment','interpretation'])
            self.field(f,'format','Формат текста',d['content_format'],['plain_text','markdown'])
            tt.Label(f,text='Текст').pack(anchor='w',pady=(6,0));self.object_body=t.Text(f,height=8,wrap='word');self.object_body.pack(fill='x');self.object_body.insert('1.0',d['body']);self.object_controls.append((self.object_body,'normal'))
            self.field(f,'author','Автор',d['author']['kind'],['unknown','user','ai','system'])
            self.field(f,'identity','Имя автора, если известно',d['author']['identity'])
            self.field(f,'model','Модель AI, если известна',d['author']['model'])
            self.list_field(f,'targets','Объекты, к которым относится заметка')
        else:
            storage=d['storage']
            if storage['mode']=='locator':
                self.field(f,'uri','Сохранённая ссылка',storage['uri']);self.field(f,'label','Подпись ссылки',storage['label'])
            else:
                tt.Label(f,text='Файл: '+storage['original_filename']+'\n'+storage['media_type']+' • '+str(storage['byte_length'])+' байт',wraplength=710).pack(anchor='w',pady=8)
                self.field(f,'replacement_path','Другой файл (не выбран — оставить текущий)')
                choose=tt.Button(f,text='Выбрать другой файл…',command=self.choose_replacement);choose.pack(anchor='w',pady=5);self.object_controls.append((choose,'normal'))
                self.field(f,'replacement_mode','Формат другого файла', 'binary',['binary','utf8_text'])
        pv=self.object_values.provenance
        self.field(f,'origin','Происхождение',pv['origin_kind'],['unknown','user_capture','external_capture','user_authored','ai_authored','derived'])
        self.field(f,'source_locator','Источник, если известен',pv['source_locator'])
        self.list_field(f,'derived_from','Основано на материалах')

    def list_values(self,key):return self.object_values.provenance['derived_from'] if key=='derived_from' else self.object_values.data[key]

    def list_field(self,parent,key,label,mode='ref'):
        box=self.ttk.LabelFrame(parent,text=label,padding=6);box.pack(fill='x',pady=8)
        lb=self.tk.Listbox(box,height=3,exportselection=False);lb.pack(fill='x');self.object_controls.append((lb,'normal'))
        self.object_lists[key]=lb
        if mode in ['text','external']:
            entry=self.tk.StringVar();c=self.ttk.Entry(box,textvariable=entry);c.pack(fill='x');self.object_controls.append((c,'normal'))
            second=None
            if mode=='external':
                second=self.tk.StringVar();c=self.ttk.Entry(box,textvariable=second);c.pack(fill='x');self.object_controls.append((c,'normal'))
            callback=lambda:self.add_value(key,entry,second)
        else:callback=lambda:self.add_selected(key)
        row=self.ttk.Frame(box);row.pack(fill='x',pady=4)
        for text,fn in [('Добавить выбранный материал' if mode=='ref' else 'Добавить',callback),
                        ('Удалить',lambda:self.remove_value(key)),('↑',lambda:self.move_value(key,-1)),('↓',lambda:self.move_value(key,1))]:
            b=self.ttk.Button(row,text=text,command=fn);b.pack(side='left',padx=2);self.object_controls.append((b,'normal'))
        self.paint_list(key)

    def paint_list(self,key):
        lb=self.object_lists[key];lb.delete(0,'end')
        for n,v in enumerate(self.list_values(key)):
            if isinstance(v,dict) and 'revision_id' in v:
                text=str(n+1)+'. '+self.model.ref_label(v)
                if self.technical_enabled():text+=' • '+v['object_id']+' / '+v['revision_id']
            else:text=v['namespace']+' : '+v['value'] if isinstance(v,dict) else v
            lb.insert('end',text)

    def add_selected(self,key):
        if self.model.busy:return
        try:
            o.need(self.model.selected is not None,'SELECT_A_VERSION');self.object_values.add_ref(key,copy.deepcopy(self.model.selected));self.paint_list(key)
        except Exception as e:self.object_status.set('Проверь выбор: '+getattr(e,'code','INVALID_REFERENCE'))

    def add_value(self,key,var,second):
        if self.model.busy:return
        try:
            value={'namespace':var.get(),'value':second.get()} if second else var.get()
            values=self.list_values(key);o.need(len(values)<128,'OBJECT_LIST_LIMIT');o.need(value not in values,'DUPLICATE_VALUE')
            if second:o.a.text(value['namespace'],4096);o.a.text(value['value'],8192)
            else:o.a.text(value,4096)
            values.append(value);self.paint_list(key);var.set('')
            if second:second.set('')
        except Exception as e:self.object_status.set('Проверь ввод: '+getattr(e,'code','INVALID_INPUT'))

    def remove_value(self,key):
        if self.model.busy:return
        indices=self.object_lists[key].curselection()
        if indices:self.list_values(key).pop(indices[0]);self.paint_list(key)

    def move_value(self,key,delta):
        if self.model.busy:return
        indices=self.object_lists[key].curselection()
        if indices:
            self.object_values.move(key,indices[0],delta);self.paint_list(key)
            index=indices[0]+delta
            if 0<=index<len(self.list_values(key)):self.object_lists[key].selection_set(index)

    def choose_replacement(self):
        if self.model.busy:return
        from tkinter import filedialog
        path=filedialog.askopenfilename(parent=self.object_form,title='Выбрать другой файл')
        if path:
            self.object_vars['replacement_path'].set(path);self.object_vars['origin'].set('unknown');self.object_vars['source_locator'].set('')

    def prepare_object(self):
        if self.model.busy or self.model.closing:return
        try:
            v=self.object_values;get=lambda k:self.object_vars[k].get();v.title=get('title')
            if v.typ=='Entity':v.data['entity_kind']=get('entity_kind')
            elif v.typ=='Annotation':
                v.data.update(kind=get('annotation_kind'),content_format=get('format'),body=self.object_body.get('1.0','end-1c'),author={'kind':get('author'),'identity':get('identity') or None,'model':get('model') or None})
            elif v.typ=='Asset':
                if v.data['storage']['mode']=='locator':v.data['storage'].update(uri=get('uri'),label=get('label') or None)
                else:v.replacement={'path':get('replacement_path'),'input_mode':get('replacement_mode')} if get('replacement_path') else None
            v.provenance.update(origin_kind=get('origin'),source_locator=get('source_locator') or None)
            if not v.has_changes():self.object_status.set('Изменений нет');return
            args=v.args();self.object_status.set('Подготовка выполняется…');self.submit('object_prepare',args)
        except Exception as e:self.object_status.set('Проверь ввод: '+getattr(e,'code','INVALID_INPUT'))

    def cancel_object(self):
        if self.model.busy and self.model.active[0]=='object_prepare' and not self.model.closing:
            self.bridge.backend.cancel.set();self.object_status.set('Запрошена отмена; ожидаем результат')

    def close_object(self):
        if self.model.busy:
            self.object_status.set('Ожидаем результат текущей операции. Подготовку можно отменить.');return
        if self.object_form:self.object_form.destroy();self.object_form=None
        self.object_controls=[];self.object_prepare_button=None;self.object_cancel_button=None;self.object_status=None
