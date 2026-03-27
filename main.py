import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from database.init_db import init_db
from services.auth_service import AuthService
from services.user_service import UserService
from services.captcha_service import CaptchaService
from views.captcha_widget import CaptchaWidget
from views.column_config import USER_COLUMNS
from views.login_view import LoginView
from views.admin_view import AdminView
from routing.navigation_manager import NavigationManager
from routing.auth_flow_handler import AuthFlowHandler
from utils.protocols import ICaptchaWidget, IUserService
from utils.view_protocols import IAdminViewFactory
from database.session_factory import SessionFactory

logging.getLogger('sqlalchemy').setLevel(logging.ERROR)


class AdminViewFactory(IAdminViewFactory):
    def create(self, user_service: IUserService, current_user_id: int):
        return AdminView(user_service, USER_COLUMNS, current_user_id)


class AppFactory:
    @staticmethod
    def create_services(session_factory):
        auth_service = AuthService(session_factory)
        user_service = UserService(session_factory)
        captcha_service = CaptchaService(list(range(4)))
        return auth_service, user_service, captcha_service

    @staticmethod
    def create_captcha_widget(captcha_service: CaptchaService) -> ICaptchaWidget:
        base_path = os.path.join(os.path.dirname(__file__), "resources")
        image_paths = [os.path.join(base_path, f"{i}.png") for i in range(1, 5)]
        return CaptchaWidget(image_paths, captcha_service)

    @staticmethod
    def create_login_view(captcha_widget: ICaptchaWidget) -> LoginView:
        return LoginView(captcha_widget)

    @staticmethod
    def create_admin_view_factory() -> IAdminViewFactory:
        return AdminViewFactory()


def main():
    app = QApplication(sys.argv)
    try:
        init_db()
    except Exception as e:
        QMessageBox.critical(None, "Ошибка БД", f"Не удалось инициализировать базу данных:\n{e}")
        sys.exit(1)

    session_factory = SessionFactory()
    auth_service, user_service, captcha_service = AppFactory.create_services(session_factory)

    captcha_widget = AppFactory.create_captcha_widget(captcha_service)
    login_view = AppFactory.create_login_view(captcha_widget)

    admin_view_factory = AppFactory.create_admin_view_factory()
    navigation_manager = NavigationManager(login_view, user_service, admin_view_factory)

    auth_flow_handler = AuthFlowHandler(auth_service, login_view, navigation_manager)

    navigation_manager.quit_application.connect(app.quit)
    navigation_manager.show_login()
    result = app.exec_()
    sys.exit(result)


if __name__ == "__main__":
    main()