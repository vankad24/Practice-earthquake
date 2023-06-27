from pydantic import BaseModel, EmailStr


class ItemBase(BaseModel):
    file_name: str


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    items: list[Item] = []

    class Config:
        orm_mode = True