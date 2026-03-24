from PyQt5.QtWidgets import QApplication
from routing.navigation_manager import NavigationManager
from utils.protocols import IAuthController, IUserController
from views.login_view import LoginView


class AuthFlowHandler:
    def __init__(
        self,
        auth_controller: IAuthController,
        user_controller: IUserController,
        login_view: LoginView,
        navigation_manager: 'NavigationManager'
    ):
        self.auth_controller = auth_controller
        self.user_controller = user_controller
        self.login_view = login_view
        self.navigation_manager = navigation_manager
        self.pending_user = None

        self.login_view.login_requested.connect(self.on_login_requested)
        self.login_view.info_closed.connect(self.on_info_closed)

    def on_login_requested(self, login: str, password: str):
        validation = self.auth_controller.validate_credentials(login, password)
        if not validation.is_valid:
            self.login_view.show_warning.emit("Ошибка ввода", validation.error_message)
            return

        if not self.login_view.captcha_solved:
            self.login_view.show_warning.emit("Капча", "Сначала соберите пазл.")
            return

        user = self.auth_controller.authenticate(login, password)

        if user:
            self.pending_user = user
            self.login_view.show_info.emit("Успех", "Вы успешно авторизовались.")
        else:
            if self.auth_controller.is_user_blocked(login):
                self.login_view.show_critical.emit("Доступ заблокирован",
                                                   "Вы заблокированы. Обратитесь к администратору.")
            else:
                attempts, max_attempts = self.auth_controller.get_attempts_info(login)
                remaining = max_attempts - attempts
                self.login_view.show_critical.emit("Ошибка авторизации",
                                                   f"Вы ввели неверный логин или пароль.\n"
                                                   f"Осталось попыток: {remaining}")
            self.login_view.reset_captcha_after_failure()

    def on_info_closed(self):
        if self.pending_user:
            user = self.pending_user
            self.pending_user = None
            if user.role.role_name == "admin":
                self.navigation_manager.show_admin(self.user_controller)
            else:
                QApplication.quit()