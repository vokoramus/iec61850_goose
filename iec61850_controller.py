import tkinter.filedialog as fd
from goose.goose_generator import GooseMessage
import threading
from time import sleep
from configparser import ConfigParser
from iec61850_view import GooseTab
from models import GooseData, MainGooseObject, GoosesContainer
from os.path import basename
from pprint import pprint



# TODO: добавить в ini новые поля
# TODO: создать новые поля из TODO.txt
# TODO: загружать одну вкладку гуся с одним гусем для ручного наполнения
# TODO: создать кнопки + и - для создания вкладок гусей
# TODO: создать кнопки + и - для создания и удаления гусь сигналов (как вариант, задавать кол-во гусей в ячейке)
# TODO:


def convert_to_dec(appid) -> int:
    appid_dec = int(str(appid), 16)
    # print(appid, appid_dec)
    return appid_dec


def open_ini_file():
    filetypes = (("ini-файл", "*.ini"),
                 # ("Любой", "*")
                 )
    filename = fd.askopenfilename(title="Открыть файл",
                                  initialdir="D:/_G_Drive_common/Python/Projects/iec61850_goose_MVC/settings",
                                  filetypes=filetypes)
    return filename


class GooseController(object):
    def __init__(self, repo, view):
        self.repo = repo
        self.view = view
        self.gooses_container = GoosesContainer()
        self.config = None
        self.goose_names = []
        self.filename = ''
        self.gooses_container.append(MainGooseObject(0, 0, 0, 0))        # создаем пустышку для занятия индекса 0.

    def binder(self):
        """ привязывает комбинации клавиш к главному окну """
        self.view.bind("<Control-o>", lambda x: self.load_from_ini())
        self.view.bind("<Control-s>", lambda x: self.save_to_ini())

    def start(self):
        """ начало работы """
        self.binder()
        self.view.mainloop()
        # self.view.protocol("WM_DELETE_WINDOW", self.stop_all_gooses)  # _tkinter.TclError: can't invoke "wm" command: application has been destroyed

    def load_from_ini(self):
        """ Запускается при нажатии кнопки "Открыть"

            - прочитать ini
            - посчитать кол-во секций гусей (N)
            - дать команду на создание N гусей, передав Config (сконвертировать перед этим в gooses_kwargs_dict)
         """
        print("on_press_open")

        self.filename = open_ini_file()
        if self.filename:
            print(self.filename)

            self.config = self.read_ini()

            # выдает список секций
            self.goose_names = self.config.sections()
            if self.goose_names == []:
                print('NOTHING to open!')
            if len(self.gooses_container) > 1:  # первый с индексом 0 - фиктивный
                self.del_all_gooses()
            self.born_gooses(self.goose_names)
            # обновить заголовок окна программы
            # self.view.config(title="IEC 61850 generator" + self.filename)
            self.view.title("IEC 61850 generator - " + basename(self.filename))

            # загрузить данные в поля
            self.load_data_to_view_tabs()

