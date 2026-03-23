# tests:
# - successful login with valid data;
# - failed login with invalid data;
# - incrementing attempt counter on failed login;
# - user blocking after 3 failed attempts;
# - blocked user cannot login;
# - successful login resets attempt counter
# uses pytest and pytest-qt for Qt widget testing.