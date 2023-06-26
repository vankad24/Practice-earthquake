from fastapi import FastAPI
from pydantic import EmailStr, BaseModel  # poetry add pydantic[email]
from fastapi import File, UploadFile

api = FastAPI()


@api.get("/")
async def index():
    # print("Hello")
    return {"Msg": "I am /"}


@api.get("/page")
async def index(name: str | None = None):
    if name:
        return {"Msg": f"I am page and you are {name}"}
    else:
        return {f"Msg": "I am page and you are None"}


@api.post("/create-user")
async def create_user(name: str, mail: EmailStr):
    return {f"Msg": f"I am create-user and you are {name} and your email is {mail}"}


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserIn(UserBase):
    passwd: str


class UserOut(UserBase):
    pass


@api.post("/create-user-model", response_model=UserOut)
async def create_user(user: UserIn):
    return user


def register_user(name, email):
    ...


@api.post("/upload")
async def upload_data(user_name: UserIn, file: UploadFile):
    filename = file.filename
    user = user_name
    file = file.file
    return {"Msg": [filename]}

# inside your environment
# pip install poetry

# poetry init
# here it goes the installation process. As a result, poetry will generate a toml file with a dependencies config
# toml looks like this:
# [tool.poetry]
# name = "project"
# version = "0.1.0"
# description = ""
# authors = ["Sergei <monyaksergey@mail.ru>"]
# license = "MIT"
# readme = "README.md"

# [tool.poetry.dependencies]
# python = ">=3.10"
# fastapi = "^0.97.0"
# uvicorn = {extras = ["standart"], version = "^0.22.0"}
# pydantic = {extras = ["email"], version = "^1.10.9"}


# [build-system]
# requires = ["poetry-core"]
# build-backend = "poetry.core.masonry.api"


# how do you work with poetry
# poetry add package/lib  # uvicorn for example
# start uvicorn app.main:api --reload  #--port  # start the fastapi server

# domain:port/redoc - api docs generator
# domain:port/docs - swagger ui to test your
