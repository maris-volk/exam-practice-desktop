from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt
from utils.protocols import IUserController


class UserDialog(QDialog):
    def __init__(self, user_controller: IUserController, user=None, parent=None):
        super().__init__(parent)
        self.user_controller = user_controller
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
        try:
            roles = self.user_controller.get_roles()
            for role in roles:
                self.role_combo.addItem(role.role_name, role.role_id)
            if self.user:
                index = self.role_combo.findData(self.user.role_id)
                if index >= 0:
                    self.role_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить роли: {e}")
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

        phone = ""
        if phone_raw:
            phone_digits = ''.join(c for c in phone_raw if c.isdigit())
            if len(phone_digits) == 11 and phone_digits[0] in ('7', '8'):
                phone = '+' + ('7' if phone_digits[0] == '8' else phone_digits[0]) + phone_digits[1:]
            else:
                QMessageBox.warning(self, "Ошибка", "Введите телефон в формате +7 (XXX) XXX-XX-XX")
                return

        is_edit = self.user is not None
        validation = self.user_controller.validate_user_data(
            login=login,
            password=password if password else None,
            last_name=last_name,
            first_name=first_name,
            patronymic=patronymic,
            phone=phone,
            is_edit=is_edit
        )
        if not validation.is_valid:
            QMessageBox.warning(self, "Ошибка", validation.error_message)
            return

        if phone:
            exclude_id = self.user.user_id if self.user else None
            if self.user_controller.is_phone_exists(phone, exclude_user_id=exclude_id):
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким номером телефона уже существует.")
                return

        try:
            if self.user is None:
                success = self.user_controller.add_user(
                    login, password, role_name, last_name, first_name, patronymic, phone
                )
                if not success:
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует.")
                    return
            else:
                success = self.user_controller.update_user(
                    self.user.user_id,
                    login=login,
                    password=password if password else None,
                    role_name=role_name,
                    last_name=last_name,
                    first_name=first_name,
                    patronymic=patronymic,
                    phone_number=phone,
                )
                if not success:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить пользователя (возможно, логин уже занят).")
                    return
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return

        super().accept()