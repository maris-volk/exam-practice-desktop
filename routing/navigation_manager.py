from PyQt5.QtWidgets import QApplication
from views.login_view import LoginView
from views.admin_view import AdminView
from utils.protocols import IUserController


class NavigationManager:
    def __init__(self, login_view: LoginView):
        self.login_view = login_view
        self.admin_view = None

    def show_login(self):
        self.login_view.show()

    def show_admin(self, user_controller: IUserController):
        try:
            self.admin_view = AdminView(user_controller)
            self.admin_view.show()
            self.login_view.hide()
        except Exception as e:
            self.login_view.show_critical.emit("Ошибка", f"Не удалось создать окно администратора:\n{e}")
            QApplication.quit()