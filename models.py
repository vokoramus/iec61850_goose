import re
import attr
# from iec61850_view import GooseTab
from time import sleep


def required(message):
    def func(self, attr, val):
        if not val:
            raise ValueError(message)
    return func


def match(pattern, message):
    regex = re.compile(pattern)

    def func(self, attr, val):
        if val and not regex.match(val):
            raise ValueError(message)
    return func


@attr.s
class GooseData(object):
    """ модель гусь сообщения """
    goose_index = attr.ib()
    goose_name = attr.ib(validator=required('goose_name обязателен'))
    goose_description = attr.ib()
    stNum = attr.ib()
    vlan = attr.ib()
    prio = attr.ib()
    dst_mac = attr.ib(validator=match(r"^\d{2}\:\d{2}$", "Ошибка в поле 'go_id'"))
    appid = attr.ib()
    go_id = attr.ib()
    inter = attr.ib()  # интервал отправки пакетов
    goose_set = attr.ib()


# @attr.s
# class GooseSignalModel(object):  # отнаследовать от dict?
#     """ модель гусь сигнала """
#     goose_no = attr.ib()
#     goose_name = attr.ib()
#     goose_index = attr.ib()
#     value = attr.ib()
#     pass


class MainGooseObject:
    def __init__(self,
                 goose_idx=None,
                 goose_data: GooseData = None,
                 goose_tab=None,
                 n_gooses=None,
                 ):
        self.goose_idx = goose_idx
        self.goose_data = goose_data
        self.goose_tab = goose_tab
        self.n_gooses = n_gooses
        self.sending_state = False

    def __del__(self):
        if self.sending_state:
            self.sending_state = False
            sleep(3)  # если вкладку будут удалять при отправке пакетов

        del self.goose_tab
        del self.goose_data
        del self


class GoosesContainer(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
