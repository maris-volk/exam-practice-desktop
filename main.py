import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from database.db_session import SessionLocal
from database.init_db import init_db
from database.sqlalchemy_session import SQLAlchemySession
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from views.captcha_widget import CaptchaWidget
from views.login_view import LoginView
from routing.navigation_manager import NavigationManager
from routing.auth_flow_handler import AuthFlowHandler
from utils.protocols import ICaptchaWidget


class AppFactory:
    @staticmethod
    def create_controllers(db_session):
        auth_controller = AuthController(db_session)
        user_controller = UserController(db_session)
        return auth_controller, user_controller

    @staticmethod
    def create_captcha_widget() -> ICaptchaWidget:
        base_path = os.path.join(os.path.dirname(__file__), "resources")
        image_paths = [os.path.join(base_path, f"{i}.png") for i in range(1, 5)]
        return CaptchaWidget(image_paths)

    @staticmethod
    def create_login_view(captcha_widget: ICaptchaWidget) -> LoginView:
        return LoginView(captcha_widget)


def main():
    app = QApplication(sys.argv)
    try:
        init_db()
    except Exception as e:
        QMessageBox.critical(None, "Ошибка БД", f"Не удалось инициализировать базу данных:\n{e}")
        sys.exit(1)

    raw_session = SessionLocal()
    db_session = SQLAlchemySession(raw_session)

    auth_controller, user_controller = AppFactory.create_controllers(db_session)
    captcha_widget = AppFactory.create_captcha_widget()
    login_view = AppFactory.create_login_view(captcha_widget)

    # NavigationManager теперь получает user_controller для создания AdminView
    navigation_manager = NavigationManager(login_view, user_controller)
    auth_flow_handler = AuthFlowHandler(
        auth_controller,
        login_view,
        navigation_manager
    )

    navigation_manager.show_login()
    result = app.exec_()
    raw_session.close()
    sys.exit(result)


if __name__ == "__main__":
    main()