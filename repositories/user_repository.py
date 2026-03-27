from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from utils.protocols import ISessionFactory
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session_factory: ISessionFactory):
        super().__init__(session_factory, User)

    def get_all(self) -> List[User]:
        with self._get_session() as session:
            return session.query(User).options(joinedload(User.role)).all()

    def get_by_login(self, login: str) -> Optional[User]:
        with self._get_session() as session:
            return session.query(User).options(joinedload(User.role)).filter_by(login=login).first()

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