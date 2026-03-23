# User management business logic for admin
# Methods: get_all_users() -> List[User],
#         add_user(user_data) -> bool (checks for duplicate login),
#         update_user(user_id, user_data) -> bool,
#         delete_user(user_id) -> bool,
#         unlock_user(user_id) -> bool (resets login_attempts to 0)

# Uses SQLAlchemy session to interact with database