import os
from dependency_injector import containers, providers

from database.session_factory import SessionFactory
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from services.auth_service import AuthService
from services.user_service import UserService
from services.captcha_service import CaptchaService
from views.captcha_widget import CaptchaWidget
from views.login_view import LoginView
from core.factories import AdminViewFactory
from routing.navigation_manager import NavigationManager
from routing.auth_flow_handler import AuthFlowHandler
from routing.admin_action_handler import AdminActionHandler

def _get_image_paths() -> list:
    base_path = os.path.join(os.path.dirname(__file__), "..", "resources")
    return [os.path.join(base_path, f"{i}.png") for i in range(1, 5)]


class Container(containers.DeclarativeContainer):
    session_factory = providers.Singleton(SessionFactory)

    user_repo = providers.Factory(UserRepository, session_factory=session_factory)
    role_repo = providers.Factory(RoleRepository, session_factory=session_factory)

    captcha_service = providers.Singleton(CaptchaService, correct_order=list(range(4)))
    auth_service = providers.Factory(AuthService, session_factory=session_factory)
    user_service = providers.Factory(UserService, session_factory=session_factory)

    get_image_paths = providers.Resource(_get_image_paths)

    captcha_widget = providers.Factory(
        CaptchaWidget,
        image_paths=get_image_paths,
        captcha_service=captcha_service,
    )

    login_view = providers.Singleton(
        LoginView,
        captcha_widget=captcha_widget,
    )

    admin_view_factory = providers.Factory(AdminViewFactory)

    admin_action_handler = providers.Factory(
        AdminActionHandler,
        user_service=user_service,
        login_view=login_view,
    )

    navigation_manager = providers.Factory(
        NavigationManager,
        login_view=login_view,
        user_service=user_service,
        admin_view_factory=admin_view_factory,
    )

    auth_flow_handler = providers.Factory(
        AuthFlowHandler,
        auth_service=auth_service,
        login_view=login_view,
        navigation_manager=navigation_manager,
    )