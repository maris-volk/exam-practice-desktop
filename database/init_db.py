from sqlalchemy import inspect
from .db_session import engine, SessionLocal
from models.base import Base
from models.role import Role
from models.user import User
from utils.password_hasher import hash_password


def init_db():
    inspector = inspect(engine)
    if not inspector.has_table("app_user"):
        Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        if session.query(Role).filter_by(role_name="admin").count() == 0:
            session.add(Role(role_name="admin"))
        if session.query(Role).filter_by(role_name="user").count() == 0:
            session.add(Role(role_name="user"))
        session.commit()

        admin_role = session.query(Role).filter_by(role_name="admin").first()
        if admin_role and session.query(User).filter_by(login="admin").count() == 0:
            admin_user = User(
                login="admin",
                password_hash=hash_password("admin123"),
                role_id=admin_role.role_id,
                last_name="Admin",
                first_name="System",
                login_attempts=0,
            )
            session.add(admin_user)
            session.commit()