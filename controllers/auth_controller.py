from typing import Optional, Tuple
from controllers.base_controller import BaseController
from models.user import User
from utils.password_hasher import verify_password
from utils.validators import validate_login, validate_password
from utils.validation_errors import ValidationResult


class AuthController(BaseController):
    def validate_credentials(self, login: str, password: str) -> ValidationResult:
        ok, msg = validate_login(login)
        if not ok:
            return ValidationResult(False, msg)
        ok, msg = validate_password(password)
        if not ok:
            return ValidationResult(False, msg)
        return ValidationResult(True)

    def authenticate(self, login: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter_by(login=login).first()
        if not user or user.login_attempts >= 3:
            return None

        def _auth():
            if verify_password(password, user.password_hash):
                user.login_attempts = 0
            else:
                user.login_attempts += 1
            return user if user.login_attempts == 0 else None

        return self._execute(_auth)

    def is_user_blocked(self, login: str) -> bool:
        user = self.db.query(User).filter_by(login=login).first()
        return user is not None and user.login_attempts >= 3

    def increment_attempts(self, login: str) -> None:
        def _inc():
            user = self.db.query(User).filter_by(login=login).first()
            if user:
                user.login_attempts += 1
        self._execute(_inc)

    def get_attempts_info(self, login: str) -> Tuple[int, int]:
        user = self.db.query(User).filter_by(login=login).first()
        if user:
            return user.login_attempts, 3
        return 0, 3