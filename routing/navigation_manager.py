from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from utils.protocols import IUserService
from utils.view_protocols import ILoginView, IAdminViewFactory
from routing.admin_action_handler import AdminActionHandler


class NavigationManager(QObject):
    quit_application = pyqtSignal()

    def __init__(self, login_view: ILoginView,
                 user_service: IUserService,
                 admin_view_factory: IAdminViewFactory):
        super().__init__()
        self.login_view = login_view
        self.user_service = user_service
        self.admin_view_factory = admin_view_factory
        self.admin_view = None
        self.action_handler = AdminActionHandler(user_service, login_view)

    def show_login(self):
        self.login_view.show()

    def on_authentication_success(self, user, role_name: str):
        try:
            if role_name == "admin":
                self.show_admin(user.user_id)
            else:
                self.quit_application.emit()
        except Exception as e:
            traceback.print_exc()
            self.login_view.show_critical.emit("Ошибка", f"Не удалось авторизоваться:\n{e}")

    def show_admin(self, current_user_id: int):
        try:
            self.admin_view = self.admin_view_factory.create(self.user_service, current_user_id)
            self.admin_view.add_user_requested.connect(self.on_add_user)
            self.admin_view.edit_user_requested.connect(self.on_edit_user)
            self.admin_view.delete_user_requested.connect(self.on_delete_user)
            self.admin_view.unlock_user_requested.connect(self.on_unlock_user)

            users = self.user_service.get_all_users()
            self.admin_view.refresh_requested.emit(users)

            self.admin_view.show()
            self.login_view.hide()
        except Exception as e:
            traceback.print_exc()
            self.login_view.show_critical.emit("Ошибка", f"Не удалось создать окно администратора:\n{e}")
            self.quit_application.emit()

    def on_add_user(self):
        self.action_handler.add_user(
            parent_widget=self.admin_view,
            on_success=self._refresh_admin_view
        )

    def on_edit_user(self, user_id: int):
        self.action_handler.edit_user(
            user_id=user_id,
            parent_widget=self.admin_view,
            on_success=self._refresh_admin_view
        )

    def on_delete_user(self, user_id: int):
        self.action_handler.delete_user(
            user_id=user_id,
            on_success=self._refresh_admin_view
        )

    def on_unlock_user(self, user_id: int):
        self.action_handler.unlock_user(
            user_id=user_id,
            on_success=self._refresh_admin_view
        )

    def _refresh_admin_view(self):
        users = self.user_service.get_all_users()
        if self.admin_view:
            self.admin_view.refresh_requested.emit(users)