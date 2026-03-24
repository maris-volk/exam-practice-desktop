from database.session_protocol import IDatabaseSession


class BaseController:
    def __init__(self, db_session: IDatabaseSession):
        self.db = db_session

    def _execute(self, func):
        try:
            result = func()
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise