import re

LOGIN_REGEX = re.compile(r'^[a-zA-Z0-9._-]+$')
LOGIN_MIN_LEN = 5
LOGIN_MAX_LEN = 50

PASSWORD_MIN_LEN = 6
PASSWORD_MAX_LEN = 100
PASSWORD_REGEX = re.compile(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:,.<>?/~`|]+$')

PHONE_REGEX = re.compile(r'^(\+7|8)?\d{10}$')


def validate_login(login: str) -> tuple[bool, str]:
    if not login:
        return False, "Логин не может быть пустым."
    if len(login) < LOGIN_MIN_LEN:
        return False, f"Логин должен содержать не менее {LOGIN_MIN_LEN} символов."
    if len(login) > LOGIN_MAX_LEN:
        return False, f"Логин не может быть длиннее {LOGIN_MAX_LEN} символов."
    if not LOGIN_REGEX.match(login):
        return False, "Логин может содержать только латинские буквы, цифры, точки, дефисы и подчёркивания."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Пароль не может быть пустым."
    if len(password) < PASSWORD_MIN_LEN:
        return False, f"Пароль должен содержать не менее {PASSWORD_MIN_LEN} символов."
    if len(password) > PASSWORD_MAX_LEN:
        return False, f"Пароль не может быть длиннее {PASSWORD_MAX_LEN} символов."
    if not PASSWORD_REGEX.match(password):
        return False, "Пароль может содержать только латинские буквы, цифры и спецсимволы (!@#$%^&*()_+-=)."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    if not phone:
        return True, ""
    phone_clean = re.sub(r'\D', '', phone)
    if len(phone_clean) != 11:
        return False, "Номер телефона должен содержать 11 цифр (например, +79123456789)."
    if phone_clean[0] not in ('7', '8'):
        return False, "Номер должен начинаться с 7 или 8 (российский формат)."
    return True, ""


def validate_name(name: str, field_name: str) -> tuple[bool, str]:
    if not name:
        return True, ""

    if name in ('.', '-', "'", ' ', ',', '(', ')', ''):
        return False, f"{field_name} не может состоять только из одного символа пунктуации."

    first = name[0]
    last = name[-1]
    if first in ('.', '-', "'", ' ', ',', ')'):
        return False, f"{field_name} не может начинаться с символа '{first}'."
    if last in ('.', '-', "'", ' ', ',', '('):
        return False, f"{field_name} не может заканчиваться символом '{last}'."

    forbidden_pairs = ['..', '--', "''", '  ', ',,', '((', '))']
    for pair in forbidden_pairs:
        if pair in name:
            return False, f"{field_name} не может содержать подряд идущие символы '{pair[0]}'."

    if '(' in name and ')' not in name:
        return False, f"{field_name} содержит открывающую скобку без закрывающей."
    if ')' in name and '(' not in name:
        return False, f"{field_name} содержит закрывающую скобку без открывающей."

    if not re.match(r'^[а-яА-ЯёЁ\s\-\.\,\'\(\)]+$', name):
        return False, f"{field_name} может содержать только кириллицу, пробелы, дефисы, апострофы, точки, запятые и скобки."

    return True, ""


def validate_fio(last_name: str, first_name: str, patronymic: str) -> tuple[bool, str]:
    ok, msg = validate_name(last_name, "Фамилия")
    if not ok:
        return False, msg
    ok, msg = validate_name(first_name, "Имя")
    if not ok:
        return False, msg
    ok, msg = validate_name(patronymic, "Отчество")
    if not ok:
        return False, msg
    return True, ""