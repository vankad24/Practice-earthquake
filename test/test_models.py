import pytest
from alchemy.models import User, Item


class TestUser:
    def test_create_user(self):
        user = User()
        user.email = "a@mail.ru"

