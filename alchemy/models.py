from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    user_name = Column(String, unique=True)
    hashed_password = Column(String)

    files = relationship("File", back_populates="user")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, unique=True)
    data_start_date = Column(DATETIME)
    data_end_date = Column(DATETIME)
    upload_date = Column(DATETIME)
    author_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="files")
