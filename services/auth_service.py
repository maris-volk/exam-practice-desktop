from typing import Optional, Tuple, NamedTuple
from models.user import User
from utils.protocols import ISessionFactory
from utils.password_hasher import verify_password
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository


class LoginResult(NamedTuple):
    success: bool
    user: Optional[User]
    blocked: bool
    attempts_remaining: int
    message: str


class AuthService:
    def __init__(self, session_factory: ISessionFactory):
        self.user_repo = UserRepository(session_factory)
        self.role_repo = RoleRepository(session_factory)

    def authenticate(self, login: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_login(login)
        if not user:
            return None
        if user.login_attempts >= 3:
            return None

        if verify_password(password, user.password_hash):
            user.login_attempts = 0
            return self.user_repo.update(user)
        else:
            user.login_attempts += 1
            self.user_repo.update(user)
            return None

    def get_user_role_name(self, user: User) -> Optional[str]:
        if not user or not user.role_id:
            return None
        role = self.role_repo.get_by_id(user.role_id)
        return role.role_name if role else None

    def is_user_blocked(self, login: str) -> bool:
        user = self.user_repo.get_by_login(login)
        return user is not None and user.login_attempts >= 3

    def increment_attempts(self, login: str) -> None:
        user = self.user_repo.get_by_login(login)
        if user and user.login_attempts < 3:
            user.login_attempts += 1
            self.user_repo.update(user)

    def get_attempts_info(self, login: str) -> Tuple[int, int]:
        user = self.user_repo.get_by_login(login)
        if user:
            return user.login_attempts, 3
        return 0, 3

    def user_exists(self, login: str) -> bool:
        return self.user_repo.get_by_login(login) is not None

    def handle_login_attempt(self, login: str, password: str, captcha_solved: bool) -> LoginResult:
        if not captcha_solved:
            if self.user_exists(login):
                self.increment_attempts(login)
                attempts, max_attempts = self.get_attempts_info(login)
                remaining = max_attempts - attempts
                if remaining <= 0:
                    return LoginResult(False, None, True, 0, "Вы заблокированы. Обратитесь к администратору.")
                else:
                    return LoginResult(False, None, False, remaining, f"Пазл собран неверно.\nОсталось попыток: {remaining}")
            else:
                return LoginResult(False, None, False, 0, "Пазл собран неверно.")

        user = self.authenticate(login, password)
        if user:
            return LoginResult(True, user, False, 0, "Вы успешно авторизовались.")
        else:
            if self.is_user_blocked(login):
                return LoginResult(False, None, True, 0, "Вы заблокированы. Обратитесь к администратору.")
            else:
                if self.user_exists(login):
                    attempts, max_attempts = self.get_attempts_info(login)
                    remaining = max_attempts - attempts
                    return LoginResult(False, None, False, remaining, f"Неверный пароль.\nОсталось попыток: {remaining}")
                else:
                    return LoginResult(False, None, False, 0, "Пользователь не найден.")