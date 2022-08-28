import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from PIL import Image, ImageTk
from models import GooseData


class GooseView(tk.Tk):
    """ главное окно программы """

    def __init__(self):
        super().__init__()
        self.title("IEC 61850 generator")
        self.iconbitmap("img/python.ico")
        self.geometry("950x600+10+10")

        # верхняя панель меню (стандартная)
        self.main_menu = MenuBar(master=self)
        self.config(menu=self.main_menu)
        # панель кнопок меню
        self.buttons_menu = ButtonsMenu(master=self)
        # ВКЛАДКИ (ttk.Notebook)
        self.notebook = Notebook(master=self)
        self.notebook.pack(
            expand=1,
            fill='both'
        )

        # стили
        self.tab_style = ttk.Style()
        self.set_style()

    def set_ctrl(self, ctrl):
        print(self.__class__, 'set_ctrl OK!')
        """ привязывает элементы управления с обработчиками """
        # self.main_menu.set_ctrl(ctrl)
        self.buttons_menu.set_ctrl(ctrl)
        self.notebook.set_ctrl(ctrl)

    def set_style(self):
        self.tab_style.configure('TNotebook.Tab', bg="gray63")
        self.tab_style.map("TNotebook.Tab", background=[("selected", "green1")])

    # def close_all_tabs(self):
    #     self.notebook.destroy()
    #     self.notebook = Notebook(master=self)

    # def get_details(self):
    #     for tab in self.notebook.children:
    #         tab.get_details


class MenuBar(tk.Menu):
    """ верхняя панель меню """

    def __init__(self, master):
        super().__init__(master)

        # item 1 - Файл
        menu_item_1 = tk.Menu(self, tearoff=0)
        menu_item_1.add_command(label="Новый файл")
        menu_item_1.add_separator()

        # menu_item_1.add_command(label="Close all tabs", command=del_all_gooses)  # todo как привязать через binder? Или как сюда передать ctrl?
        menu_item_1.add_command(label="Debug")

        self.add_cascade(label="Файл", menu=menu_item_1)
        menu_item_1.add_separator()

        # item 2 - Выйти
        self.add_command(label="Выйти", command=master.destroy)

    # def set_ctrl(self, ctrl):
    # print(self.__class__, 'set_ctrl OK!')
    # self.cmd_new.config(ctrl.new...)
    # self.cmd_close_all.config(ctrl.del_all_gooses)


class ButtonsMenu:
    # ImageTk_array = []
    def __init__(self, master):
        self.master = master
        self.group_icons_tab = tk.LabelFrame(master=master, padx=0, pady=0, text="")
        self.group_icons_tab.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)

        self.btn_open = MenuButton(self.group_icons_tab, 'img\\open.png')
        self.btn_save = MenuButton(self.group_icons_tab, 'img\\save.png')
        self.btn_send_all_gooses = MenuButton(self.group_icons_tab, 'img\\gooses.png')
        self.btn_stop_all_gooses = MenuButton(self.group_icons_tab, 'img\\no_gooses.png')
        self.btn_close_project = MenuButton(self.group_icons_tab, 'img\\close.png')
        # debug common
        # tk.Label(self.group_icons_tab, text="debug").pack(padx=2, pady=2, side=tk.LEFT)
        # self.btn_debug = MenuButton(self.group_icons_tab, text='debug')
        # self.__common_debug_widget = tk.Entry(self.group_icons_tab, width=15)
        # self.__common_debug_widget.pack(padx=2, pady=2, side=tk.LEFT)

    def set_ctrl(self, ctrl):
        print(self.__class__, 'set_ctrl OK!')
        self.btn_open.bind_button(ctrl.load_from_ini)
        self.btn_save.bind_button(ctrl.save_to_ini)
        self.btn_send_all_gooses.bind_button(ctrl.send_all_gooses)
        self.btn_stop_all_gooses.bind_button(ctrl.stop_all_gooses)
        self.btn_close_project.bind_button(ctrl.del_all_gooses)
        # debug common
        # self.btn_debug.bind_button(lambda: ctrl.update_goose_data(0))


