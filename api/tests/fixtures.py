import pytest

from api import services


@pytest.fixture
def users():
    user_one = services.User.objects.create(
        username="walterwhite",
        name="Walter Hartwell White",
        email="walter@graymatter.tech",
        password="albuquerque1992",
        is_active=True,
    )

    user_two = services.User.objects.create(
        username="jessepinkman",
        name="Jesse Bruce Pinkman",
        email="jesseyo@outlook.com",
        password="therealog",
        is_active=True,
    )

    return user_one, user_two
