from utils.protocols import IAuthService, INavigationManager
from utils.view_protocols import ILoginView
from utils.validators import validate_login, validate_password
from utils.validation_errors import ValidationResult


class AuthFlowHandler:
    def __init__(
            self,
            auth_service: IAuthService,
            login_view: ILoginView,
            navigation_manager: INavigationManager
    ):
        self.auth_service = auth_service
        self.login_view = login_view
        self.navigation_manager = navigation_manager
        self.pending_user = None

        self.login_view.login_requested.connect(self.on_login_requested)
        self.login_view.info_closed.connect(self.on_info_closed)

    def validate_credentials(self, login: str, password: str) -> ValidationResult:
        ok, msg = validate_login(login)
        if not ok:
            return ValidationResult(False, msg)
        ok, msg = validate_password(password)
        if not ok:
            return ValidationResult(False, msg)
        return ValidationResult(True)

    def on_login_requested(self, login: str, password: str):
        validation = self.validate_credentials(login, password)
        if not validation.is_valid:
            self.login_view.show_warning.emit("Ошибка ввода", validation.error_message)
            return

        result = self.auth_service.handle_login_attempt(login, password, self.login_view.captcha_solved)

        if result.success:
            self.pending_user = result.user
            self.login_view.show_info.emit("Успех", result.message)
        else:
            if result.blocked:
                self.login_view.show_critical.emit("Доступ заблокирован", result.message)
            else:
                self.login_view.show_warning.emit("Ошибка", result.message)
            self.login_view.reset_captcha_after_failure()

    def on_info_closed(self):
        if self.pending_user:
            role_name = self.auth_service.get_user_role_name(self.pending_user)
            self.navigation_manager.on_authentication_success(self.pending_user, role_name)
            self.pending_user = None