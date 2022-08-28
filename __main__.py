from iec61850_repository import GooseRepository
from iec61850_view import GooseView, GooseTab
from iec61850_controller import GooseController


def main():
    repo = GooseRepository()
    view = GooseView()
    ctrl = GooseController(repo, view)

    view.set_ctrl(ctrl)     # подключить управление
    ctrl.start()            # старт (загрузка данных и запуск окна программы)

if __name__ == "__main__":
    main()
