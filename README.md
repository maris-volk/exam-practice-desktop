# exam-practice-desktop
Десктопное приложение на PyQt5 для авторизации пользователей с интерактивной капчей в виде пазла из четырех фрагментов. Поддерживаемые роли: Администратор и Пользователь.

## Требования

- Python 3.11
- PostgreSQL 16 или выше

## Установка и запуск

### Клонирование репозитория

```bash
git clone https://github.com/maris-volk/exam-practice-desktop
cd project
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка базы данных
Создать базу данных PostgreSQL и настроить подключение в файле database/db_session.py:
```bash
DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/dbname"
```