class MenuButton(tk.Button):
    def __init__(self, master, image=None, text='text', **kwargs):
        if image:
            self.image = image
            self.image_resized = self.img_resize()
            image = self.image_resized
        else:
            image = None
        super().__init__(master, image=image, text=text, padx=10, pady=10, **kwargs)
        self.pack(padx=2, pady=2, side=tk.LEFT)

    def img_resize(self):
        with Image.open(self.image) as im:
            im = im.resize((30, 30), Image.ANTIALIAS)
            ph = ImageTk.PhotoImage(im)
            return ph
            # self.ImageTk_array.append(ph)  # костыль

    def bind_button(self, callback):
        self.config(command=callback)


class Notebook(ttk.Notebook):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # self.tabs = list(map(self.load_tab, ))

    def set_ctrl(self, ctrl):
        print(self.__class__, 'set_ctrl OK!')
        """ привязывает элементы управления с обработчиками """
        for tab in self.children:
            tab.set_ctrl(ctrl)

    # def load_tab(self, tab, name):
    #     self.add(tab, text='GOOSE {}' % name)


# class TabsContainer(list):
#     """ контейнер для вкладок гусей """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


class GooseTab(ttk.Frame):
    def __init__(self, goose_idx, goose_name, n_gooses, master=None):
        super().__init__(master)
        self.goose_idx = goose_idx  # нумерация с 1 !!!
        self.goose_name = goose_name
        self.n_gooses = n_gooses
        frame_top = tk.Frame(self)
        self.commands_area = CommandsArea(frame_top, self.goose_idx, text="Команды", padx=5, pady=5)
        self.goose_descr_area = GooseDescriptionArea(frame_top, text="Описание GOOSE", padx=5, pady=5)
        self.settings_area = SettingsArea(self, text="Настройки", padx=10, pady=10)
        self.gooses_signals_area = GoosesSignalsArea(self, padx=5, pady=5, text=f"{self.goose_name} signals")

        self.commands_area.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y, )
        self.goose_descr_area.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X)
        frame_top.pack(side=tk.TOP)

        self.settings_area.pack(fill=tk.X,
                                # side=tk.TOP,
                                padx=5, pady=5)
        self.gooses_signals_area.pack(fill=tk.BOTH, expand=True,
                                      # side=tk.LEFT,
                                      padx=5, pady=5)

    def close_tab(self):
        self.destroy()

    def load_details(self, goose):
        """передать составляющим объектам"""
        self.goose_descr_area.load_details(goose)
        self.settings_area.load_details(goose)
        self.gooses_signals_area.load_details(goose)
        pass

    def get_details(self) -> GooseData:
        """ собирает данные от своих дочерних элементов """
        # details_descr_area
        details_descr_area = self.goose_descr_area.get_details()
        # details_settings_area
        details_settings_area = self.settings_area.get_details()
        # details_goose_signals
        details_goose_signals = self.gooses_signals_area.get_details()
        # common details
        fields = {'goose_index': self.goose_idx,
                  }
        common_details = {}
        for par_name, dict_ in fields.items():
            common_details[par_name] = fields[par_name]

        # GooseData building
        goose_data = GooseData(
            goose_index=common_details['goose_index'],
            goose_name=details_descr_area['goose_name'],
            goose_description=details_descr_area['goose_description'],
            stNum=details_settings_area['stNum'],
            vlan=details_settings_area['vlan'],
            prio=details_settings_area['prio'],
            dst_mac=details_settings_area['dst_mac'],
            appid=details_settings_area['appid'],
            go_id=details_settings_area['go_id'],
            inter=details_settings_area['inter'],
            goose_set=details_goose_signals,
        )
        return goose_data

    def set_ctrl(self, ctrl):
        print(self.__class__, 'set_ctrl OK!')
        """ привязывает элементы управления с обработчиками """
        self.commands_area.set_ctrl(ctrl)
        self.goose_descr_area.set_ctrl(ctrl)
        # self.settings_area.set_ctrl(ctrl)
        # self.gooses_signals_area.set_ctrl(ctrl)

    def set_tab_to_sending_state(self, state):
        self.set_tab_header_to_sending_state(state)
        self.commands_area.set_command_buttons_to_sending_state(state)

    def set_tab_header_to_sending_state(self, state):
        """ установливает имя вкладки в зав-ти от режима отправки гуся """
        if state:
            text = f'(*){self.goose_name}'
        else:
            text = f'(  ){self.goose_name}'

        self.master.tab(self.goose_idx - 1, text=text)

    def update_stNum_view(self, stNum_value):
        self.settings_area.update_stNum_view(stNum_value)


