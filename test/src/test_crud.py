import src.crud
import pytest
from sqlalchemy.orm import Session

from src.models import User
from src.database import SessionLocal, Base, engine


class TestCRUD:
    def setup_class(self):
        # opens up a connection to the database which will last until all test are done
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        self.valid_user = User(
            user_name="testuser",
            email="test@gmail.com",
            hashed_password="password"
        )

    def test_get_user_by_id(self):
        self.db.add(self.valid_user)
        print("database info", self.db.info)
        self.db.commit()
        print("Hey")
        # self.db.query(User).filter(User.user_name == self.valid_user.user_name).first()
        # print(self.valid_user)
        # assert User.user_name.key == self.valid_user.user_name
        # assert User.email == self.valid_user.email
        # assert User.hashed_password == self.valid_user.hashed_password

    def teardown_class(self):
        # closes the connection when all tests are done
        self.db.rollback()
        self.db.close()
