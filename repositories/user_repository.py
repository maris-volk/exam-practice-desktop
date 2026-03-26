from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from utils.protocols import ISessionFactory
from models.user import User


class UserRepository:
    def __init__(self, session_factory: ISessionFactory):
        self._session_factory = session_factory

    def _get_session(self) -> Session:
        return self._session_factory()

    def get_all(self) -> List[User]:
        with self._get_session() as session:
            return session.query(User).options(joinedload(User.role)).all()

    def get_by_login(self, login: str) -> Optional[User]:
        with self._get_session() as session:
            return session.query(User).options(joinedload(User.role)).filter_by(login=login).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self._get_session() as session:
            return session.get(User, user_id)

    def add(self, user: User) -> User:
        with self._get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update(self, user: User) -> User:
        with self._get_session() as session:
            existing = session.get(User, user.user_id)
            if not existing:
                raise ValueError(f"User with id {user.user_id} not found")
            existing.login = user.login
            existing.password_hash = user.password_hash
            existing.role_id = user.role_id
            existing.last_name = user.last_name
            existing.first_name = user.first_name
            existing.patronymic = user.patronymic
            existing.phone_number = user.phone_number
            existing.login_attempts = user.login_attempts
            session.commit()
            session.refresh(existing)
            return existing

    def delete(self, user_id: int) -> bool:
        with self._get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False
            session.delete(user)
            session.commit()
            return True

    def unlock(self, user_id: int) -> Optional[User]:
        with self._get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return None
            user.login_attempts = 0
            session.commit()
            return user

    def is_phone_exists(self, phone: str, exclude_user_id: Optional[int] = None) -> bool:
        if not phone:
            return False
        with self._get_session() as session:
            query = select(User).where(User.phone_number == phone)
            if exclude_user_id is not None:
                query = query.where(User.user_id != exclude_user_id)
            return session.execute(query).first() is not None