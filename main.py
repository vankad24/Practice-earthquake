from fastapi import Depends, FastAPI, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src import crud, models, schemas
from src.storage import FileStorage
from src.database import SessionLocal, engine
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

storage: FileStorage = FileStorage()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/create", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    created_user = crud.create_user(db=db, user=user)
    storage.create_user_folder(created_user.id)
    return created_user


@app.get("/users/", response_model=list[schemas.User])
def get_users_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/user/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return db_user


@app.post("/user/get", response_model=schemas.User)
async def get_user_by_email(user: schemas.UserBase, db: Session = Depends(get_db)):
    """
        Я заменил email на user (UserBase) и тест заработал
        https://stackoverflow.com/questions/59929028/python-fastapi-error-422-with-post-request-when-sending-json-data
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return db_user


# @app.post("/user/get", response_model=schemas.User)
# async def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=email)
#     if db_user is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
#     return db_user


@app.post("/user/{user_id}/file/upload")
async def upload_file(user_id: int, data_start_date: str, data_end_date: str, file: UploadFile,
                      db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with id '{user_id}' not found")
    db_file = crud.get_file(db, user_id, file.filename)
    if db_file is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File '{file.filename}' already uploaded")

    crud.save_user_file(db, user_id, file, data_start_date, data_end_date)
    try:
        await storage.save_uploaded_file(user_id, file)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"There was an error uploading the file")

    return {"message": f"The file '{file.filename}' was uploaded"}


# @app.get("/user/{user_id}/file/download", response_class=FileResponse)
# async def download_file(user_id: int, file_name: str):
#     return "files/"+path


@app.post("/user/{user_id}/files", response_model=list[schemas.File])
async def get_user_files_list(user_id: int, from_date, to_date, limit, db: Session = Depends(get_db)):
    """ from_date and to_date accepts only the following format: yyyy-mm-dd hh:mm:ss (ex. 2020-12-01 12:39:48) """
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist")
    return crud.get_user_files_list(db, user_id, from_date, to_date, limit)


@app.get("/user/{user_id}/generate", response_class=FileResponse)
def generate_images_from_file(user_id: int, file_name: str, db: Session = Depends(get_db)):
    db_file = crud.get_file(db, user_id, file_name)
    if db_file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File not found")

    if not db_file.image_generated:
        pass
        # generate_images()
        # storage.save_images()

    return "path/to/images"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)  # , reload=True)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # http://127.0.0.1:8000/docs
