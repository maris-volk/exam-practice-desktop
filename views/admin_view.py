from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QMessageBox, QHeaderView, QDialog)
from views.table_model import ConfigurableTableModel
from views.user_dialog import UserDialog
from utils.protocols import IUserController


USER_COLUMNS = [
    {"header": "ID", "getter": lambda u: str(u.user_id)},
    {"header": "Логин", "getter": lambda u: u.login},
    {"header": "Роль", "getter": lambda u: u.role.role_name if u.role else ""},
    {"header": "Попытки", "getter": lambda u: str(u.login_attempts)},
    {"header": "Фамилия", "getter": lambda u: u.last_name or ""},
    {"header": "Имя", "getter": lambda u: u.first_name or ""},
    {"header": "Отчество", "getter": lambda u: u.patronymic or ""},
    {"header": "Телефон", "getter": lambda u: u.phone_number or ""},
]


class AdminView(QWidget):
    def __init__(self, user_controller: IUserController, current_user_id: int, parent=None):
        super().__init__(parent)
        self.user_controller = user_controller
        self.current_user_id = current_user_id
        self.init_ui()
        self.setWindowTitle("Панель администратора")
        self.setMinimumSize(800, 600)
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table_view = QTableView()
        self.table_model = ConfigurableTableModel([], USER_COLUMNS)
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSortingEnabled(True)

        self.table_view.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table_view)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить пользователя")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        self.unlock_btn = QPushButton("Разблокировать")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.unlock_btn)
        layout.addLayout(btn_layout)

        self.setTabOrder(self.table_view, self.add_btn)
        self.setTabOrder(self.add_btn, self.edit_btn)
        self.setTabOrder(self.edit_btn, self.delete_btn)
        self.setTabOrder(self.delete_btn, self.unlock_btn)

        self.add_btn.clicked.connect(self.add_user)
        self.edit_btn.clicked.connect(self.edit_user)
        self.delete_btn.clicked.connect(self.delete_user)
        self.unlock_btn.clicked.connect(self.unlock_user)

    def focusNextPrevChild(self, next_child: bool) -> bool:
        current = self.focusWidget()
        if next_child:
            if current == self.unlock_btn:
                self.table_view.setFocus()
                return True
        else:
            if current == self.table_view:
                self.unlock_btn.setFocus()
                return True
        return super().focusNextPrevChild(next_child)

    def load_users(self):
        try:
            users = self.user_controller.get_all_users()
            self.table_model.refresh(users)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить пользователей: {e}")
            self.table_model.refresh([])

    def get_selected_user(self):
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            return None
        row = selection[0].row()
        if row < len(self.table_model.users):
            return self.table_model.users[row]
        return None

    def add_user(self):
        dialog = UserDialog(self.user_controller, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def edit_user(self):
        user = self.get_selected_user()
        if not user:
            QMessageBox.information(self, "Редактирование", "Выберите пользователя.")
            return
        dialog = UserDialog(self.user_controller, user, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def delete_user(self):
        user = self.get_selected_user()
        if not user:
            QMessageBox.information(self, "Удаление", "Выберите пользователя.")
            return

        if user.user_id == self.current_user_id:
            QMessageBox.warning(self, "Недопустимая операция", "Вы не можете удалить свою собственную учётную запись.")
            return

        reply = QMessageBox.question(self, "Подтверждение", f"Удалить пользователя '{user.login}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            success = self.user_controller.delete_user(user.user_id)
            if success:
                self.load_users()
            else:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось удалить пользователя.\n"
                                 f"Возможно, есть связанные данные.\n\n"
                                 f"Детали: {e}")

    def unlock_user(self):
        user = self.get_selected_user()
        if not user:
            QMessageBox.information(self, "Разблокировка", "Выберите пользователя.")
            return
        if user.login_attempts < 3:
            QMessageBox.information(self, "Разблокировка", "Пользователь не заблокирован.")
            return
        self.user_controller.unlock_user(user.user_id)
        self.load_users()
        QMessageBox.information(self, "Разблокировка", f"Пользователь '{user.login}' разблокирован.")