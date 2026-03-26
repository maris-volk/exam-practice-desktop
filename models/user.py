from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "app_user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("role.role_id"), nullable=False)
    last_name = Column(String(100))
    first_name = Column(String(100))
    patronymic = Column(String(100))
    phone_number = Column(String(20))
    login_attempts = Column(Integer, default=0)

    role = relationship("Role", back_populates="users")