class CommandsArea(tk.LabelFrame):
    """ГРУППА команд"""

    def __init__(self, master, goose_idx, **kwargs):
        super().__init__(master, **kwargs)
        self.goose_idx = goose_idx

        self.btn_generate = MenuButton(self, 'img\\goose.png')
        self.btn_stop = MenuButton(self, 'img\\no_goose.png')

        self.btn_close = tk.Button(self, text="close tab",
                                   # image=ph4,
                                   )
        # debug tab
        self.btn_debug = tk.Button(self, text='debug')


        self.btn_generate.pack(padx=10, pady=10, side=tk.LEFT)
        self.btn_stop.pack(padx=10, pady=10, side=tk.LEFT)
        # self.btn_close.pack(padx=10, pady=10, side=tk.BOTTOM)  # кнопка "закрыть вкладку"
        self.btn_stop.config(state=tk.DISABLED)
        # debug tab
        # self.btn_debug.pack(padx=10, pady=10, side=tk.LEFT)

    def set_ctrl(self, ctrl):
        print(self.__class__, self.goose_idx, f'set_ctrl OK!')
        """ привязывает элементы управления с обработчиками """
        self.bind_command_button(self.btn_generate, ctrl.generate_one_goose, self.goose_idx)
        self.bind_command_button(self.btn_stop, ctrl.stop_one_goose, self.goose_idx)
        self.bind_command_button(self.btn_close, ctrl.del_goose, self.goose_idx)
        # debug tab
        # mgo = ctrl.get_mgo_by_idx(self.goose_idx)
        # self.bind_command_button(self.btn_debug, ctrl.update_goose_data, mgo)

    @staticmethod
    def bind_command_button(widget, callback, *args):
        def command():
            return callback(*args)

        widget.config(command=command)

    def set_command_buttons_to_sending_state(self, state):
        """ установливает имя вкладки в зав-ти от режима отправки гуся """
        if state:
            color = 'lightgreen'
            self.btn_generate.config(bg=color, state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            color = 'lightgray'
            self.btn_generate.config(bg=color, state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)


class GooseDescriptionArea(tk.LabelFrame):
    """Описание GOOSE"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.__goose_name = tk.LabelFrame(self, padx=5, pady=5, text="goose_name")
        self.__goose_name_widget = tk.Entry(self.__goose_name, width=15)
        self.__goose_desc_widget = tk.Text(self, width=45, height=3)
        self.__goose_index_widget = tk.Entry(self.__goose_name, width=5)

        self.__goose_name.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        self.__goose_name_widget.grid(row=0, column=0)
        self.__goose_desc_widget.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)

        self.__goose_index_widget.grid(row=0, column=1, padx=5,)
        self.__goose_index_widget.config(state=tk.DISABLED)

    def set_ctrl(self, ctrl):
        """ привязывает элементы управления с обработчиками """
        self.bind_context_menu(self.__goose_name_widget)
        self.bind_context_menu(self.__goose_desc_widget)

    def load_details(self, goose):
        """ загружает свою часть гуся в поля формы """
        self.__goose_name_widget.insert(0, goose.goose_name)
        self.__goose_desc_widget.insert(1.0, goose.goose_description)
        self.__goose_index_widget.config(state=tk.NORMAL)
        self.__goose_index_widget.insert(0, goose.goose_index)
        self.__goose_index_widget.config(state=tk.DISABLED)

    def get_details(self) -> dict:
        """ собирает данные с полей """
        details = {}
        fields = {'goose_name': {'type': str, 'widget': self.__goose_name_widget},
                  'goose_description': {'type': str, 'widget': self.__goose_desc_widget},
                  }
        for par_name, dict_ in fields.items():
            # print(par_name)
            details[par_name] = self.get_value(dict_['widget'], dict_['type'])

        return details

    @staticmethod
    def get_value(par, type_: type = str):
        """ возвращает значение и приводит к нужному типу """
        # print()
        if isinstance(par, tk.Text):
            return type_(par.get("1.0", tk.END)).rstrip()
        else:
            return type_(par.get())

    def bind_context_menu(self, widget):
        widget.bind("<Button-3>",
                    lambda event: self.show_popup(event, widget=widget)
                    )

    @staticmethod
    def show_popup(event, widget):
        # print(widget)
        popup = ContextMenu(widget)
        popup.show_popup(event)


class SettingsArea(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # ГРУППА 1 - VLAN
        self.__group_vlan = tk.LabelFrame(self, padx=5, pady=5, text="VLAN")
        tk.Label(self.__group_vlan, text="vlan").grid(row=0, column=0)
        tk.Label(self.__group_vlan, text="prio").grid(row=1, column=0)
        self.__vlan_widget = tk.Spinbox(self.__group_vlan, from_=3, to=255, width=5)
        self.__prio_widget = tk.Spinbox(self.__group_vlan, from_=4, to=255, width=5)

        self.__vlan_widget.grid(row=0, column=1, sticky=tk.W)
        self.__prio_widget.grid(row=1, column=1, sticky=tk.W)
        self.__group_vlan.pack(side=tk.LEFT, padx=5, pady=5)

        # ГРУППА 2 - APP ID
        self.__group_appid = tk.LabelFrame(self, padx=5, pady=5, text="APP ID")
        self.__appid_widget = tk.Entry(self.__group_appid, width=6)

        self.__group_appid.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        self.__appid_widget.grid(row=0)

        # ГРУППА 2.1 - goID
        self.__group_goid = tk.LabelFrame(self, padx=5, pady=5, text="goID")
        self.__group_goid.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)

        self.__go_id_widget = tk.Entry(self.__group_goid, width=20)
        self.__go_id_widget.grid(row=0)

        # ГРУППА 2.2 - dst MAC
        self.__group_dst_mac = tk.LabelFrame(self, padx=5, pady=5, text="dst MAC")
        tk.Label(self.__group_dst_mac, text="01:0c:cd:01:").grid(row=0, column=0)
        self.__dst_MAC_widget = tk.Entry(self.__group_dst_mac, width=8)

        self.__group_dst_mac.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        self.__dst_MAC_widget.grid(row=0, column=1, sticky=tk.W)

        # ГРУППА 2.3 - stNum
        self.__group_stnum = tk.LabelFrame(self, padx=5, pady=5, text="stNum")
        self.__stNum_widget = tk.Entry(self.__group_stnum, width=6)

        self.__group_stnum.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        self.__stNum_widget.grid(row=0)
        self.__stNum_widget.config(state='readonly')

        # inter
        self.__group_inter = tk.LabelFrame(self, padx=5, pady=5, text="inter")
        self.__inter_widget = tk.Entry(self.__group_inter, width=6)

        self.__group_inter.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        self.__inter_widget.grid(row=0)


    def load_details(self, goose):
        """ загружает свою часть гуся в поля формы """
        self.__vlan_widget.delete(0, tk.END)
        self.__vlan_widget.insert(0, goose.vlan)
        self.__prio_widget.delete(0, tk.END)
        self.__prio_widget.insert(0, goose.prio)
        self.__appid_widget.insert(0, goose.appid[2:])
        self.__go_id_widget.insert(0, goose.go_id)
        self.__dst_MAC_widget.insert(0, goose.dst_mac)
        self.__inter_widget.insert(0, goose.inter)

        self.update_stNum_view(str(goose.stNum))

    def update_stNum_view(self, stNum_value):
        self.stNum_widget_enable()
        self.__stNum_widget.delete(0, tk.END)
        self.__stNum_widget.insert(0, stNum_value)
        self.stNum_widget_disable()

    def stNum_widget_enable(self):
        self.__stNum_widget.config(state='normal')

    def stNum_widget_disable(self):
        self.__stNum_widget.config(state='readonly')

    def get_details(self) -> dict:
        """ собирает данные с полей """
        details = {}
        fields = {'vlan': {'type': int, 'widget': self.__vlan_widget},
                  'prio': {'type': int, 'widget': self.__prio_widget},
                  'appid': {'type': str, 'widget': self.__appid_widget},
                  'go_id': {'type': str, 'widget': self.__go_id_widget},
                  'dst_mac': {'type': str, 'widget': self.__dst_MAC_widget},
                  'stNum': {'type': int, 'widget': self.__stNum_widget},
                  'inter': {'type': float, 'widget': self.__inter_widget},
                  }
        # map(lambda type, widget: self.get_value(type, widget), )
        for par_name, dict_ in fields.items():
            details[par_name] = self.get_value(dict_['widget'], dict_['type'])

        details['appid'] = '0x' + details['appid']
        return details

    @staticmethod
    def get_value(par, type_: type = str):
        """ возвращает значение и приводит к нужному типу """
        return type_(par.get())


class GoosesSignalsArea(tk.LabelFrame):
    n_rows_in_col = 10

    # ГРУППА - GOOSE
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.n_signals = master.n_gooses
        self.gooses_signals_fields_dict = {}
        self.create_gooses_grid()

    def create_gooses_grid(self):
        """ создает решетку из полей GooseSignalArea """
        gs_idx = 1
        for col in range(int(self.n_signals / self.n_rows_in_col) + 1):
            for row in range(self.n_rows_in_col):
                if gs_idx > self.n_signals:
                    break
                gs = GooseSignalArea(self, gs_idx)
                gs.grid(row=row, column=col, padx=5)
                self.gooses_signals_fields_dict['goose_' + str(gs_idx)] = gs
                gs_idx += 1

    def load_details(self, goose):
        """ загружает параметры гусь-сигналов в поля формы """
        for gs_id, gs_obj in self.gooses_signals_fields_dict.items():
            gs_obj.load_details(goose)

    def get_details(self) -> dict:
        """ собирает данные с полей """
        details = {}
        # signals_array = []
        for gs_name, gs_obj in self.gooses_signals_fields_dict.items():
            child_details = gs_obj.get_details()
            details = {**details, **child_details}
            # print()
        # details ={gs_name: gs_obj.get_value() for gs_name, gs_obj in self.gooses_signals_fields_dict.items()}
        return details

        # обновить имя гусь-сигнала в виджете
    # for n, gs in enumerate(g.signals_objects_array):
    #     # установить значение чекбоксов в соответствии с прочитанным значением
    #     # param = f'goose_{n + 1}'
    #     param = f'goose_{n + 1}_name'
    #     new_val = config.get(section, param)
    #     gs.entry.delete(0, tk.END)
    #     gs.entry.insert(0, new_val)


class GooseSignalArea(tk.Frame):
    def __init__(self, master, gs_idx, **kwargs):
        super().__init__(master, **kwargs)
        self.gs_idx = gs_idx  # нумерация начинается с 1
        self.var = tk.IntVar()
        self.color = None

        self.__gs_btn = tk.Checkbutton(master=self,
                                       # text=str(self.goose_idx),
                                       bg=self.color,
                                       variable=self.var,
                                       command=self.btn_change,
                                       )

        self.__gs_btn.pack(side=tk.LEFT)
        # self.color_update()

        self.__gs_index_widget = tk.Entry(master=self, fg="yellow", bg="gray", width=4)
        self.__gs_index_widget.pack(side=tk.LEFT)

        self.__gs_name_widget = tk.Entry(master=self, fg="yellow", bg="gray", width=15)
        self.__gs_name_widget.pack(side=tk.LEFT, padx=3)

    #     self.add_goose_signal(idx, self)
    #
    # def add_goose_signal(self, idx, master):
    #     self.signals_objects_array.append(GooseSignalField(idx, master))

    def btn_change(self):
        """ выводит в консоль положение гусь-сигнала при изменении """
        state = self.get_value()
        print(f"goose {self.gs_idx}: {state == 1}")
        self.color_update(state)
        self.__gs_btn.config(bg=self.color)

    def get_value(self):  # RENAME?   def load_details(self, goose):
        """ возвращает значение гусь-сигнала """
        return self.var.get()

    def load_details(self, goose):
        """ вытаскивает из гуся и загружает параметры гусь-сигналов в поля формы """

        key = 'goose_' + str(self.gs_idx)
        gs_value = goose.goose_set[key]['value']
        gs_index = goose.goose_set[key].get('index', 0)
        gs_name = goose.goose_set[key]['name']

        self.set_value(gs_value)  # установка / снятие галки

        self.__gs_index_widget.delete(0, tk.END)
        self.__gs_index_widget.insert(0, gs_index)

        self.__gs_name_widget.delete(0, tk.END)
        self.__gs_name_widget.insert(0, gs_name)

    def get_details(self) -> dict:
        """ собирает данные с полей """
        details = {}
        key = 'goose_' + str(self.gs_idx)
        details[key] = {}
        details[key]['name'] = self.__gs_name_widget.get()
        try:
            details[key]['index'] = int(self.__gs_index_widget.get())
        except ValueError:
            details[key]['index'] = ''
        details[key]['value'] = bool(self.get_value())
        return details

    def set_value(self, value: bool):
        self.update_checkbox_value(value)

    def update_checkbox_value(self, state):
        # установить или снять чекбокс гусь-сигнала
        self.__gs_btn.select() if state else self.__gs_btn.deselect()
        self.color_update(state)

    def color_update(self, state):
        self.color = 'darkgreen' if state else 'lightgray'
        self.__gs_btn.config(bg=self.color)


class ContextMenu:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.menu = tk.Menu(self.parent_widget, tearoff=0,
                            postcommand=self.enable_selection,
                            )
        self.menu.add_command(label="Вырезать", command=self.cut_text)
        self.menu.add_command(label="Копировать", command=self.copy_text)
        self.menu.add_command(label="Вставить", command=self.paste_text)
        self.menu.add_command(label="Удалить", command=self.delete_text)
        # self.test()
        self.widget_type = self.get_widget_type()
        self.selection = self.get_selection()
        # print(self.selection)
        # print()

    def get_widget_type(self):
        if isinstance(self.parent_widget, tk.Entry):
            return 'entry'
        elif isinstance(self.parent_widget, tk.Text):
            return 'text'
        else:
            return 'other'

    # def test(self):
    #     print(self.parent_widget.select_from(2))
    #     print(self.parent_widget.select_from(3))
    #     print()
    #     pass

    def get_selection(self):
        try:
            return self.parent_widget.selection_get()
        except tk.TclError:
            return

    def show_popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def enable_selection(self):
        state_selection = tk.ACTIVE if self.selection else tk.DISABLED
        state_clipboard = tk.ACTIVE

        try:
            self.parent_widget.clipboard_get()
        except tk.TclError:
            state_clipboard = tk.DISABLED

        self.menu.entryconfig(0, state=state_selection)  # Вырезать
        self.menu.entryconfig(1, state=state_selection)  # Копировать
        self.menu.entryconfig(2, state=state_clipboard)  # Вставить
        self.menu.entryconfig(3, state=state_selection)  # Удалить

    def cut_text(self):
        print('cut')
        if self.widget_type == 'text':
            self.copy_text()
            self.delete_text()
        else:
            print('oooops!')

    def copy_text(self):
        if self.widget_type == 'text':
            if self.selection:
                selection = self.parent_widget.tag_ranges(tk.SEL)
                self.parent_widget.clipboard_clear()
                self.parent_widget.clipboard_append(self.parent_widget.get(*selection))
        else:
            print('oooops!')

    def paste_text(self):
        self.parent_widget.insert(tk.INSERT, self.parent_widget.clipboard_get())

    def delete_text(self):
        if self.widget_type == 'text':
            selection = self.parent_widget.tag_ranges(tk.SEL)
            if selection:
                self.parent_widget.delete(*selection)
        else:
            print('oooops!')
