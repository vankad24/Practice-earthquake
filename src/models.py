from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    user_name = Column(String, unique=True)
    hashed_password = Column(String)
    # token = Column(String)
    files = relationship("File", back_populates="user")


# Эта штука нужна, чтоб все правильно работало. Как работает, не понял
dt = DATETIME(storage_format="%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d",
              regexp=r"(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    # data_start_date = Column(dt)
    # data_end_date = Column(dt)
    upload_date = Column(dt)
    author_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="files")

# read about relationship, class Config in schemas

class GenFile(Base):
    __tablename__ = "gen_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))


