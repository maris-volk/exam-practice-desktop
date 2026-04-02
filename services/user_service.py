from typing import Optional, List, Tuple
from models.user import User
from models.role import Role
from utils.protocols import ISessionFactory, IUserService
from utils.password_hasher import hash_password
from utils.validators import (
    validate_login, validate_password, validate_phone, validate_fio,
    normalize_phone
)
from utils.validation_errors import ValidationResult
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository


class UserValidationService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def validate_user_data(
        self,
        login: str,
        password: Optional[str] = None,
        last_name: str = "",
        first_name: str = "",
        patronymic: str = "",
        phone: str = "",
        is_edit: bool = False
    ) -> ValidationResult:
        ok, msg = validate_login(login)
        if not ok:
            return ValidationResult(False, msg)

        if not is_edit or password:
            ok, msg = validate_password(password or "")
            if not ok:
                return ValidationResult(False, msg)

        if phone:
            ok, msg = validate_phone(phone)
            if not ok:
                return ValidationResult(False, msg)

        ok, msg = validate_fio(last_name, first_name, patronymic)
        if not ok:
            return ValidationResult(False, msg)

        return ValidationResult(True)

    def prepare_user_data(self, data: dict, is_edit: bool) -> Tuple[Optional[dict], str]:
        login = data.get("login", "")
        password = data.get("password", "")
        role_name = data.get("role_name", "")
        last_name = data.get("last_name", "")
        first_name = data.get("first_name", "")
        patronymic = data.get("patronymic", "")
        phone_raw = data.get("phone", "")

        phone = normalize_phone(phone_raw)

        validation = self.validate_user_data(
            login=login, password=password if password else None,
            last_name=last_name, first_name=first_name,
            patronymic=patronymic, phone=phone, is_edit=is_edit
        )
        if not validation.is_valid:
            return None, validation.error_message

        prepared = {
            "login": login,
            "password": password,
            "role_name": role_name,
            "last_name": last_name,
            "first_name": first_name,
            "patronymic": patronymic,
            "phone": phone,
        }
        return prepared, ""

    def is_phone_exists(self, phone: str, exclude_user_id: Optional[int] = None) -> bool:
        return self.user_repo.is_phone_exists(phone, exclude_user_id)


class UserPersistenceService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def get_all_users(self) -> List[User]:
        return self.user_repo.get_all()

    def get_roles(self) -> List[Role]:
        return self.role_repo.get_all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

    def get_user_by_login(self, login: str) -> Optional[User]:
        return self.user_repo.get_by_login(login)

    def add_user(self, user: User) -> Optional[User]:
        if self.user_repo.get_by_login(user.login):
            return None
        return self.user_repo.add(user)

    def update_user(self, user: User) -> Optional[User]:
        existing = self.user_repo.get_by_id(user.user_id)
        if not existing:
            return None

        if user.login != existing.login:
            conflict = self.user_repo.get_by_login(user.login)
            if conflict and conflict.user_id != user.user_id:
                return None

        if user.phone_number and user.phone_number != existing.phone_number:
            if self.user_repo.is_phone_exists(user.phone_number, exclude_user_id=user.user_id):
                return None

        return self.user_repo.update(user)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete(user_id)

    def unlock_user(self, user_id: int) -> bool:
        user = self.user_repo.unlock(user_id)
        return user is not None


