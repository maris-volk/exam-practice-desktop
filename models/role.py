# sqlachemy orm model for the "user" table
# fields: id (PK), login, password (hashed), role_id (FK to roles),
#         last_name, first_name, patronymic, phone_number, login_attempts
# includes relationship to Role model