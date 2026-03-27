from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from utils.protocols import ISessionFactory
from models.base import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session_factory: ISessionFactory, model: Type[T]):
        self._session_factory = session_factory
        self._model = model

    def _get_session(self) -> Session:
        return self._session_factory()

    def get_all(self) -> List[T]:
        with self._get_session() as session:
            return session.query(self._model).all()

    def get_by_id(self, obj_id: int) -> Optional[T]:
        with self._get_session() as session:
            return session.get(self._model, obj_id)

    def add(self, obj: T) -> T:
        with self._get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def update(self, obj: T) -> T:
        with self._get_session() as session:
            pk_attr = self._model.__mapper__.primary_key[0].name
            pk_value = getattr(obj, pk_attr)

            existing = session.get(self._model, pk_value)
            if not existing:
                raise ValueError(f"{self._model.__name__} with {pk_attr}={pk_value} not found")

            for key, value in obj.__dict__.items():
                if not key.startswith('_') and key != pk_attr:
                    setattr(existing, key, value)

            session.commit()
            session.refresh(existing)
            return existing

    def delete(self, obj_id: int) -> bool:
        with self._get_session() as session:
            obj = session.get(self._model, obj_id)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True