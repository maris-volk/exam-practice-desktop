# Authentication business logic
# methods: authenticate(login, password) -> bool,
#         check_captcha_completed() -> bool,
#         get_user_by_credentials(login, password) -> User or None,
#         increment_attempts(user_id),
#         is_user_blocked(user_id) -> bool,
#         reset_attempts(user_id)

# handles failed attempt counting and blocking after 3 failures
# depends on SQLAlchemy session