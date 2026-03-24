from PyQt5.QtWidgets import QApplication
from views.login_view import LoginView
from views.admin_view import AdminView
from utils.protocols import IUserController


class NavigationManager:
    def __init__(self, login_view: LoginView, user_controller: IUserController):
        self.login_view = login_view
        self.user_controller = user_controller
        self.admin_view = None

    def show_login(self):
        self.login_view.show()

    def on_authentication_success(self, user):
        if user.role.role_name == "admin":
            self.show_admin(user.user_id)
        else:
            QApplication.quit()

    def show_admin(self, current_user_id: int):
        try:
            self.admin_view = AdminView(self.user_controller, current_user_id)
            self.admin_view.show()
            self.login_view.hide()
        except Exception as e:
            self.login_view.show_critical.emit("Ошибка", f"Не удалось создать окно администратора:\n{e}")
            QApplication.quit()