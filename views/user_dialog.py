from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal


class UserDialog(QDialog):
    data_submitted = pyqtSignal(dict)

    def __init__(self, roles: list, user=None, parent=None):
        super().__init__(parent)
        self.roles = roles
        self.user = user
        self.setWindowTitle("Добавить пользователя" if user is None else "Редактировать пользователя")
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.init_ui()
        self.setMinimumSize(450, 500)

    def init_ui(self):
        layout = QFormLayout()
        self.setLayout(layout)

        self.login_edit = QLineEdit()
        self.login_edit.setMaxLength(50)
        if self.user:
            self.login_edit.setText(self.user.login)
        layout.addRow("Логин:", self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMaxLength(100)
        if self.user is not None:
            self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять")
        layout.addRow("Пароль:", self.password_edit)

        self.role_combo = QComboBox()
        for role in self.roles:
            self.role_combo.addItem(role.role_name, role.role_id)
        if self.user:
            index = self.role_combo.findData(self.user.role_id)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        layout.addRow("Роль:", self.role_combo)

        self.last_name_edit = QLineEdit()
        self.last_name_edit.setMaxLength(100)
        if self.user:
            self.last_name_edit.setText(self.user.last_name or "")
        layout.addRow("Фамилия:", self.last_name_edit)

        self.first_name_edit = QLineEdit()
        self.first_name_edit.setMaxLength(100)
        if self.user:
            self.first_name_edit.setText(self.user.first_name or "")
        layout.addRow("Имя:", self.first_name_edit)

        self.patronymic_edit = QLineEdit()
        self.patronymic_edit.setMaxLength(100)
        if self.user:
            self.patronymic_edit.setText(self.user.patronymic or "")
        layout.addRow("Отчество:", self.patronymic_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setMaxLength(20)
        self.phone_edit.setInputMask("+7 (999) 999-99-99;_")
        if self.user and self.user.phone_number:
            phone_digits = ''.join(c for c in self.user.phone_number if c.isdigit())
            if len(phone_digits) == 11 and phone_digits[0] in ('7', '8'):
                if phone_digits[0] == '8':
                    phone_digits = '7' + phone_digits[1:]
                self.phone_edit.setText(f"+7 ({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:9]}-{phone_digits[9:]}")
        layout.addRow("Телефон:", self.phone_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()
        role_name = self.role_combo.currentText()
        last_name = self.last_name_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        patronymic = self.patronymic_edit.text().strip()
        phone_raw = self.phone_edit.text().strip()

        self.data_submitted.emit({
            "login": login,
            "password": password,
            "role_name": role_name,
            "last_name": last_name,
            "first_name": first_name,
            "patronymic": patronymic,
            "phone": phone_raw,
            "is_edit": self.user is not None,
            "user_id": self.user.user_id if self.user else None,
        })