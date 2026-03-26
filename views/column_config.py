USER_COLUMNS = [
    {"header": "ID", "getter": lambda u: u.user_id},
    {"header": "Логин", "getter": lambda u: u.login},
    {"header": "Роль", "getter": lambda u: u.role.role_name if u.role else ""},
    {"header": "Попытки", "getter": lambda u: u.login_attempts},
    {"header": "Фамилия", "getter": lambda u: u.last_name or ""},
    {"header": "Имя", "getter": lambda u: u.first_name or ""},
    {"header": "Отчество", "getter": lambda u: u.patronymic or ""},
    {"header": "Телефон", "getter": lambda u: u.phone_number or ""},
]