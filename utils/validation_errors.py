from typing import NamedTuple, Optional


class ValidationResult(NamedTuple):
    is_valid: bool
    error_message: Optional[str] = None