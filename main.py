import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from database.init_db import init_db
from core.container import Container

logging.getLogger('sqlalchemy').setLevel(logging.ERROR)


def main():
    app = QApplication(sys.argv)

    try:
        init_db()
    except Exception as e:
        QMessageBox.critical(None, "Ошибка БД", f"Не удалось инициализировать базу данных:\n{e}")
        sys.exit(1)

    container = Container()
    container.init_resources()

    auth_flow_handler = container.auth_flow_handler()
    navigation_manager = container.navigation_manager()
    navigation_manager.quit_application.connect(app.quit)
    navigation_manager.show_login()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()