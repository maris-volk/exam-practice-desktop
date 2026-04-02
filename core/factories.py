from utils.view_protocols import IAdminViewFactory, IUserService
from views.admin_view import AdminView
from views.column_config import USER_COLUMNS


class AdminViewFactory(IAdminViewFactory):
    def create(self, user_service: IUserService, current_user_id: int) -> AdminView:
        return AdminView(user_service, USER_COLUMNS, current_user_id)