##########

    def read_ini(self):
        return self.repo.open_file(self.filename)

    def born_gooses(self, goose_names) -> None:
        for i, goose_name in enumerate(goose_names):
            goose_idx = i + 1
            mgo = self.born_goose(goose_idx, goose_name)
            self.gooses_container.append(mgo)
            self.set_goose_tab_ctrl(mgo)

    def born_goose(self, goose_idx, goose_name):
        mgo = MainGooseObject()
        mgo.goose_idx = goose_idx
        # создаем GooseData
        goose_data = self.born_goose_data(goose_name, goose_idx)
        mgo.goose_data = goose_data
        # создаем GooseTab
        n_gooses = len(goose_data.goose_set)
        mgo.n_gooses = n_gooses
        goose_tab = self.born_goose_tab(goose_name, goose_idx, n_gooses)
        mgo.goose_tab = goose_tab
        self.view.notebook.add(goose_tab, text=goose_name)
        return mgo

    def born_goose_data(self, goose_name, goose_idx) -> GooseData:
        """ собирает данные из секции ini и создает объект GooseData """
        section = goose_name
        goose_description = self.config.get(section, 'goose_description')
        stNum = 0
        vlan = self.config.getint(section, 'vlan')
        prio = self.config.getint(section, 'prio')
        dst_mac = self.config.get(section, 'dst_mac')
        appid = self.config.get(section, 'appid')
        go_id = self.config.get(section, 'go_id')
        inter = self.config.get(section, 'inter')                                                   # TODO self.config.getint(section, 'inter')

        g_args_names = ('goose_index', 'goose_name', 'goose_description', 'stNum',
                        'vlan', 'prio', 'dst_mac', 'appid', 'go_id', 'inter')
        g_args_values = (goose_idx, goose_name, goose_description, stNum,
                         vlan, prio, dst_mac, appid, go_id, inter)
        gooses_kwargs_dict = self.build_gooses_kwargs_dict(g_args_names, g_args_values, section)
        goose_data = GooseData(**gooses_kwargs_dict)
        return goose_data

    def build_gooses_kwargs_dict(self, g_args_names, g_args_values, section):
        gooses_kwargs_dict = dict(zip(g_args_names, g_args_values))
        gooses_kwargs_dict['goose_set'] = self.get_goose_set(section)
        return gooses_kwargs_dict

    def get_goose_set(self, section) -> dict:
        """ читает секцию ini и создает словарь гусь-сигналов """
        """
        # string_val = config.get('section_a', 'string_val')
        # bool_val = config.getboolean('section_a', 'bool_val')
        # int_val = config.getint('section_a', 'int_val')
        # float_val = config.getfloat('section_a', 'pi_val')
        """
        section_obj = self.config[section]
        goose_set = {}  # TODO    Ordered_Dict !!!!!!!!
        # from collections import OrderedDict
        # xx = OrderedDict(sorted(xx.items(), key=lambda xx: xx[0]))
        n = 1

        # TODO: использовать класс GooseSignalModel для гусь сигналов, а не куча сигналов в goose_set
        for param_name in section_obj:
            # print()
            if param_name.startswith('goose_'):
                # name
                if param_name == 'goose_' + str(n) + '_name':
                    goose_set['goose_' + str(n)]['name'] = section_obj.get(param_name)
                # index
                elif param_name == 'goose_' + str(n) + '_index':
                    try:
                        par = section_obj.getint(param_name)
                    except ValueError:
                        par = ''
                    goose_set['goose_' + str(n)]['index'] = par

                    n += 1   # обязательно должен находиться в последней ветви elif перед веткой, где считывается state
                             # (слабое место, возможно уйдет при использовании OrderedDict)
                # state
                elif param_name == 'goose_' + str(n):
                    goose_set['goose_' + str(n)] = {}
                    goose_set['goose_' + str(n)]['value'] = section_obj.getboolean(param_name)
        return goose_set

    def set_goose_tab_ctrl(self, mgo) -> None:
        # подключаем управление на вкладке
        mgo.goose_tab.set_ctrl(self)

    def born_goose_tab(self, goose_name, goose_idx, n_gooses) -> GooseTab:
        """ создает вкладку гуся """
        goose_tab = GooseTab(master=self.view.notebook, goose_name=goose_name, goose_idx=goose_idx, n_gooses=n_gooses)
        return goose_tab

    def load_data_to_view_tabs(self) -> None:
        """ загрузка данных в поля всех вкладок  """
        for mgo in self.get_mgo_list():
            self.load_data_to_view_tab(mgo)  # команда создания view и загрузки данных в поля view

    @staticmethod
    def load_data_to_view_tab(mgo) -> None:
        """ загрузка данных в поля вкладки конкретного гуся """
        mgo.goose_tab.load_details(mgo.goose_data)

    # Конец методов, исполняемых при создании гусей

    ###############################################
    # СОХРАНЕНИЕ В ФАЙЛ
    ###############################################

    def save_to_ini(self):
        print("on_press_save")
        new_file = fd.asksaveasfile(title="Сохранить файл", defaultextension=".ini",
                                    filetypes=(("ini-файл", "*.ini"),))
        if new_file:
            print('save to: ', new_file.name)
            config = self.collect_data_to_save_file()
            self.repo.save_to_file(new_file.name, config)

    def collect_data_to_save_file(self) -> ConfigParser:
        config = ConfigParser()

        for mgo in self.get_mgo_list():
            self.update_goose_data(mgo)
            data = mgo.goose_data

            # записываем в ini
            section = data.goose_name
            config.add_section(section)

            config.set(section, 'vlan', str(data.vlan))
            config.set(section, 'prio', str(data.prio))
            config.set(section, 'appid', str(data.appid))
            config.set(section, 'go_id', str(data.go_id))
            config.set(section, 'dst_MAC', str(data.dst_mac))
            config.set(section, 'goose_index', str(data.goose_index))
            config.set(section, 'goose_description', str(data.goose_description))
            config.set(section, 'inter', str(data.inter))

            for gs_name, value in data.goose_set.items():
                config.set(section, f'{gs_name}', str(data.goose_set[gs_name]['value']))
                config.set(section, f'{gs_name}_name', str(data.goose_set[gs_name]['name']))
                config.set(section, f'{gs_name}_index', str(data.goose_set[gs_name]['index']))

        return config

    def update_goose_data(self, mgo) -> None:
        new_goose_data = mgo.goose_tab.get_details()
        mgo.goose_data = new_goose_data

    ###############################################
    # ОТПРАВКА ГУСЬ-СООБЩЕНИЙ
    ###############################################

    def generate_one_goose(self, goose_idx) -> None:
        """ Отправка одного гусь-сообщения
        срабатывает при нажатии на кнопку """
        print('__onPressGenerate__')
        mgo = self.get_mgo_by_idx(goose_idx)
        self.update_goose_data(mgo)     #  Load actual data from widjets!!!!

        state = mgo.sending_state = True
        mgo.goose_tab.set_tab_to_sending_state(state=state)
        # goose_message.send_pack()     # для однократной отправки

        # self.return_values()
        # self.repo.save_to_pcap(filename=f'goose_{self.idx}_{self.go_id}_({self.stNum})')
        # self.repo.save_to_pcap(filename=f'goose_{goose_idx}')

        thread = threading.Thread(target=self.separate_thread_sending, args=(mgo,))
        thread.start()
        self.check_thread(thread, mgo)

    def separate_thread_sending(self, mgo) -> None:
        """ Отдельный поток! """
        while mgo.sending_state:
            print('RUNNING')
            # print(goose_message.sending_state)

            goose_message = self.born_goose_message(mgo)
            goose_message.send_pack()
            self.update_stNum(mgo)
            sleep(mgo.goose_data.inter)

    def born_goose_message(self, mgo) -> GooseMessage:
        """ создает GooseMessage """
        goose_data = mgo.goose_data
        goose_message = GooseMessage(
            goose_signals=self.signals_array(goose_data.goose_set),
            gocbRef=goose_data.go_id,
            stNum=goose_data.stNum,
            sqNum=1,
            dst_MAC=goose_data.dst_mac,
            vlan=goose_data.vlan,
            prio=goose_data.prio,
            appid=convert_to_dec(goose_data.appid),
            timeAllowedtoLive=4800,     # TODO создать в GUI
            test=False,                  # TODO создать в GUI
            confRev=1,              # TODO создать в GUI
            ndsCom=False,           # TODO создать в GUI
            # sending_state=False,
        )
        return goose_message

    def check_thread(self, thread, mgo) -> None:
        # ОбНОВИТЬ СОСТОЯНИЕ ВИДЖЕТА
        # self.test_show_send_state()

        if thread.is_alive() and mgo.sending_state:
            self.view.after(500, lambda: self.check_thread(thread, mgo))
        else:
            print(f'GOOSE {mgo.goose_idx} sending has stopped')
            # del goose_message

            state = mgo.sending_state
            mgo.goose_tab.set_tab_to_sending_state(state=state)
            # self.test_show_send_state()

    def stop_one_goose(self, goose_idx) -> None:
        mgo = self.get_mgo_by_idx(goose_idx)
        print(f'StopOneGoose ({mgo.goose_idx})')
        mgo.sending_state = False

    @staticmethod
    def update_stNum(mgo) -> None:
        mgo.goose_data.stNum += 1
        stNum_value = mgo.goose_data.stNum
        mgo.goose_tab.update_stNum_view(stNum_value)

    def send_all_gooses(self) -> None:   # todo
        """ Отправка всех гусей: Нажимает кнопки Отправить на всех вкладках """
        print("send_all_gooses")
        for mgo in self.get_mgo_list():
            self.generate_one_goose(mgo.goose_idx)

    def stop_all_gooses(self) -> None:   # todo
        """ Остановка всех гусей: Нажимает кнопки Стоп на всех вкладках """
        print("stop_all_gooses")
        for mgo in self.get_mgo_list():
            self.stop_one_goose(mgo.goose_idx)

    def del_all_gooses(self):
        slice = self.gooses_container[:0:-1]
        for mgo in slice:    # исключая пустышку с индексом 0
            self.del_goose(mgo.goose_idx)

    def del_goose(self, goose_idx):
        mgo = self.get_mgo_by_idx(goose_idx)
        mgo.goose_tab.destroy()  # todo: удаляет следующую вкладку за требуемой, тк кол-во гусей становится меньше, а индексы гусей остаются прежними.
        del self.gooses_container[goose_idx]
        # при одиночном вызове метода - возможно, удалить имя гуся из goose_names
        # print()

    # Образец рекурсивного дестроя виджета tk
    # def destroy(self):
    #     """Destroy this and all descendants widgets."""
    #     for c in list(self.children.values()): c.destroy()
    #     self.tk.call('destroy', self._w)
    #     if self._name in self.master.children:
    #         del self.master.children[self._name]
    #     Misc.destroy(self)

##################################

    @staticmethod
    def signals_array(goose_set) -> list:
        # todo - восстановить порядок гусей, сейчас вразнобой из-за dict
        arr = []
        for gs_name, sub_dict in goose_set.items():
            value = goose_set[gs_name]['value']
            arr.append(value)

        return arr

    def get_mgo_list(self) -> list:
        return self.gooses_container[1:]  # get_mgo_list

    def get_mgo_by_idx(self, goose_idx) -> MainGooseObject:
        mgo = self.gooses_container[goose_idx]
        return mgo

    def test_show_send_state(self):
        print('---------')
        for gm in self.gooses_container:
            print(f'sending_state:   {gm.idx}:{gm.sending_state}   ', end='')
        print('=========')

    # def return_values(self, short=True):
    #     """ выводит положение всех сигналов гусь-сообщения """
    #     print(f'Номер GOOSE-сообщения: {self.idx}')
    #     print(f'APP ID: {self.appid_hex} ({self.appid_dec})')
    #     print(f'vlan: {self.vlan}, prio: {self.prio}')
    #     print(f'stNum: {self.stNum}')
    #     print(f'Кол-во GOOSE-сигналов в GOOSE-сообщении {len(self.signals_objects_array)}')
    #
    #     if short:
    #         print(' '.join([str(s)[0] for s in self.signals_array]))
    #     else:
    #         for n, signal in enumerate(self.signals_array):
    #             print(n + 1, signal == 1)
