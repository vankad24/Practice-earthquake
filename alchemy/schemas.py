from pydantic import BaseModel, EmailStr


class FileBase(BaseModel):
    file_name: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int

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
