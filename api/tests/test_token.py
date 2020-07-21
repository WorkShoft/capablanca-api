import pytest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.serializers import CustomTokenObtainPairSerializer

from unittest.mock import MagicMock

from fixtures import JWT_TOKEN, users


TokenObtainPairSerializer.validate = MagicMock(return_value=JWT_TOKEN)


@pytest.mark.django_db
def test_custom_jwt_token(users):
    user_one, _ = users

    custom_token_serializer = CustomTokenObtainPairSerializer()
    custom_token_serializer.user = user_one

    data = custom_token_serializer.validate("foo")

    assert data.get("refresh", "") == JWT_TOKEN["refresh"]
    assert data.get("access", "") == JWT_TOKEN["access"]
    assert data.get("name", "") == user_one.username
    assert data.get("active", "") == user_one.active
