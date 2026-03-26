import traceback
from typing import Optional, Callable
from PyQt5.QtCore import QObject
from utils.protocols import IUserService
from utils.view_protocols import ILoginView
from views.user_dialog import UserDialog


class AdminActionHandler(QObject):
    def __init__(self, user_service: IUserService, login_view: ILoginView):
        super().__init__()
        self.user_service = user_service
        self.login_view = login_view
        self._operation_in_progress = False

    def add_user(self, parent_widget, on_success: Optional[Callable] = None):
        roles = self.user_service.get_roles()
        dialog = UserDialog(roles, parent=parent_widget)
        dialog.data_submitted.connect(lambda data: self._handle_user_data(data, dialog, is_edit=False, on_success=on_success))
        dialog.open()

    def edit_user(self, user_id: int, parent_widget, on_success: Optional[Callable] = None):
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            self.login_view.show_warning.emit("Ошибка", "Пользователь не найден.")
            return
        roles = self.user_service.get_roles()
        dialog = UserDialog(roles, user=user, parent=parent_widget)
        dialog.data_submitted.connect(lambda data: self._handle_user_data(data, dialog, is_edit=True, user_id=user_id, on_success=on_success))
        dialog.open()

    def delete_user(self, user_id: int, on_success: Optional[Callable] = None):
        try:
            success = self.user_service.delete_user(user_id)
            if success:
                if on_success:
                    on_success()
            else:
                self.login_view.show_warning.emit("Ошибка", "Не удалось удалить пользователя.")
        except Exception as e:
            traceback.print_exc()
            self.login_view.show_critical.emit("Ошибка", f"Не удалось удалить пользователя: {e}")

    def unlock_user(self, user_id: int, on_success: Optional[Callable] = None):
        try:
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                self.login_view.show_warning.emit("Ошибка", "Пользователь не найден.")
                return
            login = user.login
            success = self.user_service.unlock_user(user_id)
            if success:
                if on_success:
                    on_success()
                self.login_view.show_info.emit("Разблокировка", f"Пользователь '{login}' разблокирован.")
            else:
                self.login_view.show_warning.emit("Ошибка", "Не удалось разблокировать пользователя.")
        except Exception as e:
            traceback.print_exc()
            self.login_view.show_critical.emit("Ошибка", f"Не удалось разблокировать пользователя: {e}")

    def _handle_user_data(self, data: dict, dialog: UserDialog, is_edit: bool, user_id: int = None, on_success: Optional[Callable] = None):
        if self._operation_in_progress:
            return
        self._operation_in_progress = True
        try:
            if is_edit:
                result = self.user_service.edit_user(user_id, data)
            else:
                result = self.user_service.add_user(data)

            if result is not None:
                if on_success:
                    on_success()
                dialog.close()
            else:
                self.login_view.show_warning.emit("Ошибка", "Неизвестная ошибка.")
        except ValueError as e:
            self.login_view.show_warning.emit("Ошибка", str(e))
        except Exception as e:
            traceback.print_exc()
            self.login_view.show_critical.emit("Ошибка", f"Не удалось выполнить операцию: {e}")
        finally:
            self._operation_in_progress = False