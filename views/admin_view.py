from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal

from utils.protocols import IUserService
from views.table_model import ConfigurableTableModel


class AdminView(QWidget):
    add_user_requested = pyqtSignal()
    edit_user_requested = pyqtSignal(int)
    delete_user_requested = pyqtSignal(int)
    unlock_user_requested = pyqtSignal(int)
    refresh_requested = pyqtSignal(list)

    def __init__(self, user_service: IUserService, columns_config: list, current_user_id: int, parent=None):
        super().__init__(parent)
        self.user_service = user_service
        self.current_user_id = current_user_id
        self.table_model = ConfigurableTableModel([], columns_config)
        self.init_ui()
        self.setWindowTitle('Молочный комбинат ООО "Полесье" - Панель администратора')
        self.setMinimumSize(800, 600)

        self.add_btn.clicked.connect(self.add_user_requested.emit)
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.unlock_btn.clicked.connect(self.on_unlock_clicked)
        self.refresh_requested.connect(self.load_users)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table_view = QTableView()
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

    def load_users(self, users):
        self.table_model.refresh(users)

    def get_selected_user_id(self):
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            return None
        row = selection[0].row()
        if row < len(self.table_model.users):
            return self.table_model.users[row].user_id
        return None

    def on_edit_clicked(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            QMessageBox.information(self, "Редактирование", "Выберите пользователя.")
            return
        self.edit_user_requested.emit(user_id)

    def on_delete_clicked(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            QMessageBox.information(self, "Удаление", "Выберите пользователя.")
            return
        if user_id == self.current_user_id:
            QMessageBox.warning(self, "Недопустимая операция", "Вы не можете удалить свою учётную запись.")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить выбранного пользователя?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_user_requested.emit(user_id)

    def on_unlock_clicked(self):
        user_id = self.get_selected_user_id()
        if user_id is None:
            QMessageBox.information(self, "Разблокировка", "Выберите пользователя.")
            return
        self.unlock_user_requested.emit(user_id)
