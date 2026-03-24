from typing import Any
from sqlalchemy.orm import Session


class SQLAlchemySession:
    def __init__(self, session: Session):
        self._session = session

    def query(self, model: Any):
        return self._session.query(model)

    def add(self, instance: Any):
        self._session.add(instance)

    def delete(self, instance: Any):
        self._session.delete(instance)

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    def close(self):
        self._session.close()