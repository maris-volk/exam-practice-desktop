from typing import Optional
from utils.protocols import ISessionFactory
from models.role import Role
from repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session_factory: ISessionFactory):
        super().__init__(session_factory, Role)

    def get_by_name(self, name: str) -> Optional[Role]:
        with self._get_session() as session:
            return session.query(Role).filter_by(role_name=name).first()