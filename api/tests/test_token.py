import pytest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.serializers import CustomTokenObtainPairSerializer

from unittest.mock import MagicMock

from fixtures import users


JWT_TOKEN = {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU5NTIzMjMxMCwianRpIjoiMTViM2ZiZGNhODJlNDBiMDkyNTBiYzA5ZTlkODQwMmYiLCJ1c2VyX2lkIjoxfQ.3UZIhcS4X14zb9V7wRnf0G3TJ1f7G6UMijThokvOD_M",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTk1MTQ1OTIyLCJqdGkiOiI1ODBjNmM3ZDcyNTk0NmJmOWJiNGY1YmMyMzcyMjY0MiIsInVzZXJfaWQiOjF9.44RKjIbKXmWqjzJA0TtpbnBTt3-3tAMxUP1EZDMJais",
}

TokenObtainPairSerializer.validate = MagicMock(return_value=JWT_TOKEN)


@pytest.mark.django_db
def test_custom_jwt_token(users):
    user_one, _ = users

    custom_token_serializer = CustomTokenObtainPairSerializer()
    custom_token_serializer.user = user_one

    data = custom_token_serializer.validate("foo")

    assert data.get("refresh", {}) == JWT_TOKEN["refresh"]
    assert data.get("access", {}) == JWT_TOKEN["access"]
    assert data.get("name", {}) == user_one.username
    assert data.get("active", {}) == user_one.active
