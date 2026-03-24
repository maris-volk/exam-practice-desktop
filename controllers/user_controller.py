from typing import Optional, List
from controllers.base_controller import BaseController
from models.user import User
from models.role import Role
from utils.password_hasher import hash_password
from utils.validators import (
    validate_login, validate_password, validate_phone, validate_fio
)
from utils.validation_errors import ValidationResult


class UserController(BaseController):
    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def get_roles(self) -> List[Role]:
        return self.db.query(Role).all()

    def is_phone_exists(self, phone: str, exclude_user_id: int = None) -> bool:
        if not phone:
            return False
        query = self.db.query(User).filter(User.phone_number == phone)
        if exclude_user_id is not None:
            query = query.filter(User.user_id != exclude_user_id)
        return query.first() is not None

    def validate_user_data(
        self,
        login: str,
        password: str = None,
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

    def add_user(
        self,
        login: str,
        password: str,
        role_name: str,
        last_name: str = "",
        first_name: str = "",
        patronymic: str = "",
        phone_number: str = ""
    ) -> bool:
        def _add():
            if self.db.query(User).filter_by(login=login).first():
                return False
            if phone_number and self.is_phone_exists(phone_number):
                return False

            role = self.db.query(Role).filter_by(role_name=role_name).first()
            if not role:
                raise ValueError(f"Роль '{role_name}' не существует")

            user = User(
                login=login,
                password_hash=hash_password(password),
                role_id=role.role_id,
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
                phone_number=phone_number,
                login_attempts=0,
            )
            self.db.add(user)
            return True

        return self._execute(_add)

    def update_user(
        self,
        user_id: int,
        login: str = None,
        password: str = None,
        role_name: str = None,
        last_name: str = None,
        first_name: str = None,
        patronymic: str = None,
        phone_number: str = None
    ) -> bool:
        def _update():
            user = self.db.query(User).get(user_id)
            if not user:
                return False

            if login is not None:
                conflict = self.db.query(User).filter_by(login=login).first()
                if conflict and conflict.user_id != user_id:
                    return False
                user.login = login

            if phone_number is not None:
                if self.is_phone_exists(phone_number, exclude_user_id=user_id):
                    return False
                user.phone_number = phone_number

            if password is not None:
                user.password_hash = hash_password(password)
            if role_name is not None:
                role = self.db.query(Role).filter_by(role_name=role_name).first()
                if role:
                    user.role_id = role.role_id
                else:
                    raise ValueError(f"Роль '{role_name}' не существует")
            if last_name is not None:
                user.last_name = last_name
            if first_name is not None:
                user.first_name = first_name
            if patronymic is not None:
                user.patronymic = patronymic

            return True

        return self._execute(_update)

    def delete_user(self, user_id: int) -> bool:
        def _delete():
            user = self.db.query(User).get(user_id)
            if not user:
                return False
            self.db.delete(user)
            return True

        return self._execute(_delete)

    def unlock_user(self, user_id: int) -> bool:
        def _unlock():
            user = self.db.query(User).get(user_id)
            if not user:
                return False
            user.login_attempts = 0
            return True

        return self._execute(_unlock)