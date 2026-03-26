from typing import Protocol
from PyQt5.QtCore import pyqtSignal
from utils.protocols import IUserService


class ILoginView(Protocol):
    login_requested: pyqtSignal
    show_info: pyqtSignal
    show_warning: pyqtSignal
    show_critical: pyqtSignal
    info_closed: pyqtSignal
    captcha_solved: bool

    def reset_captcha_after_failure(self) -> None: ...
    def show(self) -> None: ...
    def hide(self) -> None: ...


class IAdminView(Protocol):
    def show(self) -> None: ...
    def hide(self) -> None: ...


class IAdminViewFactory(Protocol):
    def create(self, user_service: IUserService, current_user_id: int) -> IAdminView: ...