class UserOperationService:
    def __init__(self, validation: UserValidationService, persistence: UserPersistenceService):
        self.validation = validation
        self.persistence = persistence

    def add_user(self, data: dict) -> Optional[User]:
        prepared, error = self.validation.prepare_user_data(data, is_edit=False)
        if not prepared:
            raise ValueError(error)

        if prepared["phone"]:
            if self.validation.is_phone_exists(prepared["phone"]):
                raise ValueError("Пользователь с таким номером телефона уже существует.")

        role_obj = next((r for r in self.persistence.get_roles() if r.role_name == prepared["role_name"]), None)
        if not role_obj:
            raise ValueError(f"Роль '{prepared['role_name']}' не найдена.")

        user = User(
            login=prepared["login"],
            password_hash=hash_password(prepared["password"]),
            role_id=role_obj.role_id,
            last_name=prepared["last_name"],
            first_name=prepared["first_name"],
            patronymic=prepared["patronymic"],
            phone_number=prepared["phone"],
            login_attempts=0,
        )
        result = self.persistence.add_user(user)
        if result is None:
            raise ValueError("Пользователь с таким логином уже существует.")
        return result

    def edit_user(self, user_id: int, data: dict) -> Optional[User]:
        existing_user = self.persistence.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Пользователь не найден.")

        prepared, error = self.validation.prepare_user_data(data, is_edit=True)
        if not prepared:
            raise ValueError(error)

        if prepared["login"] != existing_user.login:
            conflict = self.persistence.get_user_by_login(prepared["login"])
            if conflict and conflict.user_id != user_id:
                raise ValueError("Пользователь с таким логином уже существует.")

        if prepared["phone"] and prepared["phone"] != existing_user.phone_number:
            if self.validation.is_phone_exists(prepared["phone"], exclude_user_id=user_id):
                raise ValueError("Пользователь с таким номером телефона уже существует.")

        role_obj = next((r for r in self.persistence.get_roles() if r.role_name == prepared["role_name"]), None)
        if not role_obj:
            raise ValueError(f"Роль '{prepared['role_name']}' не найдена.")

        updated_user = User(
            user_id=user_id,
            login=prepared["login"],
            password_hash=hash_password(prepared["password"]) if prepared["password"] else existing_user.password_hash,
            role_id=role_obj.role_id,
            last_name=prepared["last_name"],
            first_name=prepared["first_name"],
            patronymic=prepared["patronymic"],
            phone_number=prepared["phone"],
            login_attempts=existing_user.login_attempts
        )

        result = self.persistence.update_user(updated_user)
        if result is None:
            raise ValueError("Не удалось обновить пользователя.")
        return result

    def delete_user(self, user_id: int) -> bool:
        return self.persistence.delete_user(user_id)

    def unlock_user(self, user_id: int) -> bool:
        return self.persistence.unlock_user(user_id)


class UserService(IUserService):
    def __init__(self, session_factory: ISessionFactory):
        user_repo = UserRepository(session_factory)
        role_repo = RoleRepository(session_factory)
        self._validation = UserValidationService(user_repo, role_repo)
        self._persistence = UserPersistenceService(user_repo, role_repo)
        self._operations = UserOperationService(self._validation, self._persistence)

    def get_all_users(self) -> List[User]:
        return self._persistence.get_all_users()

    def get_roles(self) -> List[Role]:
        return self._persistence.get_roles()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._persistence.get_user_by_id(user_id)

    def get_user_by_login(self, login: str) -> Optional[User]:
        return self._persistence.get_user_by_login(login)

    def is_phone_exists(self, phone: str, exclude_user_id: Optional[int] = None) -> bool:
        return self._validation.is_phone_exists(phone, exclude_user_id)

    def validate_user_data(self, login: str, password: Optional[str] = None,
                           last_name: str = "", first_name: str = "",
                           patronymic: str = "", phone: str = "",
                           is_edit: bool = False) -> ValidationResult:
        return self._validation.validate_user_data(login, password, last_name, first_name, patronymic, phone, is_edit)

    def prepare_user_data(self, data: dict, is_edit: bool) -> Tuple[Optional[dict], str]:
        return self._validation.prepare_user_data(data, is_edit)

    def add_user(self, data: dict) -> Optional[User]:
        return self._operations.add_user(data)

    def edit_user(self, user_id: int, data: dict) -> Optional[User]:
        return self._operations.edit_user(user_id, data)

    def delete_user(self, user_id: int) -> bool:
        return self._operations.delete_user(user_id)

    def unlock_user(self, user_id: int) -> bool:
        return self._operations.unlock_user(user_id)

    def update_user(self, user: User) -> Optional[User]:
        return self._persistence.update_user(user)