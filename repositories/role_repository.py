from typing import List, Optional
from utils.protocols import ISessionFactory
from models.role import Role


class RoleRepository:
    def __init__(self, session_factory: ISessionFactory):
        self._session_factory = session_factory

    def _get_session(self):
        return self._session_factory()

    def get_all(self) -> List[Role]:
        with self._get_session() as session:
            return session.query(Role).all()

    def get_by_id(self, role_id: int) -> Optional[Role]:
        with self._get_session() as session:
            return session.query(Role).get(role_id)

    def get_by_name(self, name: str) -> Optional[Role]:
        with self._get_session() as session:
            return session.query(Role).filter_by(role_name=name).first()