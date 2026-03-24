from .validators import (
    validate_login, validate_password, validate_phone, validate_name, validate_fio,
    LOGIN_MIN_LEN, LOGIN_MAX_LEN, PASSWORD_MIN_LEN, PASSWORD_MAX_LEN
)
from .validation_errors import ValidationResult