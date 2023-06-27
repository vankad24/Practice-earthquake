from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    user_name = Column(String, unique=True)
    hashed_password = Column(String)

    items = relationship("Item", back_populates="user")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    path_to_file = Column(String, unique=True)
    data_start_date = Column(DATETIME)
    data_end_date = Column(DATETIME)
    upload_date = Column(DATETIME)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="items")
