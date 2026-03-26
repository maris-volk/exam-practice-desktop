from sqlalchemy.orm import Session
from .db_session import SessionLocal


class SessionFactory:
    def __call__(self) -> Session:
        return SessionLocal()