from pydantic import BaseModel, EmailStr
from datetime import datetime


class FileBase(BaseModel):
    file_name: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    # data_start_date: datetime
    # data_end_date: datetime
    upload_date: datetime
    author_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    files: list[File] = []

    class Config:
        orm_mode = True

class Epicenter(BaseModel):
    lat: float
    lon: float
    time: datetime

class Params(BaseModel):
    epicenter: Epicenter

class GenerateParams(Params):
    file_names: list[str]
    times: list[datetime]

class GenerateDistanceParams(Params):
    file_name: str
