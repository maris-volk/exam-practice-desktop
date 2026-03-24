from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from utils.protocols import ICaptchaWidget


class LoginView(QWidget):
    login_requested = pyqtSignal(str, str)
    show_info = pyqtSignal(str, str)
    show_warning = pyqtSignal(str, str)
    show_critical = pyqtSignal(str, str)
    info_closed = pyqtSignal()

    def __init__(self, captcha_widget: ICaptchaWidget, parent=None):
        super().__init__(parent)
        self.captcha_widget = captcha_widget
        self.captcha_solved = False
        self.init_ui()
        self.setWindowTitle("Авторизация")
        self.setMinimumSize(500, 500)

        self.show_info.connect(self._show_info)
        self.show_warning.connect(self._show_warning)
        self.show_critical.connect(self._show_critical)

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        login_group = QGroupBox("Данные для входа")
        login_layout = QVBoxLayout()
        login_group.setLayout(login_layout)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)

        login_layout.addWidget(QLabel("Логин:"))
        login_layout.addWidget(self.login_edit)
        login_layout.addWidget(QLabel("Пароль:"))
        login_layout.addWidget(self.password_edit)

        captcha_group = QGroupBox("Капча: соберите пазл")
        captcha_layout = QVBoxLayout()
        captcha_group.setLayout(captcha_layout)

        self.captcha_widget.solved.connect(self.on_captcha_solved)
        captcha_layout.addWidget(self.captcha_widget)

        reset_btn = QPushButton("Сбросить пазл")
        reset_btn.clicked.connect(self.on_reset_captcha)
        captcha_layout.addWidget(reset_btn)

        main_layout.addWidget(login_group)
        main_layout.addWidget(captcha_group)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.on_login_clicked)
        main_layout.addWidget(self.login_btn)

        self.setTabOrder(self.login_edit, self.password_edit)
        self.setTabOrder(self.password_edit, self.captcha_widget)
        self.login_edit.setFocus()

    def on_reset_captcha(self):
        self.captcha_widget.reset()
        self.captcha_solved = False

    def on_captcha_solved(self):
        self.captcha_solved = True
        self.show_info.emit("Капча", "Пазл собран верно!")

    def on_login_clicked(self):
        if not self.captcha_solved:
            self.show_warning.emit("Капча", "Сначала соберите пазл")
            return
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        self.login_requested.emit(login, password)

    def reset_captcha_after_failure(self):
        self.captcha_widget.reset()
        self.captcha_solved = False

    def _show_info(self, title: str, text: str):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.finished.connect(lambda: self.info_closed.emit())
        msg_box.open()

    def _show_warning(self, title: str, text: str):
        QMessageBox.warning(self, title, text)

    def _show_critical(self, title: str, text: str):
        QMessageBox.critical(self, title, text)