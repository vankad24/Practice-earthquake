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
        raise HTTPException(status_code=400, detail="Email already registered")
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
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/user/get", response_model=schemas.User)
async def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/user/{user_id}/file/upload")
async def upload_file(user_id: int, data_start_date:int, data_end_date:int, file: UploadFile):

    if not crud.user_exist(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with id '{user_id}' not found")
    if crud.file_exist(user_id, file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File '{file.filename}' already uploaded")

    crud.save_user_file(user_id, file, data_start_date, data_end_date)
    try:
        await storage.save_user_file(user_id, file)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"There was an error uploading the file")

    return {"message": f"The file '{file.filename}' was uploaded"}

# @app.get("/user/{user_id}/file/download", response_class=FileResponse)
# async def download_file(user_id: int, file_name: str):
#     return "files/"+path

#todo сделать путь "/user/{user_id}/files"
@app.post("/users/{user_name}/files", response_model=list[schemas.File])
async def get_user_files_list(user_name, from_date, to_date, limit, db: Session = Depends(get_db)):
    """ from_date and to_date accepts only the following format: yyyy-mm-dd hh:mm:ss (ex. 2020-12-01 12:39:48) """
    try:
        user_id = crud.get_id_by_user_name(db, user_name)
    except crud.UserNotExist: #todo удалить это исключение
        raise HTTPException(status_code=404, detail="User doesn't exist")
    return crud.get_user_files_list(db, user_id, from_date, to_date, limit)

# @app.get("/files/", response_model=list[schemas.File])
# def read_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     files = crud.get_files(db, skip=skip, limit=limit)
#     return files




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)  # , reload=True)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # http://127.0.0.1:8000/docs
